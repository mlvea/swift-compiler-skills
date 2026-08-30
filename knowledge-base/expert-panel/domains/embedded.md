# embedded (conditional)

Embedded Swift (restricted runtime, specialized witnesses,
no-allocation paths) and Wasm/WASI hooks. Sit only on a primary file
hit (`test/embedded/`, `lib/Sema/TypeCheckEmbedded*`, wasm/wasi
product files).

## Protects

- Embedded has no full runtime by default. Fixes that call
  metadata/runtime entry points must be guarded or lowered away.
- Existential/generic crashes on Embedded often belong in shared SIL
  utilities (`Generics.cpp`) with `test/embedded/` coverage (#91566).
- Wasm lacks ObjC runtime; typed-throws async lowering cannot assume
  it (#89320 class).
- `-no-allocations` / no-allocation Embedded must not grow a path
  that requires the full runtime allocator.

## Plan review

- Repro with `-enable-experimental-feature Embedded` (or the current
  equivalent flag in-tree).
- Runtime/metadata call on an Embedded path, or a hole in a shared
  SIL utility (`Generics.cpp`)? Shared utility stays general, with
  `test/embedded/` coverage.

## PR review

- `test/embedded/` (or the wasm/wasi product test already in tree).
- Do not encode `embedded` as a special case at a SIL verifier
  assert; restore the producing pass's general check.

## Reject unless

- Do not encode `embedded` as a special case at a SIL verifier assert;
  restore the producing pass's general check (#90931 class).
- Do not mix Embedded ABI (`$e` mangling, unstable) with full Swift
  metadata on the same path.
- Do not specialize `witness_method` when the requirement is ABI-more-
  generic than the protocol (swift#91581 / issue #91566). Those calls
  need unspecialized generics, which Embedded forbids.

## Evolution

Embedded's design is the Embedded Swift vision, not SE-0433 (that SE
is `Mutex`). Expanding or shrinking the Embedded subset is a language-
mode change for that compilation model. Metadata-using runtime calls
on an Embedded path are a compiler bug, not a subset expansion.

## Forum

Embedded has no full runtime by default. That is the compilation
model, not a missing convenience. Wasm has no ObjC runtime — typed
throws / async lowering must not assume one.

## Abstain

No primary Embedded/Wasm files. An Embedded feature flag in the plan
text is not enough to sit; seating requires a primary glob hit.
