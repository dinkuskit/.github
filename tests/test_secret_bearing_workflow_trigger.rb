# frozen_string_literal: true

require "minitest/autorun"
require "open3"
require "tmpdir"
require "yaml"
require_relative "../scripts/secret_bearing_workflow_trigger"

class SecretBearingWorkflowTriggerTest < Minitest::Test
  ROOT = File.expand_path("..", __dir__)
  FIXTURES = File.join(__dir__, "fixtures", "secret-bearing-workflow-trigger")
  SCRIPT = File.join(ROOT, "scripts", "secret_bearing_workflow_trigger.rb")
  RULE = SecretBearingWorkflowTrigger::RULE

  def fixture(name)
    File.join(FIXTURES, name)
  end

  def findings(name)
    SecretBearingWorkflowTrigger.check_file(fixture(name))
  end

  def test_gated_pull_request_target_passes
    assert_empty findings("pass-gated-pull-request-target.yml")
  end

  def test_gated_issue_comment_with_github_script_passes
    assert_empty findings("pass-gated-issue-comment.yml")
  end

  def test_pull_request_trigger_is_out_of_scope
    assert_empty findings("pass-pull-request-not-risky.yml")
  end

  def test_ungated_secrets_inherit_is_rejected
    result = findings("fail-ungated-inherit.yml")
    assert_equal 1, result.size
    assert_equal 8, result.first.line
    assert_match(/job "preview" passes secrets .* on pull_request_target but does not `needs`/, result.first.message)
  end

  def test_gate_not_in_needs_is_rejected
    result = findings("fail-gate-not-needed.yml")
    assert_equal ["command"], result.map { |f| f.message[/job "([^"]+)"/, 1] }
    assert_match(/on issue_comment but does not `needs`/, result.first.message)
  end

  def test_gate_output_not_required_is_rejected
    result = findings("fail-gate-output-unused.yml")
    assert_equal 1, result.size
    assert_match(/has no `if` requiring a permission-gate output/, result.first.message)
  end

  def test_gate_bypass_by_disjunction_is_rejected
    result = findings("fail-gate-bypass.yml")
    assert_equal 1, result.size
    assert_match(/uses `\|\|`/, result.first.message)
  end

  def test_negated_gate_is_rejected
    text = File.read(fixture("pass-gated-pull-request-target.yml")).sub(
      "if: needs.permission-gate.outputs.allowed == 'true'",
      "if: \"!(needs.permission-gate.outputs.allowed == 'true')\""
    )
    result = SecretBearingWorkflowTrigger.check_text("negated.yml", text)
    assert_match(/`!` negation/, result.first&.message)
  end

  def test_removing_needs_from_gated_fixture_is_rejected
    text = File.read(fixture("pass-gated-pull-request-target.yml"))
    ungated = text.sub("    needs: permission-gate\n", "")
    refute_equal text, ungated
    assert_equal 1, SecretBearingWorkflowTrigger.check_text("ungated.yml", ungated).size
  end

  # Proves the gate rejects a non-author before the secret-bearing `uses:` job:
  # the gate step fails and sets allowed=false for actors without write access,
  # and the guard confirms the `uses:` job needs that gate and requires
  # allowed == 'true'.
  def test_non_author_is_rejected_before_uses
    workflow = YAML.safe_load(File.read(fixture("pass-gated-pull-request-target.yml")), aliases: true)
    jobs = workflow.fetch("jobs")
    caller = jobs.fetch("preview")
    assert caller.key?("uses")
    assert_equal ["permission-gate"], SecretBearingWorkflowTrigger.needs(caller)
    assert_equal ["allowed"], SecretBearingWorkflowTrigger.gate_outputs(jobs.fetch("permission-gate"))
    assert_includes caller.fetch("if"), "needs.permission-gate.outputs.allowed == 'true'"

    gate_step = jobs.fetch("permission-gate").fetch("steps").find { |step| step["id"] == "gate" }
    %w[read triage none].each do |permission|
      status, output, calls = run_gate(gate_step.fetch("run"), actor: "mallory", permission: permission)
      refute status.success?, "#{permission} actor must fail the gate"
      assert_equal "allowed=false\n", output
      assert_equal "api repos/dinkuskit/payments/collaborators/mallory/permission --jq .permission\n", calls
    end
    %w[write maintain admin].each do |permission|
      status, output, = run_gate(gate_step.fetch("run"), actor: "maintainer", permission: permission)
      assert status.success?, "#{permission} actor must pass the gate"
      assert_equal "allowed=true\n", output
    end
  end

  def test_cli_reports_actionlint_format_and_exit_status
    out, status = Open3.capture2e("ruby", SCRIPT, fixture("fail-ungated-inherit.yml"), fixture("pass-gated-pull-request-target.yml"))
    assert_equal 1, status.exitstatus
    assert_equal 1, out.lines.size
    assert_match(/fail-ungated-inherit\.yml:8:3: .* \[#{RULE}\]\n\z/, out)

    out, status = Open3.capture2e("ruby", SCRIPT, fixture("pass-gated-issue-comment.yml"))
    assert_equal 0, status.exitstatus
    assert_empty out
  end

  private

  def run_gate(script, actor:, permission:)
    Dir.mktmpdir do |dir|
      bin = File.join(dir, "bin")
      Dir.mkdir(bin)
      File.write(File.join(bin, "gh"), <<~SH)
        #!/usr/bin/env bash
        printf '%s\\n' "$*" >> "$FAKE_GH_CALLS"
        printf '%s\\n' "$FAKE_PERMISSION"
      SH
      File.chmod(0o755, File.join(bin, "gh"))
      output = File.join(dir, "github_output")
      calls = File.join(dir, "gh_calls")
      File.write(output, "")
      File.write(calls, "")
      env = {
        "PATH" => "#{bin}:#{ENV.fetch('PATH')}",
        "GITHUB_OUTPUT" => output,
        "FAKE_GH_CALLS" => calls,
        "FAKE_PERMISSION" => permission,
        "GH_TOKEN" => "",
        "REPO" => "dinkuskit/payments",
        "ACTOR" => actor
      }
      _, status = Open3.capture2e(env, "bash", "-e", "-c", script)
      [status, File.read(output), File.read(calls)]
    end
  end
end
