# distributed (conditional)

The scope is distributed actors and synthesis of distributed protocols.
Sit only on a primary Distributed* hit.

## Protects

- A distributed method has a serialization boundary.
  A non-Sendable argument is not "just isolation".
  The argument is on-the-wire.
- Synthesis of distributed protocol witnesses must stay on the CodeSynthesisDistributed path.
  Do not do that synthesis as ad-hoc SILGen.
- Runtime checks in the `recordGenericSubstitution` style are load-bearing.

## Plan review

- Is the bug the serialization boundary for on-the-wire arguments, or is it actor isolation?
  Send an isolation-only bug to `concurrency`.
  Sit this seat only when `distributed` or Distributed* is in the change.
- Put synthesis in `CodeSynthesisDistributed*`.
  Do not put synthesis in SILGen.

## PR review

- Put tests in `test/Distributed/` and `test/decl/protocol/special/DistributedActor.swift`.
- Isolation of a distributed actor still follows the `concurrency` rules.
  This seat comments only on the distributed part.

## Reject unless

- A remote-call thunk must not bypass isolation.
  It must not bypass `Sendable` requirements or `Codable` requirements.
  The `concurrency` seat is adjacent for the isolation half.
- Synthesis in `CodeSynthesisDistributed*` must agree with the stdlib `DistributedActor` protocol.
  Do not invent a witness in SILGen.
- Mangle a distributed thunk or getter as the distributed protocol.
  Use the storage name for `_distributed_get`.
  Do not mangle that symbol as an ordinary accessor (swift#72416).

## Evolution

Distributed actors shipped in SE-0336 and in the follow-ons.
A new transport-visible protocol requirement needs a pitch.

## Forum

On-the-wire is not "just Sendable".
A distributed method has a serialization boundary.
That boundary remains even when local isolation would allow the value.

## Abstain

Abstain for a plain actor or for Sendable when the change has no `distributed` keyword and no Distributed* file.
