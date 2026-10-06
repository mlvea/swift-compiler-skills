# concurrency

The scope is actor isolation, Sendable, and region-based isolation (RBI).
The scope includes `sending` and isolation inference.
Sema classification is in scope.
Mandatory SIL region diagnostics are in scope.

The surface convention is `sending` (feature `SendingArgsAndResults`).
Do not revive `transferring` as user-facing syntax.

## Protects

- Isolation is a language rule.
  It is not an optimizer opinion.
  A patch that silences a race by skipping `SendNonSendable` or `FlowIsolation` is a `block`.
- AST-level Sendable and isolation (Sema) are separate from value-flow regions (mandatory SIL).
  The split is by design.
  Fix the layer whose identity is wrong.
- `@unchecked Sendable` and `nonisolated(unsafe)` are user escape hatches.
  They are not tools for the compiler implementation.
- For `@preconcurrency` overrides, strip concurrency before you match the superclass type (SE-0337).
  A sendability mismatch is a diagnostic.
  It is not a hard error of the form "types do not match, so the override is also illegally mutable" (swift#73158).
- Closures that call global-actor-isolated code are isolated to that actor (SE-0414 revision).
  Do not regress this rule.

## Plan review

- Can you show the reducer at `-typecheck` (Sema), or only after `-emit-sil` (region analysis)?
- Does the plan transfer a non-Sendable value that is still in use?
  Does the plan merge two actor regions?
  Those cases must stay errors (SE-0414).
- `assumeIsolated` and isolated closures must not launder task-isolated parameters into an actor region.

## PR review

- Put tests in `test/Concurrency/`.
  Cover the allowed transfer and the diagnosed use-after-transfer.
- A region-analysis change needs a SIL test or a Swift test.
  The test must fail if the merge rule is weakened.
- Do not add a new implicit `Sendable` conformance.

## Reject unless

- Diagnostics must name isolation domains that the user can name.
  Use an actor, a task, or `@MainActor`.
  Do not print only region ids.
- Do not model `sending` (SE-0430, implemented as `SendingArgsAndResults`) as an ordinary `@Sendable` closure.
- A runtime concurrency patch in `stdlib/public/Concurrency` that changes actor executor hops needs the `runtime` seat adjacent.
  A Sema-only story is not enough.

## Evolution

- SE-0306 actors are reentrant.
  Cross-actor `inout` is illegal.
- SE-0313 covers `isolated` and `nonisolated`.
  SE-0316 covers global actors.
- SE-0337: `@preconcurrency` downgrades checking.
  It does not delete checking.
- SE-0414 is region-based isolation.

  https://forums.swift.org/t/se-0414-region-based-isolation/68805

  https://forums.swift.org/t/pitch-region-based-isolation/67888
- SE-0418 covers inferring Sendable.
- SE-0430 covers `sending` parameters and results.
  It does not cover `transferring`.
- SE-0461 covers nonisolated async isolation.
  The contrast is `@concurrent` versus staying.
- Data-race safety is a Swift 6 language-mode invariant.
  Do not weaken it to recover Swift 5 source without an upcoming-feature flag.
  Diagnostics must print the surface spelling (`@concurrent`, `nonisolated(nonsending)`).
  Do not print an internal enum (swift#88335).

## Forum

Missing RBI diagnostics are usually trackable-value bugs or partition-op bugs.
They do not mean that "the code is fine".

https://forums.swift.org/t/lets-debug-missing-rbi-data-race-diagnostics/78910

## Abstain

Abstain when the change has no isolation, Sendable, actor, task, or `sending`.
Distributed-actor runtime belongs to `distributed` when those files are primary.
