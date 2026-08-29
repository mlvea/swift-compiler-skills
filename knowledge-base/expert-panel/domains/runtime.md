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

## Abstain

Frontend-only diagnostics or SIL that never reaches a runtime symbol.
