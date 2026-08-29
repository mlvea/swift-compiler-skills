---
name: swift-expert-panel
description: Domain expert panel that reviews a Swift compiler fix plan or PR. Required after a written plan (before compiler edits) and again on the diff (before marking a PR ready). Also use on demand for "ask the panel", "expert panel", or review this plan/PR/diff.
---

# Swift Expert Panel

Supplementary review, not a second triage. Playbooks say where to look;
this panel says whether the change is acceptable in the domains it
touches. Seats are compiler domains (`type-system`, `concurrency`,
`sil-optimizer`).

## When (required)

| `kind` | Run after | Artifact | Blocked until chair `approve` |
| --- | --- | --- | --- |
| `plan` | Fix-loop step 4 (bug explained) | Written invariant, broken assumption, path, intended change, likely files | Any compiler source edit |
| `pr` | Fix-loop step 8 (patch + tests ready) | Diff, PR description, changed files | Marking the PR ready for review |

Also sit on demand given a plan, diff, PR URL, or case file.

**Skip only** for comment-only, docs-only, or test-expectation-only
edits that do not encode a language rule. If unsure, sit. A small Sema
check is not a skip.

After `request-changes`, apply `must_address` and **re-sit** the same
`kind` before continuing.

## How

Inputs: `kind` (`plan`|`pr`), triage `stage`, files (likely paths or
`git diff --name-only`), artifact (plan text or patch + description).

1. **Seat from files, not by hand:**

```bash
python3 swift-expert-panel/scripts/seat.py --stage <triage-stage> \
  --text-file <plan-or-pr-body> -- <files relative to the swift checkout>
```

Use the JSON `chair` + `seated`. Do not add or drop domains. Out-of-
charter seats abstain themselves.

2. **Independent ballots** — one read-only subagent per seated domain,
   in parallel. Grok: `/workflow swift-expert-panel` with
   `{kind, chair, seated, artifact, files, kb_root}`. Other hosts: spawn
   the same way. Each agent:
   - Reads only `knowledge-base/expert-panel/domains/<id>.md`,
     `evolution-gate.md`, `ballot.md`, and the artifact (with tools).
   - Empty `blockers` is valid only after inspecting `Protects` and
     `Reject unless`. Those rules are **fail-closed**: a violation is
     `block` unless the artifact cites the exception in the same
     official doc the brief names.
   - **Abstains** when outside its charter. Abstention is success.
   - Does not discuss other domains' hypothetical votes.

3. **Chair** — one more agent: the script's `chair`. It reads
   `chair-protocol.md`, `evolution-gate.md`, its brief, and every
   ballot. Weight: chair in-scope 1.0 (`block` is final); other
   in-scope 0.5 (`block` needs a written invariant rebuttal);
   abstain/failed 0 (not approval).

4. **Obey the chair:** `approve` continue; `request-changes` fix then
   re-sit; `block` do not land. Record seating, ballots, and verdict in
   the case file under `## Expert panel`.

## Hard Rules

- Seating is the script. The chair is the script's `chair`.
- Do not average votes.
- User-visible language/stdlib behavior changes go through
  `evolution-gate.md` even if framed as a bugfix.
- Do not restate stage playbooks. Experts judge *acceptability*.
- Named invariants in a seated brief beat a plausible local patch.
  Closed-world defaults (not listed in the official doc ⇒ break;
  solution application cannot fail; OSSA exactly-once; never drop a
  debug variable) are the bar a hurried human pass skips.
