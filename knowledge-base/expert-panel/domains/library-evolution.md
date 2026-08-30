# library-evolution

Availability, resilience, `@frozen` / `@inlinable` / `@usableFromInline`,
upcoming-feature flags, source compatibility.

## Protects

- `@inlinable` bodies cannot reference non-`@usableFromInline`
  details of a non-frozen type (`discard self` in inlinable methods
  of non-frozen types is the #84975 class).
- Availability diagnostics must match `AvailabilityContext`, including
  inferred platforms. False "useless availability" warnings are still
  this seat.
- New language behavior that is source-breaking ships behind an
  upcoming-feature flag (`Features.def`) or a language mode, not as a
  silent Sema change.
- Feature flags in `Features.def` are language configuration →
  evolution process applies (process.md).
- ABI-public change not listed as permitted in
  `docs/LibraryEvolution.rst` is a binary break by default. That
  document is closed-world: anything not listed is unsafe. Named
  defaults: new protocol requirement without a defaulted available
  implementation; adding or removing `@frozen` on an existing
  ABI-public struct or enum is forbidden.
- Default-argument expressions of ABI-public functions are implicitly
  `@_alwaysEmitIntoClient`. They must not reference non-`public`
  entities even if those entities are `@usableFromInline` /
  `@inlinable` — a caller must be able to write the default explicitly.

## Plan review

- Does the patch change what already-shipped modules can load?
- Is `#available` / `@available` / `@_spi` involved?
- Will existing inlinable code in the wild fail to typecheck?

## PR review

- `test/Availability/` and resilience tests as used by neighbors.
  Public ABI: neighboring `test/api-digester/` dump/compare, not only
  typecheck.
- Both objc and non-objc where the attribute is ABI-visible.
- Softened diagnostics for `@_originallyDefinedIn` / access notes
  follow existing `softenIfAccessNote` patterns.

## Reject unless

- "Fix" that removes an availability check inside inlinable code
  without a substitute still executable on the deployment target.
- Enabling a feature by default without LSG / release-note path.
- Fragile/inlinable checks use `getFragileFunctionKind()`, not a
  hardcoded attribute list (swift#84975).
- Constraint-solver behavior changes request source-compatibility CI.

## Evolution

process.md summary-acceptance examples include gating a change behind
an upcoming-feature flag after source-compatibility problems. That is
the approved escape hatch — use it rather than shipping the break.

## Forum

The ABI contract is `docs/LibraryEvolution.rst` plus process.md, not
reviewer folklore. "Looks source-compatible" is not ABI-safe. Pitches:
https://forums.swift.org/c/evolution/pitches/5

## Abstain

No availability, inlinable/resilience, or feature-flag default-on
change.
