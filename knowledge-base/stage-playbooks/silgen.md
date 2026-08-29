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

## Common Bug Classes And Fix Patterns

### Class G1: Crash because Sema allowed a shape SILGen does not expect

First question: should this program have been rejected in Sema?
If yes, fix Sema (see sema.md class S2). Only teach SILGen to handle or
diagnose-invalid when the AST is legitimately valid. Never emit
`unimplemented()` for a case a user can write.

Worked example: typed-throws crash 86463 (still open). Issue discussion:
reject in Sema; do not implement the SILGen `E2→E1` throw conversion
(`feature not implemented`). Durable lesson: "SILGen lowering assumes checked error
destinations" in `wiki/compiler-understanding.md`.

### Class G2: Wrong SIL emitted (valid program lowered incorrectly)

Pattern: reproduce with `-emit-silgen` vs `-emit-sil`; read emitted SIL with
`-Xfrontend -sil-print-types` style flags or dump to file. Identify which
managed value / cleanup ordering breaks ownership or lifetime. Fix by using
the right `ManagedValue` borrow/ownership operation, not by inserting
`copy_value` band-aids unless that genuinely matches the semantics.

Worked examples from local cases: 87141 (consumed storage address),
87396 (borrowed projection for noncopyable member rvalues), 85941 (borrow
through conditional expressions).

### Class G3: Missing lowering path for a new feature

New syntax/features often parse+typecheck but lack a lowering switch arm.
The fix adds the missing arm mirroring an existing sibling case.
Check both `-Onone` and `-O` since optimization passes assume well-formed
raw SIL.

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
