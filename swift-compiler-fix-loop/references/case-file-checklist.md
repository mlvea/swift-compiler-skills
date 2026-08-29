# Case File Checklist

Use this when work on one issue becomes serious enough to deserve durable
memory.

## Where To Write

Create:

`issues/cases/issue-<number>/README.md`

Start from:

`templates/issue-case.md`

Add supporting files only when they help:

- `fix-log.md` for chronological notes during implementation
- `handoff.md` for exact next steps when stopping midstream
- `chapter-draft.md` when the fix teaches a reusable compiler lesson
- `mentor-guidance.md` only when issue-local guidance needs to live with the case
- `artifacts/swift.patch` for the recoverable Swift checkout patch
- `artifacts/changed-files.txt` and `artifacts/diffstat.txt` for review

## Required Sections

Every active case should explain:

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
- Expert panel: seating JSON, ballots, chair verdict (required except
  the skip cases in `swift-expert-panel/SKILL.md`)

## Quality Bar

The case file should answer:

- What program or command failed?
- What compiler invariant was violated?
- Which exact files and functions were involved?
- Which files were opened, and from what *this-issue* signal?
- Why does the patch restore the invariant THIS reducer violated?
- What tests prove it?
- Which patch artifact recovers the current worktree changes?

Avoid notes like "changed file X" without mechanism. A future agent should be
able to continue the work without reopening the whole investigation from
scratch.

## Minimal Completion Standard

Do not mark work as done unless the case file records:

- the final reproducer
- the fix in plain language
- hand-reviewed mentor guidance consulted or explicitly not available
- the patch artifact path and base commit
- exact verification commands
- what remains uncertain, if anything

If the patch is not built or tested, state that directly.
