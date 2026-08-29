# distributed (conditional)

Distributed actors and distributed protocol synthesis. Sit only on a
primary Distributed* hit.

## Protects

- Distributed methods have a serialization boundary. Non-Sendable
  arguments are not "just isolation" — they are on-the-wire.
- Synthesis of distributed protocol witnesses must stay in the
  CodeSynthesisDistributed path, not ad-hoc SILGen.
- Runtime recordGenericSubstitution-style checks are load-bearing.

## Plan / PR

- Tests in `test/Distributed/` and
  `test/decl/protocol/special/DistributedActor.swift`.
- Isolation of distributed actors still obeys `concurrency` rules;
  this seat comments on the distributed part only.

## Evolution

Distributed actors shipped via SE-0336 and follow-ons. New
transport-visible protocol requirements need a pitch.

## Abstain

Plain actors / Sendable with no `distributed` keyword or Distributed*
files.
