# Regression Test Cookbook

These rules say how to write a test for the layer of the fix.
Copy the style from the nearest neighboring test.
This cookbook takes the conventions from the actual suite in `test/` of the `swiftlang/swift` checkout.

## Universal Rules

1. Use one semantic regression for each issue. Keep the reducer minimal. Add a second test only if it guards a distinct path.
2. Prefer the natural topic name. For an issue-specific file, use `issue-<number>-<slug>.swift`. The existing convention is `test/Constraints/existential_collection_assignment_issue_85116.swift`.
3. Put a pure-crasher robustness reducer in `validation-test/compiler_crashers_fixed/issue-<n>.swift`. Put a behavioral regression under `test/<Area>/`.
4. Every test must fail before your patch. Every test must pass after your patch. Verify both directions. Stash the source change. Run the new test again.
5. Never weaken an existing expectation to make a suite pass. Update expectations only when the intended behavior changed. Say so in the PR.

## Layer-Specific RUN Lines (real examples from this tree)

These RUN lines are real examples from this tree.

### Type checking / diagnostics (Sema)

```swift
// RUN: %target-typecheck-verify-swift -swift-version 5

func f(_ a: Int) {}
f(a: 5) // expected-error{{extraneous argument label 'a:' in call}}{{4-7=}}
```

`-verify` requires every expected diagnostic to match exactly.
The match includes ranges when the test gives ranges.
For a note, use `expected-note`.
For a warning, use `expected-warning`.

### SILGen shape

```swift
// RUN: %target-swift-emit-silgen -disable-availability-checking -verify %s
// or with FileCheck:
// RUN: %target-swift-emit-silgen %s | %FileCheck %s
```

### SIL pass unit tests (.sil inputs)

```sil
// RUN: %target-sil-opt -sil-print-types -enable-sil-verify-all <pass-flags> %s | %FileCheck %s
```

Copy `<pass-flags>` from a neighboring test of the same pass.
The flags differ by pipeline configuration, for example `-bcopts` and `-passes=...`.

### IRGen

```swift
// RUN: %target-swift-frontend -emit-ir -primary-file %s | %FileCheck %s
```

Use `%target-cp` prefixes or mock-sdk variants only when you copy a neighbor that needs them.
Those neighbors need ObjC interop or C interop.

### Executable behavior (runtime/stdlib/miscompiles)

```swift
// RUN: %target-run-simple-swift
// REQUIRES: executable_test
```

These tests run the program.
They need a working runnable stdlib.
See environments.

### IDE / completion

```swift
// RUN: %target-swift-ide-test -code-completion -source-filename %s -code-completion-token HERE | %FileCheck %s
```

Put a `-code-completion-token` marker comment at the completion point.
Assert the candidates with `CHECK:` lines.
Copy those lines from neighboring tests.

### Generic signatures

```swift
// RUN: %target-swift-frontend -typecheck -verify %s -debug-generic-signatures 2>&1 | %FileCheck %s
```

## Choosing The Test Directory

Choose the test directory from the layer of the fix.

| Fix layer | Directory |
| --- | --- |
| Parser | `test/Parse/`. For invalid syntax, use `test/Parse/invalid/`. |
| Sema diagnostics, types, or constraints | `test/Constraints/`, `test/Sema/`, `test/type/`, `test/expr/`, `test/decl/` |
| Generics or requirements | `test/Generics/`, `test/AssociatedTypeInference/` |
| Concurrency or isolation (Sema) | `test/Concurrency/` |
| SILGen | `test/SILGen/` |
| Mandatory passes, region isolation, or move-only | `test/SILOptimizer/`, `test/SIL/OwnershipVerifier/`, `test/Concurrency/` |
| Optimizer passes | `test/SILOptimizer/<PassName>/` |
| IRGen or ABI | `test/IRGen/`, `test/ABI/` |
| Runtime or casting | `test/Runtime/`, `test/Casting/`, `test/stdlib/` |
| Embedded Swift | `test/embedded/` |
| IDE | `test/IDE/`. For SourceKit requests, use `test/SourceKit/`. |
| Driver flags | `test/Driver/` |
| Macros | `test/Macros/` |
| ABI digester or TBD | `test/api-digester/`, `test/TBD/`, `test/abi/` |

## Running Tests Locally (verified on macOS arm64, August 2026)

These commands were verified on macOS arm64 in August 2026.

```bash
# $LIT $CFG: swift-local-build-test/scripts/export-env.py
"$LIT" -sv --param swift_site_config="$CFG" <file-or-dir>
```

For a public ABI change, run the neighboring dump and compare test in `test/api-digester/`.
Do not run only a typecheck.
For TBD, `test/TBD/` must still list the new symbol.

For one untracked test without lit, run its RUN line by hand.
Use `bin/swift-frontend` or a similar tool from that RUN line.
Replace `%s` with the path.
Or save the file inside `test/`.
Then use `$LIT ... --param` as in the block above.

## Expected-Failure Hygiene

If a fix changes diagnostics on purpose, search the whole affected test directory for the old message text.
Do this search before you land the change.
A cascade often breaks expectations in other tests.
That break can stay silent in CI.
