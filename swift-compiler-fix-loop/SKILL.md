---
name: swift-compiler-fix-loop
description: Use when working from the swift-issue-fix-plans repo to investigate a Swift compiler issue or PR end to end - triage the pipeline stage, reproduce the failure in the swiftlang/swift checkout, implement the smallest sound fix, add matching regression tests, verify locally, and record durable case notes, handoff, and PR or CI follow-up.
---

# Swift Compiler Fix Loop

One complete Swift compiler bug fix loop. This is the orchestrator; it
delegates to four sibling skills:

- `swift-issue-triage` — classify stage from THIS issue before touching code
- `swift-local-build-test` — build trees, test invocation, environment traps
- `swift-expert-panel` — domain review of the plan and PR
- `swift-knowledge-curator` — after fixes, evolve these skills (validation-gated)

Shared knowledge base: `/Users/madushan/Documents/Github/swift-compiler-skills/knowledge-base/`

## Repo Roles

- Wiki repo: `/Users/madushan/Documents/Github/swiftlang/swift-issue-fix-plans`
- Swift checkout: `/Users/madushan/Documents/Github/swiftlang/swift`

Compiler patches go in the Swift checkout. Plans, case notes, handoffs,
tracker updates, and book notes stay in the wiki repo.

## Work Loop

1. **Load THIS issue.** Read the GitHub issue (body, comments, linked
   PRs). Tracker/status files say whether work is already in flight.
   Harvested plans (`issues/plans-by-search-page/`), mentor guidance,
   `wiki/compiler-understanding.md`, and other issues' case files are
   optional file-name hints *after* reproduce. They are not the
   diagnosis and not proof of a patch.

2. **Triage before proposing a patch.** Run the triage skill. Stage
   comes from THIS stack or flag ladder.

3. **Reproduce the smallest real failure of THIS issue.** Strongest
   signal first: this issue's reducer → this issue's PRs/CI → existing
   lit test. Inspect worktree state (`git status`!), nearby tests, and
   the compiler path THIS reducer hits. Environment skill for all
   build/test commands.

4. **Explain the bug from THIS reducer before patching.** Write down:
   - the language rule / compiler invariant it violates
   - the broken assumption in the code it reaches
   - the exact path where it fails
   Then run `swift-expert-panel` on the **plan** (seat.py on likely
   files). Do not implement through a chair `block` / unrebutted
   `request-changes`. Skip only comment/docs/test-expectation-only edits.

5. **Implement the smallest change that restores that invariant.** No
   refactors on bug-fix branches unless the design itself is wrong. If
   a change broadens a condition, rerun neighboring tests immediately.

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
   Run `swift-expert-panel` on the **PR/diff** before marking ready.
   Record seating + chair verdict in the case file.

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
- Guidance, search families, similar issues, harvested plans, and local
  case files are file-search hints, not proof of correctness.
- If THIS issue already has PRs (merged, open, or `CHANGES_REQUESTED`),
  read those. Do not copy a different issue's patch.
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
- `../swift-expert-panel/SKILL.md`
- `/Users/madushan/Documents/Github/swiftlang/swift-issue-fix-plans/issues/guidance/README.md`
- `/Users/madushan/Documents/Github/swiftlang/swift-issue-fix-plans/wiki/compiler-understanding.md`
