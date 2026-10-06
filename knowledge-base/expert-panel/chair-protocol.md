# Chair synthesis protocol

The chair is the primary domain from `seat.py`.
The chair is not a generalist.
The chair issues the only verdict that the fix loop obeys.

## Inputs

The chair uses these inputs.

- Read the seating JSON. It has `chair`, `seated`, and `reasons`.
- Read every sitting ballot. The schema is in `ballot.md`.
- Read this file, `evolution-gate.md`, and the chair domain brief.
- Open the plan or the diff again only when a ballot is unusable or the ballot contradicts the artifact.

## Rules

The reviewer is one read-only subagent.
The reviewer has the plan or the diff.
The reviewer has the seated briefs.
The reviewer has the official docs that those briefs name.
The reviewer does not have the author's reasoning.

Only the reviewer writes a rebuttal.
Only the reviewer decides that rebuttal.

The same rules apply when the opt-in panel writes separate ballots.
Do not sum verdicts.
Do not average verdicts.
Nothing here shows that several agents beat one reviewer who reads the same briefs.

`request-changes` means this.
Apply the named changes.
Review that artifact again.
A rebuttal does not clear `request-changes`.
A rebuttal answers a `block` from another brief.
A `block` from the chair brief is final.

| Source | Rule |
| --- | --- |
| Chair brief, in scope | Its `block` is final. |
| Other seated brief, in scope | A `block` needs a written rebuttal. Name the invariant. Say why this change does not violate it. |
| Abstain | Ignore the ballot. |
| Missing ballot or failed ballot | This is not an approval. If the chair ballot is missing, write it before the verdict. |

An adjacent `request-changes` is part of the verdict.
Apply the named changes.
Review the artifact again.
An adjacent `approve` does not clear a chair `request-changes`.

## Evolution

Run `evolution-gate.md` on the change.
Do not run it on the issue title.

- If any in-scope ballot has `evolution: needs-proposal`, put that class in the verdict.
- If `evolution-gate.md` calls the change a language design change, use `block`.
  If `evolution-gate.md` calls the change a stdlib design change, use `block`.
  Write that the change needs the Language Steering Group.
  Do not use `block` for this reason when an experimental flag hides the behavior.
  Do not use `block` for this reason when the behavior is unreleased.
- A diagnostic-only change gets `none`.
  A crash fix gets `none`.
  A miscompile fix gets `none`.
  An accepts-invalid fix gets `none` when it restores a rule that is already accepted.

## Verdict rules

1. Collect `blockers` from each in-scope ballot.
   Put a chair-domain blocker in `must_address`.
   Put an adjacent blocker in `must_address` unless you rebut it.
2. Put `concerns` in `may_defer`.
   Promote a concern when it is cheap and local.
   A missing test is cheap and local.
   Diagnostic wording is cheap and local.
3. Use `approve` only when no unrebutted item remains in `must_address`.
   The result from `evolution-gate.md` must be `none` or already satisfied.
4. Use `request-changes` when the layer is right and the patch is incomplete.
   Tests, generality, or diagnostic placement can be incomplete.
5. Use `block` when the layer is wrong.
   Use `block` when an invariant is violated.
   Use `block` when the change needs evolution.

Write one paragraph for each adjacent blocker.
`Out of scope` is not a rebuttal.
Use that phrase only when the adjacent ballot should have abstained.

## Specialist bar

Briefs record documented invariants for a closed world.
Apply each brief fail-closed.

- A violation of `Protects` is `block`.
  A violation of `Reject unless` is `block`.
  Use `request-changes` only when the layer is right and the patch is incomplete.
  The gap can be a missing test.
  The gap can be diagnostic placement.
- When an adjacent `block` names an official doc, cite the exception in that same doc.
  `Equivalent in practice` is not a rebuttal.
  `Existing tests pass` is not a rebuttal.
- Do not skip a closed-world default because the patch is small.
  Do not skip a closed-world default because the issue is a crash.

## Output

Use the chair schema in `ballot.md`.
Name the domain ids in the rationale.
Quote file paths and SE numbers.
