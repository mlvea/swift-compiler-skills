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

## Common Bug Classes And Fix Patterns

### Class P1: Valid syntax rejected

Check whether the grammar change belongs to the C++ parser only or also to
SwiftSyntax-based parsing (`swift-syntax` sibling repo). Both must accept.
Fix by extending the grammar site and updating
`swift-syntax/Sources/SwiftParser/` mirror when applicable.

### Class P2: Invalid syntax accepted (accepts-invalid)

Add the rejection at the narrowest production; check existing "invalid"
tests under `test/Parse/invalid/` for message style.

### Class P3: Bad recovery producing cascading junk diagnostics

Recovery should resynchronize at statement/declaration boundaries and
preserve token ownership. Prefer local guards near the failing production;
do not reorder global diagnostic emission.

Worked example: #80929, fixed as a side-effect of #80928 (#80927). Align
interpolation trailing-comma handling in `parseListItem` with other comma
lists. Do not add a one-off `parseExprPrimary` nullptr check (author
considered and rejected that alternative in #80928).

### Class P4: Crash in parser (assertion/segfault)

Usually infinite recursion or missing null-check after a failed sub-parse.
Reduce to smallest snippet; guard the specific recursion/optional. Add the
reducer under `test/Parse/invalid/` (or crashers dir for pure robustness).

### Class P5: Parser differences between legacy and new parser

When a fix touches shared productions, run both parser paths:
`-experimental-allow-non-resilient-modules` irrelevant—instead compare
`swift-parse-test` behavior vs `swift-frontend -parse`. Keep them consistent
or gate intentionally.

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
