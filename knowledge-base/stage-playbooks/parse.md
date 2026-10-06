# Parser Playbook

This stage lexes the source and parses it into syntax.
This bug family is the smallest in the 2026-08 harvest.
The harvest has about 11 parser issues out of 418.
A parser break has high visibility.

## Key Sources

| Area | Files |
| --- | --- |
| C++ parser (current mainline) | `lib/Parse/ParseExpr.cpp`, `ParseDecl.cpp`, `ParseStmt.cpp`, `ParseType.cpp`, `ParsePattern.cpp`, `ParseGeneric.cpp` |
| Lexer | The lexer is `lib/Parse/Lexer.cpp`. Token definitions are in `include/swift/Basic/TokenKinds.def`. |
| Syntax production / ASTGen bridge | `lib/ASTGen/` does generated syntax-node construction. Parser requests are in `lib/Parse/ParseRequests.cpp`. |
| Parser diagnostics | Message definitions are in `include/swift/AST/DiagnosticsParse.def`. Recovery logic is in the `Parse*.cpp` files. |

Correction note: verify the exact names at your base commit.
Run `ls lib/Parse/`.

## Common Bug Classes (what to inspect)

### Class P1: Valid syntax rejected

Inspect the C++ parser.
Also inspect SwiftSyntax-based parsing in the `swift-syntax` sibling repo.
The path that actually parses THIS program must accept it.

### Class P2: Invalid syntax accepted (accepts-invalid)

Inspect the narrowest production that should reject THIS tokens.
For message style, use `test/Parse/invalid/`.

### Class P3: Bad recovery producing cascading junk diagnostics

Inspect recovery at the failing production.
Check list items, statement boundaries, and token ownership.
Do not reorder global diagnostic emission to paper over THIS cascade.

### Class P4: Crash in parser (assertion/segfault)

The usual cause is infinite recursion.
Or a null-check is missing after a failed sub-parse.
Reduce THIS snippet.
Inspect that recursion or that optional.

### Class P5: Parser differences between legacy and new parser

Compare `swift-parse-test` with `swift-frontend -parse` on THIS input.
Keep the two parsers consistent.
Or leave a documented difference.

## Verification Loop

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
ninja -C "$B" swift-frontend swift-parse-test

# quick manual parse check (no typecheck)
"$FE" -parse -dump-parse /tmp/repro.swift
```

Then run lit on the focused tests.
The command is `$LIT -sv --param swift_site_config=$CFG test/Parse <new test>`.

## Regression Test Placement

- Put tests in `test/Parse/<topic>.swift`.
- Put invalid-code regressions in `test/Parse/invalid/`.
- One RUN line is `// RUN: %target-typecheck-verify-swift -parse`.
- The plain RUN line is `%target-swift-frontend -parse %s | %FileCheck`.
- If the fix affects source ranges or fix-its, assert the ranges. Use `{{4-7=...}}` annotations. Copy those annotations from neighboring tests.
