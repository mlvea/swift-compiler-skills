# ownership

OSSA, borrow scopes, consuming/borrowing parameters, move-only /
noncopyable, address lowering, SIL ownership verifier.

## Protects

- The ownership verifier is the spec. Never weaken it to land a pass.
- `load` and `load_borrow` are different instructions; a safety check
  on one does not cover the other (merged #90945 vs rejected #90931).
- Move-only values (`~Copyable`, SE-0390) cannot be copied, even by an
  optimizer that "knows" the copy is dead.
- Borrow scopes must dominate all uses and end exactly once on each
  path.

## Plan review

- Is the assert an ownership verifier error? Then find the producing
  pass (SILGen vs mandatory vs opt), not the verifier line.
- Does the plan insert `copy_value` to "make it work"? That is usually
  a lifetime bug, not a fix.
- Address lowering / opaque values: is the representation change
  local to mandatory SIL?

## PR review

- `.sil` tests that run the verifier (`// REQUIRED: sil-ownership` or
  the directory's existing convention).
- Neighboring move-only tests in `test/SILOptimizer/moveonly*` and
  `test/Sema/moveonly*`.
- No `#ifdef` or feature-flag around verifier checks for convenience.

## Reject unless

- Symptom-specific guards at the assert (`#available`, weakly
  imported, embedded) when a sibling instruction already has the
  general check — `block` (pattern of #90931).
- `copyable` wrappers to smuggle a move-only C++ type without a
  `~Copyable` suppression story (`clang-importer` adjacent).

## Evolution

- SE-0377 `consume`/`copy`
- SE-0390 noncopyable structs/enums
- SE-0429/0432 borrowing/consuming parameter ownership
- SE-0446 `~Escapable` / lifetime dependence (do not implement
  lifetime dependence by raw pointer in stdlib)

Ownership manifesto / OSSA:
https://forums.swift.org/t/sil-ownership-model-proposal-refreshed/16872
https://forums.swift.org/t/proposal-sil-ownership-model-verifier/4665

## Abstain

No borrow/consume/move-only/OSSA/verifier change. Pure Sema
diagnostics with no SIL ownership.
