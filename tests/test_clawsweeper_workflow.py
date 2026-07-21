from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "clawsweeper-command.yml"


def authorization_script() -> str:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    step = lines.index("      - name: Validate review request")
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


class ClawSweeperReusableWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.script = authorization_script()

    def run_case(self, body: str, *, prior_verdict: bool = False) -> bool:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp)
            mock_bin = root / "bin"
            mock_bin.mkdir()
            gh = mock_bin / "gh"
            gh.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    if [ "${MOCK_PRIOR_VERDICT:-0}" = 1 ]; then
                      printf '%s\\n' 'clawsweeper-verdict: clean'
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
        }
        for body, expected in cases.items():
            with self.subTest(body=body):
                self.assertEqual(self.run_case(body), expected)

    def test_rereview_requires_prior_bot_verdict(self) -> None:
        self.assertTrue(self.run_case("@clawsweeper re-review", prior_verdict=True))
        self.assertFalse(self.run_case("@clawsweeper re-review", prior_verdict=False))
        self.assertFalse(
            self.run_case("do not @clawsweeper re-review", prior_verdict=True)
        )

    def test_public_repo_authorization_stays_off_spark(self) -> None:
        self.assertIn("authorize:\n", self.workflow)
        self.assertIn("runs-on: ubuntu-latest", self.workflow)
        self.assertIn("needs: authorize", self.workflow)
        self.assertIn(
            "runs-on: [self-hosted, spark-2, clawsweeper-dinkuskit]",
            self.workflow,
        )
        self.assertNotIn("actions/checkout", self.workflow)
        self.assertIn("CLAWSWEEPER_COMMAND_LOCK_HELD=1", self.workflow)


if __name__ == "__main__":
    unittest.main()
