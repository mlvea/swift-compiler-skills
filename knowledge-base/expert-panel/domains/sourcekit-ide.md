# sourcekit-ide

SourceKit, code completion, cursor info, indexing, refactoring,
swift-ide-test. Evolution process does **not** cover IDE design
(process.md); still subject to compiler-invariant review.

## Protects

- IDE must not report a type that batch `-typecheck` would reject, or
  hide an error that batch mode emits, except where delayed resolution
  is an explicit IDE cache issue.
- Completion solver (`TypeCheckCodeCompletion`) may be more
  opportunistic; it must not persist those speculative types into the
  AST used for emission.
- Index / USR stability: USR changes are ABI-like for IDEs.

## Plan review

- Repro with `swift-ide-test` / SourceKit protocol, not only Xcode.
- Is this delayed re-resolution of an AST batch mode never builds?

## PR review

- Tests in `test/IDE/`, `test/SourceKit/`, `test/Index/`, or
  `test/refactoring/`.
- Completion tests cover the exact annotation format of neighbors.
- No global SourceKit caches without a session key.

## Reject unless

- A completion crash is not "fixed" by skipping type check for that
  position if it also skips diagnostics users rely on.
- Refactoring rewrite must round-trip through the same syntax the
  parser accepts.

## Evolution

None for pure IDE behavior. If completion starts accepting a new
language form, that form still needs the language gate.

## Forum

process.md: IDE design is not language evolution. This seat still
cannot report a type that batch `-typecheck` would reject, or hide an
error batch mode emits.

## Abstain

No IDE/SourceKit/index/refactor path. Batch-compiler diagnostics
without completion → `parser-diagnostics` or `type-system`.
