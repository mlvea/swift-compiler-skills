# SILGen Playbook

This stage lowers the checked AST into raw SIL.
In the 2026-08 harvest, 35 of 418 closed issues carry the `SILGen` label.
Many unlabeled crashes also land here.

## Key Sources

| Area | Files |
| --- | --- |
| Function emission core | `lib/SILGen/SILGenFunction.cpp/.h`, `SILGenFunctionBuilder.cpp` |
| Expressions | `lib/SILGen/SILGenExpr.cpp` (`emitExpr`, `emitApplyExpr`, `emitLoadOfRValue`) |
| Statements / patterns | `lib/SILGen/SILGenStmt.cpp`, `SILGenPattern.cpp` (`emitCatchDispatch`), `SILGenLValue.cpp` |
| Declarations / types | `lib/SILGen/SILGenDecl.cpp`, `SILGenType.cpp`, `SILGenConstructor.cpp`, `SILGenDestructor.cpp` |
| Closures / partial apply | `lib/SILGen/SILGenFunction.cpp` (`visitClosureExpr`), `lib/SILGen/SILGenProlog.cpp` (capture emission) |
| Cleanup / scope management | `lib/SILGen/Scope.cpp`, `Cleanup.cpp`, `ManagedValue.cpp` |
| Concurrency lowering | The file is `lib/SILGen/SILGenConcurrency.cpp`. Calls and actors are in `SILGenApply.cpp` and `SILGenExpr.cpp`. |
| Bridging ObjC/errors | `lib/SILGen/SILGenBridging.cpp` |

Correction note: closure-capture planning has moved between files across releases.
Locate that code at your base commit.
Run `grep -rn "CaptureInfo\|PartialApplyInst" lib/SILGen/*.cpp | head`.

## Common Bug Classes (what to inspect)

### Class G1: Crash on a shape SILGen does not expect

The first question uses THIS reducer.
Is the program valid?
If `-typecheck` is clean and the program is invalid, open Sema.
If the program is valid, open the crashing SILGen emit path.

### Class G2: Wrong SIL emitted (valid program lowered incorrectly)

Inspect `-emit-silgen` and `-emit-sil` on THIS reducer.
Inspect managed-value ordering and cleanup ordering.
`copy_value` band-aids are wrong unless they match THIS semantics.

### Class G3: Missing lowering path for a new feature

Inspect whether THIS program is valid.
Inspect whether a sibling lowering arm exists.
Check both `-Onone` and `-O`.

### Class G4: Diagnostic quality after lowering

Some diagnostics are emitted during mandatory SIL phases.
Those diagnostics are definite initialization, unreachable code, and move-only liveness.
Read sil-optimization.md before you assume that they belong here.

## Verification Loop

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
ninja -C "$B" swift-frontend

# direct repro without lit (fast iteration)
"$FE" -emit-silgen -target arm64-apple-macosx13.0 /tmp/repro.swift

# focused tests
"$LIT" -sv --param swift_site_config="$CFG" <test files>
```

A SILGen change can shift every later stage.
Also run this command before you declare the work done.
The command is `$LIT -sv --param swift_site_config=$CFG test/SILGen test/SILOptimizer/Mandatory`.
Or run the closest subdirectory instead of those two paths.

## Regression Test Placement

- Use `test/SILGen/<topic>.swift`. One RUN line is `// RUN: %target-swift-emit-silgen -disable-availability-checking -verify %s`.
- To check the emitted SIL shape, use `%target-swift-emit-silgen ... | %FileCheck`.
- For ownership-sensitive lowering, add ownership-verifier coverage in `test/SILOptimizer/`. Add that coverage only if the bug escaped into the mandatory passes.
- For typed throws, pair neighbors of `test/SILGen/typed_throws*.swift` with `test/decl/func/typed_throws.swift`.
