# Chair Synthesis Protocol

The chair is the primary domain from `seat.py`, not a generalist. It
issues the only verdict the fix-loop obeys.

## Inputs

- Seating JSON (`chair`, `seated`, `reasons`)
- Every sitting ballot (schema in `ballot.md`)
- This file, `evolution-gate.md`, and the chair's own domain brief
- The plan or diff (re-open only if a ballot is unusable or contradicts
  the artifact)

## Weighting

| Source | Weight | Override |
| --- | --- | --- |
| Chair ballot, `in_scope: in` | 1.0 | Its `block` is final |
| Other seated, `in_scope: in` | 0.5 | `block` requires a written rebuttal that names the invariant and why this change does not violate it |
| `in_scope: abstain` | 0 | Ignore |
| Missing/failed ballot | 0 | Not an approval. If the failed seat was the chair, re-run the chair ballot before synthesizing |

Adjacent `request-changes` does not outvote a chair `approve` unless the
chair cannot rebut the named invariant. Adjacent `approve` cannot wash
out a chair `request-changes`.

## Evolution

Run `evolution-gate.md` on the *change*, not on the issue title.

- Any in-scope ballot with `evolution: needs-proposal` forces a gate
  classification in the verdict.
- If the gate says language/stdlib design change → `block` with "needs
  Language Steering Group / evolution", unless the behavior is
  experimental-flagged or unreleased.
- Diagnostic-only, crash, miscompile, and accepts-invalid restorations of
  an already-accepted rule → `none`.

## Verdict rules

1. Collect `blockers` from in-scope ballots. Chair-domain blockers are
   `must_address`. Adjacent blockers become `must_address` unless
   rebutted.
2. `concerns` become `may_defer` unless they are cheap and local (test
   missing, diagnostic wording) — those promote to `must_address`.
3. `approve` only when no unrebutted `must_address` remains and the
   evolution gate is `none` or already satisfied.
4. `request-changes` when the patch is the right layer but incomplete
   (tests, generality, diagnostic placement).
5. `block` when the layer is wrong, an invariant is violated, or
   evolution is required.

Write the rebuttal, if any, as one paragraph per adjacent blocker. "Out
of scope" is not a rebuttal unless the adjacent ballot should have
abstained.

## Specialist bar

Briefs encode closed-world documented invariants. Apply them
fail-closed:

- A `Protects` / `Reject unless` violation is `block`. Use
  `request-changes` only when the layer is right but incomplete (test,
  diagnostic placement).
- Rebutting an adjacent `block` that names an official doc requires
  citing the exception in **that same document**. "Equivalent in
  practice" / "existing tests pass" is not a rebuttal.
- The chair does not skip a closed-world default because the patch is
  small or the issue is a crash.

## Output

Use the chair schema in `ballot.md`. The rationale names domain ids.
Quote file paths and SE numbers.
