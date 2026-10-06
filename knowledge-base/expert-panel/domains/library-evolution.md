# library-evolution

The scope is availability, resilience, and source compatibility.
The scope includes `@frozen`, `@inlinable`, `@usableFromInline`, and upcoming-feature flags.

## Protects

- An `@inlinable` body cannot reference a detail that is not `@usableFromInline` on a type that is not frozen.
  `discard self` in an inlinable method of a non-frozen type is the #84975 class.
- Availability diagnostics must match `AvailabilityContext`, including inferred platforms.
  A false "useless availability" warning is still this seat.
- Ship new source-breaking language behavior behind an upcoming-feature flag in `Features.def`, or behind a language mode.
  Do not ship that behavior as a silent Sema change.
- Feature flags in `Features.def` are language configuration.
  The evolution process in process.md applies.
- An ABI-public change is a binary break by default when `docs/LibraryEvolution.rst` does not list it as permitted.
  That document is closed-world.
  Anything that the document does not list is unsafe.
  One forbidden default is a new protocol requirement without a defaulted available implementation.
  Another forbidden default is adding or removing `@frozen` on an existing ABI-public struct or enum.
- Default-argument expressions of ABI-public functions are implicitly `@_alwaysEmitIntoClient`.
  They must not reference entities that are not `public`.
  The ban applies even when those entities are `@usableFromInline` or `@inlinable`.
  A caller must be able to write the default explicitly.

## Plan review

- Does the patch change what already-shipped modules can load?
- Is `#available`, `@available`, or `@_spi` involved?
- Will existing inlinable code in the wild fail to typecheck?

## PR review

- Use `test/Availability/` and the resilience tests that neighbors use.
  For a public ABI, use a neighboring `test/api-digester/` dump.
  Compare that dump.
  Do not use only a typecheck test.
- Test both objc and non-objc when the attribute is ABI-visible.
- Diagnostics for `@_originallyDefinedIn` and for access notes stay softened.
  Follow the existing `softenIfAccessNote` patterns.

## Reject unless

- Do not remove an availability check inside inlinable code without a substitute.
  That substitute must still run on the deployment target.
- Do not enable a feature by default without an LSG path and a release-note path.
- Fragile checks and inlinable checks must use `getFragileFunctionKind()`.
  Do not use a hardcoded attribute list (swift#84975).
- A change to constraint-solver behavior must request source-compatibility CI.

## Evolution

process.md gives summary-acceptance examples.
One example puts a change behind an upcoming-feature flag after source-compatibility problems.
That step is the approved escape hatch.
Use that escape hatch.
Do not ship the break.

## Forum

The ABI contract is `docs/LibraryEvolution.rst` plus process.md.
The contract is not reviewer folklore.
"Looks source-compatible" is not ABI-safe.
Pitches are in this forum category:

https://forums.swift.org/c/evolution/pitches/5

## Abstain

Abstain when the change has no availability change, no inlinable or resilience change, and no feature-flag default-on change.
