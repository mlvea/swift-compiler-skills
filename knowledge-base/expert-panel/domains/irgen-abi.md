# irgen-abi

The scope is SIL to LLVM IR, type layout, and witness tables.
The scope includes calling conventions, mangling, and ABI stability.

## Protects

- Adding a stored property to a type that is not `@frozen` and not `@_alwaysEmitIntoClient` is a `block` without a library-evolution story.
  A change to enum layout for that type is the same `block`.
  A change to a calling convention for that type is the same `block`.
- Mangling is ABI.
  Silent remangling of existing symbols breaks archives.
- A witness table must match the protocol descriptor that the runtime will see.
  Generic specialization cannot invent extra witnesses.
- IRGen assertions often trigger on SIL that is already illegal.
  Check that the producing SIL pass is not the real bug.
  The reference is `pipeline-map` heuristic 9.
- Metadata pointer identity is in `docs/ABI/TypeMetadata.rst`.
  Request **complete** metadata for an ordinary generic call.
  Request **complete** metadata for a metatype value and for `Self`.
  Request **complete** metadata for an opaque existential.
  Request abstract metadata only when you construct other metadata.
- Do not present abstract-only metadata to an ordinary generic call, a metatype or `Self` value, or an opaque existential.
  Do not present layout-complete metadata to those same uses.
- Closed-world ABI follows `docs/LibraryEvolution.rst`.
  A layout change is a break when that document does not permit it.
  A mangling change is a break when that document does not permit it.
  A witness change is a break when that document does not permit it.
  The `library-evolution` seat is adjacent.
- Older runtimes must not discover noncopyable type metadata as a copyable type.
  The safe forms are a separate section and `RuntimeResolvableTypes2` (swift#64215).
- Do not build an explosion schema only to count registers for a very large type.
  That schema causes a compile-time blowup.
  Mark `IsVeryLargeType` (swift#86148).
  Keep the type indirect.

## Plan review

- Does `-emit-ir` fail while `-emit-sil` is well-formed?
  Then this seat chairs.
  If the SIL is already wrong, this seat is adjacent only.
- For a layout change, is the type `@frozen`?
  Is the type `@usableFromInline`?
- For undefined symbols at link, is the cause `SILDeclRef` identity or actual missing emission?

## PR review

- Use FileCheck on the IR in `test/IRGen/`.
  For a public ABI, use `test/abi/` or the api-digester.
- Check cross-platform behavior.
  Cover pointer-size.
  Cover objc-interop versus non-objc.
- Do not hard-code LLVM IR that exists only on apple-silicon.

## Reject unless

- The fix "emit a thunk for this one stdlib type" must have a general convention rule.
- Do not hide a change to `swiftcc` or to context-pointer passing inside a crash fix.

## Evolution

SE-0260 library evolution is resilient by default.
`@frozen` is a forever layout promise.
ABI detail is in `docs/ABI/`.
C-compatible `@objc` layout is also `clang-importer`.

## Forum

Mangling, layout, and witness-table shape are shipping contracts.
An "internal refactor" that remangles a resilient type is an ABI incident.
An "internal refactor" that reorders a resilient type is an ABI incident.
The references are SE-0260 and `docs/LibraryEvolution.rst`.

## Abstain

Abstain when there is no IR change, no layout change, no mangling change, and no witness-table change.
Send runtime C++ that does not change IRGen contracts to `runtime`.
