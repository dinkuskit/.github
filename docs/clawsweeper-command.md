# ClawSweeper command workflow

Current DinkusKit product repositories call the reusable
`.github/workflows/clawsweeper-command.yml` workflow in this repository.
A trusted owner, member, or collaborator can request the final advisory review
by placing `@clawsweeper review` on its own line in a pull-request comment.

The authorization job runs on a GitHub-hosted runner. Only an accepted command
schedules the separately labeled `clawsweeper-dinkuskit` runner on Spark-2.
The workflow never checks out PR code as an Actions step. The Spark lane admits
only exact repositories configured in the ClawSweeper target registry, refreshes
a dedicated owner-qualified cache, and invokes ClawSweeper's read-only review
sandbox. Reviews post advice; they never merge, close, deploy, or publish.

Live activation additionally requires all of these gated operator actions:

1. Merge the reusable workflow and each product repo's thin caller.
2. Install the `saari-clawsweeper` GitHub App on the selected DinkusKit repos.
3. Create a DinkusKit runner group limited to those repos, then register the
   distinct Spark-2 runner with labels `spark-2,clawsweeper-dinkuskit`.
4. Deploy and build the matching ClawSweeper and Spark target-profile commits.
5. Run one canary on a current PR and verify eyes, a bot verdict, rocket, and
   exact-head proof before widening use.

App installation, runner-group policy, registration, merges, and any live
service change are human-gated. No credential belongs in this repository.
