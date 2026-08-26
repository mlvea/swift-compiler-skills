# Skill Optimization Journal

Append-only. One entry per curator epoch. Never rewrite history; supersede
with a new entry.

## Format

```
## YYYY-MM-DD epoch N (<trigger>)
Evidence: <case paths / issue numbers / command transcripts>
Proposed: <bounded edit summary>
Gate: replay | counterexample | execution — <result>
Accepted/Rejected: <files changed or why refused>
Held-out check: <which solved cases were re-triaged>
```

## 2026-08-25 epoch 1 (suite bootstrap)

Evidence:
- Full environment verification session: lit invocation of
  `test/Constraints/argument_matching.swift` failed with module version
  skew (`Swift 6.5 module vs 6.4 frontend`).
- `ninja swift-stdlib-macosx-arm64 swift-frontend` failed with LLVM API
  mismatch (`Integer_Width` rename commit `53aae6619484` on 2026-05-20;
  `maybeAddDependency` arity change) — swift@`699da1ef` (2026-04-14)
  incompatible with llvm-project@stable/21.x@May-23.
- Harvested 418 closed issues across 10 searches into
  `data/resolved-issues-2026-08/`; family frequencies extracted.

Proposed + Accepted (bootstrap, execution-gated):
- Created suite: triage, local-build-test, knowledge-curator skills;
  knowledge-base with pipeline map, six stage playbooks, test cookbook,
  resolved-issue patterns; upgraded fix-loop orchestrator.
- Rewound llvm-project onto new branch `swift-main-compat-699da1ef`
  @ `0d0fbd53c95d` (reversible; documented in environments.md).
- All commands in build-test skill execution-gated on this machine.

Gate: execution (commands verified live during bootstrap).
Held-out check: n/a (first epoch).

## 2026-08-25 epoch 2 (triage dry-run validation)

Evidence:
- Replay gate: 5 solved local cases re-triaged from titles/reproducers
  (86472→sema/A2, 87540→sil-mandatory/A4, 85111→importer/A10,
  85557→irgen/A7, 85646→tooling/A6) — all routed to their recorded stages.
- Counterexample gate: fresh issue #91566 (embedded existential generic
  crash, closed 2026-08-19) predicted stage "verifier/irgen embedded";
  actual fix `lib/SILOptimizer/Utils/Generics.cpp` + test
  `test/embedded/existential-generic-error.swift`. Two doc gaps found:
  shared-SIL-utility mechanism for embedded bugs; missing test/embedded/
  row. Fresh issue #90916 replayed correctly to sil-opts/A3.

Proposed + Accepted (counterexample-gated):
- `regression-test-cookbook.md`: added Embedded Swift → `test/embedded/`.
- `resolved-issue-patterns.md` A8: recorded shared-utility mechanism +
  #91566/#90916 examples with file pointers.

Rejected: none this epoch.

Held-out check: the 5 replayed cases above still route identically after
the edits (no misrouting introduced).

## 2026-08-25 epoch 3 (environment fix, second attempt after gate failure)

Evidence:
- Epoch-1 remedy (rewind llvm to `stable/21.x`@Apr-14) PASSED compile of
  the two probe objects but FAILED at link:
  `ClangImporterDependencyCollector::maybeAddDependency` symbol not found.
  Root cause of the miss: swift `main` tracks llvm-project **`next`**
  lineage; `stable/21.x` is the release train with different API timing.
  Also ruled out: llvm `main` branch is frozen at 2025-12.
- Correct pairing verified empirically: `next`@`95cd48bf202a` (2026-04-14)
  compiles both probe objects clean.

Proposed + Accepted (execution-gated):
- Repointed local branch `swift-main-compat-699da1ef` to `95cd48bf202a`.
- `environments.md`: documented branch-lineage contract
  (main↔next, release↔stable), the three-symptom signature, the cheap
  negative-probe rule (compile 2–3 previously failing objects before any
  long rebuild), and the zsh `$var:path` brace pitfall when inspecting
  files at a ref.

Lesson recorded: environment remedies must pass BOTH compile and link
gates before being written as fact.

## 2026-08-25 epoch 4 (forward migration; pairing rule corrected twice)

Evidence:
- Epoch-3 pairing (llvm `next`@Apr-14) compiled probe objects but failed
  full build: `Triple::NaCl`, `PunnedPointer::getFromOpaqueValue` missing —
  removed on `next` before mid-March. Exhaustive first-parent scan of
  `next` Feb–May 2026 (8958 commits) found NO commit satisfying swift@Apr-14
  → the old checkout was only ever coherent through cached objects.
- User approved forward migration. Preserved staged SIL debug-info work on
  branch `debug-value-type-chain-fix`@`cca5c934393`; fast-forwarded swift
  main to `a13bb5a43db` (2026-08-25); cherry-picked the fix back
  (`0465de93585`), resolving 3 conflicts while preserving patch intent
  (guarded tuple-fragment appends in InstOptUtils + SILSROA; test file got
  both upstream DOE run and mem2reg variant).
- swift@Aug-25 vs llvm `next`@Aug-25 still failed (`DenseMapInfo::getEmptyKey`
  removed upstream 2026-06-06). AUTHORITATIVE source found:
  `swift/utils/update_checkout/update-checkout-config.json` maps scheme
  `main` → llvm-project **`stable/21.x`**. Repointed to its tip
  (`98631a845ece`); rebuilt tblgen tools + generated headers; frontend
  rebuild then clean.

Proposed + Accepted (execution-gated):
- environments.md rewritten: authoritative pairing rule (read
  update-checkout-config.json, never infer), both-direction failure
  signatures, stale-tblgen signature + regeneration commands, zsh brace
  pitfall.
- Suite README unchanged; no triage/knowledge changes this epoch (compiler-
  content docs unaffected by environment work).

Lesson recorded: when a config file exists that DEFINES repo pairings, read
it before inferring from git archaeology. Cost of inference: ~3 wasted
build cycles (~40 min).

## 2026-08-25 epoch 5 (migration completed; patch improved under test)

Evidence:
- Full forward migration executed (user-approved): swift-syntax/cmark/
  llbuild also required refresh — ASTGen failed on missing
  `Parser.LanguageFeatures` until swift-syntax moved May→Aug. Sibling
  coherence applies to ALL pinned repos, not just llvm.
- Rebased user fix hit 3 conflict classes, each handled differently:
  (1) structural upstream rewrites → port intent into new shape
      (InstOptUtils, SILSROA); (2) API drift → mechanical rename
      (`getOperand()`→`getSingleOperand()` in DebugInfoVerifier);
  (3) dead flags → drop stale RUN line (`-mem2reg` removed by the
      DeadObjectElimination rewrite), keep the hardening NOTE.
- Lit validation caught a REAL defect in the user's guard:
  `dead-obj-elim.sil` regression proved appendTupleFragmentIfValid rejected
  valid chains like `op_fragment:#S.tupleField` + `op_tuple_fragment`
  because it consulted only the root declared type. Fixed by walking the
  recorded DIExpr to compute the narrowed running type (struct fragments via
  VarDecl field type, tuple fragments via recorded tuple operand, deref via
  object type). Both tests now pass; test/DebugInfo 336/337 (remaining one
  is pre-existing modulecache.swift, unrelated to SIL).

Proposed + Accepted (execution-gated):
- environments.md: stale-tool dyld signature + fix; embedded-stdlib skew +
  target; sil-opt symlink fact; pre-existing failure list; validation
  record.
- No triage/knowledge-base changes (compiler content untouched).

Lesson recorded: lit regressions against a patch's OWN changed behavior are
the highest-signal review tool — they caught an over-broad guard that code
review alone would likely have passed ("skip invalid" looked safe until an
existing expectation proved the skip destroyed valid debug info).

## 2026-08-26 epoch 6 (suite relocated to its own repository)

Evidence: user requested the suite live as a standalone repo under
`~/Documents/Github/swift-compiler-skills`, pushed to
`github.com/mlvea/swift-compiler-skills`.

Accepted changes:
- Physical move of all four skills + knowledge-base + optimization journal
  out of `swift-issue-fix-plans/skills/`; wiki keeps pointer docs only.
- All internal absolute references re-pointed; two relative wiki references
  in fix-loop absolutized; stale-reference audit clean (35 abs refs, 0 missing).
- New top-level README + docs/design.md + docs/validation.md for public use.

Held-out check: reference audit script passes from the new root.
