# Parser Playbook

Stage: lexing and parsing into syntax. Smallest bug family (~11 of 418 in
the 2026-08 harvest) but high-visibility when it breaks.

## Key Sources

| Area | Files |
| --- | --- |
| C++ parser (current mainline) | `lib/Parse/ParseExpr.cpp`, `ParseDecl.cpp`, `ParseStmt.cpp`, `ParseType.cpp`, `ParsePattern.cpp`, `ParseGeneric.cpp` |
| Lexer | `lib/Parse/Lexer.cpp`; token definitions in `include/swift/Basic/TokenKinds.def` |
| Syntax production / ASTGen bridge | `lib/ASTGen/` (generated syntax-node construction); parser requests in `lib/Parse/ParseRequests.cpp` |
| Parser diagnostics | `include/swift/AST/DiagnosticsParse.def` (message definitions), recovery logic in the `Parse*.cpp` files |

Correction note: verify exact names at your base commit:
`ls lib/Parse/`.

## Common Bug Classes (what to inspect)

### Class P1: Valid syntax rejected

Inspect: C++ parser *and* SwiftSyntax-based parsing (`swift-syntax`
sibling repo). THIS program must be accepted on the path that actually
parses it.

### Class P2: Invalid syntax accepted (accepts-invalid)

Inspect: the narrowest production that should reject THIS tokens.
Message style: `test/Parse/invalid/`.

### Class P3: Bad recovery producing cascading junk diagnostics

Inspect: recovery at the failing production (list items, statement
boundaries, token ownership). Do not reorder global diagnostic emission
to paper over THIS cascade.

### Class P4: Crash in parser (assertion/segfault)

Usually infinite recursion or a missing null-check after a failed
sub-parse. Reduce THIS snippet; inspect that recursion/optional.

### Class P5: Parser differences between legacy and new parser

Compare `swift-parse-test` vs `swift-frontend -parse` on THIS input.
Keep them consistent or gate intentionally.

## Verification Loop

```bash
ninja -C /Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64 swift-frontend swift-parse-test

# quick manual parse check (no typecheck)
FE=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/bin/swift-frontend
$FE -parse -dump-parse /tmp/repro.swift
```

Then lit on focused tests:
`$LIT -sv --param swift_site_config=$CFG test/Parse <new test>`.

## Regression Test Placement

- `test/Parse/<topic>.swift`; invalid-code regressions in `test/Parse/invalid/`
- RUN style: `// RUN: %target-typecheck-verify-swift -parse` or plain
  `%target-swift-frontend -parse %s | %FileCheck`
- If the fix affects source ranges/fix-its, assert ranges with
  `{{4-7=...}}` annotations copied from neighbors
