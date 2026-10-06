# SIL Optimization Playbook

This file covers mandatory SIL passes and the optimizing pipeline.
It also covers ownership verification and region verification at SIL level.
At least 9 issues in the 2026-08 harvest carry a `SIL` label.
Most miscompiles that show only at `-O` land here.
Most crashes that report "SIL verification error" land here.

## Key Sources

| Area | Files |
| --- | --- |
| Mandatory pass pipeline | The directory is `lib/SILOptimizer/Mandatory/`. Notable files include `OwnershipModelEliminator.cpp`, `FlowIsolation.cpp`, `SendNonSendable.cpp`, `MoveOnly*Checker*.cpp`, `DefiniteInitialization.cpp`, `DataflowDiagnostics.cpp`, `PredictableMemOpt.cpp`, and `RawSILInstLowering.cpp`. Definite-initialization diagnostics do run here as a dataflow pass. They do not run only in Sema. |
| Region-based isolation | The pass is `lib/SILOptimizer/Mandatory/SendNonSendable.cpp`. The analysis is `lib/SILOptimizer/Analysis/RegionAnalysis.cpp`. The header is `RegionAnalysisImplementation.h`. |
| Flow isolation | The file is `lib/SILOptimizer/Mandatory/FlowIsolation.cpp`. The function is `FunctionInfo::analyze`. |
| Pass manager / pipelines | The directory is `lib/SILOptimizer/PassManager/`. Pipeline definitions are in `lib/SILOptimizer/PassManager/Pipelines.cpp`. |
| ARC / ownership opts | The directory is `lib/SILOptimizer/Transforms/`. Files include `SILMem2Reg.cpp`, `SILSROA.cpp`, the ARC-related passes, and `DeadObjectElimination.cpp`. |
| Analyses | The directory is `lib/SILOptimizer/Analysis/`. Examples include Escape, ValueLifetime, AliasAnalysis, and others. |
| Utils used by many passes | Many passes use `lib/SILOptimizer/Utils/InstOptUtils.cpp`. Many passes use `ValueUtils.cpp`. |
| Verifier | `lib/SIL/Verifier/` |
| Cross-module opt | This area reads serialized SIL. The code is in `lib/Serialization/`. The flag is `-experimental-cross-module-optimization`. |

Correction note: mandatory-pass file names shift between releases.
Passes are renamed or folded.
Always confirm the name before you use it.
Run `ls lib/SILOptimizer/Mandatory/ | grep -i <topic>`.

## Common Bug Classes (what to inspect)

### Class O1: SIL verifier assertion ("SIL verification error")

The message names the broken invariant.
Read the guard in `lib/SIL/Verifier/*.cpp`.
Find the earlier pass that produced the ill-formed instruction on THIS reducer.

Start with `-Xfrontend -sil-verify-none`.
Then enable verification again after `-emit-silgen`.
Then enable verification again after the mandatory passes.
Then enable verification again after the optimized passes.
Or run `sil-opt --sil-pass-pipeline-dump`.

Never weaken the verifier to silence the assert.

### Class O2: -O-only miscompile or crash

Reproduce the clean case with `-Onone`.
Reproduce the broken case with `-O` or `-Osize`.

Dump the pipeline.
Run `sil-opt` one pass at a time until THIS SIL diverges.
The last applied pass is the suspect.
Read the safety checks that already exist in that pass.
Do not assume that the source-level symptom is the missing condition.

### Class O3: Region/isolation diagnostics wrong (SendNonSendable)

Sema classifies the boundaries.
SendNonSendable tracks value regions through SIL.
Open both `RegionAnalysis*` and the Sema walk.
Decide from the identity of THIS value.
Closures, partial applies, or temporaries can hide that identity.

### Class O4: Ownership transfer function bugs (noncopyable, borrowing)

Symptoms include the message "value is consumed".
Symptoms include partial-initialization liveness.
Symptoms include a borrow-scope violation.

Inspect `lib/SILOptimizer/Mandatory/MoveOnly*`.
Inspect the lowering that produced the borrow on THIS reducer.
For a producing-pass bisect, use a named pass and `--sil-opt-pass-count`.
The procedure is in `producing-pass.md`.

## Verification Loop

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
ninja -C "$B" swift-frontend

# unit-test a .sil change directly
"$SO" -enable-sil-verify-all <pass flags> /tmp/case.sil
```

For an end-to-end behavior difference, use `%target-run-simple-swift` tests.
Those tests execute the program.
Do not use a FileCheck-only test when the bug is a miscompile.

## Regression Test Placement

- For a pure SIL shape, use `test/SILOptimizer/<PassName>/*.sil`. Use `%target-sil-opt ... | %FileCheck`.
- For mandatory isolation or ownership, use `test/SILOptimizer/` and `test/Concurrency/`. Copy RUN lines from neighboring tests.
- For an executable miscompile, use `test/<Area>/` with `%target-run-simple-swift`.
- Keep each `.sil` reducer minimal. Strip everything that survives deletion.
