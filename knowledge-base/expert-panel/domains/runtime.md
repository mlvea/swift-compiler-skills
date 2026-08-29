# runtime

Swift runtime: casts, refcounting, metadata, reflection, threading,
backtrace, bridging entrypoints.

## Protects

- Dynamic cast must not invent Swift protocol conformances that the
  static type system would refuse (bridging-as-proof, case 85111).
- Refcount / retain-release operations are not allowed to be "best
  effort" on a path that user code can hit.
- Metadata for generic / tuple / existential types must match IRGen
  layout. Diverging the two is an ABI incident.
- Overflow in size/layout math traps; it must not wrap.
- Type-metadata pointers are identity: two metadata pointers compare
  equal iff the types are equivalent (`docs/ABI/TypeMetadata.rst`).
  Metadata never backtracks state; complete remains complete. Ordinary
  generic arguments (except metadata/witness access functions),
  metatype values including `Self`, and opaque existentials require
  **complete** metadata — not abstract or layout-complete.
- Reflection, threading, and backtrace entry points are this seat
  when those files change; they must stay safe for concurrent first
  use.

## Plan review

- Reproducer compiles and fails when *run*? This seat is in play.
- Is the bug a bad runtime function, or IRGen calling the wrong
  entrypoint?
- Source-compatibility: a tighter cast that starts trapping on
  previously-running code needs `library-evolution` and possibly
  evolution.

## PR review

- `test/Runtime/` or `test/Casting/` (or stdlib tests if the entry
  point is user-facing).
- No process-lifetime global caches without invalidation.
- ObjC-interop tests gated; non-ObjC platforms still build.

## Reject unless

- Naive `swift_dynamicCast` widening to make `as?` succeed for a
  bridged type that is not really `Equatable`/`Error` in Swift —
  `block` (85111 class). `any Error: Error` is the special
  self-conformance; do not generalize “existential conforms to P”.
- Changing retain/release of foreign-reference C++ types without
  `clang-importer` agreement on the FRT contract.

## Evolution

Runtime implementation of accepted language rules is not evolution.
New runtime-visible protocols or cast semantics are.

## Forum

A cast that succeeds "for convenience" is not better bridging.
Bridging must not invent conformances the type system would refuse
(85111 class). `any Error: Error` is the documented self-conformance
exception, not a pattern to copy.

## Abstain

Frontend-only diagnostics or SIL that never reaches a runtime symbol.
