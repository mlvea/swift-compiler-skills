---
name: swift-issue-triage
description: Use when given a Swift compiler issue, bug report, crash log, or failing test and you need to classify which compiler pipeline stage owns it (parse/sema/silgen/sil-opts/irgen/runtime/tooling) and which files to open before any fix attempt.
---

# Swift Issue Triage

Classify the *stage* from THIS issue. Do not classify the *patch*.

## Inputs To Accept

Issue number/URL (`swiftlang/swift#NNNNN`), title + body, stack
trace/assertion text, reproducer snippet, or a failing local test path.

## Triage Procedure

1. **Signals from THIS issue, in order:**
   - Assertion / stack frames (strongest). Function names → stage via
     `../knowledge-base/pipeline-map.md`.
   - If the stack does not settle the stage, run THIS reducer through
     the flag ladder (required, not optional):
     `-typecheck` → `-emit-silgen` → `-emit-sil` → compile+run
     (environment skill). Crashes at `-typecheck` → Sema; at
     `-emit-silgen` → SILGen; only under `-O` → optimizer; compiles
     but misbehaves when run → IRGen/runtime; editor-only → tooling.
   - Title keywords + labels last.

2. **Map to stage** using the identification table in
   `../knowledge-base/pipeline-map.md`. Machine checkouts:
   `../swift-local-build-test/references/paths.json`.

3. **Optional search family** (after stage is known) in
   `../knowledge-base/resolved-issue-patterns.md`. Extra *directories*
   to open. Not a recipe.

4. **Record:**

```
Stage:            <parse|sema|silgen|sil-mandatory|sil-opts|irgen|runtime|driver|tooling|importer|serialization|autodiff|debuginfo>
Family:           <crash|accepts-invalid|rejects-valid|wrong-diagnostic|missing-diagnostic|miscompile|runtime-crash|editor-only|build>
Search family:    <A1..A10 or none>
Confidence:       high|medium|low + one-line reason from THIS stack or flag ladder
Likely files:     <2-5 paths from the stage playbook>
Test home:        <test dir(s) per regression-test-cookbook.md>
Repro command:    <exact swift-frontend/lit invocation>
Playbook:         knowledge-base/stage-playbooks/<stage>.md
Open questions:   <what THIS reducer still has not shown>
```

## Hard Rules

- Never propose a fix before this record exists.
- Stack traces override titles; this reducer overrides labels.
- A crash/assert is the observation site. Find the producing pass on
  THIS repro (pipeline-map heuristic 9).
- Other issues, search families, case files, harvested plans, and wiki
  lessons do not decide the patch. If THIS issue has PRs or maintainer
  comments, those are in scope.
- Record the triage into the issue's case file when work becomes real.
