# generics

Generic signatures, requirement machine, associated type inference,
protocol conformances, existentials, parameter packs, opaque types.

## Protects

- Requirement machine is the source of reduced generic signatures.
  Ad-hoc `isSubtype` shortcuts that bypass it bit-rot.
- `any P` vs `some P` vs generic `P` are different abstractions
  (SE-0309, SE-0328, SE-0346, SE-0353). Do not "fix" diagnostics by
  treating them as the same.
- Inverse constraints (`~Copyable`, `~Escapable`) are part of the
  generic signature, not a SIL-only property.
- Associated-type inference must not succeed by picking an unrelated
  default that fails later in SILGen.

## Plan review

- Does the bug vanish with a spelled-out generic signature? If yes,
  inference is the likely layer, not lowering.
- Is the program using an existential member that needs opening
  (SE-0352) rather than a missing witness table?
- Embedded/generic crashes often belong in shared SIL utilities
  (`lib/SILOptimizer/Utils/Generics.cpp`) — adjacent, not auto-chair.

## PR review

- Tests in `test/Generics/` or `test/decl/protocol/`.
- Signature dumps (`-dump-generic-signature` / requirement-machine
  tests) when the reduced signature is the invariant.
- No new `GenericSignature` cache keyed on incomplete requests.

## Reject unless

- Witness/conformance failures that are really missing SE-0341/SE-0361
  rules are not patched in IRGen.
- Parameter-pack substitution (SE-0393/0398/0399) is done through pack
  expansion machinery, not by flattening to a tuple "for now".
- Same-type requirements involving packs/opaques do not get a
  one-off `matches()` branch.

## Evolution

- SE-0142 / 0157 (where clauses, associated types)
- SE-0309 existentials for all protocols
- SE-0335 existential any
- SE-0346/0353 implicit opening
- SE-0347 opaque parameter syntax
- SE-0361 implicit lifetime
- SE-0393/0398/0399 packs
- SE-0390 / SE-0446 `~Copyable` / `~Escapable` as signature constraints

New sugar for existentials or union-like `(T | U)` → `needs-proposal`
(commonly rejected).

## Forum

https://forums.swift.org/t/improving-the-ui-of-generics/38150 —
existentials vs generics must stay distinct in diagnostics and
implementation.

## Abstain

Concrete overload ranking with no generic signature involved;
pure isolation; ABI layout without signature change.
