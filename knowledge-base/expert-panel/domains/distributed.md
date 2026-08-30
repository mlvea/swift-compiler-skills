# distributed (conditional)

Distributed actors and distributed protocol synthesis. Sit only on a
primary Distributed* hit.

## Protects

- Distributed methods have a serialization boundary. Non-Sendable
  arguments are not "just isolation" — they are on-the-wire.
- Synthesis of distributed protocol witnesses must stay in the
  CodeSynthesisDistributed path, not ad-hoc SILGen.
- Runtime recordGenericSubstitution-style checks are load-bearing.

## Plan review

- Is the bug the serialization boundary (on-the-wire arguments) or
  actor isolation? Isolation-only → `concurrency`; this seat only if
  `distributed` / Distributed* is in play.
- Synthesis belongs in `CodeSynthesisDistributed*`, not SILGen.

## PR review

- Tests in `test/Distributed/` and
  `test/decl/protocol/special/DistributedActor.swift`.
- Isolation of distributed actors still obeys `concurrency` rules;
  this seat comments on the distributed part only.

## Reject unless

- Remote-call thunks do not bypass isolation or `Sendable`/`Codable`
  requirements (`concurrency` adjacent for the isolation half).
- Synthesis (`CodeSynthesisDistributed*`) agrees with the stdlib
  `DistributedActor` protocol; do not invent witnesses in SILGen.
- Distributed thunks/getters mangle as the distributed protocol
  (storage name for `_distributed_get`), not as ordinary accessors
  (swift#72416).

## Evolution

Distributed actors shipped via SE-0336 and follow-ons. New
transport-visible protocol requirements need a pitch.

## Forum

On-the-wire is not "just Sendable". Distributed methods have a
serialization boundary even when local isolation would allow the
value.

## Abstain

Plain actors / Sendable with no `distributed` keyword or Distributed*
files.
