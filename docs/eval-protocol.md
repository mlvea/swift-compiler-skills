# Eval protocol

This suite is a **directory skill** for Swift compiler work. YAML
name/description is always visible; `SKILL.md` loads when the skill
triggers; the knowledge base and scripts load on demand.

After each real fix the curator applies **one bounded edit**. Accept
only if replay, counterexample, or execution says so. One helpful or
harmful bullet goes in `optimization/deltas.md`. Do not rewrite a whole
playbook because one issue hurt.

## Splits

Lock file: `optimization/splits/split_manifest.json`.

| Split | Use | Never |
| --- | --- | --- |
| `D_tr` | Harvest, mining, scorecard, brief `Reject unless` | Report specialist numbers |
| `D_sel` | Accept or reject a staged seating/skill edit | Harvest into playbooks; final report |
| `D_test` | Final with-skill vs no-skill numbers only | Harvest, mining, scorecard, accept/reject, journal evidence |

Related PR clusters stay in one split. IDs already in
`docs/validation.md`, `optimization/edit-log.md`, or
`scorecard-corpus.json` are `D_tr`. They must not move into `D_test`.

```bash
python3 swift-expert-panel/scripts/check_split.py
python3 swift-expert-panel/scripts/check_split.py --harvest data/resolved-issues-<date>/*.json
python3 swift-expert-panel/scripts/score_pr.py --corpus   # D_tr seating regression
python3 swift-expert-panel/scripts/score_pr.py --sel      # D_sel seating accept gate
```

`check_split.py` fails if a `D_test` id appears outside
`optimization/splits/`, or if a harvest JSON contains a `D_test` id.

## Metrics

| Metric | How | Pass |
| --- | --- | --- |
| Stage routing | Triage stage matches the merged PR's files | exact |
| Seating chair | `seat.py` vs `expected_chair` | exact |
| Review-invariant | Ballot names the landed `CHANGES_REQUESTED` rule | named match |
| End-to-end fix | Repro fails pre-patch; new test + neighbors pass | all hold |

`--corpus` / `--sel` are cheap seating regressions. They are **not** a
claim the panel beats a human specialist. A specialist number is
with-skill vs no-skill on **`D_test`**, same harness and model. That
run has not been done yet.

## Matrix (not yet run)

skill combo (none / this directory) × harness (this loop, Codex CLI,
Claude Code) × model. Report `D_test` only.

## Out of scope

We do not run Microsoft SkillOpt (`skillopt-train`) or other external
skill-file trainers. Optional later: a prompt-only baseline on `D_test`
after a with-skill vs no-skill run. That run has not happened.
