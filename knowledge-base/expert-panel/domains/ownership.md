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
- OSSA (`docs/SIL/Ownership.md`): every value (except on a dead-end
  block post-dominated by `unreachable`) has exactly one lifetime-ending
  use on each path to `return`/`throw`; those uses jointly post-dominate
  non-lifetime-ending uses. Weakening that to land a pass is a
  leak/UAF class.
- SE-0176 exclusivity: two accesses to the same variable must not
  overlap unless both are reads. Overlapping `inout` is accepts-invalid.
- Lexical lifetimes (`docs/SIL/Ownership.md`): destroys of
  `begin_borrow [lexical]`, `move_value [lexical]`, lexical function
  arguments, and `alloc_stack [lexical]` must not move across deinit
  barriers. Check `ValueBase::isLexical` before shrinking a lifetime.
  Inlining inserts lexical borrow/move for `@guaranteed`/`@owned`
  arguments that are not already lexical.
- Interior-pointer instructions take only `@guaranteed` operands;
  transitive address uses are liveness of that operand. Unknown
  instructions must fail the verifier (no silent "safe" default).
  `pointer_to_address` is an explicit escape; do not extend that
  pointer's lifetime.

## Plan review

- Is the assert an ownership verifier error? Then find the producing
  pass (SILGen vs mandatory vs opt), not the verifier line.
- Does the plan insert `copy_value` to "make it work"? That is usually
  a lifetime bug, not a fix. Does it move a lexical destroy across a
  deinit barrier, or treat an interior pointer as an ordinary address?
- Address lowering / opaque values: is the representation change
  local to mandatory SIL?

## PR review

- Ownership-verifier tests live in `test/SIL/OwnershipVerifier/`
  (`-sil-ownership-verifier-enable-testing`), plus move-only neighbors
  in `test/SILOptimizer/moveonly*` and `test/Sema/moveonly*`.
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

## Forum

OSSA is the spec, not an optimizer convenience. Weakening the verifier
or skipping lexical/deinit-barrier rules to land a pass is the usual
hurried-review miss:
https://forums.swift.org/t/sil-ownership-model-proposal-refreshed/16872
https://forums.swift.org/t/proposal-sil-ownership-model-verifier/4665

## Abstain

No borrow/consume/move-only/OSSA/verifier/exclusivity change. Pure
Sema diagnostics with no SIL ownership. Inverse constraints that only
change a generic signature (`test/Generics/inverse*`) chair as
`generics`; this seat sits when SIL lowering of those types is in the
diff.
