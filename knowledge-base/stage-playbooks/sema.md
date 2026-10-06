# Sema / Type Checking Playbook

This stage builds the AST and type-checks it.
This is the largest bug family in the 2026-08 harvest.
About 75 of 418 closed issues carry the `type checker` label.
Many crash issues also land here.
Many diagnostics-quality issues also land here.

## Key Sources

| Area | Files |
| --- | --- |
| Constraint solver | `lib/Sema/ConstraintSystem.cpp`, `CSSolver.cpp`, `Constraint.cpp` |
| Constraint simplification (calls, arguments) | `lib/Sema/CSSimplify.cpp` (`matchCallArguments`, `matchCallArgumentsImpl`, `bindNextParameter`, `claimNextNamed`) |
| Diagnostics from failed solutions | `lib/Sema/CSDiagnostics.cpp`, `CSDiagnosticsDiff.cpp` |
| Code completion solver use | `lib/IDE/CodeCompletion.cpp` and related files. The Sema side is `lib/Sema/TypeCheckCodeCompletion.cpp`. |
| Name lookup | `lib/Sema/TypeCheckNameLookup.cpp`, `lib/Sema/LookupVisibleDecls.cpp`, `lib/AST/NameLookup.cpp` |
| Protocol conformance checking | `lib/Sema/TypeCheckProtocol.cpp`, `TypeCheckProtocolInference.cpp`, `AssociatedTypeInference.cpp` |
| Generics | `lib/Sema/TypeCheckGeneric.cpp`. `GenericSignature.cpp` is in `lib/AST`. |
| Captures / isolation / sendability | `lib/Sema/TypeCheckCaptures.cpp`, `TypeCheckConcurrency.cpp`. Use `TypeCheckConcurrencyV2.cpp` if that file is present. |
| Effects (throws, rethrows, typed throws) | Effects cover throws, rethrows, and typed throws. The file is `lib/Sema/TypeCheckEffects.cpp`. The AST contract is `include/swift/AST/ThrownErrorDestination.h`. |
| Attributes / availability | `lib/Sema/TypeCheckAttr.cpp`, `TypeCheckAvailability.cpp`, `TypeCheckObjC.h` |
| Pattern and type resolution | `lib/Sema/TypeCheckPatterns.cpp`, `TypeResolution.cpp`, `TypeCheckType.cpp` |
| Misc requests | `lib/Sema/TypeChecker.cpp` wires the requests. |

Correction note: when a listed file is missing at your base commit, do not guess.
Find the owning request by its diagnostic or by its request name.
Run `grep -rn "<RequestName>" lib/Sema include/swift/AST`.

## Common Bug Classes (what to inspect)

### Class S1: Crash on invalid program (robustness)

The symptom is an assertion or a segfault during typechecking of odd code.
Inspect the violated assumption.
Decide from THIS reducer whether the program is valid or invalid.
Then inspect the pass that first sees that shape.
Put crashers in `validation-test/compiler_crashers_fixed/issue-<n>.swift`.
Put behavioral regressions under `test/<Area>/`.

### Class S2: Accepts-invalid

The symptom is code that compiles but should not compile.
Inspect the language rule in the book or in an evolution proposal.
Inspect the existing enforcement site.
Find why the check was skipped for THIS reducer.
A cause can be an early exit, recovery, or a missing substitution.
Do not add a parallel check downstream until you know that cause.

### Class S3: Rejects-valid / wrong error

The symptom is a false positive, a misleading error, or a cascade.
Inspect `-typecheck -verify` on THIS reducer.
If a cascade appears, open the recovery ordering first.
Check argument matching and trailing closures.
Do that before you change the primary check.

### Class S4: Failed to produce diagnostic

The symptom is the message "failed to produce diagnostic for expression".
Or the compiler silently accepts an invalid expression.
Inspect solver salvage for THIS expression.
Inspect `SolutionApplication` for THIS expression.
Inspect `CSDiagnostics.cpp` for THIS expression.

### Class S5: Solver performance blowup

The symptom is a timeout or a hang on pathological but small input.
Inspect `-solver-expression-time-threshold`.
Inspect the disjunction explosion.
Do not weaken soundness as a fix.

## Verification Loop

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
# rebuild frontend only (Sema changes never need stdlib rebuild)
ninja -C "$B" swift-frontend

# run focused lit test(s)
"$LIT" -sv --param swift_site_config="$CFG" <test files>
```

Also rerun the closest neighboring tests.
Use the same directory and a similar feature.
Recovery changes leak into adjacent diagnostics.

## Regression Test Placement

- For argument matching or calls, use `test/Constraints/argument_matching.swift` or `test/Constraints/calls.swift`. Or add `test/Constraints/issue-<n>*.swift`.
- For isolation or concurrency Sema, use `test/Concurrency/*.swift`. Copy `-strict-concurrency=complete` style RUN lines from neighbors.
- For generics or substitutions, use `test/Generics/`. When the requirement system changed, add `-debug-generic-signatures` FileCheck.
- For effects or typed throws, use `test/decl/func/typed_throws.swift` and its neighbors.
- For a pure robustness crash reducer, use `validation-test/compiler_crashers_fixed/`. Name the file `issue-<n>.swift`.
