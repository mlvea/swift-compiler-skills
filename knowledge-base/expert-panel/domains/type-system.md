# type-system

Constraint solver, overload resolution, argument matching, solution
application, solver diagnostics. Location hints: stage playbook
`knowledge-base/stage-playbooks/sema.md` — do not repeat it.

## Protects

- Solver soundness over convenience: do not prune a disjunction if that
  accepts invalid programs.
- Diagnostics come from failed solutions (`CSDiagnostics*`), not from
  guessed AST shapes after a crash.
- Argument-matching recovery must keep source-order intent
  (`matchCallArgumentsImpl`). Cascades are recovery bugs, not a new
  primary check.
- Request-evaluator purity: no new global type-checker state.

## Plan review

- Is the program invalid at the language level, or is the solver
  missing a disjunct/conversion?
- If "failed to produce diagnostic", is the salvage path producing a
  bogus solution instead of a new diagnostic case?
- Does the plan add a special-case in `CSSimplify` that should be a
  general constraint?

## PR review

- Tests under `test/Constraints/` (or nearest) with `-typecheck -verify`,
  not only a crasher.
- Neighboring overload/ambiguity tests still mean the same thing.
- No solver timeout "fix" that disables a constraint kind.

## Reject unless

- Crash-on-invalid is paired with a user-facing diagnostic in the pass
  that first sees the bad shape — not a downstream null check.
- New conversion/overload ranking cites an existing rule (book or SE).
  Ranking changes are source-breaking; run the evolution gate.
- Performance patches show a captured disjunction explosion and a
  soundness argument, not just a raised solver limit.
- Salvage/diagnostic mode is not a second language: it must not change
  the successful solution.
- Fixes land in `CSFix` / diagnostics, not a one-off in `CSGen`
  (review pattern on swift#91656).
- No `if (isStdlibModule)` special case in `CSSimplify` (swift#86773).

## Evolution

- Disjunctions/unions in type constraints are commonly rejected
  (https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md).
- Overload ranking and implicit conversion changes need a pitch.

## Forum / SE

- Diagnostic quality threads treat "failed to produce diagnostic" as a
  solver-salvage bug, not an IR/SIL problem.
- SE-0117 / result-type scoring history: do not quietly re-rank.

## Abstain

No constraint/overload/argument-matching change. Isolation-only changes
belong to `concurrency` even if they live under `lib/Sema/`.
