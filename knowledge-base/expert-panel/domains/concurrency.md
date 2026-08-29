# concurrency

Actor isolation, Sendable, region-based isolation (RBI), sending /
transferring, isolation inference. Sema classification **and**
mandatory SIL region diagnostics are in scope.

## Protects

- Isolation is a language rule, not an optimizer opinion. A patch that
  silences a race by skipping `SendNonSendable` or `FlowIsolation` is a
  `block`.
- AST-level Sendable/isolation (Sema) and value-flow regions (mandatory
  SIL) are split by design. Fix the layer whose identity is wrong.
- `@unchecked Sendable` and `nonisolated(unsafe)` are user escape
  hatches, not compiler implementation tools.
- Closures that call global-actor-isolated code are isolated to that
  actor (SE-0414 revision). Do not regress this.

## Plan review

- Can the reducer be shown at `-typecheck` (Sema) or only after
  `-emit-sil` (region analysis)?
- Does the plan transfer a non-Sendable value that is still used, or
  merge two actor regions? Those must stay errors (SE-0414).
- `assumeIsolated` / isolated closures must not launder task-isolated
  parameters into an actor region.

## PR review

- Tests in `test/Concurrency/` covering both the allowed transfer and
  the diagnosed use-after-transfer.
- Region analysis changes need a SIL or Swift test that fails if the
  merge rule is weakened.
- No new implicit `Sendable` conformance.

## Reject unless

- Diagnostics refer to isolation domains the user can name (actor,
  task, `@MainActor`), not "region ids".
- `sending` / `transferring` (SE-0430) conventions are not modeled as
  ordinary `@Sendable` closures.
- Runtime concurrency (`stdlib/public/Concurrency`) patches that change
  actor executor hops need `runtime` adjacent, not a Sema-only story.

## Evolution

- SE-0306 actors (reentrant; cross-actor `inout` illegal)
- SE-0313 isolated/nonisolated; SE-0316 global actors
- SE-0337 `@preconcurrency` downgrades, does not delete, checking
- SE-0414 region-based isolation
  https://forums.swift.org/t/se-0414-region-based-isolation/68805
  https://forums.swift.org/t/pitch-region-based-isolation/67888
- SE-0418 inferring Sendable
- SE-0430 transferring / `sending` parameters and results
- SE-0461 nonisolated async isolation (`@concurrent` vs staying)
- Data-race safety is a Swift 6 language mode invariant; do not weaken
  it to recover Swift 5 source without an upcoming-feature flag. Diagnostics
  must print surface spelling (`@concurrent`, `nonisolated(nonsending)`),
  not an internal enum (swift#88335).

## Forum

Missing RBI diagnostics are usually trackable-value / partition-op
bugs, not "the code is fine":
https://forums.swift.org/t/lets-debug-missing-rbi-data-race-diagnostics/78910

## Abstain

No isolation, Sendable, actor, task, or `sending` in the change.
Distributed-actor runtime belongs to `distributed` when those files
are primary.
