# irgen-abi

SIL → LLVM IR, type layout, witness tables, calling conventions,
mangling, ABI stability.

## Protects

- Resilient ABI: adding a stored property, changing enum layout, or
  changing a calling convention for a non-`@frozen` / non-`@_alwaysEmitIntoClient`
  type is a `block` without a library-evolution story.
- Mangling is ABI. Silent remangling of existing symbols breaks
  archives.
- Witness tables must match the protocol descriptor the runtime will
  see. Generic specialization cannot invent extra witnesses.
- IRGen assertions often fire on SIL that is already illegal; check
  that the producing SIL pass is not the real bug (`pipeline-map`
  heuristic 9).

## Plan review

- Does `-emit-ir` fail while `-emit-sil` is well-formed? Then this
  seat chairs. If SIL is already wrong, adjacent only.
- Layout change: is the type `@frozen`? `@usableFromInline`?
- Undefined symbols at link: SILDeclRef identity vs actual missing
  emission.

## PR review

- `test/IRGen/` FileCheck of the IR, or `test/abi/` / api-digester
  when public ABI is involved.
- Cross-platform: pointer-size and objc-interop vs non-objc.
- No hard-coded LLVM IR that exists only on apple-silicon.

## Reject unless

- "Fix by emitting a thunk for this one stdlib type" has a general
  convention rule.
- Changing `swiftcc` / context-pointer passing is not buried in a
  crash fix.

## Evolution

SE-0260 library evolution: resilient by default; `@frozen` is a
forever layout promise. ABI / `docs/ABI/`. C-compatible `@objc`
layout is also `clang-importer`.

## Abstain

No IR, layout, mangling, or witness-table change. Runtime C++ that
does not change IRGen contracts → `runtime`.
