# SILGen Playbook

Stage: lowering the checked AST into raw SIL. 35 of 418 closed issues in the
2026-08 harvest carry the `SILGen` label; many unlabelled crashes land here.

## Key Sources

| Area | Files |
| --- | --- |
| Function emission core | `lib/SILGen/SILGenFunction.cpp/.h`, `SILGenFunctionBuilder.cpp` |
| Expressions | `lib/SILGen/SILGenExpr.cpp` (`emitExpr`, `emitApplyExpr`, `emitLoadOfRValue`) |
| Statements / patterns | `lib/SILGen/SILGenStmt.cpp`, `SILGenPattern.cpp` (`emitCatchDispatch`), `SILGenLValue.cpp` |
| Declarations / types | `lib/SILGen/SILGenDecl.cpp`, `SILGenType.cpp`, `SILGenConstructor.cpp`, `SILGenDestructor.cpp` |
| Closures / partial apply | `lib/SILGen/SILGenFunction.cpp` (`visitClosureExpr`), `lib/SILGen/SILGenProlog.cpp` (capture emission) |
| Cleanup / scope management | `lib/SILGen/Scope.cpp`, `Cleanup.cpp`, `ManagedValue.cpp` |
| Concurrency lowering | `lib/SILGen/SILGenConcurrency.cpp`; calls/actors in `SILGenApply.cpp`, `SILGenExpr.cpp` |
| Bridging ObjC/errors | `lib/SILGen/SILGenBridging.cpp` |

Correction note: closure-capture planning has moved between files across
releases. Locate it at your base commit with:
`grep -rn "CaptureInfo\|PartialApplyInst" lib/SILGen/*.cpp | head`.

## Common Bug Classes (what to inspect)

### Class G1: Crash on a shape SILGen does not expect

First question, from THIS reducer: is the program valid? If `-typecheck`
is clean and the program is invalid, open Sema. If the program is valid,
open the crashing SILGen emit path.

### Class G2: Wrong SIL emitted (valid program lowered incorrectly)

Inspect: `-emit-silgen` vs `-emit-sil` on THIS reducer; managed value /
cleanup ordering. `copy_value` band-aids are wrong unless they match
THIS semantics.

### Class G3: Missing lowering path for a new feature

Inspect: whether THIS program is valid and whether a sibling lowering
arm exists. Check both `-Onone` and `-O`.

### Class G4: Diagnostic quality after lowering

Some diagnostics (definite initialization, unreachable code, move-only
liveness) are emitted during mandatory SIL phases — see
sil-optimization.md before assuming they belong here.

## Verification Loop

```bash
ninja -C /Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64 swift-frontend

# direct repro without lit (fast iteration)
FE=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/bin/swift-frontend
$FE -emit-silgen -target arm64-apple-macosx13.0 /tmp/repro.swift

# focused tests
LIT=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64/bin/llvm-lit
CFG=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/test-macosx-arm64/lit.site.cfg
$LIT -sv --param swift_site_config=$CFG <test files>
```

Because SILGen changes can shift every later stage, also run:
`$LIT -sv --param swift_site_config=$CFG test/SILGen test/SILOptimizer/Mandatory`
(or the closest subdirectory) before declaring done.

## Regression Test Placement

- `test/SILGen/<topic>.swift` with RUN lines like:
  `// RUN: %target-swift-emit-silgen -disable-availability-checking -verify %s`
- For checking emitted SIL shape use `%target-swift-emit-silgen ... | %FileCheck`
- Ownership-sensitive lowering: add `test/SILOptimizer/` ownership-verifier
  coverage only if the bug escaped into mandatory passes
- Typed throws: pair `test/SILGen/typed_throws*.swift` neighbors with
  `test/decl/func/typed_throws.swift`
