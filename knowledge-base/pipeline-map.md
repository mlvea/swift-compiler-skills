# Swift Compiler Pipeline Map For Triage

Ground truth for deciding which compiler stage an issue belongs to.
Swift checkout: `/Users/madushan/Documents/Github/swiftlang/swift`.
All paths below are relative to that checkout unless absolute.

Label frequency across 418 closed issues harvested 2026-08 (see
`resolved-issue-patterns.md`): crash 153, type checker 75, concurrency 37,
SILGen 35, diagnostics quality 34, IRGen 17, parser 11. Most issues are
crashes or diagnostic problems; use the symptom first, labels second.

## The Pipeline In Order

```
source text
  -> Parse/Lex        lib/Parse, lib/Markup            syntax trees
  -> AST/Sema         lib/Sema, lib/AST, lib/ASTGen    typed, checked AST
  -> SILGen           lib/SILGen                       raw SIL
  -> Mandatory SIL    lib/SILOptimizer/Mandatory       ownership, isolation, diagnostics
  -> SIL Optimizations lib/SILOptimizer/{Transforms,Analysis,...}  optimized SIL
  -> IRGen            lib/IRGen                        LLVM IR
  -> LLVM backend     llvm-project (local sibling checkout)
  -> Runtime          stdlib/public/runtime, lib/Runtime
```

Tooling layers run beside this pipeline: Driver (`lib/Driver`, swift-driver),
IDE (`lib/IDE`, `tools/SourceKit`), ClangImporter (`lib/ClangImporter`),
Serialization (`lib/Serialization`).

## Stage Identification Table

Decide in this order: (1) stack trace / assertion function names, (2) the
reproducer's failure mode under flags, (3) title keywords and labels.

| Stage | Owns | Stack-trace signals | Reproducer signal | Primary tests |
| --- | --- | --- | --- | --- |
| Parser | tokens -> syntax, recovery | `swift::Parser::`, `swift::Lexer::`, `parse*Expr/Decl/Type` | `-dump-parse` alone crashes or differs; bad error recovery positions; invalid syntax accepted at parse level | `test/Parse/`, `test/Parse/invalid/` |
| Sema / Type checking | name lookup, constraints, overload resolution, conformance checking, captures, effects, availability | `TypeCheck*.cpp`, `ConstraintSystem`, `CSSimplify`, `CSDiagnostics`, `SolverTrail` | fails/crashes with just `-typecheck`; wrong or missing diagnostics; accepts-invalid | `test/Constraints/`, `test/decl/`, `test/expr/`, `test/type/`, `test/Generics/`, `test/Sema/`, `test/Availability/`, `test/attr/` |
| Concurrency Sema | actor isolation, sendability of AST-level checks, `sending`, global actor inference | `TypeCheckConcurrency.cpp`, `TypeCheckCaptures.cpp` | isolation/sendable errors wrong or missing at typecheck time | `test/Concurrency/` (files without `SIL` lowering focus), `test/Interop/Concurrency/` |
| SILGen | checked AST -> SIL | `SILGenFunction::`, `emit*`, `SILBuilder`, crashes during `-emit-silgen` | `-emit-silgen` crashes or emits wrong SIL while `-typecheck` is clean | `test/SILGen/` |
| Mandatory SIL passes | ownership transfer functions, borrow scopes, region-based isolation, move-only liveness, definite initialization on SIL, mandatory diagnostics | `FlowIsolation`, `SendNonSendable`, `OwnershipModelElimination`, `MoveOnlyChecker`, `SILVerifier`, "SIL verification error" | `-Onone` still broken; verifier fires after sil-gen or after mandatory passes; raw SIL tests fail | `test/SILOptimizer/` (mandatory), `test/Concurrency/` (region diagnostics), `test/SIL/OwnershipVerifier/` |
| SIL optimizations | performance passes: ARC opts, LICM, mem2reg, inlining, closure specialization, CMO, vectorization | pass names like `ArcCodeMotion`, `LoopInvariantCodeMotion`, `SILMem2Reg`, `SILSROA`, `DeadObjectElimination` | only broken under `-O`/`-Osize`, or fixed by `-Onone`; `.sil` unit tests fail | `test/SILOptimizer/`, `validation-test/SILOptimizer/` |
| IRGen | SIL -> LLVM IR, ABI, layout, witness tables, thunks | `irgen::`, `IRGenModule::`, "IRGen assertion" | `-emit-ir`/link crashes; undefined symbols; only release builds wrong | `test/IRGen/`, `test/ABI/`, `api-digester` |
| Runtime / stdlib | runtime casts, reflection, concurrency runtime, stdlib behavior | `swift_` runtime symbols, `EXC_BAD_ACCESS` in running binary | compiled fine, misbehaves or crashes when *run* | `test/stdlib/`, `test/Runtime/`, `test/Casting/`, `validation-test/stdlib/` |
| Driver / build | flag handling, frontend invocation, module resolution, WMO batching | `swift::driver::`, JobExecutor, swift-driver | different result driver vs direct frontend invocation; bad flag errors | `test/Driver/`, swift-driver repo tests |
| IDE / SourceKit | completion, refactoring, syntax highlighting, cursor info, indexing | `swift-ide-test` stack, `SourceKit` | editor-only; reproducible via `swift-ide-test -code-completion` etc. | `test/IDE/`, `test/SourceKit/`, sourcekit-lsp repo |
| ClangImporter / C++ interop | importing C/Objective-C/C++ decls, bridging | `ClangImporter`, `ImporterImpl`, `swift::importer` | needs a C header / `-cxx-interoperability-mode`; only with Foundation/ObjC | `test/ClangImporter/`, `test/Interop/Cxx/`, `test/APINotes/` |
| Serialization / modules | swiftmodule emit/read, module cache, cross-module refs | `Serialization`, `deserialize*`, `ModuleBuffer` | stale/corrupt module cache symptoms; cross-module optimization crashes reading serialized SIL | `test/Serialization/`, `test/ModuleInterface/` |
| AutoDiff | differentiation transforms | `AutoDiff`, `DifferentiationTransformer`, `PullbackCloner` | `@differentiable`, `derivative(of:)` reproducers | `test/AutoDiff/` |
| DebugInfo | SIL debug info, DWARF emission | `SILDebugInfoExpression`, `DebugInfoVerifier`, DWARF tests | debugger shows wrong values; `-debug-info` related; lldb-only failures | `test/DebugInfo/` |

## Cross-Stage Heuristics

These decide *where to look* from THIS reducer. They do not decide the
patch.

1. **Crash in SILGen or later** → run the flag ladder on THIS reducer.
   If `-typecheck` is clean, ask whether THIS program is valid. If it is
   invalid, open Sema. If it is valid, open the crashing emit path. Do
   not assume the answer from a similar crash.
2. **Wrong diagnostic cascade from one small mistake** → open recovery
   at the claim site (argument matching: `matchCallArgumentsImpl` in
   `lib/Sema/CSSimplify.cpp`; parse: `lib/Parse/`), not only the primary
   check.
3. **Sendability/isolation disagreement between Sema and `-Onone`** →
   enforcement is split: AST classification in Sema, value-flow regions
   in mandatory `SendNonSendable`. Open both; decide from THIS value's
   identity.
4. **Works at `-Onone`, breaks at `-O`** → optimization pass. Bisect the
   pass pipeline with `-Xllvm` debug flags or `sil-opt` on dumped
   pipelines before editing source.
5. **Only in editor / LSP, not batch compile** → IDE layer or a parse/
   completion context batch mode never hits. `lib/IDE` has its own
   caches; missing type-completion context is a different failure.
6. **Only cross-module** → serialization / TBD / mangling of the
   missing fact.
7. **Only embedded/wasm/watchos** → target-specific paths *and* shared
   SIL utilities that expand generics/existentials. Confirm the repro is
   target-gated before assuming general breakage.
8. **Assertion message names an invariant** → search the string in
   `swift` + `llvm-project`; read the comment above the guard. The
   assert is the observation, not the patch.
9. **Crash site is not automatically the patch site.** Find which pass
   first created the bad state on THIS repro (flag ladder / sil-opt
   bisect). Do not patch the assert until that is known.

## Where To Look Next

Per-stage detail (entry points, what to inspect, verification
commands): `stage-playbooks/<stage>.md`.

Test-writing rules per layer: `regression-test-cookbook.md`.

Mined patterns from resolved GitHub issues: `resolved-issue-patterns.md`.
