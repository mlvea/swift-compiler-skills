# parser-diagnostics

The scope is the lexer, the parser, recovery, diagnostic wording, and fix-its.
The scope includes the ASTGen and SwiftSyntax bridge, and `diagnostic groups`.

## Protects

- Recovery must not make a plausible-but-wrong AST from invalid syntax when Sema would accept that AST.
- A fix-it must compile when the user applies it.
  If the fix-it does not compile, do not emit it.
- A diagnostic identifier is API for tooling (`diagnostic groups`).
  A rename with no group alias is a tooling break.
- The parser must parse a file when it has not seen every import.
  A common rejection is an identifier-grammar operator that requires operator declarations to parse.
  The list is commonly_proposed.md.

## Plan review

- Does `-dump-parse` already show the bug?
  If the bug appears only at `-typecheck`, this seat is adjacent at most.
- Is the request a change to language syntax?
  Use evolution-gate.md.

## PR review

- Use `test/Parse/` with `-verify` and with fix-it tests.
  Use the CHECK style that the suite already has.
- Add an ASTGen test when the SwiftSyntax path must match the C++ parse.
- Add an entry for a new diagnostic where the tree already requires that entry.

## Reject unless

- These syntax changes are a `block` because evolution rejected them.
  The changes are brace syntax, indent syntax, removal of semicolons, replacement of `?:`, and a rename of `guard`.
  The list is commonly_proposed.md.

  https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md
- Parser "helpfulness" that needs type context is not allowed.

## Evolution

New syntax, a new attribute, or a new effects keyword needs a proposal.
It usually also needs a feature flag in `Features.def`.
The `library-evolution` seat is adjacent.

## Forum

Syntax proposals in commonly_proposed.md stay rejected.
The proposals are brace syntax, indent syntax, removal of semicolons, replacement of `?:`, and a rename of `guard`.
Parser "helpfulness" that needs type context belongs in Sema, or it belongs nowhere.

## Abstain

Abstain for a solver-only change or a SIL-only change with no diagnostic string and no parse change.
Send macro expansion, or `test/Macros/` with no parse change, to `macros`.
