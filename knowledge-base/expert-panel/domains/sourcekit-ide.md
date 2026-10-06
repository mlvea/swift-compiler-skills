# sourcekit-ide

The scope is SourceKit, code completion, cursor info, indexing, and refactoring.
The scope includes swift-ide-test.
The evolution process does not cover IDE design (process.md).
This seat is still subject to compiler-invariant review.

## Protects

- The IDE must not report a type that batch `-typecheck` would reject.
  The IDE must not hide an error that batch mode emits.
  The exception is delayed resolution when that delay is an explicit IDE cache issue.
- The completion solver (`TypeCheckCodeCompletion`) is allowed to be more opportunistic.
  It must not persist those speculative types into the AST used for emission.
- Index stability and USR stability are in this seat.
  A USR change is ABI-like for IDEs.

## Plan review

- Reproduce the bug with `swift-ide-test` or with the SourceKit protocol.
  Do not reproduce the bug only in Xcode.
- Is this a delayed re-resolution of an AST that batch mode never builds?

## PR review

- Put tests in `test/IDE/`, `test/SourceKit/`, `test/Index/`, or `test/refactoring/`.
- A completion test must cover the exact annotation format of a neighboring test.
- Do not add a global SourceKit cache that has no session key.

## Reject unless

- Do not "fix" a completion crash by skipping the type check for that position.
  That skip is bad when it also skips diagnostics that users rely on.
- A refactoring rewrite must round-trip through the same syntax that the parser accepts.

## Evolution

No evolution rule applies to pure IDE behavior.
If completion begins to accept a new language form, use evolution-gate.md for that form.

## Forum

process.md says that IDE design is not language evolution.
This seat still cannot report a type that batch `-typecheck` would reject.
This seat still cannot hide an error that batch mode emits.

## Abstain

Abstain when the change has no IDE path, no SourceKit path, no index path, and no refactor path.
Send batch-compiler diagnostics that are not about completion to `parser-diagnostics` or to `type-system`.
