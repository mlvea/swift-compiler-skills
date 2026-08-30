# Design

## Problem

Generic coding agents fail at Swift compiler work in predictable ways:

1. They misclassify which pipeline stage owns a symptom and patch the wrong
   layer.
2. They lose hours to environment traps (repo skew, HOSTTOOLS drift, stale
   tablegen outputs) that have been seen before.
3. Their regression tests don't match the layer of the fix, so CI disagrees
   with local results.
4. Lessons from each fix evaporate with the chat session.

This suite attacks each failure mode with a dedicated skill plus a shared,
evidence-grounded knowledge base.

## Architecture

```
swift-compiler-skills/
├── swift-compiler-fix-loop/     orchestrator (default entry)
│   └── references/              case-file checklist, PR/CI notes
├── swift-issue-triage/          stage/family classifier (not the patch)
├── swift-local-build-test/      verified build/test commands + env contract
│   └── references/environments.md   the machine's pinned truth
├── swift-expert-panel/          domain review of a plan or PR
│   └── scripts/seat.py          deterministic seating from files
├── swift-knowledge-curator/     SkillOpt-style meta-loop over the suite itself
├── knowledge-base/
│   ├── pipeline-map.md          symptoms → stage → files → tests
│   ├── stage-playbooks/         one playbook per compiler stage
│   ├── regression-test-cookbook.md
│   ├── resolved-issue-patterns.md   search families A1–A10 (files, not patches)
│   └── expert-panel/            domain briefs, seats.json, evolution gate
└── optimization/edit-log.md     append-only training journal
```

Data flow for one fix:

```
issue ──▶ stack/flag-ladder stage ──▶ playbook ──▶ plan ──▶ expert panel ──▶ patch
                          └ optional search family (directories only)
                                                                  │
        curator ◀── trajectory ◀── panel-on-PR ◀── tests ◀────────┘
           │
           └─ gated edits ▶ knowledge-base / SKILL.mds
```

Playbooks (issue-mined) say where to look. The expert panel says
whether a plan or patch is acceptable in the compiler domains it
touches, using per-domain briefs, forums, and evolution constraints.

## The Triage Model

Stage identification uses signals in strict priority: stack frames /
assertion text > reproducer behavior under a flag ladder (`-typecheck` →
`-emit-silgen` → `-emit-sil` → run) > title keywords and labels. The output
is a fixed-shape record so downstream steps can rely on it.

Failure families map to ten *search families* (A1–A10). They name extra
files to open. They do not predict the patch. The current issue's
reproducer, stack, and the code that reducer reaches are the only
evidence of what to change. Other issues, case files, and wiki lessons
are file-search hints. A merged or rejected PR is in scope only when it
is *this* issue's PR.

## Skill-crafting stack (not SkillOpt-train)

SkillOpt's research engine is best-in-class for **one compact markdown
file** with batched selection scores. This suite's trainable state is a
**directory** plus corpus, and a rollout is one real fix. Do not migrate
production skills onto `skillopt-train`, SAGE weights, or GEPA/TextGrad
as the skill store. Protocol: `docs/eval-protocol.md`.

Local loop (ACE-style batch-1 + SkillOpt-Sleep harvest, no `skillopt/`
dependency):

| SkillOpt concept | Local implementation |
| --- | --- |
| trainable parameter θ | the SKILL.mds + knowledge-base corpus |
| rollout | one real fix attempt (success or failure) |
| trajectory score | repro fixed? tests pass? regressions? time lost? |
| gradient signal | where the agent lost time / misrouted / hit a stale fact |
| bounded update (learning rate) | ≤3 rule changes + ≤30 KB lines per epoch |
| validation gate | replay / counterexample / execution; `D_sel` seating; never `D_test` |
| rejected-edit buffer | journal entries marked Rejected, revisited after 2 confirmations |
| epochs | triggered by finished fixes, repeated friction, or ≥50 new closed issues |

The gates are deliberately conservative: a proposed rule must re-route
already-solved cases correctly AND explain at least one case the current
docs misroute (or be backed by a command actually executed).

## Expert panel

A sitting panel is 1 chair + up to 3 other domains, chosen by
`seat.py` from `seats.json` (file globs, keywords, pipeline stage).
Each seat votes independently from its brief and may abstain. The
chair synthesizes with weight 1.0 on its own in-scope ballot and 0.5
on adjacent in-scope ballots; a chair `block` cannot be overridden.
`evolution-gate.md` is the process.md test for "bugfix vs language
change."

## Non-Goals

- No generic "how to code" advice — this is Swift-compiler-specific.
- No reliance on network access during fixes (harvesting is offline-first;
  GitHub harvests are cached under `data/` in the wiki repo).
- No silent self-modification: every epoch is journaled with evidence.
