---
name: swift-expert-panel
description: Domain expert panel that reviews a Swift compiler fix plan or PR. Seats are compiler domains, independent ballots, weighted chair verdict. Use when asked to review a plan or PR, "ask the panel", "expert panel", or after a fix-loop plan/PR is ready.
---

# Swift Expert Panel

Supplementary review, not a second triage. Playbooks say where to look;
this panel says whether the change is acceptable in the domains it
touches.

Seats are compiler domains (`type-system`, `concurrency`, `sil-optimizer`).

## When To Sit

- After fix-loop step 4 (bug explained, before patching) — **plan** review.
- After fix-loop step 8 (patch + tests, before marking the PR ready) — **PR** review.
- On demand: plan text, diff, PR URL, or case file.

Skip only for comment-only, docs-only, or test-expectation-only edits that
do not encode a language rule. When unsure, sit.

## Procedure

1. **Seat from files, not vibes.** Run:

```bash
python3 swift-expert-panel/scripts/seat.py --stage <triage-stage> \
  --text-file <plan-or-pr-body> -- <changed files relative to swift checkout>
```

Use `chair` + `seated` from the JSON. Do not add extra domains. Do not
drop a seated domain because it looks unrelated — that domain abstains
itself if needed.

2. **Independent ballots.** Spawn one read-only subagent per seated domain
   in parallel (Grok: `/swift-expert-panel` workflow, or this skill's
   host parallel). Each agent:
   - Reads only `knowledge-base/expert-panel/domains/<id>.md` plus
     `evolution-gate.md` and the artifact (plan or diff).
   - Must inspect the actual plan/diff with tools. Empty `blockers` is
     valid only after that inspection.
   - Returns the ballot schema in `knowledge-base/expert-panel/ballot.md`.
   - **Abstains** (`in_scope: abstain`) when the change is outside its
     charter. Abstention is success.
   - Never discusses other domains' hypothetical votes.

3. **Chair verdict.** After every ballot is in, spawn **one** more agent:
   the `chair` domain. It reads `chair-protocol.md`, `evolution-gate.md`,
   its own brief, and every ballot. It does not re-review the diff from
   scratch unless a ballot is unusable. Weighting:

   | Ballot | Weight |
   | --- | --- |
   | Chair domain, `in_scope: in` | 1.0 — its `block` cannot be overridden |
   | Other seated, `in_scope: in` | 0.5 — `block` needs a written rebuttal naming the invariant |
   | `abstain` or failed agent | 0 |

   Failed or missing ballots are not silent approvals.

4. **Stop or proceed.**
   - `approve` — continue the fix-loop.
   - `request-changes` — address `must_address` before implementing / marking ready.
   - `block` — do not land; evolution or invariant failure.
   Record the seating JSON, ballots, and chair verdict in the case file
   under `## Expert panel`.

## Hard Rules

- Seating is the script. The chair is the script's `chair`.
- Do not average votes. The chair decides, with the weights above.
- User-visible language/stdlib behavior changes go through
  `evolution-gate.md` even if the patch "fixes a bug".
- Do not restate stage playbooks. Experts judge *acceptability*.
