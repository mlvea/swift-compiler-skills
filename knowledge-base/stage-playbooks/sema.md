# Sema / Type Checking Playbook

Stage: AST building and type checking. The largest bug family (~75 of 418
closed issues in the 2026-08 harvest carry the `type checker` label; many
crash and diagnostics-quality issues also land here).

## Key Sources

| Area | Files |
| --- | --- |
| Constraint solver | `lib/Sema/ConstraintSystem.cpp`, `CSSolver.cpp`, `Constraint.cpp` |
| Constraint simplification (calls, arguments) | `lib/Sema/CSSimplify.cpp` (`matchCallArguments`, `matchCallArgumentsImpl`, `bindNextParameter`, `claimNextNamed`) |
| Diagnostics from failed solutions | `lib/Sema/CSDiagnostics.cpp`, `CSDiagnosticsDiff.cpp` |
| Code completion solver use | `lib/IDE/CodeCompletion.cpp` and friends; Sema side in `lib/Sema/TypeCheckCodeCompletion.cpp` |
| Name lookup | `lib/Sema/TypeCheckNameLookup.cpp`, `lib/Sema/LookupVisibleDecls.cpp`, `lib/AST/NameLookup.cpp` |
| Protocol conformance checking | `lib/Sema/TypeCheckProtocol.cpp`, `TypeCheckProtocolInference.cpp`, `AssociatedTypeInference.cpp` |
| Generics | `lib/Sema/TypeCheckGeneric.cpp`, `GenericSignature.cpp` (in `lib/AST`) |
| Captures / isolation / sendability | `lib/Sema/TypeCheckCaptures.cpp`, `TypeCheckConcurrency.cpp`, `TypeCheckConcurrencyV2.cpp` if present |
| Effects (throws/rethrows/typed throws) | `lib/Sema/TypeCheckEffects.cpp`; AST contract in `include/swift/AST/ThrownErrorDestination.h` |
| Attributes / availability | `lib/Sema/TypeCheckAttr.cpp`, `TypeCheckAvailability.cpp`, `TypeCheckObjC.h` |
| Pattern/type resolution | `lib/Sema/TypeCheckPatterns.cpp`, `TypeResolution.cpp`, `TypeCheckType.cpp` |
| Misc requests | `lib/Sema/TypeChecker.cpp` (request wiring) |

Correction note: when a file listed above is missing at your base commit,
locate the owning request via its diagnostic or request name with
`grep -rn "<RequestName>" lib/Sema include/swift/AST` instead of guessing.

## Common Bug Classes And Fix Patterns

### Class S1: Crash on invalid program (robustness)

Symptom: assertion/segfault while typechecking odd code.
Pattern: find the violated assumption; decide whether the program is
*actually valid* (fix the check that rejected it) or *invalid* (add a
recovery guard + user-facing diagnostic). Prefer a diagnostic in the pass
that first sees the bad shape. Add the reducer to
`validation-test/compiler_crashers_fixed/issue-<n>.swift` only for crashers;
normal regressions go under `test/<Area>/`.

Worked example: 86438, 86437 (see `issues/cases/`).

### Class S2: Accepts-invalid

Symptom: code compiles that should not.
Pattern: identify the language invariant (read the Swift book section /
evolution proposal), find where it is enforced, learn why the check was
skipped (early exit, recovery path, missing substitution). Fix by restoring
enforcement at that point, not by adding a parallel check downstream.

Worked examples: 86026, 85742 (isolated conformance), 85111 (bridging proves
conformance), recorded in case files.

### Class S3: Rejects-valid / wrong error

Symptom: false positive, misleading error, cascade.
Pattern: reproduce with `-typecheck -verify`; if a *cascade* appears,
suspect recovery ordering (argument matching, trailing closures) before the
primary check. Keep source-order intent stable during recovery.
Worked example: 86472 (`test/Constraints/argument_matching.swift`).

### Class S4: Failed to produce diagnostic

Symptom: "failed to produce diagnostic for expression" or silently accepted
invalid expression.
Pattern: usually the solver salvages a solution that should fail, or a
diagnostic path bails after `SolutionApplication` fails. Trace
`solutionApply` failures; often the fix teaches the failure diagnostic
system one more case (`CSDiagnostics.cpp`).

### Class S5: Solver performance blowup

Symptom: timeout/hang on pathological but small input.
Pattern: capture with `-solver-expression-time-threshold`, find disjunction
explosion (overloads × conversions × literal conformances). Fixes usually
prune disjunctions earlier or add short-circuit rules. Never "fix" by
weakening soundness.

## Verification Loop

```bash
# rebuild frontend only (Sema changes never need stdlib rebuild)
ninja -C /Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64 swift-frontend

# run focused lit test(s)
LIT=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64/bin/llvm-lit
CFG=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/test-macosx-arm64/lit.site.cfg
$LIT -sv --param swift_site_config=$CFG <test files>
```

Also always rerun the closest neighboring tests (same directory, similar
feature) because recovery changes leak into adjacent diagnostics.

## Regression Test Placement

- Argument matching / calls: `test/Constraints/argument_matching.swift`,
  `test/Constraints/calls.swift`, or new `test/Constraints/issue-<n>*.swift`
- Isolation/concurrency Sema: `test/Concurrency/*.swift` with
  `-strict-concurrency=complete` style RUN lines copied from neighbors
- Generics/substitutions: `test/Generics/` plus
  `-debug-generic-signatures` FileCheck when the requirement system changed
- Effects/typed throws: `test/decl/func/typed_throws.swift` and neighbors
- Crash reducers that are pure robustness:
  `validation-test/compiler_crashers_fixed/` (named issue-<n>.swift)
