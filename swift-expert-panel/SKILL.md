---
name: swift-expert-panel
description: Use this skill to review a Swift compiler plan or diff. One clean-context reviewer is the default, and a full panel is opt-in.
---

# Swift expert panel

This review adds a check. It is not a second triage.
A playbook says where to look. A seated brief says whether the change is acceptable.

`seat.py` chooses the briefs to load. That choice has a measured check, `score_pr.py --corpus`.
Several readers of those briefs have no comparison yet, so the default is one read-only subagent.
That subagent has not seen the author's reasoning.

## Default: one reviewer

The reviewer is not the author.
Spawn one read-only subagent from a clean context.
Give that subagent only these inputs.

- the plan or the diff
- `chair-protocol.md` and `evolution-gate.md`
- each seated brief, `domains/<id>.md`
- each official document named in those briefs, from the swift checkout

Do not give it the author's reasoning. Do not give it the triage notes. Do not give it a rebuttal.
The reviewer reads each official document before it accepts a cited exception.

Only the reviewer returns `approve`, `request-changes`, or `block`.
Verdict rules are in `chair-protocol.md`.

- A chair block is final.
- Another seated brief may block. That block needs a written rebuttal.
- The reviewer writes the rebuttal and decides it. The author does not accept it.
- `request-changes` means apply the named changes and review that diff again.
- When the artifact is a plan, review the plan again after those changes.
- A rebuttal does not replace the named changes.
- Abstain when the brief says to abstain.
- Do not average verdicts.

On the full loop, review the written plan before any compiler edit.
Review the diff before the pull request is marked ready.
The fast path in `swift-compiler-fix-loop` still starts with triage.
Then do one clean-context review of the diff.

If `chair` is unseated, the author chooses the briefs and says why.
Otherwise, do not add or drop domains.
Record the seating JSON and the verdict in the case file when you keep one.
Skip this review only for a narrow edit.

The edit may change only comments, only docs, or only a test expectation.
That edit must not encode a language rule.
Do the review when you are not sure.
A small Sema check still gets this reviewer.

Do not spawn one subagent for each brief on that check.

## Opt-in: full panel

A full panel is opt-in.
Use one read-only subagent for each seated domain. Then spawn the chair.
Do that only when separate writeups are requested.

Pass the plan or the diff as the artifact. Do not pass the author's reasoning.
The chair accepts or rejects each rebuttal.
Each domain subagent reads only these files.

- `knowledge-base/expert-panel/domains/<id>.md`
- `evolution-gate.md` and `ballot.md`
- the artifact
- each official document path named in that brief

Read those documents from `swift_checkout` in `paths.json`.
Briefs are the fail-closed index. The cited document is the spec.
An empty `blockers` list is valid only after a reading of `Protects` and `Reject unless`.

A violation is `block` unless the artifact cites the exception in the same official document.
Abstain when the artifact is outside the charter. Abstention is a success.
Do not discuss a hypothetical vote from another domain.

The chair reads `chair-protocol.md`, `evolution-gate.md`, its brief, and every ballot.
The chair uses the same rules as the single reviewer.
A chair block is final.
A block from another seat needs a written rebuttal.

Do not average votes. There is no computed weight.

## Seat from files

```bash
python3 swift-expert-panel/scripts/seat.py --stage <triage-stage> \
  --text-file <plan-or-pr-body> -- <files relative to the swift checkout>
```

Use the JSON fields `chair` and `seated`.
Pass `--stage` from triage.
Pass `--text-file` for the plan or for the pull-request title.
When `chair` is `unseated`, choose the briefs and say why.

Otherwise, do not add or drop domains.

## Hard rules

Seating comes from the script. Use its `chair`, unless that value is `unseated`.
Do not average votes.
Send a user-visible language change through `evolution-gate.md`.

Send a user-visible stdlib change through `evolution-gate.md`.
Do that even when the change is framed as a bugfix.
Do not restate a stage playbook. The review judges acceptability.

A named invariant in a seated brief beats a plausible local patch.
These closed-world defaults are the bar.

- A change breaks a behavior that the official document does not list.
- Solution application cannot fail.
- OSSA is exactly-once.
- Do not drop a debug variable.

A hurried pass skips this bar.
