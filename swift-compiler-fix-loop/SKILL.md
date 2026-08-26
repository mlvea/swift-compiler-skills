---
name: swift-compiler-fix-loop
description: Use when working from the swift-issue-fix-plans repo to investigate a Swift compiler issue or PR end to end - triage the pipeline stage, reproduce the failure in the swiftlang/swift checkout, implement the smallest sound fix, add matching regression tests, verify locally, and record durable case notes, handoff, and PR or CI follow-up.
---

# Swift Compiler Fix Loop

One complete Swift compiler bug fix loop. This is the orchestrator; it
delegates to three sibling skills:

- `swift-issue-triage` — classify stage + archetype before touching code
- `swift-local-build-test` — build trees, test invocation, environment traps
- `swift-knowledge-curator` — after fixes, evolve these skills (validation-gated)

Shared knowledge base: `/Users/madushan/Documents/Github/swift-compiler-skills/knowledge-base/`

## Repo Roles

- Wiki repo: `/Users/madushan/Documents/Github/swiftlang/swift-issue-fix-plans`
- Swift checkout: `/Users/madushan/Documents/Github/swiftlang/swift`

Compiler patches go in the Swift checkout. Plans, case notes, handoffs,
tracker updates, and book notes stay in the wiki repo.

## Work Loop

1. **Load durable memory.**

Read: `AGENTS.md`, `STATUS.md`, `tracker/active.md`, `tracker/backlog.md`,
`wiki/00-start-here.md`, `wiki/compiler-understanding.md`, plus the issue's
plan under `issues/plans-by-search-page/` and hand-reviewed guidance under
`issues/guidance/` when listed in `manual-review.md`.

2. **Triage before anything else.** Run the triage procedure (triage skill)
   and produce the triage record: stage, family, archetype A1–A10,
   confidence, likely files, test home. Do not propose patches without it.

3. **Reproduce the smallest real failure.** Strongest signal first:
   issue reproducer → failing PR status → CI log snippet → existing lit
   test. Before editing, inspect worktree state (`git status`!), nearby
   tests, and the exact compiler path involved. Use the environment skill
   for all build/test commands; if an environment error appears, fix the
   environment first and record it.

4. **Explain the bug before patching.** Write down:
   - the language rule / compiler invariant
   - the broken assumption
   - the exact path where it fails
   - whether mentor guidance changes the likely layer

5. **Implement the smallest invariant fix.** Narrowest change that restores
   the invariant; no refactors on bug-fix branches unless the design itself
   is wrong. If a change broadens a condition, rerun neighboring tests
   immediately — regressions surface in adjacent behavior first.
   Prefer fixing upstream of observation, except user-facing diagnostics,
   which belong in Sema even when later stages could also guard.

6. **Add regression tests that match the layer.** Follow
   `../knowledge-base/regression-test-cookbook.md`: minimal reducer, nearest
   directory, real RUN-line style copied from neighbors, named per repo
   convention. The new test must fail pre-patch and pass post-patch.

7. **Verify in layers.** Minimum: exact reproducer, closest neighbors, all
   new tests. Record exact commands and outcomes. Never claim CI is green
   until bots say so.

8. **Prepare patch and PR cleanly.** Commit only intended changes; human
   commit message explaining issue + invariant; Draft PR until ready;
   description covers explanation, scope, risk, testing, reviewers.
   Upstream triggers: `references/swift-pr-and-ci.md`.

9. **Leave durable project memory.** Update the case file with root cause,
   path, patch notes, artifact paths + base commit, tests, verification,
   risks. Generate recoverable artifacts:

```bash
git -C <swift-worktree> diff --binary --full-index --output=<case>/artifacts/swift.patch
git -C <swift-worktree> diff --name-status --output=<case>/artifacts/changed-files.txt
git -C <swift-worktree> diff --stat --output=<case>/artifacts/diffstat.txt
```

10. **Feed the loop.** Any durable lesson, corrected fact, or repeated
    friction goes through the curator skill (validation-gated edits to
    knowledge-base/playbooks) — skills are trainable state, not static docs.

## Working Heuristics

- Exact file/function/test references beat subsystem labels.
- Guidance files are mentor input, not proof of correctness.
- Multi-platform CI failures: look for one shared semantic regression first.
- Highest-signal local loop: incremental rebuild → focused lit → neighbors →
  reducer.
- When a fix regresses neighbors, narrow the condition; back out only if the
  design is wrong.
- Explanations in case files must survive without jargon.

## References

- `references/case-file-checklist.md`
- `references/swift-pr-and-ci.md`
- `../knowledge-base/pipeline-map.md`
- `../knowledge-base/resolved-issue-patterns.md`
- `/Users/madushan/Documents/Github/swiftlang/swift-issue-fix-plans/issues/guidance/README.md`
- `/Users/madushan/Documents/Github/swiftlang/swift-issue-fix-plans/wiki/compiler-understanding.md`
