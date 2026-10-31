#!/usr/bin/env ruby
# frozen_string_literal: true

# Custom actionlint-style rule: secret-bearing-workflow-trigger.
#
# A workflow triggered by pull_request_target or issue_comment runs with the
# base repository's secrets on behalf of any actor who can open a pull request
# or write a comment. When such a workflow calls a reusable workflow and passes
# it secrets (`secrets: inherit` or an explicit mapping), the calling job must
# be gated on a preceding permission check:
#
#   * the calling job lists a gate job directly in `needs`;
#   * the gate job has a step with an `id` that queries the actor's repository
#     permission (`repos/.../collaborators/.../permission` or
#     `getCollaboratorPermissionLevel`);
#   * the gate job exports that step's output in `outputs`;
#   * the calling job's `if` requires `needs.<gate>.outputs.<name> == 'true'`
#     and contains no `||` or `!` negation that could bypass it.
#
# actionlint has no plugin interface, so this rule runs beside it and reports
# findings in actionlint's `path:line:col: message [rule]` format.

require "yaml"

module SecretBearingWorkflowTrigger
  RULE = "secret-bearing-workflow-trigger"
  RISKY_TRIGGERS = %w[pull_request_target issue_comment].freeze
  PERMISSION_QUERY = %r{collaborators/[^\s"']+/permission|getCollaboratorPermissionLevel}.freeze

  Finding = Struct.new(:path, :line, :column, :message) do
    def to_s
      "#{path}:#{line}:#{column}: #{message} [#{RULE}]"
    end
  end

  module_function

  def triggers(workflow)
    on = workflow.key?("on") ? workflow["on"] : workflow[true]
    case on
    when String then [on]
    when Array then on.map(&:to_s)
    when Hash then on.keys.map(&:to_s)
    else []
    end
  end

  def passes_secrets?(job)
    return false unless job.is_a?(Hash) && job["uses"].is_a?(String)

    secrets = job["secrets"]
    secrets == "inherit" || (secrets.is_a?(Hash) && !secrets.empty?)
  end

  def needs(job)
    Array(job["needs"]).map(&:to_s)
  end

  # Returns the ids of steps in a job that query the actor's permission.
  def gate_step_ids(job)
    return [] unless job.is_a?(Hash) && job["steps"].is_a?(Array)

    job["steps"].map do |step|
      next unless step.is_a?(Hash) && step["id"]

      source = [step["run"], step.dig("with", "script")].compact.join("\n")
      step["id"].to_s if source.match?(PERMISSION_QUERY)
    end.compact
  end

  # Returns output names of a gate job that are wired to a permission step.
  def gate_outputs(job)
    outputs = job.is_a?(Hash) ? job["outputs"] : nil
    return [] unless outputs.is_a?(Hash)

    ids = gate_step_ids(job)
    outputs.map do |name, value|
      name.to_s if ids.any? { |id| value.to_s.include?("steps.#{id}.outputs.") }
    end.compact
  end

  def condition_problem(condition, gate_refs)
    text = condition.to_s
    return "has no `if` requiring a permission-gate output" if text.strip.empty?
    return "`if` uses `||`, which can bypass the permission gate" if text.include?("||")
    return "`if` uses `!` negation, which can bypass the permission gate" if text.match?(/!(?!=)/)

    required = gate_refs.any? do |gate, output|
      text.match?(/needs\.#{Regexp.escape(gate)}\.outputs\.#{Regexp.escape(output)}\s*==\s*'true'/)
    end
    return nil if required

    expected = gate_refs.map { |gate, output| "needs.#{gate}.outputs.#{output} == 'true'" }
    if expected.empty?
      "`if` does not require a permission-gate output"
    else
      "`if` does not require #{expected.join(' or ')}"
    end
  end

  def job_lines(text)
    root = Psych.parse(text)&.root
    return {} unless root.is_a?(Psych::Nodes::Mapping)

    jobs = root.children.each_slice(2).find { |key, _| key.respond_to?(:value) && key.value == "jobs" }&.last
    return {} unless jobs.is_a?(Psych::Nodes::Mapping)

    jobs.children.each_slice(2).to_h { |key, _| [key.value.to_s, [key.start_line + 1, key.start_column + 1]] }
  end

  def check_text(path, text)
    workflow = YAML.safe_load(text, aliases: true)
    return [] unless workflow.is_a?(Hash) && workflow["jobs"].is_a?(Hash)

    risky = triggers(workflow) & RISKY_TRIGGERS
    return [] if risky.empty?

    jobs = workflow["jobs"]
    lines = job_lines(text)
    jobs.each_with_object([]) do |(name, job), findings|
      next unless passes_secrets?(job)

      gate_refs = needs(job).flat_map do |gate|
        gate_outputs(jobs[gate]).map { |output| [gate, output] }
      end
      problem =
        if gate_refs.empty?
          "does not `needs` a job whose step checks the actor's repository permission and exports it in `outputs`"
        else
          condition_problem(job["if"], gate_refs)
        end
      next unless problem

      line, column = lines.fetch(name.to_s, [1, 1])
      findings << Finding.new(
        path, line, column,
        "job \"#{name}\" passes secrets to reusable workflow \"#{job['uses']}\" " \
        "on #{risky.join('/')} but #{problem}"
      )
    end
  rescue Psych::Exception => e
    [Finding.new(path, 1, 1, "could not parse workflow: #{e.message}")]
  end

  def check_file(path)
    check_text(path, File.read(path))
  end

  def main(argv)
    paths = argv.empty? ? Dir.glob(".github/workflows/*.{yml,yaml}").sort : argv
    findings = paths.flat_map { |path| check_file(path) }
    findings.each { |finding| puts finding }
    findings.empty? ? 0 : 1
  end
end

exit SecretBearingWorkflowTrigger.main(ARGV) if $PROGRAM_NAME == __FILE__
