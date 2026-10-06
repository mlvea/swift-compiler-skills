# Swift Compiler Pipeline Map For Triage

This file is the ground truth for the stage of an issue.
The Swift checkout is `swiftlang/swift`.
The path for this machine is `swift_checkout` in `swift-local-build-test/references/paths.json`.
Each compiler path below is relative to that checkout, unless the path is absolute.

`resolved-issue-patterns.md` gives label counts for 418 closed issues from the 2026-08 harvest.
The counts are crash 153, type checker 75, concurrency 37, SILGen 35, diagnostics quality 34, IRGen 17, and parser 11.
Most issues are crashes or diagnostic problems.
Use the symptom first.
Use the labels second.

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

Tooling layers run beside this pipeline.
The driver layer is `lib/Driver` and swift-driver.
The IDE layer is `lib/IDE` and `tools/SourceKit`.
ClangImporter is `lib/ClangImporter`.
Serialization is `lib/Serialization`.

## Stage Identification Table

Decide the stage in this order.

1. Use the stack trace and the assertion function names.
2. Use the failure mode of this reproducer under the flags.
3. Use the title keywords and the labels.

| Stage | Owns | Stack-trace signals | Reproducer signal | Primary tests |
| --- | --- | --- | --- | --- |
| Parser | The parser owns the token-to-syntax step. The parser owns recovery. | `swift::Parser::`, `swift::Lexer::`, `parse*Expr/Decl/Type` | `-dump-parse` alone crashes or the output differs. Error recovery positions are bad. The parser accepts invalid syntax at parse level. | `test/Parse/`, `test/Parse/invalid/` |
| Sema / Type checking | Sema owns name lookup and constraints. Sema owns overload resolution and conformance checking. Sema owns captures, effects, and availability. | `TypeCheck*.cpp`, `ConstraintSystem`, `CSSimplify`, `CSDiagnostics`, `SolverTrail` | The check fails or crashes with only `-typecheck`. Diagnostics are wrong or missing. The case is accepts-invalid. | `test/Constraints/`, `test/decl/`, `test/expr/`, `test/type/`, `test/Generics/`, `test/Sema/`, `test/Availability/`, `test/attr/` |
| Concurrency Sema | This stage owns actor isolation. This stage owns AST-level sendability checks. This stage owns `sending` and global actor inference. | `TypeCheckConcurrency.cpp`, `TypeCheckCaptures.cpp` | Isolation or sendable errors are wrong or missing at typecheck time. | Tests are the `test/Concurrency/` files that do not focus on SIL lowering. Tests also include `test/Interop/Concurrency/`. |
| SILGen | SILGen lowers a checked AST to SIL. | `SILGenFunction::`, `emit*`, `SILBuilder`. The crash occurs during `-emit-silgen`. | `-emit-silgen` crashes or emits the wrong SIL. `-typecheck` is clean. | `test/SILGen/` |
| Mandatory SIL passes | These passes own ownership transfer functions and borrow scopes. These passes own region-based isolation and move-only liveness. These passes own definite initialization on SIL. These passes own mandatory diagnostics. | `FlowIsolation`, `SendNonSendable`, `OwnershipModelElimination`, `MoveOnlyChecker`, `SILVerifier`, "SIL verification error" | The failure is at `-emit-sil` without `-O`. `-emit-silgen` is clean. Region-isolation diagnostics appear only here. The verifier fires after the mandatory passes. | Use `test/SILOptimizer/` for mandatory passes. Use `test/Concurrency/` for region diagnostics. Use `test/SIL/OwnershipVerifier/`. |
| SIL optimizations | These are performance passes. They include ARC opts, LICM, mem2reg, and inlining. They include closure specialization, CMO, and vectorization. | Pass names such as `ArcCodeMotion`, `LoopInvariantCodeMotion`, `SILMem2Reg`, `SILSROA`, and `DeadObjectElimination`. | The bug shows only under `-O` or `-Osize`. The same case is clean under `-Onone`. `.sil` unit tests fail. | `test/SILOptimizer/`, `validation-test/SILOptimizer/` |
| IRGen | IRGen lowers SIL to LLVM IR. IRGen owns ABI, layout, witness tables, and thunks. | `irgen::`, `IRGenModule::`, "IRGen assertion" | `-emit-ir` crashes or the link crashes. The build has undefined symbols. Only a release build is wrong. | `test/IRGen/`, `test/ABI/`, `api-digester` |
| Runtime / stdlib | This stage owns runtime casts, reflection, and the concurrency runtime. This stage owns stdlib behavior. | The stack shows `swift_` runtime symbols. The stack shows `EXC_BAD_ACCESS` in the running binary. | The code compiles. It misbehaves or crashes when it runs. | `test/stdlib/`, `test/Runtime/`, `test/Casting/`, `validation-test/stdlib/` |
| Driver / build | The driver owns flag handling and frontend invocation. The driver owns module resolution and WMO batching. | `swift::driver::`, JobExecutor, swift-driver | The driver result differs from a direct frontend invocation. Flag errors are bad. | `test/Driver/`, tests in the swift-driver repo |
| IDE / SourceKit | This stage owns completion, refactoring, and syntax highlighting. This stage owns cursor info and indexing. | The stack is in `swift-ide-test` or `SourceKit`. | The failure is editor-only. Reproduce it with `swift-ide-test -code-completion` or a similar command. | `test/IDE/`, `test/SourceKit/`, sourcekit-lsp repo |
| ClangImporter / C++ interop | This stage imports C, Objective-C, and C++ declarations. This stage owns bridging. | `ClangImporter`, `ImporterImpl`, `swift::importer` | The reproducer needs a C header or `-cxx-interoperability-mode`. The failure shows only with Foundation or ObjC. | `test/ClangImporter/`, `test/Interop/Cxx/`, `test/APINotes/` |
| Serialization / modules | This stage emits and reads a swiftmodule. This stage owns the module cache and cross-module references. | `Serialization`, `deserialize*`, `ModuleBuffer` | Symptoms include a stale or corrupt module cache. Cross-module optimization crashes while it reads serialized SIL. | `test/Serialization/`, `test/ModuleInterface/` |
| AutoDiff | AutoDiff owns differentiation transforms. | `AutoDiff`, `DifferentiationTransformer`, `PullbackCloner` | Reproducers use `@differentiable` or `derivative(of:)`. | `test/AutoDiff/` |
| Macros | This stage owns expansion of attached macros and freestanding macros. | `TypeCheckMacros`, `MacroExpansion`, ASTGen | Reproducers use `@freestanding`, `@attached`, or `#externalMacro`. | `test/Macros/` |
| DebugInfo | This stage owns SIL debug info and DWARF emission. | `SILDebugInfoExpression`, `DebugInfoVerifier`, DWARF tests | The debugger shows wrong values. The failure relates to `-debug-info`. Some failures are lldb-only. | `test/DebugInfo/` |

## Cross-Stage Heuristics

These rules tell you where to look from THIS reducer.
These rules do not decide the patch.

1. **Crash in SILGen or later.** Run the flag ladder on THIS reducer. If `-typecheck` is clean, ask whether THIS program is valid. If the program is invalid, open Sema. If the program is valid, open the crashing emit path. Do not assume the answer from a similar crash.
2. **Wrong diagnostic cascade from one small mistake.** Open recovery at the claim site. For argument matching, open `matchCallArgumentsImpl` in `lib/Sema/CSSimplify.cpp`. For parse recovery, open `lib/Parse/`. Do not inspect only the primary check.
3. **Sendability or isolation disagreement between Sema and `-Onone`.** Enforcement is split. Sema classifies the AST. Mandatory `SendNonSendable` tracks value-flow regions. Open both of those areas. Decide from the identity of THIS value.
4. **Works at `-Onone`, breaks at `-O`.** The cause is an optimization pass. Bisect the pass pipeline with `-Xllvm` debug flags. Or bisect that pipeline with `sil-opt` on the dumped pipelines. Do the bisect before you edit the source.
5. **Only in the editor or LSP, not in batch compile.** Batch compile does not show the failure. Open the IDE layer. Or open a parse context or a completion context that batch mode never hits. `lib/IDE` has its own caches. A missing type-completion context is a different failure.
6. **Only cross-module.** Open serialization, TBD, or the mangling of the missing fact.
7. **Only embedded, wasm, or watchos.** Open the target-specific paths. Also open the shared SIL utilities that expand generics or existentials. Always check whether THIS reproducer fails only on that target before you assume general breakage.
8. **Assertion message names an invariant.** Search for that string in `swift` and in `llvm-project`. Read the comment above the guard. The assert is the observation. The assert is not the patch.
9. **The crash site is not automatically the patch site.** Find which pass first created the bad state on THIS repro. Use the procedure in `stage-playbooks/producing-pass.md`. That file gives the flag ladder, `-sil-print-pass-name`, and the `--sil-opt-pass-count` bisect. Do not patch the assert until that pass is known.

## Where To Look Next

Read `stage-playbooks/<stage>.md` for the detail on one stage.
That file has the entry points, the inspection items, and the verification commands.

Read `regression-test-cookbook.md` for the test rules for each layer.

For a bug in `swift-driver`, `swift-syntax`, `sourcekit-lsp`, or LLVM proper, read `sibling-repos.md`.
Do not invent a frontend patch for those bugs.

Read `resolved-issue-patterns.md` for mined patterns from resolved GitHub issues.
