# Expert panel knowledge

Review judgment for compiler plans and PRs. Complementary to
stage playbooks (location) and resolved-issue patterns (file-search).

When and how to sit: `swift-expert-panel/SKILL.md` (required after the
written plan, before compiler edits; and again on the diff, before
marking a PR ready).

| File | Role |
| --- | --- |
| `seats.json` | Machine seating table (globs, neighbors, keywords) |
| `roster.md` | Seating algorithm |
| `ballot.md` | Expert and chair JSON schemas |
| `chair-protocol.md` | Weighted synthesis |
| `evolution-gate.md` | Bugfix vs language change |
| `domains/<id>.md` | Per-seat review brief (loaded by that seat only) |

Every domain brief uses the same headings: **Protects**, **Plan
review**, **PR review**, **Reject unless**, **Evolution**, **Forum**,
**Abstain**. `Protects` and `Reject unless` are fail-closed: a
violation is `block` unless the artifact cites the exception in the
same official doc.

Skill entry: `swift-expert-panel/SKILL.md`.
Seating: `swift-expert-panel/scripts/seat.py`.
Scorecard: `scorecard.md` + `scorecard-corpus.json` (`score_pr.py --corpus`,
`D_tr`). Seating accept gate: `score_pr.py --sel` (`D_sel`).
Official docs load from `swift_checkout` in
`swift-local-build-test/references/paths.json`
(`official-docs.md`; `scripts/probe_globs.py` checks they exist).
