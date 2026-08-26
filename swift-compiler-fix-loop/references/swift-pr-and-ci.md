# Swift PR And CI Notes

Use this reference once the local fix is understood and the branch is ready for
review or bot testing.

## Branch And PR Flow

- Work in your fork branch.
- Open the PR against `swiftlang/swift:main`.
- Prefer a Draft PR until the patch, explanation, and tests are ready.
- Significant changes need explicit approval before merge.

## Commit Guidance

- Commit only intended files.
- Use a commit message that explains the bug and the invariant, not just the
  touched files.
- If you add regression tests, make sure they are part of the commit unless you
  intentionally want a temporary local-only test.

## Swift CI

Swift PR testing is triggered on the upstream PR via `@swift-ci` comments.

Common triggers:

- `@swift-ci Please smoke test`
- `@swift-ci Please test`
- `@swift-ci Please test Linux platform`
- `@swift-ci Please test macOS platform`

Use smoke tests for smaller changes when simulators are not involved. Use full
validation for broader or riskier changes.

If you do not have commit access to trigger `@swift-ci`, ask a maintainer or
reviewer to post the command on the PR.

## Local Verification Expectations

Before asking for upstream CI, try to have:

- the reproduced failing test passing locally
- the nearest neighboring tests passing locally
- any new regression tests passing locally

Be precise in the PR or handoff about what was and was not verified. Do not say
"all failures fixed" unless you either reproduced each one locally or the
upstream bots reran cleanly.

## PR Description

A good Swift PR description usually covers:

- Explanation
- Scope
- Issues
- Original PRs, if this is a backport
- Risk
- Testing
- Reviewers

Keep the explanation mechanism-first. State what invalid assumption the
compiler made and what invariant the patch now enforces.
