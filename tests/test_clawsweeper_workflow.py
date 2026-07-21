from __future__ import annotations

import hashlib
import json
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
CALLER = ROOT / "caller-clawsweeper-command.yml"


def source_comment_record(
    body: str,
    *,
    association: str = "OWNER",
    author: str = "alice",
    updated_at: str = "2026-07-21T20:00:00Z",
) -> dict[str, object]:
    return {
        "id": 99,
        "issue_url": "https://api.github.com/repos/dinkuskit/blocks/issues/7",
        "html_url": "https://github.com/dinkuskit/blocks/pull/7#issuecomment-99",
        "user": {"login": author, "type": "User"},
        "author_association": association,
        "updated_at": updated_at,
        "body": body,
    }


def source_comment_hashes(record: dict[str, object]) -> tuple[str, str]:
    body = str(record["body"])
    body_sha = hashlib.sha256(body.encode()).hexdigest()
    user = record["user"]
    assert isinstance(user, dict)
    canonical = {
        "id": str(record["id"]),
        "issue_url": record["issue_url"],
        "html_url": record["html_url"],
        "author": user["login"],
        "author_type": user["type"],
        "association": record["author_association"],
        "updated_at": record["updated_at"],
        "body_sha256": body_sha,
    }
    canonical_bytes = json.dumps(
        canonical, sort_keys=True, separators=(",", ":")
    ).encode() + b"\n"
    digest = hashlib.sha256(
        canonical_bytes
    ).hexdigest()
    return body_sha, digest


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


def step_script(name: str) -> str:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    marker = f"      - name: {name}"
    step = lines.index(marker)
    run = lines.index("        run: |", step)
    body: list[str] = []
    for line in lines[run + 1 :]:
        if line.startswith("      - name:") or re.match(
            r"^  [a-zA-Z0-9_-]+:$", line
        ):
            break
        body.append(line[10:] if line.startswith(" " * 10) else "")
    script = "\n".join(body).strip()
    if not script:
        raise AssertionError(f"script not found for step: {name}")
    return script


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
        association: str = "OWNER",
        daily_reviews: int = 0,
        prior_other_model_same_pair: int = 0,
        prior_same_pair: int = 0,
        prior_other_pairs: int = 0,
        live_body: str | None = None,
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
                    if [[ "$*" == *"issues/comments/99"* ]]; then
                      printf '%s\\n' "$MOCK_SOURCE_COMMENT"
                    elif [[ "$*" == *"pulls/7"* ]]; then
                      printf '%s\\n' '{"head":{"sha":"abc123"},"base":{"sha":"base123"}}'
                    elif [[ "$*" == *"issues/7/comments"* ]]; then
                      printf '%s\\n' "$MOCK_PR_COMMENTS"
                    elif [[ "$*" == *"issues/comments"* ]]; then
                      printf '%s\\n' "$MOCK_REPO_COMMENTS"
                    fi
                    """
                ),
                encoding="utf-8",
            )
            gh.chmod(0o755)
            output = root / "github-output"
            source = source_comment_record(
                body if live_body is None else live_body,
                association=association,
            )
            bot_user = {"login": "dinkuskit-clawsweeper[bot]", "type": "Bot"}
            pr_comments: list[dict[str, object]] = []
            pr_comments.extend(
                {
                    "user": bot_user,
                    "body": "<!-- clawsweeper-hosted path-b model=gpt-5.6-terra base=base123 head=abc123 -->\nclawsweeper-verdict: clean",
                }
                for _ in range(prior_same_pair)
            )
            pr_comments.extend(
                {
                    "user": bot_user,
                    "body": "<!-- clawsweeper-hosted path-b model=other-model base=base123 head=abc123 -->\nclawsweeper-verdict: clean",
                }
                for _ in range(prior_other_model_same_pair)
            )
            pr_comments.extend(
                {
                    "user": bot_user,
                    "body": "<!-- clawsweeper-hosted path-b model=gpt-5.6-terra base=oldbase head=oldhead -->\nclawsweeper-verdict: clean",
                }
                for _ in range(prior_other_pairs)
            )
            review_day = subprocess.run(
                ["date", "-u", "+%F"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            repo_comments = [
                {
                    "user": bot_user,
                    "body": f"<!-- clawsweeper-hosted path-b day={review_day} association=CONTRIBUTOR model=gpt-5.6-terra base=oldbase head=oldhead -->",
                }
                for _ in range(daily_reviews)
            ]
            env = os.environ.copy()
            env.update(
                {
                    "APP_BOT_LOGIN": "dinkuskit-clawsweeper[bot]",
                    "AUTHOR_ASSOCIATION": association,
                    "COMMENT_AUTHOR": "alice",
                    "COMMENT_BODY": body,
                    "COMMENT_ID": "99",
                    "GITHUB_OUTPUT": str(output),
                    "GITHUB_RUN_ATTEMPT": "1",
                    "GITHUB_RUN_ID": "99",
                    "MODEL": "gpt-5.6-terra",
                    "MOCK_PR_COMMENTS": json.dumps(pr_comments),
                    "MOCK_REPO_COMMENTS": json.dumps(repo_comments),
                    "MOCK_SOURCE_COMMENT": json.dumps(source),
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
            return "review_requested=true" in values

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

    def test_edited_triggering_comment_is_not_admitted(self) -> None:
        self.assertFalse(
            self.run_case(
                "@clawsweeper review",
                live_body="command removed after event delivery",
            )
        )

    def test_rereview_is_bounded_to_maintainers_and_current_pair(self) -> None:
        self.assertTrue(
            self.run_case("@clawsweeper re-review", prior_same_pair=1)
        )
        self.assertTrue(
            self.run_case(
                "@clawsweeper re-review", prior_other_model_same_pair=1
            )
        )
        self.assertFalse(self.run_case("@clawsweeper re-review"))
        self.assertFalse(
            self.run_case("@clawsweeper re-review", prior_same_pair=2)
        )
        self.assertFalse(
            self.run_case(
                "@clawsweeper re-review",
                association="CONTRIBUTOR",
                prior_same_pair=1,
            )
        )

    def test_quota_markers_are_read_only_from_comment_first_lines(self) -> None:
        command = named_step("Validate standalone command")
        self.assertEqual(command.count('(.body | split("\\n")[0])'), 2)
        self.assertNotIn("| .body'", command)
        self.assertIn('--arg login "$APP_BOT_LOGIN"', command)
        self.assertNotIn("github-actions[bot]", command)

    def test_primary_review_is_deduplicated_per_base_head_pair(self) -> None:
        self.assertFalse(
            self.run_case("@clawsweeper review", prior_same_pair=1)
        )
        self.assertFalse(
            self.run_case(
                "@clawsweeper review", prior_other_model_same_pair=1
            )
        )

    def test_contributor_receives_one_review_per_pr(self) -> None:
        self.assertTrue(
            self.run_case("@clawsweeper review", association="CONTRIBUTOR")
        )
        self.assertFalse(
            self.run_case(
                "@clawsweeper review",
                association="CONTRIBUTOR",
                prior_other_pairs=1,
            )
        )
        self.assertTrue(
            self.run_case(
                "@clawsweeper review",
                association="OWNER",
                prior_other_pairs=1,
            )
        )

    def test_contributor_daily_allowance_is_repository_bounded(self) -> None:
        self.assertTrue(
            self.run_case(
                "@clawsweeper review",
                association="CONTRIBUTOR",
                daily_reviews=4,
            )
        )
        self.assertFalse(
            self.run_case(
                "@clawsweeper review",
                association="CONTRIBUTOR",
                daily_reviews=5,
            )
        )
        self.assertTrue(
            self.run_case(
                "@clawsweeper review",
                association="OWNER",
                daily_reviews=5,
            )
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
        self.assertIn('raw_review="$tmp_dir/review.raw"', model_step)
        self.assertIn('error_log="$tmp_dir/copilot.stderr"', model_step)
        self.assertNotIn('raw_review="$out_dir/', model_step)
        self.assertNotIn('error_log="$out_dir/', model_step)

    def test_deterministic_jobs_own_github_reads_and_publish(self) -> None:
        prepare = named_step("Prepare immutable review request")
        publish = named_step("Publish exact-head advisory comment")

        self.assertIn("GH_TOKEN: ${{ github.token }}", prepare)
        self.assertNotIn("COPILOT_GITHUB_TOKEN", prepare)
        self.assertIn("GH_TOKEN: ${{ steps.app_token.outputs.token }}", publish)
        self.assertNotIn("COPILOT_GITHUB_TOKEN", publish)
        self.assertNotIn('> "$out_dir/pr.diff" || true', prepare)
        self.assertIn('refs/heads/$base_ref:refs/remotes/origin/clawsweeper-base', prepare)
        self.assertIn('refs/pull/$PR/head:refs/remotes/origin/clawsweeper-head', prepare)
        self.assertIn('merge-base "$base_sha" "$head_sha"', prepare)
        self.assertIn('"$merge_base_sha" "$head_sha"', prepare)
        self.assertIn('--no-ext-diff', prepare)
        self.assertIn('--no-textconv', prepare)
        self.assertNotIn('repos/$REPO/compare/', prepare)
        self.assertIn("AUTHORIZED_HEAD", prepare)
        self.assertIn("AUTHORIZED_BASE", prepare)
        self.assertNotIn('title="$(printf', prepare)
        self.assertNotIn('head_ref="$(printf', prepare)
        self.assertIn('[ "$current_head" != "$AUTHORIZED_HEAD" ]', prepare)
        self.assertIn('[ "$current_base" != "$AUTHORIZED_BASE" ]', prepare)
        self.assertIn('diff_sha256="$(sha256sum', prepare)
        self.assertIn('prompt_sha256="$(sha256sum', prepare)

        head_check = publish.index('current_pr="$(gh api')
        base_check = publish.index('current_base="$(printf')
        stale_compare = publish.index('[ "$current_head" != "$PREPARED_HEAD" ]')
        comment = publish.index('patch_reservation "$body_file"')
        self.assertLess(head_check, stale_compare)
        self.assertLess(base_check, stale_compare)
        self.assertIn('[ "$current_base" != "$PREPARED_BASE" ]', publish)
        self.assertIn('(.repo == $repo)', publish)
        self.assertIn('(.pr == $pr)', publish)
        self.assertIn('(.head_sha == $head)', publish)
        self.assertIn('(.base_sha == $base)', publish)
        self.assertIn('(.merge_base_sha == $merge_base_sha)', publish)
        self.assertIn('(.diff_sha256 == $diff_sha256)', publish)
        self.assertIn('(.diff_truncated == $diff_truncated)', publish)
        self.assertIn('(.full_diff_sha256 == $full_diff_sha256)', publish)
        self.assertIn('(.unreviewable_changes == $unreviewable_changes)', publish)
        self.assertIn("clean verdict was prohibited", publish)
        self.assertIn('(.prompt_sha256 == $prompt_sha256)', publish)
        self.assertIn('(.source_comment.sha256 == $source_comment_sha256)', publish)
        self.assertIn('(.workflow.run_id == $run_id)', publish)
        self.assertIn("source_comment_matches", publish)
        self.assertIn("reservation_is_owned", publish)
        self.assertIn('(.path == "github-hosted-dinkuskit")', publish)
        self.assertLess(stale_compare, comment)
        self.assertIn('post_pr="$(gh api', publish)
        self.assertIn('gh api -X PATCH', publish)

    def test_model_output_is_bounded_and_contract_checked(self) -> None:
        model_step = named_step("Run credential-isolated Copilot review")
        publish = named_step("Publish exact-head advisory comment")
        self.assertIn('[ "$review_bytes" -gt 50000 ]', model_step)
        self.assertIn("verdict_count", model_step)
        self.assertIn("final_line", model_step)
        self.assertIn("Prevent model-authored GitHub @-mentions", model_step)
        mention_sanitize = model_step.index("perl -CSDA")
        transformed_bound = model_step.index('safe_bytes="$(wc -c')
        self.assertLess(mention_sanitize, transformed_bound)
        self.assertIn('[ "$safe_bytes" -gt 50000 ]', model_step)
        self.assertIn("tr -d '\\000-\\010", publish)
        self.assertIn("verdict_count", publish)
        self.assertIn("final_line", publish)
        publish_sanitize = publish.index("perl -CSDA")
        publish_bound = publish.index('transformed_bytes="$(wc -c')
        self.assertLess(publish_sanitize, publish_bound)
        self.assertIn('[ "$transformed_bytes" -le 50000 ]', publish)
        self.assertIn('cat "$safe_review"', publish)
        self.assertNotIn('cat "$review_file"', publish)
        self.assertIn('[ "$body_bytes" -gt 60000 ]', publish)

    def test_prompt_stays_below_linux_single_argument_limit(self) -> None:
        prepare = named_step("Prepare immutable review request")
        self.assertIn('head -c 90000', prepare)
        self.assertIn('diff truncated to 90 KB', prepare)
        self.assertIn('full_diff_sha256="$(sha256sum', prepare)
        self.assertIn('diff_truncated=true', prepare)
        self.assertIn('unreviewable_changes=true', prepare)
        self.assertIn('git-lfs.github.com/spec/v1', prepare)
        self.assertIn("tr -d '\\000'", prepare)
        self.assertIn('must not return a clean verdict', prepare)
        self.assertIn('[ "$prompt_bytes" -gt 110000 ]', prepare)
        self.assertNotIn('head -c 160000', prepare)

    def test_pr_diff_uses_merge_base_not_diverged_base_tip(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            repo = Path(raw_temp)

            def git(*args: str) -> str:
                result = subprocess.run(
                    ["git", *args],
                    cwd=repo,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode, 0, result.stderr or result.stdout
                )
                return result.stdout.strip()

            git("init", "-q", "-b", "main")
            git("config", "user.name", "ClawSweeper Test")
            git("config", "user.email", "clawsweeper@example.invalid")
            git("config", "commit.gpgsign", "false")
            (repo / "common.txt").write_text("common\n", encoding="utf-8")
            git("add", "common.txt")
            git("commit", "-q", "-m", "common")
            git("switch", "-q", "-c", "feature")
            (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
            git("add", "feature.txt")
            git("commit", "-q", "-m", "feature")
            feature_sha = git("rev-parse", "HEAD")
            git("switch", "-q", "main")
            (repo / "base-only.txt").write_text("base only\n", encoding="utf-8")
            git("add", "base-only.txt")
            git("commit", "-q", "-m", "base advance")
            base_sha = git("rev-parse", "HEAD")
            merge_base = git("merge-base", base_sha, feature_sha)

            two_tip = set(
                git("diff", "--name-only", base_sha, feature_sha).splitlines()
            )
            pr_semantics = set(
                git("diff", "--name-only", merge_base, feature_sha).splitlines()
            )
            self.assertEqual(two_tip, {"base-only.txt", "feature.txt"})
            self.assertEqual(pr_semantics, {"feature.txt"})

    def test_artifact_failures_still_reach_bounded_publisher(self) -> None:
        request_download = named_step("Download immutable review request")
        initialize = named_step("Initialize deterministic failure output")
        request_validation = named_step("Validate immutable review request")
        output_download = named_step("Download bounded review output")
        output_upload = named_step("Upload bounded review output")
        publish = named_step("Publish exact-head advisory comment")

        self.assertIn("id: request_artifact", request_download)
        self.assertIn("continue-on-error: true", request_download)
        self.assertIn("if: always()", initialize)
        self.assertIn("EXPECTED_DIFF_SHA", initialize)
        self.assertIn("EXPECTED_PROMPT_SHA", initialize)
        self.assertIn("clawsweeper-verdict: blocked", initialize)
        self.assertIn('sha256sum "$request_dir/prompt.diff"', request_validation)
        self.assertIn('sha256sum "$request_dir/prompt.txt"', request_validation)
        self.assertIn('(.prompt_sha256 == $prompt_sha256)', request_validation)
        self.assertIn("id: output_artifact", output_download)
        self.assertIn("continue-on-error: true", output_download)
        self.assertIn("id: publish", publish)
        self.assertIn("if: always()", publish)
        self.assertIn("write_blocked_review", publish)
        self.assertIn("OUTPUT_ARTIFACT_OUTCOME", publish)
        self.assertIn(
            "artifact-ids: ${{ needs.gate.outputs.request_artifact_id }}",
            request_download,
        )
        self.assertIn(
            "artifact-ids: ${{ needs.review.outputs.output_artifact_id }}",
            output_download,
        )
        for artifact in ("receipt.json", "review.md", "exit-code"):
            self.assertIn(f"clawsweeper-output/{artifact}", output_upload)
        self.assertNotIn(
            "path: ${{ runner.temp }}/clawsweeper-output\n", output_upload
        )
        self.assertEqual(self.workflow.count("merge-multiple: true"), 2)

    def test_model_spend_and_success_reaction_are_bounded(self) -> None:
        model_step = named_step("Run credential-isolated Copilot review")
        completion = named_step("Acknowledge completion")
        command = named_step("Validate standalone command")
        reserve = named_step("Persist review admission before model access")
        self.assertIn("--max-ai-credits=50", model_step)
        self.assertIn('daily_review_count', command)
        self.assertIn('[ "$daily_review_count" -ge 5 ]', command)
        self.assertIn("association=CONTRIBUTOR", command)
        self.assertIn("association=$REQUESTER_ASSOCIATION", reserve)
        self.assertIn("This admission counts", reserve)
        self.assertLess(
            self.workflow.index("      - name: Persist review admission before model access"),
            self.workflow.index("      - name: Prepare immutable review request"),
        )
        self.assertLess(
            self.workflow.index("      - name: Persist review admission before model access"),
            self.workflow.index("  review:"),
        )
        self.assertIn(
            "group: clawsweeper-${{ github.repository_id }}", self.workflow
        )
        self.assertNotIn(
            "group: clawsweeper-${{ github.repository_id }}-${{ github.event.issue.number }}",
            self.workflow,
        )
        self.assertIn(
            "steps.publish.outputs.publish_valid == 'true'", completion
        )
        self.assertIn(
            "steps.publish.outputs.model_success == 'true'", completion
        )

    def run_publisher_case(
        self,
        *,
        artifact_outcome: str = "success",
        review: str = "Review for @maintainers.\n\nclawsweeper-verdict: clean\n",
        receipt_overrides: dict[str, object] | None = None,
        diff_truncated: bool = False,
        unreviewable_changes: bool = False,
        exit_code: str = "0\n",
        live_source_body: str | None = None,
    ) -> tuple[str, str]:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp)
            output_dir = root / "clawsweeper-output"
            output_dir.mkdir()
            capture = root / "comment.md"
            github_output = root / "github-output"
            mock_bin = root / "bin"
            mock_bin.mkdir()
            gh = mock_bin / "gh"
            gh.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    set -euo pipefail
                    if [ "$1" = api ] && [[ "$*" == *"issues/comments/123"* ]] && [[ "$*" == *"-X PATCH"* ]]; then
                      while [ "$#" -gt 0 ]; do
                        if [ "$1" = --input ]; then
                          jq -r '.body' "$2" > "$MOCK_COMMENT_BODY"
                          break
                        fi
                        shift
                      done
                      exit 0
                    fi
                    if [ "$1" = api ] && [[ "$*" == *"issues/comments/123"* ]]; then
                      printf '%s\\n' "$MOCK_RESERVATION_COMMENT"
                      exit 0
                    fi
                    if [ "$1" = api ] && [[ "$*" == *"issues/comments/99"* ]]; then
                      printf '%s\\n' "$MOCK_SOURCE_COMMENT"
                      exit 0
                    fi
                    if [ "$1" = api ] && [[ "$*" == *"pulls/7"* ]]; then
                      printf '%s\\n' '{"head":{"sha":"abc123"},"base":{"sha":"base123"}}'
                      exit 0
                    fi
                    exit 1
                    """
                ),
                encoding="utf-8",
            )
            gh.chmod(0o755)

            source = source_comment_record("@clawsweeper review")
            source_body_sha, source_sha = source_comment_hashes(source)
            live_source = source_comment_record(
                live_source_body
                if live_source_body is not None
                else str(source["body"]),
                updated_at=(
                    "2026-07-21T20:01:00Z"
                    if live_source_body is not None
                    else str(source["updated_at"])
                ),
            )
            marker = (
                "<!-- clawsweeper-hosted path-b day=2026-07-21 "
                f"association=OWNER v=1 source={source_sha} run=99 attempt=1 "
                "model=gpt-5.6-terra base=base123 head=abc123 -->"
            )
            reservation = {
                "id": 123,
                "issue_url": "https://api.github.com/repos/dinkuskit/blocks/issues/7",
                "user": {"login": "dinkuskit-clawsweeper[bot]", "type": "Bot"},
                "body": f"{marker}\n\nPending",
            }

            if artifact_outcome == "success":
                receipt: dict[str, object] = {
                    "repo": "dinkuskit/blocks",
                    "pr": 7,
                    "model": "gpt-5.6-terra",
                    "head_sha": "abc123",
                    "base_sha": "base123",
                    "merge_base_sha": "m" * 40,
                    "diff_sha256": "d" * 64,
                    "diff_truncated": diff_truncated,
                    "full_diff_bytes": 100000 if diff_truncated else 1000,
                    "full_diff_sha256": "f" * 64,
                    "unreviewable_changes": unreviewable_changes,
                    "prompt_sha256": "p" * 64,
                    "requester_association": "OWNER",
                    "review_day": "2026-07-21",
                    "source_comment": {
                        "id": "99",
                        "updated_at": source["updated_at"],
                        "body_sha256": source_body_sha,
                        "author": "alice",
                        "sha256": source_sha,
                    },
                    "workflow": {"run_id": "99", "run_attempt": 1},
                    "path": "github-hosted-dinkuskit",
                }
                receipt.update(receipt_overrides or {})
                (output_dir / "receipt.json").write_text(
                    json.dumps(receipt), encoding="utf-8"
                )
                (output_dir / "review.md").write_text(review, encoding="utf-8")
                (output_dir / "exit-code").write_text(
                    exit_code, encoding="utf-8"
                )

            env = os.environ.copy()
            env.update(
                {
                    "ADMISSION_RUN_ATTEMPT": "1",
                    "ADMISSION_RUN_ID": "99",
                    "APP_BOT_LOGIN": "dinkuskit-clawsweeper[bot]",
                    "GITHUB_OUTPUT": str(github_output),
                    "GITHUB_RUN_ATTEMPT": "1",
                    "GITHUB_RUN_ID": "99",
                    "MODEL": "gpt-5.6-terra",
                    "MOCK_COMMENT_BODY": str(capture),
                    "MOCK_RESERVATION_COMMENT": json.dumps(reservation),
                    "MOCK_SOURCE_COMMENT": json.dumps(live_source),
                    "OUTPUT_ARTIFACT_OUTCOME": artifact_outcome,
                    "PATH": f"{mock_bin}{os.pathsep}{env['PATH']}",
                    "PREPARED_BASE": "base123",
                    "PREPARED_DIFF_SHA": "d" * 64,
                    "PREPARED_DIFF_TRUNCATED": (
                        "true" if diff_truncated else "false"
                    ),
                    "PREPARED_FULL_DIFF_BYTES": (
                        "100000" if diff_truncated else "1000"
                    ),
                    "PREPARED_FULL_DIFF_SHA": "f" * 64,
                    "PREPARED_UNREVIEWABLE_CHANGES": (
                        "true" if unreviewable_changes else "false"
                    ),
                    "PREPARED_HEAD": "abc123",
                    "PREPARED_MERGE_BASE": "m" * 40,
                    "PREPARED_PROMPT_SHA": "p" * 64,
                    "PREPARED_REVIEW_DAY": "2026-07-21",
                    "PR": "7",
                    "REPO": "dinkuskit/blocks",
                    "REQUESTER_ASSOCIATION": "OWNER",
                    "RESERVATION_COMMENT_ID": "123",
                    "REVIEW_JOB_RESULT": "success",
                    "RUNNER_TEMP": str(root),
                    "SOURCE_COMMENT_AUTHOR": "alice",
                    "SOURCE_COMMENT_BODY_SHA": source_body_sha,
                    "SOURCE_COMMENT_ID": "99",
                    "SOURCE_COMMENT_SHA": source_sha,
                    "SOURCE_COMMENT_UPDATED_AT": str(source["updated_at"]),
                    "COMMENT_ID": "99",
                }
            )
            result = subprocess.run(
                ["bash", "-c", step_script("Publish exact-head advisory comment")],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            return (
                capture.read_text(encoding="utf-8"),
                github_output.read_text(encoding="utf-8"),
            )

    def test_publisher_posts_only_independently_sanitized_output(self) -> None:
        comment, outputs = self.run_publisher_case(
            review="Review for @maintainers; do not forge clawsweeper-hosted.\n\nclawsweeper-verdict: clean\n"
        )
        self.assertNotIn("@maintainers", comment)
        self.assertIn("@\u200bmaintainers", comment)
        self.assertNotIn("forge clawsweeper-hosted", comment)
        self.assertIn("forge clawsweeper-\u200bhosted", comment)
        self.assertIn("clawsweeper-verdict: clean", comment)
        self.assertIn("publish_valid=true", outputs)
        self.assertIn("model_success=true", outputs)

    def test_publisher_neutralizes_an_edited_source_comment(self) -> None:
        comment, outputs = self.run_publisher_case(
            live_source_body="command removed after model run"
        )
        self.assertIn("triggering command comment was edited or deleted", comment)
        self.assertIn("verdict=stale", comment)
        self.assertIn("publish_valid=false", outputs)
        self.assertIn("model_success=false", outputs)

    def test_publisher_fails_closed_on_missing_or_mismatched_artifact(self) -> None:
        for kwargs in (
            {"artifact_outcome": "failure"},
            {"receipt_overrides": {"head_sha": "attacker-head"}},
            {
                "review": "clawsweeper-verdict: clean\nclawsweeper-verdict: findings\n"
            },
            {"diff_truncated": True},
            {"unreviewable_changes": True},
            {"exit_code": "22\n"},
        ):
            with self.subTest(kwargs=kwargs):
                comment, outputs = self.run_publisher_case(**kwargs)
                self.assertIn("hosted review blocked", comment)
                self.assertIn("clawsweeper-verdict: blocked", comment)
                self.assertIn("publish_valid=false", outputs)
                self.assertIn("model_success=false", outputs)

    def test_supply_chain_versions_are_pinned(self) -> None:
        self.assertIn(
            "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020",
            self.workflow,
        )
        self.assertIn("node-version: '22.23.1'", self.workflow)
        self.assertIn(
            "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
            self.workflow,
        )
        self.assertIn(
            "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093",
            self.workflow,
        )
        self.assertEqual(
            self.workflow.count(
                "actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1"
            ),
            2,
        )
        install = named_step("Install version-pinned Copilot CLI tree")
        self.assertIn("@github/copilot@1.0.73", install)
        self.assertIn("detect-libc@2.1.2", install)
        self.assertIn("--ignore-scripts", install)
        self.assertIn('all(. == "2.1.2")', install)
        self.assertIn('^@github/copilot-(linux|darwin|win32)', install)

    def test_permissions_do_not_request_actions_read(self) -> None:
        self.assertNotIn("actions: read", self.workflow)

    def test_caller_requires_app_identity_and_reviewed_immutable_ref(self) -> None:
        if not CALLER.is_file():
            self.skipTest("caller template belongs to the source apply pack")
        caller = CALLER.read_text(encoding="utf-8")
        self.assertNotIn("@main", caller)
        self.assertIn("@<reviewed-full-commit-sha>", caller)
        self.assertIn("clawsweeper_app_id: ${{ vars.CLAWSWEEPER_APP_ID }}", caller)
        self.assertIn(
            "clawsweeper_app_bot_login: ${{ vars.CLAWSWEEPER_APP_BOT_LOGIN }}",
            caller,
        )
        self.assertIn(
            "CLAWSWEEPER_APP_PRIVATE_KEY: ${{ secrets.CLAWSWEEPER_APP_PRIVATE_KEY }}",
            caller,
        )
        self.assertNotIn("issues: write", caller)

    def test_partial_reruns_bind_the_original_admission_attempt(self) -> None:
        publish = named_step("Publish exact-head advisory comment")
        request_validation = named_step("Validate immutable review request")
        self.assertIn('run=$ADMISSION_RUN_ID attempt=$ADMISSION_RUN_ATTEMPT', publish)
        self.assertIn('--arg run_id "$ADMISSION_RUN_ID"', publish)
        self.assertIn('--argjson run_attempt "$ADMISSION_RUN_ATTEMPT"', publish)
        self.assertIn(
            '--arg run_id "$EXPECTED_ADMISSION_RUN_ID"', request_validation
        )
        self.assertIn(
            '--argjson run_attempt "$EXPECTED_ADMISSION_RUN_ATTEMPT"',
            request_validation,
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
