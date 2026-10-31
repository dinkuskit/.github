# frozen_string_literal: true

require "fileutils"
require "json"
require "minitest/autorun"
require "open3"
require "stringio"
require "tmpdir"
require_relative "../scripts/pin_audit"

class PinAuditTest < Minitest::Test
  ROOT = File.expand_path("..", __dir__)
  FIXTURES = File.join(__dir__, "fixtures", "pin-audit")
  SCRIPT = File.join(ROOT, "scripts", "pin_audit.rb")
  MANIFEST = File.join(FIXTURES, "reviewed-pins.json")

  def fixture(name)
    File.join(FIXTURES, name)
  end

  def findings(name, **options)
    PinAudit.run([fixture(name)], manifest: MANIFEST, out: StringIO.new, **options)
  end

  def git(dir, *args)
    out, err, status = Open3.capture3("git", "-C", dir, *args)
    raise "git #{args.join(' ')}: #{err}" unless status.success?
    out.strip
  end

  # A local bare repository standing in for a pinned GitHub source.
  def source_repo(root, repository)
    work = File.join(root, "work", repository)
    FileUtils.mkdir_p(work)
    git(work, "init", "--quiet")
    git(work, "config", "user.email", "fixture@example.invalid")
    git(work, "config", "user.name", "fixture")
    commit = lambda do |content, subject|
      File.write(File.join(work, "action.yml"), content)
      git(work, "add", "action.yml")
      git(work, "commit", "--quiet", "-m", subject)
      git(work, "rev-parse", "HEAD")
    end
    reviewed = commit.call("runs: reviewed\n", "reviewed release")
    pinned = commit.call("runs: pinned-change\n", "unreviewed release")
    bare = File.join(root, "remote", "#{repository}.git")
    FileUtils.mkdir_p(File.dirname(bare))
    git(root, "clone", "--quiet", "--bare", work, bare)
    git(bare, "config", "uploadpack.allowReachableSHA1InWant", "true")
    [reviewed, pinned]
  end

  def write_manifest(dir, pins)
    path = File.join(dir, "reviewed-pins.json")
    File.write(path, JSON.generate("schema" => 1, "pins" => pins))
    path
  end

  def test_reviewed_pins_pass_with_case_insensitive_repositories
    assert_empty findings("pass-reviewed-pins.yml")
  end

  def test_local_docker_tag_branch_and_expression_refs_are_not_pins
    assert_empty findings("pass-unpinned-and-local.yml")
  end

  def test_unreviewed_reusable_workflow_is_rejected
    result = findings("fail-unreviewed-reusable-workflow.yml")
    assert_equal 1, result.size
    assert_equal 6, result.first.line
    assert_match(%r{pins dinkuskit/\.github to 4{40}, which is not listed in reviewed-pins\.json}, result.first.message)
  end

  def test_unreviewed_action_is_rejected
    result = findings("fail-unreviewed-action.yml")
    assert_equal ["actions/checkout@#{'5' * 40}"], result.map { |f| f.message[/\A(\S+)/, 1] }
  end

  def test_numeric_looking_skill_checkout_sha_must_be_reviewed_for_its_own_repository
    result = findings("fail-unreviewed-skill-checkout.yml")
    assert_equal 1, result.size
    assert_equal 11, result.first.line
    assert_match(%r{dinkuskit/skills@1{40} \(checkout\) pins dinkuskit/skills}, result.first.message)
  end

  def test_composite_action_runtime_pin_is_rejected
    result = findings("composite/action.yml")
    assert_equal 1, result.size
    assert_match(%r{dinkuskit/runtime/setup@6{40}}, result.first.message)
  end

  def test_directory_scan_finds_every_unreviewed_pin
    result = PinAudit.run([FIXTURES], manifest: MANIFEST, out: StringIO.new)
    assert_equal 4, result.size
  end

  def test_unfetchable_source_still_fails_closed
    Dir.mktmpdir do |dir|
      result = findings("fail-unreviewed-action.yml", diff_dir: File.join(dir, "diffs"), git_base: "file://#{dir}/missing/")
      assert_equal 1, result.size
      assert_match(/source could not be fetched/, result.first.message)
    end
  end

  def test_source_diff_from_last_reviewed_sha_is_written
    Dir.mktmpdir do |dir|
      reviewed, pinned = source_repo(dir, "dinkuskit/runtime")
      manifest = write_manifest(dir, [{ "repository" => "dinkuskit/runtime", "sha" => reviewed, "review" => "fixture" }])
      workflow = File.join(dir, "ci.yml")
      File.write(workflow, "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: dinkuskit/runtime@#{pinned}\n")
      diffs = File.join(dir, "diffs")

      result = PinAudit.run([workflow], manifest: manifest, diff_dir: diffs, git_base: "file://#{dir}/remote/", out: StringIO.new)

      assert_equal 1, result.size
      name = "dinkuskit__runtime__#{pinned[0, 12]}.diff"
      assert_match(/source diff: #{name}/, result.first.message)
      diff = File.read(File.join(diffs, name))
      assert_includes diff, "# diff: last reviewed #{reviewed}..#{pinned}"
      assert_includes diff, "# subject unreviewed release"
      assert_includes diff, "-runs: reviewed"
      assert_includes diff, "+runs: pinned-change"
    end
  end

  def test_source_diff_without_reviewed_baseline_is_full_tree
    Dir.mktmpdir do |dir|
      _reviewed, pinned = source_repo(dir, "dinkuskit/skills")
      manifest = write_manifest(dir, [])
      workflow = File.join(dir, "ci.yml")
      File.write(workflow, "on: push\njobs:\n  a:\n    uses: dinkuskit/skills/.github/workflows/x.yml@#{pinned}\n")
      diffs = File.join(dir, "diffs")

      PinAudit.run([workflow], manifest: manifest, diff_dir: diffs, git_base: "file://#{dir}/remote/", out: StringIO.new)

      diff = File.read(File.join(diffs, "dinkuskit__skills__#{pinned[0, 12]}.diff"))
      assert_includes diff, "# diff: full tree at #{pinned} (no reviewed baseline)"
      assert_includes diff, "+runs: pinned-change"
    end
  end

  def test_manifest_entries_require_a_review_and_full_sha
    Dir.mktmpdir do |dir|
      entry = { "repository" => "a/b", "sha" => "1" * 40, "review" => "x" }
      [
        [[entry.reject { |k, _| k == "review" }], /"review" must link/],
        [[entry.merge("sha" => "abc123")], /40-hex/],
        [[entry.merge("repository" => "checkout")], %r{owner/repo}],
        [[entry, entry], /duplicate/]
      ].each do |pins, pattern|
        path = write_manifest(dir, pins)
        error = assert_raises(PinAudit::ManifestError) { PinAudit.load_manifest(path) }
        assert_match pattern, error.message
      end
    end
  end

  def test_cli_reports_annotations_and_exit_status
    out, _err, status = Open3.capture3("ruby", SCRIPT, "--manifest", MANIFEST, fixture("fail-unreviewed-action.yml"))
    assert_equal 1, status.exitstatus
    assert_match(/^::error file=.*fail-unreviewed-action\.yml,line=8,title=unreviewed-external-pin::/, out)

    out, _err, status = Open3.capture3("ruby", SCRIPT, "--manifest", MANIFEST, fixture("pass-reviewed-pins.yml"))
    assert_equal 0, status.exitstatus, out
    assert_match(/5 pin\(s\) checked, 0 unreviewed/, out)
  end

  def test_repository_manifest_is_valid
    PinAudit.load_manifest(File.join(ROOT, "reviewed-pins.json"))
  end

  def test_repository_workflows_pass
    result = PinAudit.run([File.join(ROOT, ".github", "workflows")], manifest: File.join(ROOT, "reviewed-pins.json"), out: StringIO.new)
    assert_empty result
  end
end
