# embedded (conditional)

Embedded Swift (restricted runtime, specialized witnesses) and
Wasm/WASI hooks. Sit on `test/embedded/` or wasm product files, or
when the plan is explicitly Embedded.

## Protects

- Embedded has no full runtime by default. Fixes that call
  metadata/runtime entry points must be guarded or lowered away.
- Existential/generic crashes on Embedded often belong in shared SIL
  utilities (`Generics.cpp`) with `test/embedded/` coverage (#91566).
- Wasm lacks ObjC runtime; typed-throws async lowering cannot assume
  it (#89320 class).

## Plan / PR

- Repro with `-enable-experimental-feature Embedded` (or the current
  equivalent flag in-tree).
- Do not encode `embedded` as a special case at a SIL verifier
  assert; fix the producing pass's general check.

## Evolution

Embedded's design is the Embedded Swift vision, not SE-0433 (that SE
is `Mutex`). Expanding or shrinking the Embedded subset is a language-
mode change for that compilation model. Metadata-using runtime calls
on an Embedded path are a compiler bug, not a subset expansion.

## Abstain

No Embedded/Wasm files and no Embedded feature flag in the plan.
