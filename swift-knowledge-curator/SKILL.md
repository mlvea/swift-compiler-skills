---
name: swift-knowledge-curator
description: Use after completing (or failing) Swift compiler fix attempts, or periodically, to evolve the fix-loop skill set itself - harvest new resolved issues, mine recurring patterns, and apply one bounded, validation-gated edit per trajectory. Also use when a playbook fact proves wrong or a triage call was missed.
---

# Swift Knowledge Curator

These files are editable. After each real fix (or failure), apply **one
bounded edit**, accepted only behind replay, counterexample, or
execution. One bullet in `optimization/deltas.md`. Do not rewrite a
whole playbook for one miss. Splits: `optimization/splits/`
(`docs/eval-protocol.md`). Do not harvest `D_test`.

## Files You Own

All paths relative to this repo root (`swift-compiler-skills/`):

- `knowledge-base/pipeline-map.md`
- `knowledge-base/stage-playbooks/*.md`
- `knowledge-base/regression-test-cookbook.md`
- `knowledge-base/resolved-issue-patterns.md`
- `knowledge-base/expert-panel/` (domain briefs, seats.json, evolution-gate)
- `swift-expert-panel/SKILL.md` and `swift-expert-panel/scripts/seat.py`
- `swift-issue-triage/SKILL.md`
- `swift-local-build-test/SKILL.md` and its
  `references/environments.md`
- `swift-compiler-fix-loop/SKILL.md` + references
- `optimization/edit-log.md` (append-only journal)
- `optimization/deltas.md` (one helpful/harmful bullet per accepted epoch)
- `optimization/splits/` and `docs/eval-protocol.md` (do not put
  `D_test` ids into other files)

Environment facts live with the build-test skill; correctness fixes to them
are execution-gated (run the command first).

Do not edit case files, tracker, or the swift checkout from this skill.

## Curation loop

### Epoch triggers

Run an epoch when any of these hold:

1. A fix attempt just finished (success or failure — failures teach more).
2. The same friction appeared twice (wrong command, missed stage, stale
   file name).
3. Calendar trigger: ≥50 new closed issues since last harvest.

Never harvest, mine, scorecard, or journal as evidence any id in
`optimization/splits/d_test.json`. After harvests run
`python3 swift-expert-panel/scripts/check_split.py` and
`python3 swift-expert-panel/scripts/check_split.py --harvest <json>`.
`D_sel` may accept/reject seating-table edits only.

### Step 1: Harvest (new closed issues)

Pull freshly closed issues for pattern drift:

```bash
curl -sG "https://api.github.com/search/issues" \
  --data-urlencode "q=repo:swiftlang/swift is:issue is:closed crash in:title" \
  --data-urlencode sort=closed --data-urlencode order=desc \
  --data-urlencode per_page=50 -o data/resolved-issues-<date>/crash.json
```

(Repeat for: assertion, diagnostic, SILGen, IRGen, sendable, type checker,
parser, completion/sourcekit. Unauthenticated API allows ~10 search
requests/min — sleep between calls.) Drop any id in `d_test.json`
before mining. Update `knowledge-base/resolved-issue-patterns.md` counts
only when family shares shift by >10% (relative to repo root).

For a search-family or replay-gate issue, fetch its closing PR and any
linked/superseded PRs. Record merged PR + files changed (file map), and
that issue's own `CHANGES_REQUESTED` reviews / maintainer comments.
Open issues and local case-file patches are not solved.

If a panel sat, compare the chair verdict to those reviews. A
`CHANGES_REQUESTED` the panel missed is a domain-brief miss (add a
reject-unless). A panel `block` that maintainers approved needs a
counterexample before deleting the rule. Procedure and corpus:
`knowledge-base/expert-panel/scorecard.md`. Re-run
`python3 swift-expert-panel/scripts/score_pr.py --corpus` and
`--sel` after seating-table edits. Scorecard (`D_tr`) epochs may
exceed the 30-line KB budget: misses vs landed reviews are
correctness, not style.

After seating-table or official-doc edits, run
`python3 swift-expert-panel/scripts/probe_globs.py` against
`paths.json` `swift_checkout`. Missing globs are the same class of
bug as epoch 10 (`test/Module/`).

### Step 2: Reflect

For each completed trajectory (case files, fix logs, this epoch's events):

- Where did the agent lose the most time? (environment, triage, location,
  test style, verification)
- Was the first triage stage correct? If not, which signal would have
  routed correctly?
- Which playbook instruction was missing, wrong, or ignored?
- Did any documented command fail? (hard error — must be fixed same epoch)

### Step 3: Propose bounded edits

Budget per epoch:

- ≤ 3 substantive rule changes across all SKILL.mds
- ≤ 30 new lines in knowledge-base total
- ≤ 5 new search-family map lines (files to open, not a patch recipe)
- Commands/environment facts corrected as needed (no budget — correctness)

Each edit must cite its evidence: issue number, case path, or command
transcript. No speculative advice. Never write a rule that states the
patch for a future, different issue.

### Step 4: Validation gate

An edit is accepted only if at least one holds:

- **Replay gate**: re-triage 2–3 merged-PR-backed **`D_tr` or `D_sel`**
  cases (never `D_test`); the new text must route each to the merged
  PR's stage/files without misrouting others. Open local cases may
  check stage routing only. For seating-table edits, re-run `seat.py`
  on `knowledge-base/expert-panel/roster.md` **and**
  `python3 swift-expert-panel/scripts/score_pr.py --sel` and require
  identical chairs.
- **Counterexample gate**: for a new pattern claim, find one resolved issue
  matching it that the current docs would have misrouted.
- **Execution gate** (commands): the exact command was run successfully on
  this machine during the epoch.

Rejected proposals go to `edit-log.md` with reason — they are often right
but premature; revisit after two confirming instances.

### Step 5: Journal

Append to `optimization/edit-log.md`:

```
## <date> epoch N (<trigger>)
Evidence: <issues/cases/...>
Proposed: <diff summary>
Gate: replay|counterexample|execution <result>
Accepted/Rejected: <what changed in which file>
Held-out check: <D_sel seating and/or D_tr replay — never D_test ids>
```

## Anti-Drift Rules

- Never delete a validated command because it looks redundant; it encodes a
  past failure.
- Prefer editing the deepest file that fixes the problem (playbook over
  SKILL.md over suite README) so entry-point skills stay lean.
- Keep each SKILL.md under ~120 rendered lines; overflow goes into
  knowledge-base.
- If two playbooks contradict, the one with a dated merged-PR *file map*
  wins; reconcile the loser same-epoch.
