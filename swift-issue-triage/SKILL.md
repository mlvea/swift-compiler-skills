---
name: swift-issue-triage
description: Use when given a Swift compiler issue, bug report, crash log, or failing test and you need to classify which compiler pipeline stage owns it (parse/sema/silgen/sil-opts/irgen/runtime/tooling), find the likely files, matching resolved-issue archetype, and the right playbook before any fix attempt.
---

# Swift Issue Triage

Classify first. A wrong stage guess wastes a full build-test cycle.

## Inputs To Accept

Any of: issue number/URL (`swiftlang/swift#NNNNN`), title + body, stack
trace/assertion text, reproducer snippet, or a failing local test path.

## Triage Procedure

1. **Extract signals in priority order:**
   - Assertion message or stack frames (strongest). Function names map
     directly to stages via `../knowledge-base/pipeline-map.md`.
   - Reproducer behavior under flags: crashes at `-typecheck` → Sema;
     at `-emit-silgen` → SILGen; only under `-O` → optimizer; compiles but
     misbehaves when run → IRGen/runtime; editor-only → tooling.
   - Title keywords + labels last (often missing/wrong; many issues are
     labeled `triage needed`).

2. **Map to stage** using the identification table in
   `/Users/madushan/Documents/Github/swift-compiler-skills/knowledge-base/pipeline-map.md`.

3. **Match to an archetype** in
   `../knowledge-base/resolved-issue-patterns.md` (A1..A10). The archetype
   predicts the fix shape before you read compiler code.

4. **Check local precedent**: grep `wiki/compiler-understanding.md` and
   `issues/cases/` for the same subsystem; read the hand-reviewed mentor
   guidance for the likely files if listed in `issues/guidance/manual-review.md`.

5. **Produce a triage record** with exactly these fields:

```
Stage:            <parse|sema|silgen|sil-mandatory|sil-opts|irgen|runtime|driver|tooling|importer|serialization|autodiff|debuginfo>
Family:           <crash|accepts-invalid|rejects-valid|wrong-diagnostic|missing-diagnostic|miscompile|runtime-crash|editor-only|build>
Archetype:        <A1..A10>
Confidence:       high|medium|low + one-line reason
Likely files:     <2-5 exact paths from the stage playbook>
Test home:        <test dir(s) per regression-test-cookbook.md>
Repro command:    <exact swift-frontend/lit invocation>
Playbook:         knowledge-base/stage-playbooks/<stage>.md
Open questions:   <what must be verified by running, if anything>
```

6. If confidence is low, run the reproducer once through the flag ladder
   (`-typecheck` → `-emit-silgen` → `-emit-sil` → full compile+run) using
   the environment skill before finalizing the stage call.

## Hard Rules

- Never propose a fix before this record exists.
- Stack traces override titles; reproducers override labels.
- If two stages are plausible, name both and pick the one that *first*
  observes the bad state (fixes upstream of observation usually win;
  exception: adding user-facing diagnostics belongs in Sema even when a
  later stage could also guard).
- Record the triage into the issue's case file when work becomes real
  (see fix-loop skill step 1).
