# type-system

The scope is the constraint solver, overload resolution, and argument matching.
The scope includes solution application and solver diagnostics.

Location hints are in the stage playbook `knowledge-base/stage-playbooks/sema.md`.
Do not repeat that playbook.

## Protects

- Put solver soundness above convenience.
  Do not prune a disjunction when the prune accepts invalid programs.
- Take diagnostics from failed solutions (`CSDiagnostics*`).
  Do not take diagnostics from guessed AST shapes after a crash.
- Argument-matching recovery must keep source-order intent (`matchCallArgumentsImpl`).
  A cascade is a recovery bug.
  A cascade is not a new primary check.
- Keep the request evaluator pure.
  Do not add new global type-checker state.
- `docs/TypeChecker.md` is the constraint spec.
  Subtype `X < Y` is not transitive.
  `X < Optional<X>` and `Optional<X> < any P` do not imply `X < any P`.
  Do not add transitivity shortcuts in `CSSimplify`.
- `ConformsTo` is stricter than `X < any P`.
  An existential `any P` does not generally conform to `P`.
  The exceptions are `any Error` and Objective-C protocol existentials.
  Existential erasure is not a conformance.
- Solution application cannot fail.
  If application of a solved system fails, constraint generation is wrong or solving is wrong.
  Do not hide that failure in application.

## Plan review

- Is the program invalid at the language level, or is the solver missing a disjunct or a conversion?
- When the failure is "failed to produce diagnostic", does the salvage path produce a bogus solution?
  Or does it produce a new diagnostic case?
- Does the plan add a special-case in `CSSimplify` that should be a general constraint?
- Does the plan use subtype transitivity, or does it treat `X < any P` as `ConformsTo`?

## PR review

- Put tests under `test/Constraints/`, or under the nearest directory, with `-typecheck -verify`.
  A crasher-only test is not enough.
- Neighboring overload tests and ambiguity tests must still mean the same thing.
- Do not "fix" a solver timeout by disabling a constraint kind.

## Reject unless

- Pair a crash-on-invalid with a user-facing diagnostic in the pass that first sees the bad shape.
  Do not use only a downstream null check.
- A new conversion rule or overload-ranking rule must cite an existing rule in the book or in an SE.
  Ranking changes are source-breaking.
  Use evolution-gate.md.
- A performance patch must show a captured disjunction explosion and a soundness argument.
  A raised solver limit is not enough.
- Salvage mode and diagnostic mode are not a second language.
  Those modes must not change the successful solution.
- Put the fix in `CSFix` or in diagnostics.
  Do not put a one-off fix in `CSGen`.
  This is the review pattern on swift#91656.
- Do not add an `if (isStdlibModule)` special case in `CSSimplify` (swift#86773).
- Keep constraint kinds distinct (`docs/TypeChecker.md`).
  Tuple shuffles are Conversion (`<c`).
  Pointer conversions are ArgumentConversion (`<a`).
  Neither kind is Subtype (`<`).
- Do not add a new failure return from solution application.

## Evolution

- Disjunctions or unions in type constraints are commonly rejected.

  https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md
- A change to overload ranking or to implicit conversion needs a pitch.

## Forum

- Diagnostic-quality threads treat "failed to produce diagnostic" as a solver-salvage bug.
  The bug is not an IR problem or an SIL problem.
- For result-type scoring, do not quietly re-rank.
  The solver must still pick the most specific solution (`docs/TypeChecker.md`).
  SE-0117 is `open` versus `public` access, not scoring.

## Abstain

Abstain when the change has no constraint change, no overload change, and no argument-matching change.
An isolation-only change belongs to `concurrency`, even when the files are under `lib/Sema/`.
