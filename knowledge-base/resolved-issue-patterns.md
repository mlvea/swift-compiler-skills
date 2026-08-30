# Resolved Issue Patterns (Search Families)

Evidence base: 418 unique closed issues harvested from
`swiftlang/swift/issues` on 2026-08-25 (`data/resolved-issues-2026-08/`,
digest in `digest.json`) plus the local corpus of 200 harvested plans
(`issues/plans-by-search-page/`) and ~62 case files.

Read this file to pick extra *files to open*. It does not decide the
patch. Prove the broken invariant from THIS issue's reducer, stack, and
the code that reducer reaches.

- A merged PR on *this* issue (including rejected earlier PRs) is in
  scope.
- Maintainer comments on *this* issue's thread are in scope.
- Other issues, local case-file patches, and wiki lessons are file-search
  hints. They are not evidence that a patch is correct.
- Open issues are not solved. Do not treat their case files as ground
  truth.

## Symptom Family Frequencies

| Family | Share | Typical stage |
| --- | --- | --- |
| Crash / assertion / verifier | largest (~40%) | any; SILGen+SIL+IRGen heavy |
| Wrong/missing diagnostic, accepts-invalid | ~30% | Sema mostly |
| Miscompile / wrong runtime behavior | ~15% | SILOpt, IRGen, runtime |
| Editor/tooling only | ~10% | IDE/SourceKit/LSP |
| Build/driver/platform | remainder | Driver, platforms |

## Search Families

Match THIS issue's symptoms to a family, then open the listed areas.
Do not copy a listed issue's patch onto this one.

### A1. Later-stage crash on odd code

- Signature: crash in SILGen/IRGen/SIL on a small unusual program.
- Open: Sema if `-typecheck` on THIS reducer is clean *and* the program
  looks invalid; also the crashing emit function. Decide validity from
  THIS reducer.
- Map (merged PR file map only): #91566 → #91581
  `lib/SILOptimizer/Utils/Generics.cpp` +
  `test/embedded/existential-generic-error.swift`. #86463 is open
  (not a map).

### A2. Diagnostic cascade after one small mistake

- Signature: several unrelated errors from one omitted label or token.
- Open: recovery at the claim site (`lib/Sema/CSSimplify.cpp` for
  argument matching; `lib/Parse/` for token recovery).
- Map (stage only): #86472 open Sema; #80929 parse.

### A3. `-O`-only miscompile or crash

- Signature: `-Onone` clean; `-O`/`-Osize` broken; or verifier after a
  named pass.
- Open: the pass the bisect names on THIS SIL. Read that pass's existing
  safety checks.
- Map (merged PR file map only): #90916 → rejected #90931, merged
  #90945 `SwiftCompilerSources/.../LoopInvariantCodeMotion.swift`.

### A4. Isolation / sendability through wrappers

- Signature: false Sendable errors, missing data-race diagnostics, actor
  hop mistakes involving closures/partial applies/temporaries.
- Open: Sema (`TypeCheckConcurrency.cpp`) *and* mandatory
  `SendNonSendable` / `RegionAnalysis*`. Decide from THIS value.
- Map (stage only): #87540, #87503 open; #85667, #87768.

### A5. New feature combination, one path crashing

- Signature: crash or "unimplemented" for one combo of a recent feature
  (typed throws, packs, macros, embedded).
- Open: switches on that shape in the crashing stage *and* the stage
  that produces its input. Confirm THIS program is valid before adding
  a lowering arm.
- Map (stage only): #86347 merged IRGen; #87030; #90818.

### A6. Editor-only, batch compile fine

- Signature: completion/tokens/cursor wrong or crashing only in the IDE.
- Open: `lib/IDE`, SourceKit request lifetime, and the parser context
  that feeds completion. More than one cause lives here.
- Map (stage only): #85582, #57248, #66785, #85646 (open).

### A7. Cross-module / TBD / serialized-SIL only

- Signature: fails only across modules, or TBD vs IR disagree.
- Open: `lib/Serialization`, TBDGen, and mangling of the missing symbol.
- Map (stage only): #85557 open; #85441; #86003.

### A8. Target-gated (embedded / wasm / watchOS / Linux / Windows)

- Signature: only one target, or only `-O` on that target.
- Open: target branches *and* shared SIL/IRGen utilities. Confirm THIS
  repro is target-gated before assuming general breakage.
- Map (merged PR file map only): #91566 → #91581 (above); #89581
  Embedded pack IRGen (`emitTypeMetadataRef`, not `.Elements` on thin
  metadata). Other ids are stage hints, not file maps, until a merged
  PR is recorded.

### A9. "Failed to produce diagnostic for expression"

- Signature: that message, or silently accepted invalid expression.
- Open: `lib/Sema/CSDiagnostics.cpp` and solver salvage /
  `SolutionApplication`.
- Map (stage only): #59618, #60793, #90258.

### A10. Bridging / interop unsoundness

- Signature: unsound cast or conformance via ObjC/C++ bridges.
- Open: the exact bridge/cast THIS reducer takes.
- Map (stage only): #85111 open; #83695.

## Triage Shortcuts

- "SIL verification error" → sil-optimization.md class O1 (observation).
- "IRGen" + assert → observation is IRGen; still find which pass
  produced the SIL on THIS repro.
- "Failed to produce diagnostic" → sema.md class S4.
- "accepts invalid" label → sema.md class S2.
- EXC_BAD_ACCESS in a user binary → irgen-runtime.md class R4, but
  first rule out miscompile (O2/R3) on THIS binary.
- `[SR-…]` prefix = old Jira migration; same pipeline rules.
- `triage needed` means nobody confirmed stage — rely on THIS
  reproducer, not labels.

## Local Corpus Pointers

File-search only (not proof of a patch):

- 200 harvested plans: `issues/plans-by-search-page/page-01..10/`
- Hand-reviewed mentor guidance index: `issues/guidance/manual-review.md`
- Durable file/subsystem notes: `wiki/compiler-understanding.md`
- Case archive: `issues/cases/<n>/README.md`
