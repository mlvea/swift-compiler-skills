---
name: swift-knowledge-curator
description: Use after completing (or failing) Swift compiler fix attempts, or periodically, to evolve the fix-loop skill set itself - harvest new resolved issues, mine recurring patterns, and apply small validation-gated edits to the knowledge base following the SkillOpt protocol. Also use when a playbook fact proves wrong or a triage call was missed.
---

# Swift Knowledge Curator

The skill suite under `skills/` is trainable state. Treat edits to it like
weight updates: bounded, evidence-driven, accepted only when validated.
Protocol adapted from microsoft/SkillOpt (text-space optimization with
validation gates) to run without external training infrastructure.

## Files You Own

All paths relative to this repo root (`swift-issue-fix-plans/`):

- `skills/knowledge-base/pipeline-map.md`
- `skills/knowledge-base/stage-playbooks/*.md`
- `skills/knowledge-base/regression-test-cookbook.md`
- `skills/knowledge-base/resolved-issue-patterns.md`
- `skills/swift-issue-triage/SKILL.md`
- `skills/swift-local-build-test/SKILL.md` and its
  `references/environments.md`
- `skills/swift-compiler-fix-loop/SKILL.md` + references
- `skills/optimization/edit-log.md` (append-only journal)

Environment facts live with the build-test skill; correctness fixes to them
are execution-gated (run the command first).

Do not edit case files, tracker, or the swift checkout from this skill.

## The Optimization Loop

### Epoch triggers

Run an epoch when any of these hold:

1. A fix attempt just finished (success OR failure — failures are the
   highest-gradient data).
2. The same friction appeared twice (wrong command, missed stage, stale
   file name).
3. Calendar trigger: ≥50 new closed issues since last harvest.

### Step 1: Harvest (new training data)

Pull freshly closed issues for pattern drift:

```bash
curl -sG "https://api.github.com/search/issues" \
  --data-urlencode "q=repo:swiftlang/swift is:issue is:closed crash in:title" \
  --data-urlencode sort=closed --data-urlencode order=desc \
  --data-urlencode per_page=50 -o data/resolved-issues-<date>/crash.json
```

(Repeat for: assertion, diagnostic, SILGen, IRGen, sendable, type checker,
parser, completion/sourcekit. Unauthenticated API allows ~10 search
requests/min — sleep between calls.) Update
`knowledge-base/resolved-issue-patterns.md` counts only when family shares
shift by >10% (relative to repo root).

### Step 2: Reflect (extract gradients)

For each completed trajectory (case files, fix logs, this epoch's events),
answer:

- Where did the agent lose the most time? (environment, triage, location,
  test style, verification)
- Was the first triage stage correct? If not, which signal would have
  routed correctly?
- Which playbook instruction was missing, wrong, or ignored?
- Did any documented command fail? (hard error — must be fixed same epoch)

### Step 3: Propose bounded edits

Budget per epoch (learning rate):

- ≤ 3 substantive rule changes across all SKILL.mds
- ≤ 30 new lines in knowledge-base total
- ≤ 5 new archetype examples (one line each)
- Commands/environment facts corrected as needed (no budget — correctness)

Each edit must cite its evidence: issue number, case path, or command
transcript. No speculative advice ("consider", "might") — only observed
mechanisms.

### Step 4: Validation gate

An edit is accepted only if at least one holds:

- **Replay gate**: re-triage 2–3 already-solved cases (from
  `issues/cases/*/README.md`) with the edited docs; the new text must route
  every one to its correct recorded stage/archetype faster or equally well,
  and must not misroute previously-correct cases.
- **Counterexample gate**: for a new pattern claim, find one resolved issue
  matching it that the current docs would have misrouted.
- **Execution gate** (commands): the exact command was run successfully on
  this machine during the epoch.

Rejected proposals go to `edit-log.md` with reason — they are often right
but premature; revisit after two confirming instances.

### Step 5: Journal

Append to `skills/optimization/edit-log.md`:

```
## <date> epoch N (<trigger>)
Evidence: <issues/cases/...>
Proposed: <diff summary>
Gate: replay|counterexample|execution <result>
Accepted/Rejected: <what changed in which file>
Held-out check: <2 solved cases re-triaged OK>
```

## Anti-Drift Rules

- Never delete a validated command because it looks redundant; it encodes a
  past failure.
- Prefer editing the deepest file that fixes the problem (playbook over
  SKILL.md over suite README) so entry-point skills stay lean.
- Keep each SKILL.md under ~120 rendered lines; overflow goes into
  knowledge-base.
- If two playbooks contradict, the one with a dated verified example wins;
  then reconcile the loser same-epoch.
