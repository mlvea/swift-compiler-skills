# Swift pull request and CI notes

Use this reference after you understand the local fix.
Use it when the branch is ready for review or for bot testing.

## Branch and pull request

Do the work on a branch in your fork.
Open the pull request against `swiftlang/swift:main`.
Keep the pull request in draft until the patch, the explanation, and the tests are ready.
Do not mark the pull request ready until the pull-request review has chair `approve`.

That review is in `swift-expert-panel/SKILL.md`.
A significant change needs explicit approval before a merge.

## Commits

Commit only the intended files.
Explain the bug and the invariant in the commit message.
Do not describe only the files that you touched.
Put each new regression test in the commit.

Omit a test only when it must stay local for a short time.

## Swift CI

An `@swift-ci` comment on the upstream pull request starts Swift CI.
Common triggers:

- `@swift-ci Please smoke test`
- `@swift-ci Please test`
- `@swift-ci Please test Linux platform`
- `@swift-ci Please test macOS platform`

Use a smoke test for a smaller change that does not use a simulator.
Use full validation for a broader change or a riskier change.
Ask a maintainer or a reviewer to post `@swift-ci` when you cannot post it.

## Local checks before upstream CI

Have these results before you ask for upstream CI.

- The reproduced failure passes on the local machine.
- The nearest neighbor tests pass on the local machine.
- Each new regression test passes on the local machine.

Say what you verified in the pull request or in the handoff.
Say what you did not verify.
Do not say that every failure is fixed unless one of these is true.

- You reproduced each failure on the local machine.
- The upstream bots ran again and finished clean.

## Pull request text

A Swift pull request usually covers these topics.

- Explanation
- Scope
- Issues
- Original pull requests, when this change is a backport
- Risk
- Testing
- Reviewers

Put the mechanism first.
State the invalid assumption that the compiler made.
State the invariant that the patch now enforces.
