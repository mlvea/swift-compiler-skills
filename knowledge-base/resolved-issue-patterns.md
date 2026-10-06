# Resolved Issue Patterns (Search Families)

This evidence base has 418 unique closed issues.
The harvest date is 2026-08-25, from `swiftlang/swift/issues`.
The files are in `data/resolved-issues-2026-08/`.
The digest file is `digest.json`.

The local corpus has 200 harvested plans in `issues/plans-by-search-page/`.
The corpus also has about 62 case files.

Read this file to pick extra files to open.
This file does not decide the patch.
Prove the broken invariant from THIS issue.
Use the reducer, the stack, and the code that the reducer reaches.

- A merged PR on THIS issue is in scope. A rejected earlier PR on THIS issue is also in scope.
- Maintainer comments on the thread for THIS issue are in scope.
- Other issues, local case-file patches, and wiki lessons are file-search hints. They are not evidence that a patch is correct.
- Open issues are not solved. Do not treat their case files as ground truth.

## Symptom Family Frequencies

| Family | Share | Typical stage |
| --- | --- | --- |
| Crash / assertion / verifier | largest (~40%) | Any stage. SILGen, SIL, and IRGen are the heavy stages. |
| Wrong or missing diagnostic, accepts-invalid | ~30% | Mostly Sema |
| Miscompile or wrong runtime behavior | ~15% | SILOpt, IRGen, runtime |
| Editor or tooling only | ~10% | IDE, SourceKit, LSP |
| Build, driver, or platform | remainder | Driver, platforms |

## Search Families

Match the symptoms of THIS issue to one family.
Then open the listed areas.
Do not copy the patch of a listed issue onto this issue.

### A1. Later-stage crash on odd code

- Signature: a crash in SILGen, IRGen, or SIL on a small unusual program.
- Open Sema if `-typecheck` on THIS reducer is clean and the program looks invalid. Also open the crashing emit function. Decide validity from THIS reducer.
- This map is a merged PR file map only. #91566 maps to #91581. The files are `lib/SILOptimizer/Utils/Generics.cpp` and `test/embedded/existential-generic-error.swift`. #86463 is open. #86463 is not a map.

### A2. Diagnostic cascade after one small mistake

- Signature: several unrelated errors come from one omitted label or one omitted token.
- Open recovery at the claim site. For argument matching, open `lib/Sema/CSSimplify.cpp`. For token recovery, open `lib/Parse/`.
- This map is a stage map only. #86472 is open and the stage is Sema. #80929 is parse.

### A3. `-O`-only miscompile or crash

- Signature: `-Onone` is clean, and `-O` or `-Osize` is broken. Or the verifier fails after a named pass.
- Open the pass that the bisect names on THIS SIL. Read the safety checks that already exist in that pass.
- This map is a merged PR file map only. #90916 maps to rejected #90931 and to merged #90945. The file is `SwiftCompilerSources/.../LoopInvariantCodeMotion.swift`.

### A4. Isolation / sendability through wrappers

- Signature: false Sendable errors, missing data-race diagnostics, or actor hop mistakes. The mistakes involve closures, partial applies, or temporaries.
- Open Sema in `TypeCheckConcurrency.cpp`. Also open mandatory `SendNonSendable` and `RegionAnalysis*`. Decide from THIS value.
- This map is a stage map only. #87540 and #87503 are open. The stage map also lists #85667 and #87768.

### A5. New feature combination, one path crashing

- Signature: one combination of a recent feature crashes, or the compiler reports `unimplemented`. Feature examples are typed throws, packs, macros, and embedded.
- Open the switches on that shape in the crashing stage. Also open the stage that produces its input. Confirm that THIS program is valid before you add a lowering arm.
- This map is a stage map only. #86347 is merged IRGen. The stage map also lists #87030 and #90818.

### A6. Editor-only, batch compile fine

- Signature: completion, tokens, or cursor info is wrong only in the IDE, or that path crashes. Batch compile is fine.
- Open `lib/IDE`, the SourceKit request lifetime, and the parser context that feeds completion. More than one cause lives here.
- This map is a stage map only. The stage map lists #85582, #57248, #66785, and #85646 (open).

### A7. Cross-module / TBD / serialized-SIL only

- Signature: the failure is only across modules, or TBD and IR disagree.
- Open `lib/Serialization`, TBDGen, and the mangling of the missing symbol.
- This map is a stage map only. #85557 is open. The stage map also lists #85441 and #86003.

### A8. One target only (embedded / wasm / watchOS / Linux / Windows)

- Signature: the failure is only on one target, or only under `-O` on that target.
- Open the target branches. Also open the shared SIL utilities and the shared IRGen utilities. Confirm that THIS reproducer fails only on that target before you assume general breakage.
- This map is a merged PR file map only. #91566 maps to #91581, as above. #89581 is Embedded pack IRGen. The map names `emitTypeMetadataRef`, not `.Elements` on thin metadata. Other ids are stage hints, not file maps, until a merged PR is recorded.

### A9. "Failed to produce diagnostic for expression"

- Signature: the message is "Failed to produce diagnostic for expression", or the compiler silently accepts an invalid expression.
- Open `lib/Sema/CSDiagnostics.cpp`, solver salvage, and `SolutionApplication`.
- This map is a stage map only. The stage map lists #59618, #60793, and #90258.

### A10. Bridging / interop unsoundness

- Signature: an unsound cast or conformance goes through an ObjC bridge or a C++ bridge.
- Open the exact bridge or cast that THIS reducer takes.
- This map is a stage map only. #85111 is open. The stage map also lists #83695.

## Triage Shortcuts

- For the text `SIL verification error`, open sil-optimization.md class O1. That class is the observation.
- For `IRGen` plus an assert, the observation is IRGen. Still find the pass that produced the SIL on THIS repro.
- For the text `Failed to produce diagnostic`, open sema.md class S4.
- For the `accepts invalid` label, open sema.md class S2.
- For `EXC_BAD_ACCESS` in a user binary, open irgen-runtime.md class R4. First, rule out a miscompile (O2 or R3) on THIS binary.
- A `[SR-…]` prefix means the old Jira migration. Use the same pipeline rules.
- `triage needed` means that nobody confirmed the stage. Rely on THIS reproducer, not on the labels.

## Local Corpus Pointers

These pointers are for file search only.
They are not proof of a patch.

- 200 harvested plans are in `issues/plans-by-search-page/page-01..10/`.
- The hand-reviewed mentor guidance index is `issues/guidance/manual-review.md`.
- Durable notes for files and subsystems are in `wiki/compiler-understanding.md`.
- The case archive is `issues/cases/<n>/README.md`.
