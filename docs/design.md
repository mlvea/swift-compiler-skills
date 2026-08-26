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
├── swift-issue-triage/          stage/family/archetype classifier
├── swift-local-build-test/      verified build/test commands + env contract
│   └── references/environments.md   the machine's pinned truth
├── swift-knowledge-curator/     SkillOpt-style meta-loop over the suite itself
├── knowledge-base/
│   ├── pipeline-map.md          symptoms → stage → files → tests
│   ├── stage-playbooks/         one playbook per compiler stage
│   ├── regression-test-cookbook.md
│   └── resolved-issue-patterns.md   archetypes A1–A10
└── optimization/edit-log.md     append-only training journal
```

Data flow for one fix:

```
issue ──▶ triage skill ──▶ stage+archetype ──▶ stage playbook ──▶ fix loop
                                                                    │
        curator ◀── trajectory (case file, lit results) ◀───────────┘
           │
           └─ gated edits ▶ knowledge-base / SKILL.mds (next epoch's weights)
```

## The Triage Model

Stage identification uses signals in strict priority: stack frames /
assertion text > reproducer behavior under a flag ladder (`-typecheck` →
`-emit-silgen` → `-emit-sil` → run) > title keywords and labels. The output
is a fixed-shape record so downstream steps can rely on it.

Failure families map to ten recurring root-cause archetypes (A1–A10), mined
from 418 closed issues plus ~200 locally harvested fix plans. Each archetype
predicts the *shape* of the fix before the compiler source is opened — e.g.
A1 ("missing upstream validity check") predicts a Sema diagnostic even when
the crash manifests in SILGen.

## The SkillOpt Adaptation

microsoft/SkillOpt trains a skill document as the frozen agent's trainable
state: rollouts produce trajectories; an optimizer turns scored trajectories
into bounded document edits; a held-out validation gate accepts only
improving edits.

Running that loop here without external training infrastructure:

| SkillOpt concept | Local implementation |
| --- | --- |
| trainable parameter θ | the SKILL.mds + knowledge-base corpus |
| rollout | one real fix attempt (success or failure) |
| trajectory score | repro fixed? tests pass? regressions? time lost? |
| gradient signal | where the agent lost time / misrouted / hit a stale fact |
| bounded update (learning rate) | ≤3 rule changes + ≤30 KB lines per epoch |
| validation gate | replay gate, counterexample gate, execution gate |
| rejected-edit buffer | journal entries marked Rejected, revisited after 2 confirmations |
| epochs | triggered by finished fixes, repeated friction, or ≥50 new closed issues |

The gates are deliberately conservative: a proposed rule must re-route
already-solved cases correctly AND explain at least one case the current
docs misroute (or be backed by a command actually executed).

## Non-Goals

- No generic "how to code" advice — this is Swift-compiler-specific.
- No reliance on network access during fixes (harvesting is offline-first;
  GitHub harvests are cached under `data/` in the wiki repo).
- No silent self-modification: every epoch is journaled with evidence.
