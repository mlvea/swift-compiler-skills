# embedded (conditional)

The scope is Embedded Swift.
Embedded Swift has a restricted runtime, specialized witnesses, and no-allocation paths.
The scope includes Wasm hooks and WASI hooks.

Sit on a primary file hit in `test/embedded/`, `lib/Sema/TypeCheckEmbedded*`, or wasm/wasi product files.
Also sit when the plan text or the title text hits the embedded keywords.
Do not sit this brief for a SILOptimizer path by itself.
Do not sit this brief for an IRGen path by itself.
Embedded bugs often land in the SILOptimizer tree or the IRGen tree (#91581).

## Protects

- Embedded has no full runtime by default.
  Guard a fix that calls a metadata entry point or a runtime entry point.
  If you do not guard it, lower that call away.
- An existential crash or a generic crash on Embedded often belongs in a shared SIL utility (`Generics.cpp`).
  Cover that fix with `test/embedded/` (#91566).
- Wasm has no ObjC runtime.
  Typed-throws async lowering cannot assume an ObjC runtime (#89320 class).
- Do not grow a `-no-allocations` path that requires the full runtime allocator.
  The same ban covers other no-allocation Embedded paths.

## Plan review

- Reproduce the bug with `-enable-experimental-feature Embedded`, or with the current equivalent flag in-tree.
- Is there a runtime call or a metadata call on an Embedded path?
  Or is the bug a hole in a shared SIL utility (`Generics.cpp`)?
  A shared utility stays general.
  Cover that utility with `test/embedded/`.

## PR review

- Use `test/embedded/`, or the wasm or wasi product test that is already in the tree.
- Do not encode `embedded` as a special case at a SIL verifier assert.
  Restore the general check in the producing pass.

## Reject unless

- Do not encode `embedded` as a special case at a SIL verifier assert.
  Restore the general check in the producing pass (#90931 class).
- Do not mix the Embedded ABI with full Swift metadata on the same path.
  The Embedded ABI uses `$e` mangling and is unstable.
- Do not specialize `witness_method` when the requirement is ABI-more-generic than the protocol (swift#91581 and issue #91566).
  Those calls need unspecialized generics.
  Embedded forbids unspecialized generics.

## Evolution

The design of Embedded Swift is the Embedded Swift vision.
That design is not SE-0433.
SE-0433 is `Mutex`.

Expanding or shrinking the Embedded subset is a language-mode change for that compilation model.
A metadata-using runtime call on an Embedded path is a compiler bug.
It is not a subset expansion.

## Forum

Embedded has no full runtime by default.
That limit is the compilation model.
It is not a missing convenience.

Wasm has no ObjC runtime.
Typed throws and async lowering must not assume an ObjC runtime.

## Abstain

- Abstain under both of the next conditions.
  There is no primary Embedded file and no primary Wasm file.
  The plan and the title do not name Embedded.
- A SILOptimizer diff or an IRGen diff with no Embedded text is not this seat.
