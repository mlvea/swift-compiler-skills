# Eval protocol

This suite is a **directory skill** for Swift compiler work. After each
real fix the curator applies **one bounded edit**, accepted only if
replay, counterexample, or execution says so.

Microsoft SkillOpt trains one compact markdown file (~300–2000 tokens)
with batched numeric scores. That is a different problem. We do not run
`skillopt-train`, SAGE weight updates, or GEPA/TextGrad as the skill
store. Optional later: use those as *prompt-only* baselines on `D_test`.

What we do run:

| Piece | Role |
| --- | --- |
| Directory load | YAML name/description always; `SKILL.md` when triggered; KB and scripts on demand |
| One-edit loop | Batch size 1; `optimization/deltas.md` (helpful/harmful); curator gates |
| Harvest | Closed merged-PR issues and transcripts; mine; replay; human adopt |
| Splits | `optimization/splits/` — train, selection, test |

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
python3 swift-expert-panel/scripts/score_pr.py --corpus   # D_tr regression
python3 swift-expert-panel/scripts/score_pr.py --sel      # D_sel accept gate
```

`check_split.py` fails if a `D_test` id appears outside
`optimization/splits/` and this file.

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
Claude Code) × model. Report `D_test` only. Do not turn on an external
skill trainer until a custom env can score `id` / hard / soft in [0, 1]
without using `D_test` for training.
