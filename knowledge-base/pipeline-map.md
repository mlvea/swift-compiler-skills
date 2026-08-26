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
| Mandatory SIL passes | ownership transfer functions, borrow scopes, region-based isolation, move-only liveness, definite initialization on SIL, mandatory diagnostics | `FlowIsolation`, `SendNonSendable`, `OwnershipModelElimination`, `MoveOnlyChecker`, `SILVerifier`, "SIL verification error" | `-Onone` still broken; verifier fires after sil-gen or after mandatory passes; raw SIL tests fail | `test/SILOptimizer/` (mandatory), `test/Concurrency/` (region diagnostics), `test/MoveOnly/` |
| SIL optimizations | performance passes: ARC opts, LICM, mem2reg, inlining, closure specialization, CMO, vectorization | pass names like `ArcCodeMotion`, `LoopInvariantCodeMotion`, `SILMem2Reg`, `SILSROA`, `DeadObjectElimination` | only broken under `-O`/`-Osize`, or fixed by `-Onone`; `.sil` unit tests fail | `test/SILOptimizer/`, `validation-test/SILOptimizer/` |
| IRGen | SIL -> LLVM IR, ABI, layout, witness tables, thunks | `irgen::`, `IRGenModule::`, "IRGen assertion" | `-emit-ir`/link crashes; undefined symbols; only release builds wrong | `test/IRGen/`, `test/ABI/`, `api-digester` |
| Runtime / stdlib | runtime casts, reflection, concurrency runtime, stdlib behavior | `swift_` runtime symbols, `EXC_BAD_ACCESS` in running binary | compiled fine, misbehaves or crashes when *run* | `test/stdlib/`, `test/Runtime/`, `test/Casting/`, `validation-test/stdlib/` |
| Driver / build | flag handling, frontend invocation, module resolution, WMO batching | `swift::driver::`, JobExecutor, swift-driver | different result driver vs direct frontend invocation; bad flag errors | `test/Driver/`, swift-driver repo tests |
| IDE / SourceKit | completion, refactoring, syntax highlighting, cursor info, indexing | `swift-ide-test` stack, `SourceKit` | editor-only; reproducible via `swift-ide-test -code-completion` etc. | `test/IDE/`, `test/SourceKit/`, sourcekit-lsp repo |
| ClangImporter / C++ interop | importing C/Objective-C/C++ decls, bridging | `ClangImporter`, `ImporterImpl`, `swift::importer` | needs a C header / `-cxx-interoperability-mode`; only with Foundation/ObjC | `test/ClangImporter/`, `test/Interop/Cxx/`, `test/APINotes/` |
| Serialization / modules | swiftmodule emit/read, module cache, cross-module refs | `Serialization`, `deserialize*`, `ModuleBuffer` | stale/corrupt module cache symptoms; cross-module optimization crashes reading serialized SIL | `test/Serialization/`, `test/Module/` |
| AutoDiff | differentiation transforms | `AutoDiff`, `DifferentiationTransformer`, `PullbackCloner` | `@differentiable`, `derivative(of:)` reproducers | `test/AutoDiff/`, `validation-test/AutoDiff/` |
| DebugInfo | SIL debug info, DWARF emission | `SILDebugInfoExpression`, `DebugInfoVerifier`, DWARF tests | debugger shows wrong values; `-debug-info` related; lldb-only failures | `test/DebugInfo/` |

## Cross-Stage Heuristics (evidence-based)

1. **Crash in SILGen or later for an odd-but-invalid program** → suspect a
   missing Sema validity check first. Prefer adding the user-facing diagnostic
   in Sema over making lower layers tolerate invalid ASTs. Precedent:
   issue 86463 (typed throws reached SILGen because an effect check was
   missing), recorded in `wiki/compiler-understanding.md`.
2. **Wrong diagnostic cascade from one small mistake** → recovery logic, not
   the primary check. Argument matching recovery lives in
   `matchCallArgumentsImpl` (`lib/Sema/CSSimplify.cpp`). Precedent: 86472.
3. **Sendability/isolation disagreement between Sema and -Onone run** →
   enforcement is split by design: AST classification in Sema, value-flow
   regions in mandatory `SendNonSendable`. Fix belongs where the value
   identity actually diverges. Precedents: 87540, 87503, 85667.
4. **Works at `-Onone`, breaks at `-O`** → optimization pass bug. Bisect the
   pass pipeline with `-Xllvm` debug flags or `sil-opt` on dumped pipelines
   before editing source.
5. **Only in editor / LSP, not batch compile** → IDE layer or delayed
   re-resolution of an AST that batch mode never exercises.
   `lib/IDE` often holds its own resolution caches.
6. **Only cross-module** → serialization boundary: what must be recorded in
   the swiftmodule vs recomputed locally.
7. **Only embedded/wasm/watchos** → check target-specific lowering paths
   (embedded uses a restricted SIL subset; wasm lacks ObjC runtime).
8. **Assertion message names the invariant** → search the string in
   `llvm-project` + `swift` to find the exact guard; read the comment above
   it; the fix usually restores the invariant, not the assert.

## Where Fix Patterns Live

Per-stage detail (entry points, common bug classes, worked examples,
verification commands): `stage-playbooks/<stage>.md`.

Test-writing rules per layer: `regression-test-cookbook.md`.

Mined patterns from resolved GitHub issues: `resolved-issue-patterns.md`.
