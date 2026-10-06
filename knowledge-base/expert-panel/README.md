# Expert panel knowledge

This directory holds review judgment for a compiler plan or a pull request.
A stage playbook says where to look.
A resolved-issue pattern is a hint for which file to open.
Use the judgment in this directory for the review.

Read `swift-expert-panel/SKILL.md` for when to review and how to review.
The default reviewer is one read-only subagent with a clean context.
A multi-agent panel is opt-in.
On the full loop, review the written plan before you edit the compiler.
Review the diff before you mark the pull request ready.
The fast path still starts with triage.

The fast path then reviews the diff once.

| File | Role |
| --- | --- |
| `seats.json` | Script seating table: globs, neighbors, and keywords. |
| `roster.md` | Seating algorithm |
| `ballot.md` | JSON schemas for the expert and the chair |
| `chair-protocol.md` | Verdict rules. A chair `block` is final. Do not average ballots. |
| `evolution-gate.md` | Separates a bug fix from a language change |
| `domains/<id>.md` | Review brief for one seat. Load that brief only for that seat. |

Every domain brief uses the same headings.
The headings are **Protects**, **Plan review**, **PR review**, **Reject unless**, **Evolution**, **Forum**, and **Abstain**.
`Protects` is fail-closed.
`Reject unless` is fail-closed.
A violation is `block` unless the artifact cites the exception in the same official doc.

Open the skill at `swift-expert-panel/SKILL.md`.
Seat a change with `swift-expert-panel/scripts/seat.py`.
The scorecard is `scorecard.md` and `scorecard-corpus.json`.
That JSON file is the regression corpus.
Score it with `scripts/score_pr.py --corpus`.
The plan-time report is `--sources-only`.

Score a new pull request in `heldout-corpus.json` before you tune.
Use `--heldout` for that file.
Load official docs from `swift_checkout` in `paths.json`.
The path list is `official-docs.md`.
`scripts/probe_globs.py --checkout` checks the globs on a swift tree.
