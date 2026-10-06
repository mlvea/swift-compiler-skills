# runtime

The scope is the Swift runtime.
The scope includes casts, refcounting, metadata, reflection, threading, backtrace, and bridging entry points.

## Protects

- A dynamic cast must not invent Swift protocol conformances that the static type system would refuse.
  The name of this bug class is bridging-as-proof, case 85111.
- Refcount operations and retain-release operations are not allowed to be "best effort" on a path that user code can hit.
- Metadata for a generic type, a tuple type, or an existential type must match the IRGen layout.
  If the two layouts diverge, the split is an ABI incident.
- Overflow in size math or layout math must trap.
  The overflow must not wrap.
- Type-metadata pointers are identity.
  The spec is `docs/ABI/TypeMetadata.rst`.
  Two metadata pointers compare equal if and only if the types are equivalent.
  Metadata never backtracks state.
  Complete metadata stays complete.
- Ordinary generic arguments need **complete** metadata, except metadata access functions and witness access functions.
  Metatype values, including `Self`, need **complete** metadata.
  Opaque existentials need **complete** metadata.
  Do not use abstract metadata where those rules require **complete** metadata.
  Do not use layout-complete metadata for that same case.
- When reflection files, threading files, or backtrace files change, those entry points are this seat.
  They must stay safe for concurrent first use.

## Plan review

- Does the reproducer compile and then fail when it runs?
  If it does, this seat is in play.
- Is the bug a bad runtime function, or is it IRGen that calls the wrong entry point?
- A tighter cast that starts trapping on previously-running code needs `library-evolution`.
  It can also need evolution.

## PR review

- Use `test/Runtime/` or `test/Casting/`.
  If the entry point is user-facing, use a stdlib test.
- Do not add a process-lifetime global cache that has no invalidation.
- ObjC-interop tests run only on a target that has ObjC.
  A non-ObjC platform must still build.

## Reject unless

- A naive widening of `swift_dynamicCast` is a `block` in the 85111 class.
  The bad widening makes `as?` succeed for a bridged type.
  That type is not really `Equatable` or `Error` in Swift.
  `any Error: Error` is the special self-conformance.
  Do not generalize "existential conforms to P".
- Do not change retain or release of a foreign-reference C++ type without `clang-importer` agreement on the FRT contract.

## Evolution

A runtime implementation of an accepted language rule is not evolution.
A new runtime-visible protocol is evolution.
New cast semantics are evolution.

## Forum

A cast that succeeds "for convenience" is not better bridging.
Bridging must not invent conformances that the type system would refuse (85111 class).
`any Error: Error` is the documented self-conformance exception.
It is not a pattern to copy.

## Abstain

Abstain for frontend-only diagnostics.
Abstain for SIL that never reaches a runtime symbol.
