---
name: swift-knowledge-curator
description: Use this skill when a durable fact changes or a playbook fact is wrong. One bounded edit must cite the check that was run.
---

# Swift knowledge curator

These files are editable.
When a durable fact changes, make one bounded edit.
A seating edit needs `score_pr.py --corpus` to still pass.
A brief edit or a playbook edit needs a named counterexample or a command that was run.

Do not rewrite a whole playbook for one miss.
The fast path in the fix loop does not come here unless that path taught a durable fact.

## Files you own

All paths are relative to the root of `swift-compiler-skills`.

- `knowledge-base/pipeline-map.md`
- `knowledge-base/stage-playbooks/*.md`
- `knowledge-base/regression-test-cookbook.md`
- `knowledge-base/resolved-issue-patterns.md`
- `knowledge-base/expert-panel/` (domain briefs, `seats.json`, `evolution-gate.md`)
- `swift-expert-panel/SKILL.md` and `swift-expert-panel/scripts/seat.py`
- `swift-issue-triage/SKILL.md`
- `swift-local-build-test/` (`SKILL.md`, `references/`, `scripts/export-env.py`)
- `swift-compiler-fix-loop/SKILL.md` and its references
- `swift-issue-explainer/SKILL.md`, plus its references and scripts
- `optimization/edit-log.md` (append-only journal)
- `references/harvest.md` in this skill

Environment facts live with the build-test skill.
Correct a command only after you have run it.
Do not edit a case file, the tracker, or the swift checkout from this skill.

## Curation loop

### When to run an epoch

Run an epoch when any one of these is true.

1. A fix attempt just finished. The attempt may be a success or a failure. A failure teaches more.
2. The same friction appeared twice. Examples are a wrong command, a missed stage, or a stale file name.
3. Fifty or more new closed issues exist since the last harvest.

### Step 1. Harvest

Follow `references/harvest.md` when a closed-issue count may have drifted.
An open issue is not solved. A patch in a local case file is not solved.
If a panel sat, compare the chair verdict with the maintainer reviews named in that file.

After an edit to the seating table or to an official document, run the checks in that file.
Those checks are `score_pr.py --corpus` and `probe_globs.py`.

### Step 2. Reflect

For each finished attempt, answer these questions.

- Where did this attempt lose the most time?
- Was the first triage stage correct?
- If it was not correct, which signal would have routed the issue correctly?
- Which playbook instruction was missing, wrong, or not followed?
- Did a documented command fail? Correct a wrong command in the same epoch.

### Step 3. Propose a bounded edit

Use this budget for one epoch.
The budget is a cap on churn. It is not a measured optimum.

- Keep substantive rule changes to 3 or fewer across all `SKILL.md` files.
- Keep new lines in the knowledge base to 30 or fewer.
- Keep new lines in the search-family map to 5 or fewer.
- Change commands and environment facts as needed. Correctness has no line budget.

A search-family line names files to open. It is not a patch.
Cite evidence for each edit.
Use an issue number, a case path, or a command transcript.

Do not give speculative advice.
Do not write the patch for a different future issue.

### Step 4. Accept or reject

Accept an edit only when at least one of these holds.

- **Regression.** A seating edit needs `score_pr.py --corpus` to still pass. Say whether `--sources-only` moved. For a triage sentence, name the resolved issue that the old text got wrong. Also name the issue that the new text routes.
- **Counterexample.** Name one resolved issue that the current text would send to the wrong place. A brief edit or a playbook edit needs a named counterexample or a command that was run.
- **Execution.** The exact command ran successfully during the epoch.

A second reading of two known cases is not a separate harness.
There is no separate replay harness.
There is no triage corpus scored by a script.
Put a rejected proposal in `edit-log.md` with the reason.

Look at that proposal again after two confirming cases.
Epoch numbers are unique. Do not reuse one.
Give the next epoch the next unused integer.

### Step 5. Journal

Append to `optimization/edit-log.md`. Do not rewrite an older epoch.

```
## <date> epoch N (<trigger>)
Evidence: <issues/cases/...>
Proposed: <diff summary>
Check: regression|counterexample|execution <result>
Accepted/Rejected: <what changed in which file>
Regression check: <corpus command, or the resolved issue you named>
```

## Limits on drift

Do not delete a validated command only because it looks redundant.
That command records a past failure.
Edit the deepest file that fixes the problem.
Use this order: the playbook, then `SKILL.md`, then the README.

That order keeps each entry skill short.
Put a long procedure in the knowledge base or in `references/` for that skill.
When two playbooks contradict, keep the playbook that has a dated file map from a merged pull request.

Fix the other playbook in the same epoch.
