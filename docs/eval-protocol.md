# Eval protocol

SkillOpt is the published leader for training **one compact markdown
file** on a frozen model (bounded edits, strict selection gate,
disjoint test). This suite is not that problem: trainable state is a
**directory** (`SKILL.md` + knowledge-base + scripts), and a rollout is
one real compiler-fix attempt.

Do **not** migrate production skills onto SkillOpt's batched
`skillopt-train` engine, SAGE weight updates, or GEPA/TextGrad as the
skill store. Keep:

| Piece | Role |
| --- | --- |
| Anthropic-style directory load | YAML always; SKILL.md on trigger; KB/scripts on demand |
| ACE-style updates | Batch size 1; one delta per trajectory; existing replay / counterexample / execution as the reliability filter |
| SkillOpt-Sleep harvest | Harvest transcripts + merged PRs, mine, replay, stage one proposal, human adopt. No `skillopt/` dependency |
| Local gates | Already in `swift-knowledge-curator/SKILL.md` |

GEPA/TextGrad/SkillOpt-compact remain **prompt-only baselines** on the
matrix after `D_test` exists. They are not the Swift skill format.

## Contamination-free splits

Lock file: `optimization/splits/split_manifest.json`.

| Split | Use | Never |
| --- | --- | --- |
| `D_tr` | Harvest, mining, scorecard, brief `Reject unless` | Report specialist numbers |
| `D_sel` | Accept or reject a staged skill edit (seating replay, cheap graders) | Harvest into playbooks; final report |
| `D_test` | Final Skill Lift / domain metrics only | Harvest, mining, scorecard, accept/reject, journal "evidence" |

Related PR clusters (rejected first + merged replacement) stay in one
split. IDs already in `docs/validation.md`, `optimization/edit-log.md`,
or `scorecard-corpus.json` are `D_tr` (they leaked). They must not move
into `D_test`.

`python3 swift-expert-panel/scripts/check_split.py` fails if a `D_test`
id appears outside `optimization/splits/` and this file.

## Domain metrics (beyond seating)

| Metric | How | 0–1 |
| --- | --- | --- |
| Stage routing | Triage stage matches merged PR's primary files' stage | exact match |
| Seating chair | `seat.py` chair vs `expected_chair` | exact match |
| Review-invariant hit | Live or offline ballot names the landed `CHANGES_REQUESTED` invariant | named match |
| End-to-end fix | Repro fails pre-patch, new test + neighbors pass post-patch | all must hold |

Seating (`score_pr.py`) stays a cheap **regression** on `D_tr`/`D_sel`.
It is not the specialist benchmark. Specialist numbers are Skill Lift
on `D_test`: with-skill vs no-skill on the same harness/model, plus the
four domain metrics.

## Matrix (after the lock)

Axes: skill combo (none / current directory / ACE deltas on current /
optional compact SkillOpt doc / GEPA prompt) × harness (this Grok loop,
Codex CLI, Claude Code) × model. Primary report: `D_test` only.

Harbor / NVIDIA SkillEvaluator / `skillopt-eval` are optional runners.
Until a custom env emits `id`/`hard`/`soft` in [0,1], do not turn on
the SkillOpt research trainer.
