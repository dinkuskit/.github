# Contributing to DinkusKit

Start with the [vision](VISION.md), [scope and planning](ROADMAP.md), and the
owning repository's current contributor instructions and product contracts.
Small fixes can stay small; a settled decision does not need a new design
discussion every time it is implemented.

## Choose one place for the conversation

Use issues for actionable bugs and tasks, and also for meaningful ideas or
unsettled product questions. Search existing issues, proposals and pull
requests first. This repository uses issues; follow a component's established
Discussions or proposal process when it provides one.

File component-specific questions in that component's repository. Use
[this repository's issues](https://github.com/dinkuskit/.github/issues) for
organization-wide product principles or questions with no clear component
owner. Give a cross-repository decision one primary record and link its
implications from other repositories. Avoid creating copies of the same
question or a separate decision queue.

Explain the business need, what is already known, the decision still needed,
and relevant evidence. Say whether you are proposing an idea, recording an
accepted design, or taking on active work. An open idea or accepted design is
not automatically a commitment to implement it.

## Use research to answer a question

Bring relevant upstream documentation, observed behavior or experiments to a
specific product or technical decision. State what the evidence establishes
and what remains uncertain. A documented API, a replayed scenario and a live
observation establish different things; none alone proves DinkusKit's behavior.

Research may support adapting an idea, keeping an existing approach, deferring
a decision or declining a feature. Do not turn every discovery into a ticket
or copy another product's backlog. Keep public proposals original and safe to
share; exclude credentials, private business data and private research records.

When a decision remains unclear, link the unresolved question and the evidence
to its primary record. A later relevant design discussion can pick it up.
Usually let unrelated discoveries wait for that discussion instead of
expanding a release in progress.

## Make the result reviewable

Keep changes focused, follow the owning repository's checks, and explain the
result and its limits. Separate what is proposed, implemented, tested and
available to users. For behavior changes, show appropriate proof against the
actual source revision, including failure recovery when relevant.

Preserve existing human approval boundaries for publishing, deployment,
production changes and external actions. A contribution or merged pull request
does not itself authorize them.
