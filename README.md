# swift-compiler-skills

Agent skills for finding, triaging, and fixing bugs in the Swift compiler
(`swiftlang/swift`) — with a validation-gated self-improvement loop adapted
from [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt).

The suite treats skill documents as **trainable state**: every command is
execution-verified before it is written down, triage *stage* rules are
mined from resolved GitHub issues, and edits are accepted only behind
replay / counterexample / execution gates. Historical issues name files
to open. They do not decide the patch for a different issue.

## Skills

| Skill | Use when |
| --- | --- |
| [`swift-compiler-fix-loop/`](swift-compiler-fix-loop/SKILL.md) | End-to-end fix of one issue: triage → reproduce → patch → regression tests → verify → durable case notes. The default entry point. |
| [`swift-issue-triage/`](swift-issue-triage/SKILL.md) | Classify an issue into pipeline stage + failure family from *this* issue's stack/repro *before* touching code. |
| [`swift-local-build-test/`](swift-local-build-test/SKILL.md) | Build targets, run lit tests, manage worktrees; the verified environment contract for this machine. |
| [`swift-expert-panel/`](swift-expert-panel/SKILL.md) | After a plan or PR exists: seat compiler-domain reviewers, collect independent ballots, chair-weighted verdict. |
| [`swift-knowledge-curator/`](swift-knowledge-curator/SKILL.md) | After fixes (or failures): evolve these skills with bounded, validation-gated edits. |

Shared knowledge base (loaded on demand):

- [`knowledge-base/pipeline-map.md`](knowledge-base/pipeline-map.md) —
  stage-identification table + cross-stage heuristics
- [`knowledge-base/stage-playbooks/`](knowledge-base/stage-playbooks/) —
  parse, sema, silgen, sil-optimization, irgen-runtime, tooling-ide,
  cross-cutting
- [`knowledge-base/regression-test-cookbook.md`](knowledge-base/regression-test-cookbook.md)
  — per-layer RUN lines and test placement, extracted from the real suite
- [`knowledge-base/resolved-issue-patterns.md`](knowledge-base/resolved-issue-patterns.md)
  — search families A1–A10 (files to open, not patch recipes)
- [`knowledge-base/expert-panel/`](knowledge-base/expert-panel/) —
  domain review briefs, seating table, evolution gate, chair protocol
  (supplementary to issue-mined playbooks)

Optimization journal (append-only): [`optimization/edit-log.md`](optimization/edit-log.md)

## Install

Symlink each skill into your agent's skill directory:

```bash
REPO=~/.agents/skills   # or ~/.claude/skills, per your agent
for s in swift-compiler-fix-loop swift-issue-triage swift-local-build-test swift-expert-panel swift-knowledge-curator; do
  ln -sfn "$PWD/$s" "$REPO/$s"
done
```

Skills reference two local checkouts by absolute path:

| Path | Role |
| --- | --- |
| `/Users/madushan/Documents/Github/swiftlang/swift` | the compiler checkout being patched |
| `/Users/madushan/Documents/Github/swiftlang/swift-issue-fix-plans` | persistent wiki: case files, tracker, mentor guidance |

Adapt those paths in the SKILL.mds if you relocate them.

## Reading Order For A Fix Task

1. `swift-compiler-fix-loop/SKILL.md`
2. `swift-issue-triage/SKILL.md` — run the triage procedure before any fix
3. `knowledge-base/<playbook for the triaged stage>`
4. `swift-local-build-test/SKILL.md` — for every build/test command
5. After the plan and again before the PR is marked ready:
   `swift-expert-panel/SKILL.md`
6. On completion (success *or* failure): `swift-knowledge-curator/SKILL.md`

## Design Principles

Derived from SkillOpt's treatment of skills as trainable parameters:

1. **Entry skills stay lean** (<~120 rendered lines); depth lives in the
   knowledge base and is loaded on demand.
2. **Execution gate**: a build/test command may only be recorded as fact
   after it has run successfully on the target machine.
3. **Replay + counterexample gates**: new triage/pattern claims must re-route
   already-solved cases correctly and explain at least one case the current
   docs would have misrouted.
4. **Bounded learning rate**: ≤3 substantive rule changes and ≤30 knowledge-
   base lines per curation epoch; rejected proposals are journaled, not lost.
5. **Failure data is training data**: misroutes, broken commands, and
   environment traps are recorded in the same epoch they are observed.
6. **Never weaken a verifier to silence an assert** — applies to both the
   compiler and this suite's gates.
7. **This issue is the only evidence of a correct patch.** Similar issues,
   archetypes, case files, and wiki lessons may name files. They must not
   be copied as the fix. If this issue already has PRs, read those.

## Validation Record

Highlights from `docs/validation.md`; full detail in the optimization journal:

- Epoch 9: flag ladder is required when the stack does not settle stage;
  search-family maps are issue+stage only; harvested plans are not the
  diagnosis.
- Epoch 8: historical issues no longer prescribe patches.
- Environment contract derived empirically: swift `main` pairs with llvm
  `stable/21.x` (authoritative source: swift's own `update-checkout-config.json`),
  plus verified signatures for six distinct failure modes.
- Post-migration toolchain validated: `test/DebugInfo` 336/337 passed
  (single pre-existing environmental failure), smoke tests across
  Constraints/SILGen pass, and a real in-flight bug fix (SIL debug-value
  type chains) was rebased, completed under lit feedback, and green.

## Docs

- [`docs/design.md`](docs/design.md) — architecture and the SkillOpt adaptation
- [`docs/validation.md`](docs/validation.md) — what was verified, and how
