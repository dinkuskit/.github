#!/usr/bin/env ruby
# frozen_string_literal: true

# pin-audit: fail when a workflow pins an external reusable workflow, action,
# skill or runtime to a commit SHA that is not listed in reviewed-pins.json.
#
# A pin is any external `uses: owner/repo[/path]@<40-hex>` and any step that
# checks out another repository with a literal `repository:` and a 40-hex
# `ref:`. Mutable refs (tags, branches) are not pins and are out of scope.
#
# For every unreviewed pin the source repository is fetched and a diff from
# the last reviewed SHA of that repository (or the full tree when none is
# reviewed) is written to --diff-dir so reviewers can inspect it.

require "fileutils"
require "json"
require "open3"
require "optparse"
require "tmpdir"
require "yaml"

module PinAudit
  RULE = "unreviewed-external-pin"
  SHA = /\A[0-9a-f]{40}\z/.freeze
  REPOSITORY = %r{\A[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\z}.freeze
  USES = %r{\A([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(/[^@]*)?@([^@\s]+)\z}.freeze
  DEFAULT_GIT_BASE = "https://github.com/"

  Pin = Struct.new(:file, :line, :repository, :sha, :reference, keyword_init: true)
  Finding = Struct.new(:file, :line, :message, keyword_init: true)

  class ManifestError < StandardError; end

  module_function

  # Returns { "owner/repo" (downcased) => [sha, ...] } in manifest order.
  def load_manifest(path)
    data = JSON.parse(File.read(path))
    raise ManifestError, "#{path}: expected \"schema\": 1" unless data.is_a?(Hash) && data["schema"] == 1
    pins = data["pins"]
    raise ManifestError, "#{path}: \"pins\" must be an array" unless pins.is_a?(Array)

    reviewed = Hash.new { |h, k| h[k] = [] }
    pins.each_with_index do |entry, index|
      where = "#{path}: pins[#{index}]"
      raise ManifestError, "#{where} must be an object" unless entry.is_a?(Hash)
      repository = entry["repository"]
      sha = entry["sha"]
      review = entry["review"]
      raise ManifestError, "#{where}: \"repository\" must be owner/repo" unless repository.is_a?(String) && REPOSITORY.match?(repository)
      raise ManifestError, "#{where}: \"sha\" must be a lowercase 40-hex commit SHA" unless sha.is_a?(String) && SHA.match?(sha)
      raise ManifestError, "#{where}: \"review\" must link the review that approved this SHA" unless review.is_a?(String) && !review.strip.empty?
      key = repository.downcase
      raise ManifestError, "#{where}: duplicate #{repository}@#{sha}" if reviewed[key].include?(sha)
      reviewed[key] << sha
    end
    reviewed
  rescue JSON::ParserError => e
    raise ManifestError, "#{path}: #{e.message}"
  end

  def workflow_files(paths)
    paths.flat_map do |path|
      if File.directory?(path)
        Dir.glob(File.join(path, "**", "*.{yml,yaml}")).sort
      else
        [path]
      end
    end
  end

  # Raw YAML scalar: keeps the source text so a SHA such as 1234e5... or an
  # all-digit SHA is never coerced to a number and skipped.
  Scalar = Struct.new(:value, :line)

  def collect_pins(file)
    doc = Psych.parse(File.read(file), filename: file)
    pins = []
    each_step_like(doc && to_tree(doc.root, {})) do |node|
      add_uses_pin(pins, file, node["uses"])
      add_checkout_pin(pins, file, node["with"])
    end
    pins
  end

  # Converts the Psych AST to Hashes/Arrays of raw Scalars, resolving aliases.
  def to_tree(node, anchors)
    tree =
      case node
      when Psych::Nodes::Alias then return anchors[node.anchor]
      when Psych::Nodes::Mapping
        node.children.each_slice(2).each_with_object({}) do |(key, value), hash|
          hash[key.value] = to_tree(value, anchors) if key.is_a?(Psych::Nodes::Scalar)
        end
      when Psych::Nodes::Sequence then node.children.map { |child| to_tree(child, anchors) }
      when Psych::Nodes::Scalar then Scalar.new(node.value, node.start_line + 1)
      end
    anchors[node.anchor] = tree if node.respond_to?(:anchor) && node.anchor
    tree
  end

  # Yields every job and step mapping in a workflow or composite action.
  def each_step_like(doc)
    return unless doc.is_a?(Hash)
    jobs = doc["jobs"]
    if jobs.is_a?(Hash)
      jobs.each_value do |job|
        next unless job.is_a?(Hash)
        yield job
        steps = job["steps"]
        steps.each { |step| yield step if step.is_a?(Hash) } if steps.is_a?(Array)
      end
    end
    runs = doc["runs"]
    steps = runs["steps"] if runs.is_a?(Hash)
    steps.each { |step| yield step if step.is_a?(Hash) } if steps.is_a?(Array)
  end

  def add_uses_pin(pins, file, uses)
    return unless uses.is_a?(Scalar)
    reference = uses.value.strip
    match = USES.match(reference)
    return unless match && SHA.match?(match[3])
    pins << Pin.new(file: file, line: uses.line, repository: match[1], sha: match[3], reference: reference)
  end

  def add_checkout_pin(pins, file, with)
    return unless with.is_a?(Hash) && with["repository"].is_a?(Scalar) && with["ref"].is_a?(Scalar)
    repository = with["repository"].value.strip
    sha = with["ref"].value.strip
    return unless REPOSITORY.match?(repository) && SHA.match?(sha)
    pins << Pin.new(file: file, line: with["ref"].line, repository: repository, sha: sha,
                    reference: "#{repository}@#{sha} (checkout)")
  end

  def unreviewed(pins, reviewed)
    pins.reject { |pin| reviewed[pin.repository.downcase].include?(pin.sha) }
  end

  # Fetches the pinned source and writes a reviewable diff. Returns the diff
  # path, or raises with a reason when the source cannot be fetched.
  def write_source_diff(pin, reviewed, diff_dir, git_base: DEFAULT_GIT_BASE, token: nil)
    FileUtils.mkdir_p(diff_dir)
    base = reviewed[pin.repository.downcase].last
    url = "#{git_base}#{pin.repository}.git"
    name = "#{pin.repository.sub('/', '__')}__#{pin.sha[0, 12]}.diff"
    path = File.join(diff_dir, name)
    Dir.mktmpdir("pin-audit-") do |dir|
      git(dir, token, "init", "--quiet", "--bare", ".")
      git(dir, token, "fetch", "--quiet", "--no-tags", url, pin.sha)
      from = base
      begin
        git(dir, token, "fetch", "--quiet", "--no-tags", url, base) if base
      rescue RuntimeError
        from = nil
      end
      header = +"# #{RULE}: #{pin.reference}\n"
      header << "# source: #{pin.repository}\n"
      header << (from ? "# diff: last reviewed #{from}..#{pin.sha}\n" : "# diff: full tree at #{pin.sha} (no reviewed baseline)\n")
      header << git(dir, token, "log", "-1", "--format=# commit %H%n# author %an <%ae>%n# date %cI%n# subject %s", pin.sha)
      from ||= git(dir, token, "hash-object", "-w", "-t", "tree", "--stdin", stdin_data: "").strip
      body = git(dir, token, "diff", "--stat", "--patch", "--binary", from, pin.sha)
      File.write(path, header + "\n" + body)
    end
    path
  end

  def git(dir, token, *args, stdin_data: "")
    env = { "GIT_TERMINAL_PROMPT" => "0" }
    if token && !token.empty?
      # Passed through the environment so the token never appears in argv.
      env["GIT_CONFIG_COUNT"] = "1"
      env["GIT_CONFIG_KEY_0"] = "http.extraHeader"
      env["GIT_CONFIG_VALUE_0"] = "Authorization: Basic #{["x-access-token:#{token}"].pack('m0')}"
    end
    out, err, status = Open3.capture3(env, "git", "-C", dir, *args, stdin_data: stdin_data)
    raise RuntimeError, "git #{args.first} failed: #{err.lines.last&.strip}" unless status.success?
    out
  end

  def run(paths, manifest:, diff_dir: nil, git_base: DEFAULT_GIT_BASE, token: nil, out: $stdout)
    reviewed = load_manifest(manifest)
    pins = workflow_files(paths).flat_map { |file| collect_pins(file) }
    findings = unreviewed(pins, reviewed).map do |pin|
      detail =
        if diff_dir
          begin
            "source diff: #{File.basename(write_source_diff(pin, reviewed, diff_dir, git_base: git_base, token: token))}"
          rescue RuntimeError => e
            "source could not be fetched (#{e.message})"
          end
        end
      message = "#{pin.reference} pins #{pin.repository} to #{pin.sha}, which is not listed in reviewed-pins.json; " \
                "review the source and add it to dinkuskit/.github reviewed-pins.json"
      message += " (#{detail})" if detail
      Finding.new(file: pin.file, line: pin.line, message: message)
    end
    out.puts "pin-audit: #{pins.size} pin(s) checked, #{findings.size} unreviewed"
    findings
  end

  def main(argv)
    options = { manifest: nil, diff_dir: nil }
    parser = OptionParser.new do |o|
      o.banner = "usage: pin_audit.rb --manifest reviewed-pins.json [--diff-dir DIR] [PATH...]"
      o.on("--manifest PATH") { |v| options[:manifest] = v }
      o.on("--diff-dir DIR") { |v| options[:diff_dir] = v }
    end
    paths = parser.parse(argv)
    abort parser.banner unless options[:manifest]
    paths = [".github/workflows", ".github/actions"].select { |p| File.exist?(p) } if paths.empty?

    findings = run(paths, manifest: options[:manifest], diff_dir: options[:diff_dir],
                          git_base: ENV.fetch("PIN_AUDIT_GIT_BASE", DEFAULT_GIT_BASE),
                          token: ENV["PIN_AUDIT_FETCH_TOKEN"])
    findings.each { |f| puts "::error file=#{f.file},line=#{f.line},title=#{RULE}::#{f.message}" }
    findings.empty? ? 0 : 1
  rescue ManifestError, Psych::SyntaxError => e
    puts "::error title=#{RULE}::#{e.message}"
    1
  end
end

exit PinAudit.main(ARGV) if $PROGRAM_NAME == __FILE__
