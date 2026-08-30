# parser-diagnostics

Lexer/parser, recovery, diagnostic wording and fix-its, ASTGen /
SwiftSyntax bridge, diagnostic groups.

## Protects

- Recovery must not turn invalid syntax into a plausible-but-wrong AST
  that Sema then accepts.
- Fix-its must compile if applied, or not be emitted.
- Diagnostic identifiers are API for tooling (`diagnostic groups`).
  Renaming without a group alias is a tooling break.
- Parser must parse a file without seeing all imports (commonly
  rejected: identifier-grammar operators that require operator decls
  to parse — commonly_proposed.md).

## Plan review

- Does `-dump-parse` already show the bug? If only `-typecheck`, this
  seat is adjacent at most.
- Is the request a language syntax change? Evolution gate.

## PR review

- `test/Parse/` with `-verify` / fix-it tests using the suite's
  existing CHECK style.
- ASTGen tests when the SwiftSyntax path must match C++ parse.
- Localization: new diags get entries where the tree already requires
  them.

## Reject unless

- Brace/indent syntax, removing semicolons, replacing `?:`, renaming
  `guard` — `block` as evolution-rejected
  (https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md).
- Parser "helpfulness" that requires type context.

## Evolution

New syntax, new attributes, or new effects keywords need a proposal
and usually a feature flag in `Features.def` (`library-evolution`
adjacent).

## Forum

Syntax bikesheds in commonly_proposed.md (brace/indent, dropping
semicolons, replacing `?:`, renaming `guard`) stay rejected. Parser
"helpfulness" that needs type context belongs in Sema, or nowhere.

## Abstain

Solver-only or SIL-only changes with no diagnostic string / parse
change. Macro expansion / `test/Macros/` with no parse change →
`macros`.
