# Regression Test Cookbook

Rules for writing tests that match the layer of the fix. Copy style from the
nearest neighboring test — conventions below are extracted from the actual
suite in `/Users/madushan/Documents/Github/swiftlang/swift/test`.

## Universal Rules

1. One semantic regression per issue, minimal reducer. Add a second test only
   if it guards a distinct path.
2. Name: prefer the natural topic name; for issue-specific files use
   `issue-<number>-<slug>.swift` (existing convention:
   `test/Constraints/existential_collection_assignment_issue_85116.swift`).
3. Pure-crasher robustness reducers go to
   `validation-test/compiler_crashers_fixed/issue-<n>.swift`; behavioral
   regressions go under `test/<Area>/`.
4. Every test must fail before your patch and pass after it. Verify both
   directions (stash the source change, rerun the new test).
5. Never weaken an existing expectation to make a suite pass; update
   expectations only when intended behavior changed, and say so in the PR.

## Layer-Specific RUN Lines (real examples from this tree)

### Type checking / diagnostics (Sema)

```swift
// RUN: %target-typecheck-verify-swift -swift-version 5

func f(_ a: Int) {}
f(a: 5) // expected-error{{extraneous argument label 'a:' in call}}{{4-7=}}
```
`-verify` requires all expected diagnostics to match exactly (including
ranges when given). For notes/warnings use `expected-note`, `expected-warning`.

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
Copy `<pass-flags>` from a neighboring test of the same pass; they differ per
pipeline configuration (`-bcopts`, `-passes=...` etc.).

### IRGen

```swift
// RUN: %target-swift-frontend -emit-ir -primary-file %s | %FileCheck %s
```
Use `%target-cp` prefixes or mock-sdk variants only when copying neighbors
that need them (ObjC/C interop).

### Executable behavior (runtime/stdlib/miscompiles)

```swift
// RUN: %target-run-simple-swift
// REQUIRES: executable_test
```
These actually run; they need a working runnable stdlib (see environments).

### IDE / completion

```swift
// RUN: %target-swift-ide-test -code-completion -source-filename %s -code-completion-token HERE | %FileCheck %s
```
Place `-code-completion-token` marker comment at the completion point;
assert candidates with `CHECK:` lines copied from neighbors.

### Generic signatures

```swift
// RUN: %target-swift-frontend -typecheck -verify %s -debug-generic-signatures 2>&1 | %FileCheck %s
```

## Choosing The Test Directory

| Fix layer | Directory |
| --- | --- |
| Parser | `test/Parse/`, invalid syntax: `test/Parse/invalid/` |
| Sema diagnostics/types/constraints | `test/Constraints/`, `test/Sema/`, `test/type/`, `test/expr/`, `test/decl/` |
| Generics/requirements | `test/Generics/`, `test/AssociatedTypeInference/` |
| Concurrency/isolation (Sema) | `test/Concurrency/` |
| SILGen | `test/SILGen/` |
| Mandatory passes / region isolation / move-only | `test/SILOptimizer/`, `test/SIL/OwnershipVerifier/`, `test/Concurrency/` |
| Optimizer passes | `test/SILOptimizer/<PassName>/` |
| IRGen/ABI | `test/IRGen/`, `test/ABI/` |
| Runtime/casting | `test/Runtime/`, `test/Casting/`, `test/stdlib/` |
| Embedded Swift | `test/embedded/` |
| IDE | `test/IDE/`, SourceKit requests: `test/SourceKit/` |
| Driver flags | `test/Driver/` |
| Macros | `test/Macros/` |
| ABI digester / TBD | `test/api-digester/`, `test/TBD/`, `test/abi/` |

## Running Tests Locally (verified on this machine)

```bash
# $LIT / $CFG from paths.json build_llvm / build_swift
LIT=<paths.json build_llvm>/bin/llvm-lit
CFG=<paths.json build_swift>/test-macosx-arm64/lit.site.cfg
$LIT -sv --param swift_site_config=$CFG <file-or-dir>
```

Public ABI: run the neighboring `test/api-digester/` dump/compare test, not
only a typecheck. TBD: `test/TBD/` must still list the new symbol.

Single untracked test without lit: run its RUN line manually with
`bin/swift-frontend` etc., substituting `%s` with the path,
or use `$LIT ... --param` as above after saving the file inside `test/`.

## Expected-Failure Hygiene

If a fix intentionally changes diagnostics, grep the whole affected test dir
for the old message text before landing: cascades often break other tests'
expectations silently in CI.
