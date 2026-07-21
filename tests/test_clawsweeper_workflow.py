from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parent


def resolve_workflow(root: Path) -> Path:
    """Resolve both the spark-dgx apply pack and deployed .github layout."""
    pack_workflow = root / "reusable-clawsweeper-command.yml"
    deployed_workflow = root.parent / ".github" / "workflows" / "clawsweeper-command.yml"
    return pack_workflow if pack_workflow.is_file() else deployed_workflow


WORKFLOW = resolve_workflow(ROOT)


def authorization_script() -> str:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    step = lines.index("      - name: Validate standalone command")
    run = lines.index("        run: |", step)
    body: list[str] = []
    for line in lines[run + 1 :]:
        if line.startswith("      - name:"):
            break
        body.append(line[10:] if line.startswith(" " * 10) else "")
    script = "\n".join(body).strip()
    if not script:
        raise AssertionError("authorization script not found")
    return script


def named_step(name: str) -> str:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    marker = f"      - name: {name}"
    start = lines.index(marker)
    body = [lines[start]]
    for line in lines[start + 1 :]:
        if line.startswith("      - name:") or re.match(r"^  [a-zA-Z0-9_-]+:$", line):
            break
        body.append(line)
    return "\n".join(body)


def named_job(name: str) -> str:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    marker = f"  {name}:"
    start = lines.index(marker)
    body = [lines[start]]
    for line in lines[start + 1 :]:
        if re.match(r"^  [a-zA-Z0-9_-]+:$", line):
            break
        body.append(line)
    return "\n".join(body)


def run_scripts() -> list[str]:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    scripts: list[str] = []
    for index, line in enumerate(lines):
        if line != "        run: |":
            continue
        body: list[str] = []
        for candidate in lines[index + 1 :]:
            if candidate and not candidate.startswith(" " * 10):
                break
            body.append(candidate[10:] if candidate.startswith(" " * 10) else "")
        scripts.append("\n".join(body))
    return scripts


class ClawSweeperPathBWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.script = authorization_script()

    def run_case(
        self,
        body: str,
        *,
        prior_verdict: bool = False,
        prior_same_head: bool = False,
    ) -> bool:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp)
            mock_bin = root / "bin"
            mock_bin.mkdir()
            gh = mock_bin / "gh"
            gh.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    if [[ "$*" == *"pulls/7"* && "$*" == *".head.sha"* ]]; then
                      printf '%s\\n' 'abc123'
                    elif [[ "$*" == *"issues/7/comments"* ]]; then
                      if [ "${MOCK_PRIOR_VERDICT:-0}" = 1 ]; then
                        printf '%s\\n' 'clawsweeper-verdict: clean'
                      fi
                      if [ "${MOCK_PRIOR_SAME_HEAD:-0}" = 1 ]; then
                        printf '%s\\n' '<!-- clawsweeper-hosted path-b model=gpt-5.6-terra head=abc123 -->'
                      fi
                    fi
                    """
                ),
                encoding="utf-8",
            )
            gh.chmod(0o755)
            output = root / "github-output"
            env = os.environ.copy()
            env.update(
                {
                    "COMMENT_BODY": body,
                    "GITHUB_OUTPUT": str(output),
                    "MOCK_PRIOR_VERDICT": "1" if prior_verdict else "0",
                    "MOCK_PRIOR_SAME_HEAD": "1" if prior_same_head else "0",
                    "PATH": f"{mock_bin}{os.pathsep}{env['PATH']}",
                    "PR": "7",
                    "REPO": "dinkuskit/blocks",
                }
            )
            result = subprocess.run(
                ["bash", "-c", self.script],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            values = output.read_text(encoding="utf-8").splitlines()
            return values[-1] == "review_requested=true"

    def test_primary_command_is_standalone_and_case_insensitive(self) -> None:
        cases = {
            "@clawsweeper review": True,
            "  @CLAWSWEEPER REVIEW  ": True,
            "context\n@ClawSweeper Review\nproof": True,
            "please do not run @clawsweeper review yet": False,
            "@clawsweeper review please": False,
            "unrelated": False,
            "@clawsweeper hosted-review": False,
        }
        for body, expected in cases.items():
            with self.subTest(body=body):
                self.assertEqual(self.run_case(body), expected)

    def test_rereview_requires_prior_verdict(self) -> None:
        self.assertTrue(self.run_case("@clawsweeper re-review", prior_verdict=True))
        self.assertFalse(self.run_case("@clawsweeper re-review", prior_verdict=False))

    def test_primary_review_is_deduplicated_per_head(self) -> None:
        self.assertFalse(
            self.run_case("@clawsweeper review", prior_same_head=True)
        )

    def test_workflow_path_resolves_after_pack_is_deployed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            repo = Path(raw_temp)
            tests_dir = repo / "tests"
            deployed = repo / ".github" / "workflows" / "clawsweeper-command.yml"
            tests_dir.mkdir()
            deployed.parent.mkdir(parents=True)
            deployed.write_text("name: test\n", encoding="utf-8")
            self.assertEqual(resolve_workflow(tests_dir), deployed)

    def test_path_b_stays_github_hosted_only(self) -> None:
        self.assertEqual(self.workflow.count("runs-on: ubuntu-latest"), 3)
        # No self-hosted runner labels (comment text may still say "no Spark self-hosted").
        self.assertNotIn("runs-on: [self-hosted", self.workflow)
        self.assertNotIn("spark-2, clawsweeper-dinkuskit", self.workflow)
        self.assertNotIn("clawsweeper-dinkuskit]", self.workflow)
        self.assertIn("gpt-5.6-terra", self.workflow)
        self.assertIn("CONTRIBUTOR", self.workflow)
        self.assertIn("COPILOT_GITHUB_TOKEN", self.workflow)
        self.assertIn("@github/copilot@1.0.73", self.workflow)

    def test_model_job_has_no_repository_token_or_mutation_tools(self) -> None:
        model_job = named_job("review")
        model_step = named_step("Run credential-isolated Copilot review")

        self.assertIn("permissions: {}", model_job)
        self.assertIn("COPILOT_GITHUB_TOKEN", model_step)
        for forbidden in (
            "${{ github.token }}",
            "\n          GH_TOKEN:",
            "\n          GITHUB_TOKEN:",
            "--allow-tool",
            "--yolo",
            "shell(git",
            "shell(gh",
            "gh api",
            "gh pr",
            "git ",
        ):
            self.assertNotIn(forbidden, model_step)

        self.assertIn("env -i", model_step)
        self.assertIn("--disable-builtin-mcps", model_step)
        self.assertIn("--deny-tool='shell,write,url,read,memory'", model_step)
        self.assertIn("--no-custom-instructions", model_step)
        self.assertIn("--no-bash-env", model_step)
        self.assertNotIn('tail ', model_step)
        self.assertNotIn('cat "$error_log"', model_step)

    def test_deterministic_jobs_own_github_reads_and_publish(self) -> None:
        prepare = named_step("Prepare immutable review request")
        publish = named_step("Publish exact-head advisory comment")

        self.assertIn("GH_TOKEN: ${{ github.token }}", prepare)
        self.assertNotIn("COPILOT_GITHUB_TOKEN", prepare)
        self.assertIn("GH_TOKEN: ${{ github.token }}", publish)
        self.assertNotIn("COPILOT_GITHUB_TOKEN", publish)
        self.assertNotIn('> "$out_dir/pr.diff" || true', prepare)

        head_check = publish.index('current_head="$(gh api')
        stale_compare = publish.index('[ "$current_head" != "$PREPARED_HEAD" ]')
        comment = publish.index('gh pr comment "$PR" --repo "$REPO" --body-file')
        self.assertLess(head_check, stale_compare)
        self.assertLess(stale_compare, comment)

    def test_model_output_is_bounded_and_contract_checked(self) -> None:
        model_step = named_step("Run credential-isolated Copilot review")
        publish = named_step("Publish exact-head advisory comment")
        self.assertIn('[ "$review_bytes" -gt 50000 ]', model_step)
        self.assertIn("verdict_count", model_step)
        self.assertIn("final_line", model_step)
        self.assertIn("Prevent model-authored GitHub @-mentions", model_step)
        self.assertIn('[ "$body_bytes" -gt 60000 ]', publish)

    def test_supply_chain_inputs_are_exactly_pinned(self) -> None:
        self.assertIn(
            "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020",
            self.workflow,
        )
        self.assertIn(
            "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
            self.workflow,
        )
        self.assertIn(
            "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093",
            self.workflow,
        )

    def test_every_inline_shell_script_parses(self) -> None:
        scripts = run_scripts()
        self.assertGreaterEqual(len(scripts), 8)
        for index, script in enumerate(scripts):
            with self.subTest(index=index):
                parsed = subprocess.run(
                    ["bash", "-n"],
                    input=script,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(parsed.returncode, 0, parsed.stderr)


if __name__ == "__main__":
    unittest.main()
