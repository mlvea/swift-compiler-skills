# Resolved Issue Patterns (Mined)

Evidence base: 418 unique closed issues harvested from
`swiftlang/swift/issues` on 2026-08-25 (`data/resolved-issues-2026-08/`,
digest in `digest.json`) plus the local corpus of 200 harvested plans
(`issues/plans-by-search-page/`) and ~62 case files with patch artifacts.

Read this file when triaging a new issue to find the closest resolved
precedent. Update it after every completed fix (see curator skill).

A numbered example is a *fix shape* only when a merged PR is cited.
Open issues are routing evidence (maintainer comments), not proof the
documented patch is right. Rejected first PRs (`CHANGES_REQUESTED`,
superseded) are the usual agent mistakes — copy those as anti-patterns,
not as the fix.

## Symptom Family Frequencies

| Family | Share | Typical stage |
| --- | --- | --- |
| Crash / assertion / verifier | largest (~40%) | any; SILGen+SIL+IRGen heavy |
| Wrong/missing diagnostic, accepts-invalid | ~30% | Sema mostly |
| Miscompile / wrong runtime behavior | ~15% | SILOpt, IRGen, runtime |
| Editor/tooling only | ~10% | IDE/SourceKit/LSP |
| Build/driver/platform | remainder | Driver, platforms |

## Recurring Root-Cause Archetypes

Each archetype lists: signature → mechanism → canonical fix shape → example.

### A1. Missing validity check upstream lets bad AST reach a lowering stage

- Signature: crash in SILGen/IRGen/SIL passes on odd code.
- Mechanism: Sema accepted an invalid shape because one effect/substitution/
  availability check was skipped for that combination.
- Fix: add the user-facing diagnostic in Sema; optionally add defensive
  lowering coverage separately. Do not implement the later-stage
  "unimplemented" conversion — that is a symptom of invalid AST.
- Examples: typed-throws SILGen crash (#86463, still open; issue
  discussion: reject in Sema, do not teach `emitThrow` `E2→E1`); embedded existential
  (#91566, merged #91581 — SIL specialization, not IRGen).

### A2. Recovery/reordering logic corrupts argument or token binding

- Signature: cascade of unrelated diagnostics after one small mistake.
- Mechanism: recovery claims bindings greedily before failure bookkeeping.
- Fix: preserve source-order intent locally at the claim site.
- Examples: #86472 argument matching (still open; routing only).
  Interpolation skip #80929 is parse P3, not this archetype.

### A3. Optimization pass violates its own preconditions

- Signature: `-O`-only miscompile/crash; verifier fires after specific pass.
- Mechanism: hoisting/sinking/speculation across guards, weak linkage,
  ownership boundaries.
- Fix: restore the pass's existing general safety check to the missing
  instruction class (sibling already has it). Do not add a symptom-specific
  carve-out (`#available`, weakly-imported, target). Never weaken the
  verifier.
- Examples: #90916 LICM (merged #90945, rejected #90931); #91480 CMO metatype.

### A4. Region/isolation identity lost through wrappers

- Signature: false Sendable errors, missing data-race diagnostics, actor
  hop mistakes.
- Mechanism: closures/partial-applies/temporaries hide value identity;
  Sema and SIL split enforcement by design.
- Fix: propagate capture identity through the wrapper in region analysis or
  adjust Sema classification — decide where the identity actually diverges.
- Examples: #87540, #87503 (both still open — routing only), #85667, #87768.

### A5. New feature lacks one lowering/checking arm

- Signature: crash or "unimplemented" only for one combination of a recent
  feature (typed throws, parameter packs, macros, embedded).
- Mechanism: switch statements elsewhere cover siblings but not the new case.
- Fix: mirror the sibling case; audit all switches on that enum/shape.
- Examples: typed throws × generics × IRGen (#86347 merged #86387: thread
  the mapped in-context error type, do not re-query maximal expansion at
  `emitAsyncReturn`; #87030), back-deployed generic typed throw (#90818).

### A6. Stale state / offset skew in IDE paths

- Signature: editor-only crash or wrong completion; batch compile fine.
- Mechanism: requests run against outdated buffers/ASTs.
- Fix: validate offsets/lifetimes, invalidate caches.
- Examples: #85582 semantic tokens; completion timeouts (#57248, #66785).
  Not this archetype: #85646 missing type completion after `any`/`some`
  (parser/completion context, class T2; still open).

### A7. Serialization boundary drops required information

- Signature: cross-module-only failures; stale-cache symptoms.
- Mechanism: something needed downstream is not recorded (or recorded
  wrongly) in swiftmodule/TBD.
- Fix: serialize the fact; bump format handling carefully both directions.
- Examples: distributed accessor TBD/IRGen mismatch (#85557, issue still
  open; main fix #90287 is SILDeclRef thunk identity, not a TBD list patch —
  review: add `Kind::DistributedThunk`, do not keep `asDistributed()` as a
  boolean on the original decl); autolink metadata (#85441); ObjC block
  swiftmodules (#86003).

### A8. Platform/target-gated path divergence

- Signature: only watchOS/wasm/embedded/Linux/Windows; or only -O; or only
  HOSTTOOLS-skewed builds.
- Mechanism: target-specific representation or runtime service missing.
  For embedded mode, the gap is often in SHARED SIL utilities that expand
  generics/existentials without honoring embedded constraints — not in a
  dedicated embedded file.
- Fix: implement/guard the target branch explicitly.
- Examples: wasm typed-throws async (#89320); Linux Glibc module maps
  (#85427); Windows macro paths (#85958); embedded existential generic
  crash fixed in `lib/SILOptimizer/Utils/Generics.cpp` + test
  `test/embedded/existential-generic-error.swift` (#91566 merged #91581:
  `specializeWitnessMethodInst` must refuse requirements more generic than
  the protocol; do not patch the IRGen `setArgs` assert); Embedded pack
  tuple projection (#89581: use static offsets, not
  `TupleTypeMetadata.Elements` on thin `{vwt,kind}` metadata); -O LICM
  (#90916, class A3).

### A9. Diagnostic machinery fails to produce any message

- Signature: "failed to produce diagnostic for expression" floods.
- Mechanism: solver salvage produces an unexplainable solution; failure
  diagnostic lacks a case.
- Fix: teach CSDiagnostics the case, or prevent the bogus salvage.
- Examples: #59618, #60793, #90258.

### A10. Bridging/interop proves something false

- Signature: unsound casts/conformance via ObjC/C++ bridges.
- Mechanism: bridge path bypasses Swift conformance proof.
- Fix: require real conformance evidence at the cast site.
- Examples: #85111 NSError→Equatable (still open; review confirms the
  NSError bridge is the false proof and flags source-compatibility risk —
  not a local-case "solved" runtime patch); Sendable C++ import (#83695).

## Triage Shortcuts

- Title contains "SIL verification error" → sil-optimization.md class O1.
- Title contains "IRGen" + assert → observation is IRGen (class R1), but
  first ask which pass produced the SIL; #91566 asserted in `GenCall`
  `setArgs` and was fixed in `specializeWitnessMethodInst`.
- "Failed to produce diagnostic" → sema.md class S4.
- "accepts invalid" label → sema.md class S2.
- EXC_BAD_ACCESS in user binary → irgen-runtime.md class R4 (runtime), but
  first rule out miscompile (class O2/R3).
- `[SR-…]` prefix = old Jira migration; still same pipeline rules.
- `triage needed` label means nobody confirmed stage yet — rely on the
  reproducer, not labels.

## Local Corpus Pointers

- 200 harvested plans: `issues/plans-by-search-page/page-01..10/`
- Hand-reviewed mentor guidance index: `issues/guidance/manual-review.md`
- Durable reconciled lessons: `wiki/compiler-understanding.md`
- Completed-case archive: `issues/cases/<n>/README.md`
