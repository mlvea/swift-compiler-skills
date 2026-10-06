# generics

The scope is generic signatures, the requirement machine, and associated-type inference.
The scope includes protocol conformances, existentials, parameter packs, and opaque types.

## Protects

- The requirement machine is the source of reduced generic signatures.
  Ad-hoc `isSubtype` shortcuts that bypass the requirement machine will bit-rot.
- `any P`, `some P`, and a generic `P` are different abstractions.
  SE-0309 and SE-0353 cover existentials.
  SE-0328 covers structural opaque results.
  SE-0346 covers primary associated types.
  Do not "fix" the diagnostic by treating the three abstractions as the same thing.
- An inverse constraint (`~Copyable`, `~Escapable`) is part of the generic signature.
  It is not a SIL-only property.
  A SIL copy or destroy of those types belongs to `ownership`.
- Associated-type inference must not succeed by picking an unrelated default that fails later in SILGen.

## Plan review

- Does the bug vanish with a spelled-out generic signature?
  If it does, the likely layer is inference, not lowering.
- Does the program use an existential member that needs opening (SE-0352), rather than a missing witness table?
- An Embedded crash or a generic crash often belongs in a shared SIL utility (`lib/SILOptimizer/Utils/Generics.cpp`).
  That utility is adjacent.
  It is not an auto-chair.

## PR review

- Put tests in `test/Generics/` or `test/decl/protocol/`.
- Use a signature dump when the reduced signature is the invariant.
  The dumps are `-dump-generic-signature` and the requirement-machine tests.
- Do not add a new `GenericSignature` cache keyed on incomplete requests.

## Reject unless

- A witness failure or a conformance failure is not an IRGen patch when the miss is really SE-0341 or SE-0361.
  Do not patch that failure in IRGen.
- Do parameter-pack substitution for SE-0393, SE-0398, and SE-0399 through pack-expansion machinery.
  Do not flatten a pack to a tuple "for now".
- Do not add a one-off `matches()` branch for a same-type requirement on a pack or an opaque type.

## Evolution

- SE-0142 and SE-0157 cover where clauses and associated types.
- SE-0309 covers existentials for all protocols.
- SE-0335 covers existential `any`.
- SE-0346 covers lightweight primary associated types.
  `P<T>` is not an existential constructor.
- SE-0352 covers implicit opening of existentials.
- SE-0353 covers constrained existentials (`any Collection<Int>`).
- SE-0341 covers opaque parameter declarations.
- SE-0347 covers type inference from default expressions.
- SE-0361 covers extensions on bound generic types.
- SE-0393 covers parameter packs.
  SE-0398 covers variadic types.
  SE-0399 covers pack expansion in tuples.
- SE-0390 and SE-0446 cover `~Copyable` and `~Escapable` as signature constraints.

New sugar for an existential, or a union-like `(T | U)`, is `needs-proposal`.
That shape is commonly rejected.

## Forum

Keep existentials and generics distinct in diagnostics and in the implementation.

https://forums.swift.org/t/improving-the-ui-of-generics/38150

## Abstain

- Abstain for concrete overload ranking when no generic signature is involved.
- Abstain for pure isolation.
- Abstain for ABI layout when the signature does not change.
- Abstain for a SIL `borrow`, `consume`, or `copy_value` of `~Copyable` when the signature does not change.
  That case is `ownership`.
