---
name: swift-issue-triage
description: Use when given a Swift compiler issue, bug report, crash log, or failing test and you need to classify which compiler pipeline stage owns it (parse/sema/silgen/sil-opts/irgen/runtime/tooling) and which files to open before any fix attempt.
---

# Swift Issue Triage

Classify the *stage* first. A wrong stage wastes a build-test cycle.
Do not classify the *patch*. Other issues, archetypes, case files, and
wiki lessons do not decide what to change.

## Inputs To Accept

Any of: issue number/URL (`swiftlang/swift#NNNNN`), title + body, stack
trace/assertion text, reproducer snippet, or a failing local test path.

## Triage Procedure

1. **Extract signals from THIS issue, in priority order:**
   - Assertion message or stack frames (strongest). Function names map
     to stages via `../knowledge-base/pipeline-map.md`.
   - Reproducer under flags: crashes at `-typecheck` → Sema;
     at `-emit-silgen` → SILGen; only under `-O` → optimizer; compiles but
     misbehaves when run → IRGen/runtime; editor-only → tooling.
   - Title keywords + labels last (often missing/wrong; many issues are
     labeled `triage needed`).

2. **Map to stage** using the identification table in
   `/Users/madushan/Documents/Github/swift-compiler-skills/knowledge-base/pipeline-map.md`.

3. **Optional search family** in
   `../knowledge-base/resolved-issue-patterns.md` (A1..A10). Use it only
   to pick extra files to open. It is not a recipe and does not decide
   the patch.

4. **File hints only** from `wiki/compiler-understanding.md`,
   `issues/cases/`, and `issues/guidance/` when listed. Those documents
   name subsystems. They are not proof of a fix for this issue.

5. **Produce a triage record** with exactly these fields:

```
Stage:            <parse|sema|silgen|sil-mandatory|sil-opts|irgen|runtime|driver|tooling|importer|serialization|autodiff|debuginfo>
Family:           <crash|accepts-invalid|rejects-valid|wrong-diagnostic|missing-diagnostic|miscompile|runtime-crash|editor-only|build>
Search family:    <A1..A10 or none — files to open, not the patch>
Confidence:       high|medium|low + one-line reason from THIS repro/stack
Likely files:     <2-5 exact paths from the stage playbook>
Test home:        <test dir(s) per regression-test-cookbook.md>
Repro command:    <exact swift-frontend/lit invocation>
Playbook:         knowledge-base/stage-playbooks/<stage>.md
Open questions:   <what THIS reducer still has not shown>
```

6. If confidence is low, run THIS reducer once through the flag ladder
   (`-typecheck` → `-emit-silgen` → `-emit-sil` → full compile+run) using
   the environment skill before finalizing the stage call.

## Hard Rules

- Never propose a fix before this record exists.
- Stack traces override titles; reproducers override labels.
- If two stages are plausible, name both. Pick the one that *first*
  observes the bad state on THIS reducer (flag ladder). User-facing
  diagnostics, when needed, belong in Sema — but only after THIS
  program is shown to be invalid.
- A crash/assert names the observation site, not the patch site (see
  pipeline-map heuristic 9). Find the producing pass on THIS repro.
- Do not take the patch from an archetype, similar issue, case file,
  or wiki lesson. If THIS issue already has PRs, read those. Everything
  else may name files.
- Record the triage into the issue's case file when work becomes real
  (see fix-loop skill step 1).
