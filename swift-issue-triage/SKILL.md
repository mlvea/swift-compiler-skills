---
name: swift-issue-triage
description: Use this skill to name the stage for a Swift issue, crash, or failing test. Run it before any attempt to fix the bug.
---

# Swift issue triage

Classify the stage from this issue. Do not classify the patch.

## Inputs

Accept any one of these inputs.

- An issue number or URL, as `swiftlang/swift#NNNNN`
- A title and a body
- A stack trace or assertion text
- A reproducer snippet
- A path to a failing local test

## Procedure

1. Read signals from this issue, in this order.

Read the assertion and the stack frames first. Those frames are the strongest signal.
Map each function name to a stage with `../knowledge-base/pipeline-map.md`.
Run this reducer through the flag ladder when the stack does not settle the stage.

The flag ladder is required. It is not optional.
Run the flags in this order. Use the environment skill.

- `-typecheck`
- `-emit-silgen`
- `-emit-sil` without `-O`
- `-O`
- compile and run

Apply these mappings.

- A crash at `-typecheck` means Sema.
- A crash at `-emit-silgen` means SILGen.
- A failure at `-emit-sil` without `-O` is sil-mandatory.
- sil-mandatory includes the mandatory SIL passes.
- sil-mandatory includes region-isolation diagnostics.
- A failure only under `-O` means the optimizer.
- A program that compiles and then misbehaves at run time means IRGen or the runtime.
- An editor-only failure means tooling.

Read the title keywords and the labels last.

2. Map the signals to a stage.

Use the identification table in `../knowledge-base/pipeline-map.md`.
For a machine checkout, copy `../swift-local-build-test/references/paths.example.json` to `paths.json`.

3. Search family, after the stage is known. This step is optional.

Read `../knowledge-base/resolved-issue-patterns.md`.
The family names extra directories to open. It is not a patch recipe.

4. Record the triage in this shape.

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

## Hard rules

Do not propose a fix before this record exists.
A stack trace overrides the title. This reducer overrides the labels.
A crash or an assert is the observation site.

Find the producing pass on this reproducer. Use heuristic 9 in the pipeline map.
Other issues do not decide the patch. Search families, case files, harvested plans, and case notes do not decide it either.

A pull request or a maintainer comment on this issue is in scope.
Record the triage in the case file when the work becomes real.
