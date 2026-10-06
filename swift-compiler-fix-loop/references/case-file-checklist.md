# Case file checklist

Use this checklist when one issue needs durable notes.

## Where to write

Create `issues/cases/issue-<number>/README.md`.
Start from `templates/issue-case.md`.
Add a support file only when it helps.

- `fix-log.md` holds notes in time order during the work.
- `handoff.md` holds the exact next steps when you stop in the middle.
- `chapter-draft.md` holds a compiler lesson that another fix can reuse.
- `mentor-guidance.md` holds issue-local guidance that must stay with the case.
- `artifacts/swift.patch` holds a patch that can restore the Swift checkout.
- `artifacts/changed-files.txt` and `artifacts/diffstat.txt` support review.

The HTML explainer is optional. Ignore it in git.
The path is `issues/explainers/<number>/index.html` under the case-notes repository.

The page does not block the patch. The layout is in `case-notes.md`.

## Required sections

Every active case must include these sections.

- Issue Summary
- Reproducer
- First Principles
- What Went Wrong
- Relevant Compiler Path
- Mentor Guidance
- Fix Strategy
- Patch Notes
- Regression Tests
- Verification
- Book Notes
- Risks / Open Questions
- Review: the seating JSON and the verdict
- The path to the HTML explainer, if you wrote one

The Review section is required on the full loop.
Skip it only for the skip cases in `swift-expert-panel/SKILL.md`.

## Quality bar

The case file must answer these questions.

- What program or command failed?
- What compiler invariant did the failure violate?
- Which exact files and functions were involved?
- Which files did you open, and which signal from this issue led there?
- Why does the patch restore the invariant that this reducer violated?
- Which tests prove that restoration?
- Which patch artifact restores the current worktree changes?

Do not write "changed file X" with no mechanism.
A later reader must be able to continue the work.
Do not force that reader to start the whole investigation again.

## Minimum record before done

Do not mark the work done until the case file records all of these items.

- the final reproducer
- the fix in plain language
- the mentor guidance reviewed by hand, or a note that none was available
- the patch artifact path and the base commit
- the exact verification commands
- what remains uncertain, if anything

State it directly when the patch is not built. State it directly when the patch is not tested.
