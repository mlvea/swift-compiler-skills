---
name: swift-compiler-fix-loop
description: Use this skill to fix one bug in swiftlang/swift. The work is triage, a reproducer, a review, a small patch, and a test.
---

# Swift compiler fix loop

This skill is for one Swift compiler bug. It calls these skills.

- `swift-issue-triage` names the stage from this issue before any compiler edit.
- `swift-local-build-test` builds, tests, and diagnoses an environment failure.
- `swift-expert-panel` supplies one read-only reviewer. A full panel is opt-in.
- `swift-issue-explainer` writes an optional HTML page. The page does not block the patch.
- `swift-knowledge-curator` runs only when a durable fact changed.

The shared knowledge base is `../knowledge-base/`.
Copy `../swift-local-build-test/references/paths.example.json` to `paths.json`.
`paths.json` is gitignored. Load it with `export-env.py`.

## Repositories

Put compiler patches in `swiftlang/swift`.
Case notes are optional. They are the user's repository, not a Swift project repository.

The layout is in `references/case-notes.md`. Set `wiki_checkout` when a checkout exists.

## Fast path

Use the fast path only when all of these are true.

- Triage has named the stage.
- The patch is in the function that causes the bug.
- The patch does not change what compiles.

A change to what compiles includes these cases.

- A new diagnostic rejects code that the compiler accepts today.
- The patch changes ABI, ownership, isolation, or a language rule.

A guard at the crash site is the full loop.

1. Triage first, so `seat.py` receives `--stage`.
2. Reproduce this issue.
3. Run `seat.py` with `--stage` and the plan text.
4. Do one clean-context review of the diff, as `../swift-expert-panel/SKILL.md` describes.
5. Make the smallest patch in the function that causes the bug.
6. Add a test in the right directory that the cookbook names.
7. Run the build-test skill.

`request-changes` means apply the named changes and review that diff again.
Skip the explainer, the plan review, the case artifacts, and the curator unless a durable fact changed.
Do not copy a patch from a different issue.

## Full loop

Use the full loop for every other change.
Review the written plan before any compiler edit.
Review the diff before the pull request is marked ready.
`approve` means continue.

`request-changes` means apply the named changes and review that diff again.
`block` means stop.
The reviewer is not the author. The reviewer writes the rebuttal and decides it.

Do not decide that rebuttal yourself. Follow `../swift-expert-panel/SKILL.md`.

### 1. Load this issue

Read the GitHub issue body, the comments, and the linked pull requests.
That read needs the network or a local copy of those pages.
Other issues, harvested plans, and old case notes may name files after the reproducer exists.
Do not treat those notes as the diagnosis or as the patch.

### 2. Triage before a patch

Triage this issue before you propose a patch.
Take the stage from this stack or from the flag ladder.

### 3. Reproduce this issue

Reproduce the smallest real failure of this issue.
Use the strongest signal first.
Start with the reducer for this issue.
Then read the pull requests and the CI logs for this issue.

Then use an existing lit test.
Use the environment skill for every build and every test.

### 4. Write the plan

Write the plan from this reducer.
State the language rule or the compiler invariant.
State the broken assumption and the path where it fails.
Then run the reviewer.

Do not edit compiler source when the verdict is `block`.
On `request-changes`, apply the named changes and review the plan again.

### 5. Explainer, if you want a page

Run `swift-issue-explainer` when you want a teaching page.
Write it at `issues/explainers/<N>/index.html` under `wiki_checkout`.
`explainers_rel` in `paths.json` is that relative path. Ignore that page in git.

The page is not required before the patch.
The reviewer reads the plan from step 4, not this page.

### 6. Implement

Make the smallest change that restores that invariant.
Do not refactor on a bug-fix branch unless the design is wrong.
Rerun the neighbor tests when a change broadens a condition.

### 7. Add tests

Add regression tests that match the layer.
Follow `../knowledge-base/regression-test-cookbook.md`.
The new test must fail before the patch. It must pass after the patch.

### 8. Verify

Verify in layers.
Run the reproducer, the closest neighbors, and the new tests.
Record the commands and the results.
Do not claim that CI is green until the bots say so.

### 9. Prepare the patch and the pull request

Commit only the intended changes.
Keep the pull request in draft until it is ready.
Run the reviewer on the diff before you mark it ready.
Upstream notes are in `references/swift-pr-and-ci.md`.

### 10. Case notes, when the work needs them

Write case notes when the work needs them.
Record the root cause, the path, the tests, the commands, and the risks.
Put them in the user's case-notes repository.

```bash
git -C <swift-worktree> diff --binary --full-index --output=<case>/artifacts/swift.patch
git -C <swift-worktree> diff --name-status --output=<case>/artifacts/changed-files.txt
git -C <swift-worktree> diff --stat --output=<case>/artifacts/diffstat.txt
```

### 11. Curator

Run the curator only when a durable fact changed. Make one bounded edit.
A seating edit needs `score_pr.py --corpus` to still pass.
A brief edit or a playbook edit needs a named counterexample or a command that was run.

There is no separate replay harness.

## Heuristics

Prefer the exact file, the function, and the test. Do not stop at a subsystem label.
Read the pull requests that belong to this issue. Do not copy a patch from a different issue.

Look first for one shared semantic regression when CI fails on more than one platform.
Narrow the condition when a fix breaks a neighbor. Back out only when the design is wrong.
Write the explanation so it makes sense without the jargon of the pass.

## References

- `references/case-file-checklist.md`
- `references/case-notes.md`
- `references/swift-pr-and-ci.md`
- `../knowledge-base/pipeline-map.md`
- `../knowledge-base/resolved-issue-patterns.md`
- `../knowledge-base/sibling-repos.md`
- `../swift-expert-panel/SKILL.md`
- `../swift-issue-explainer/SKILL.md`
