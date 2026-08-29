# SIL Optimization Playbook

Covers both mandatory SIL passes and the optimizing pipeline, plus SIL-level
ownership/region verification. 9+ issues in the 2026-08 harvest carry `SIL`
labels; most `-O`-only miscompiles and "SIL verification error" crashes land
here.

## Key Sources

| Area | Files |
| --- | --- |
| Mandatory pass pipeline | `lib/SILOptimizer/Mandatory/` — notable: `OwnershipModelEliminator.cpp`, `FlowIsolation.cpp`, `SendNonSendable.cpp`, `MoveOnly*Checker*.cpp`, `DefiniteInitialization.cpp`, `DataflowDiagnostics.cpp`, `PredictableMemOpt.cpp`, `RawSILInstLowering.cpp`. Note: definite-initialization diagnostics DO run here as a dataflow pass, not only in Sema |
| Region-based isolation | `lib/SILOptimizer/Mandatory/SendNonSendable.cpp`, analysis in `lib/SILOptimizer/Analysis/RegionAnalysis.cpp`, `RegionAnalysisImplementation.h` |
| Flow isolation | `lib/SILOptimizer/Mandatory/FlowIsolation.cpp` (`FunctionInfo::analyze`) |
| Pass manager / pipelines | `lib/SILOptimizer/PassManager/`, pipeline definitions in `lib/SILOptimizer/PassManager/Pipelines.cpp` |
| ARC / ownership opts | `lib/SILOptimizer/Transforms/` — `SILMem2Reg.cpp`, `SILSROA.cpp`, ARC-related passes, `DeadObjectElimination.cpp` |
| Analyses | `lib/SILOptimizer/Analysis/` (Escape, ValueLifetime, AliasAnalysis, ...) |
| Utils used by many passes | `lib/SILOptimizer/Utils/InstOptUtils.cpp`, `ValueUtils.cpp` |
| Verifier | `lib/SIL/Verifier/` |
| Cross-module opt | serialized-SIL reading: `lib/Serialization/`, `-experimental-cross-module-optimization` |

Correction note: mandatory pass file names shift between releases (passes get
renamed or folded). Always confirm with:
`ls lib/SILOptimizer/Mandatory/ | grep -i <topic>`.

## Common Bug Classes (what to inspect)

### Class O1: SIL verifier assertion ("SIL verification error")

The message names the broken invariant. Read the guard in
`lib/SIL/Verifier/*.cpp`, then find which earlier pass produced the
ill-formed instruction on THIS reducer: `-Xfrontend -sil-verify-none`,
then re-enable after `-emit-silgen` / mandatory / optimized, or
`sil-opt --sil-pass-pipeline-dump`. Never weaken the verifier to silence
the assert.

### Class O2: -O-only miscompile or crash

Reproduce with `-Onone` (clean) vs `-O`/`-Osize` (broken). Bisect: dump
the pipeline, run `sil-opt` one pass at a time until THIS SIL diverges.
The last pass applied is the suspect. Read that pass's existing safety
checks; do not assume the source-level symptom is the missing condition.

### Class O3: Region/isolation diagnostics wrong (SendNonSendable)

Sema classifies boundaries; SendNonSendable tracks value regions through
SIL. Open both `RegionAnalysis*` and the Sema walk; decide from THIS
value's identity (closures/partial applies/temporaries can hide it).

### Class O4: Ownership transfer function bugs (noncopyable, borrowing)

Symptoms: "value is consumed", partial-initialization liveness, borrow
scope violations. Inspect `lib/SILOptimizer/Mandatory/MoveOnly*` and the
lowering that produced the borrow on THIS reducer.

## Verification Loop

```bash
ninja -C /Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64 swift-frontend sil-opt

# unit-test a .sil change directly
SO=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/bin/sil-opt
$SO -enable-sil-verify-all <pass flags> /tmp/case.sil
```

For end-to-end behavior differences use
`%target-run-simple-swift` tests (they execute) rather than FileCheck-only,
when the bug is a miscompile.

## Regression Test Placement

- Pure SIL shape: `test/SILOptimizer/<PassName>/*.sil` using
  `%target-sil-opt ... | %FileCheck`
- Mandatory isolation/ownership: `test/SILOptimizer/` + `test/Concurrency/`
  RUN lines copied from neighbors
- Executable miscompiles: `test/<Area>/` with `%target-run-simple-swift`
- Keep `.sil` reducers minimal: strip everything that survives deletion
