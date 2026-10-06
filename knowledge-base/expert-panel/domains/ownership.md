# ownership

The scope is OSSA, borrow scopes, and consuming or borrowing parameters.
The scope includes move-only and noncopyable types, address lowering, and the SIL ownership verifier.

## Protects

- The ownership verifier is the spec.
  Do not weaken the verifier to land a pass.
- `load` and `load_borrow` are different instructions.
  A safety check on one instruction does not cover the other.
  The contrast is merged #90945 versus rejected #90931.
- A move-only value (`~Copyable`, SE-0390) cannot be copied.
  An optimizer cannot copy that value, even when the optimizer "knows" that the copy is dead.
- A borrow scope must dominate all uses.
  A borrow scope must end exactly once on each path.
- OSSA is specified in `docs/SIL/Ownership.md`.
  Every value has exactly one lifetime-ending use on each path to `return` or `throw`.
  The exception is a value on a dead-end block that `unreachable` post-dominates.
  Those lifetime-ending uses jointly post-dominate non-lifetime-ending uses.
  If you weaken that rule to land a pass, the class is a leak or a UAF.
- Under SE-0176, two accesses to the same variable must not overlap unless both accesses are reads.
  Overlapping `inout` is accepts-invalid.
- Lexical lifetimes are specified in `docs/SIL/Ownership.md`.
  The relevant destroys are for `begin_borrow [lexical]` and `move_value [lexical]`.
  They are also for lexical function arguments and `alloc_stack [lexical]`.
  Do not move those destroys across a deinit barrier.
  Check `ValueBase::isLexical` before you shrink a lifetime.
  Inlining inserts a lexical borrow or a lexical move for a `@guaranteed` or `@owned` argument that is not already lexical.
- Interior-pointer instructions take only `@guaranteed` operands.
  Transitive address uses are liveness of that operand.
  An unknown instruction must fail the verifier.
  Do not use a silent "safe" default.
  `pointer_to_address` is an explicit escape.
  Do not extend the lifetime of that pointer.

## Plan review

- Is the assert an ownership-verifier error?
  If it is, find the producing pass.
  The producing pass is SILGen, a mandatory pass, or an opt pass.
  The verifier line is not the bug.
- Does the plan insert `copy_value` to "make it work"?
  That change is usually a lifetime bug, not a fix.
  Does the plan move a lexical destroy across a deinit barrier?
  Does the plan treat an interior pointer as an ordinary address?
- For address lowering or opaque values, is the representation change local to mandatory SIL?

## PR review

- Ownership-verifier tests are in `test/SIL/OwnershipVerifier/` (`-sil-ownership-verifier-enable-testing`).
  Move-only neighbors are in `test/SILOptimizer/moveonly*` and `test/Sema/moveonly*`.
- Do not put `#ifdef` or a feature-flag around a verifier check for convenience.

## Reject unless

- A symptom-specific guard at the assert is a `block` when a sibling instruction already has the general check.
  The guard forms are `#available`, weakly imported, and embedded.
  This is the pattern of #90931.
- Do not use a `copyable` wrapper to smuggle a move-only C++ type without a `~Copyable` suppression story.
  The `clang-importer` seat is adjacent.

## Evolution

- SE-0366: `consume` ends the lifetime of a binding.
- SE-0377 covers `borrowing` parameters, `consuming` parameters, and the explicit `copy` operator.
- SE-0390 covers noncopyable structs and enums.
- SE-0429 covers partial consumption of noncopyable values.
- SE-0432 covers borrowing and consuming pattern matching.
- SE-0446 covers `~Escapable` and lifetime dependence.
  Do not implement lifetime dependence with a raw pointer in the stdlib.

## Forum

OSSA is the spec.
OSSA is not an optimizer convenience.
The usual hurried-review miss weakens the verifier to land a pass.
The same miss skips lexical rules and deinit-barrier rules.

https://forums.swift.org/t/sil-ownership-model-proposal-refreshed/16872

https://forums.swift.org/t/proposal-sil-ownership-model-verifier/4665

## Abstain

Abstain when the change has no borrow, consume, move-only, OSSA, verifier, or exclusivity change.
Abstain for pure Sema diagnostics with no SIL ownership.
Inverse constraints that only change a generic signature chair as `generics`.
Those tests match `test/Generics/inverse*`.
Sit this seat when the diff has SIL lowering of those types.
