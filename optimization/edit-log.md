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

## 2026-08-29 epoch 7 (PR-review audit of 10 load-bearing precedents)

Evidence: GitHub issue + closing/superseded PRs + reviews for the 10
highest-influence examples (86472, 87540, 85111, 85557, 85646, 91566,
90916, 86463, 80929, 86347).

Findings:
- 6/10 still open with no merged PR (86472, 87540, 85111, 85646, 86463,
  85557). Epoch-2 replay used local case files as "solved" ground truth.
- #90916: CHANGES_REQUESTED on #90931 ("wrong fix"); merged
  #90945 restores speculative-hoist check for scoped insts. Docs had
  described the rejected weakly-imported/`#available` special case.
- #91566: merged #91581 in `specializeWitnessMethodInst`; crash is IRGen
  `setArgs` — that is the wrong patch site (epoch-2 already caught stage,
  not the anti-pattern).
- #86347: merged #86387; first approved commit did not compile; real fix
  threads in-context typed-error type into `emitAsyncReturn`.
- #80929: parse P3, actually #80928 for sibling #80927; author rejected a
  `parseExprPrimary` one-off. Was miscited under A2.
- #85646: T2 missing completion, not A6 stale-buffer.
- #85557: #90287 review: `SILDeclRef::Kind::DistributedThunk`, not a TBD
  list hole. #85111 review: mechanism right, compatibility risk unstated.
- #86463: issue discussion confirms Sema reject; do not implement SILGen E2→E1.

Proposed + Accepted (counterexample-gated on #90916 rejected-PR vs merged
PR, and #85646 A6 misroute):
- Rule: crash site ≠ fix site; restore the producing pass's existing
  general check, do not encode the source symptom (pipeline-map #9, A3).
- Rule: worked examples need a merged PR; record CHANGES_REQUESTED as
  anti-patterns (curator harvest + fix-loop heuristic).
- Factual: 85646 T2 not A6; 80929 parse not A2; 90916/91566/86347/85557/
  86463/85111 examples rewritten from review evidence.

Rejected: mining all 418 harvested issues for PR comments. Most PRs are
LGTM/CI; signal is `CHANGES_REQUESTED` on first PRs and maintainer issue
comments. Open issues have no review to check.

Held-out check: #90916 still sil-opts/A3 (fix shape corrected); #86347
still IRGen/A5; #80929 now parse P3 not A2; #85646 now T2 not A6. Open
cases 86472/87540 keep stage routing only.

Line budget: exceeded the 30-line cap because existing examples were
factually wrong (corrections, not speculative growth).

## 2026-08-29 epoch 8 (issue-local evidence; user-requested)

Evidence: epoch-7 review showed the suite used other issues' "canonical
fix shapes" (including open local case files) as if they were the patch
for a new issue. User: agent must not derive fix accuracy except from
the issue itself.

Proposed + Accepted (user-requested; supersedes the 30-line cap):
- Rule: THIS issue's reducer, stack, thread, and PRs are the only
  evidence of a correct patch. Similar issues / archetypes / case files /
  wiki lessons are file-search hints.
- Rewrote triage, fix-loop, design, patterns (dropped "Fix:" recipes),
  pipeline-map heuristics, all playbooks, curator harvest, README
  principle 7.

Rejected: keeping A1–A10 as patch predictors with "do not copy" nits
appended. That still moves the agent toward a historical shape.

Held-out check: #90916 → sil-opts from THIS title/`-O` (no LICM recipe);
#86347 → IRGen from THIS stack `emitAsyncReturn` (no emitAsyncReturn
plumbing recipe); #80929 → parse from THIS skip-following-expr symptom
(no parseListItem recipe).

## 2026-08-29 epoch 9 (flag ladder required; maps are stage-only)

Evidence: leftover wrong-paths after epoch 8. Search-family Map lines
still named other issues' patches (`Generics.cpp`, SILDeclRef kind,
#90945 vs #90931, #85646 "is T2"). Flag ladder was optional, so stage
could be guessed from titles/families. Harvested plans were loaded as
durable memory for THIS issue. Heuristic 9 forbade `#available` /
weakly-imported / embedded as the missing check (a #90916 rule applied
to future bugs). G1 forbade implementing "unimplemented" conversions
(#86463).

Proposed + Accepted:
- Triage: flag ladder is required when the stack does not settle
  stage; search family comes last and names directories only.
- Fix-loop: GitHub issue + this issue's PRs first; harvested plans /
  wiki / other case files are optional hints after reproduce.
- Patterns: Map lines are `issue + stage` only (no function, no
  rejected-PR anti-recipe, no diagnosis of open issues).
- Heuristic 9 / G1 / R2 / A7: dropped other-issue patch forbids.

Held-out: #90916 still sil-opts from THIS `-O` + pass name; #91566
stage from THIS stack/flag ladder (not from A8 naming Generics.cpp);
#85646 stage from THIS editor-only symptom (family A6 files to open,
no T2 root-cause claim).

## 2026-08-29 epoch 8 (issue 89581 Embedded pack IRGen)

Evidence: `issues/cases/issue-89581/README.md`; 6.3.2 stack
`emitTypeMetadataRef` / `bindOpenedElementArchetypesAtIndex`; current
main `-Onone` SIGSEGV vs `-O` success; IR GEP of `%swift.tuple_type.Elements`
on `$eSb_SSSitMf` which is only `{vwt, kind}`.

Proposed + Accepted (execution-gated: original binary rc 139 → 0;
`test/embedded/parameter-packs.swift` fail-then-pass; neighbors
`variadic_generics.sil` and `accessors.swift` pass):
- A8 example: #89581 static tuple offsets, not thin-metadata `.Elements`.
- irgen-runtime R4: 89581 as `-Onone` Embedded pack SIGSEGV that looks
  `-O`-only because unrolling hides the query.

Held-out check: #91566 remains SIL specialization / A8; #89581 is IRGen
A8 (layout), not a missing Sema diagnostic.

Rejected: unrolling pack loops in mandatory Embedded SIL as the first
fix. Correct but larger; static offsets restore the IRGen invariant
directly.

## 2026-08-29 epoch 9 (expert-panel bootstrap)

Evidence:
- Review: #90931 CHANGES_REQUESTED vs merged #90945; #81054 ObjC
  representability; process.md evolution scope; SE-0414 / commonly_proposed.md;
  forums RBI + FRT + OSSA threads.
- Compiler tree layout (`lib/Sema`, `lib/SILGen`, `lib/IRGen`, …) and
  pipeline-map stages.

Proposed + Accepted (bootstrap, execution-gated seating replay):
- New skill `swift-expert-panel` + `knowledge-base/expert-panel/`
  (14 core seats, 4 conditional).
- `seat.py` deterministic seating; replay examples in `roster.md`
  all returned the expected chair.
- Workflow `swift-expert-panel` smoke-checked (canned-host path).
- Fix-loop gates: panel on plan (step 4) and PR (step 8).
- Curator owns domain briefs; seating-table edits re-run roster
  examples.

Gate: execution (`seat.py` replay OK) + workflow `validate_only`.
Held-out check: six roster chairs unchanged after the neighbor-stage
tweak (stage-only domains no longer flood the panel).

Rejected: seating every domain that shares a pipeline stage. That
produced 4-seat panels on a single CSSimplify.cpp edit.

## 2026-08-29 epoch 10 (panel brief path and invariant corrections)

Evidence: swiftlang/swift main tree listing (`test/` has
`ModuleInterface/` and `AutoDiff/`, not `Module/` or
`validation-test/AutoDiff/`; `test/SIL/OwnershipVerifier/`;
`docs/SIL/`; wasm products under
`utils/swift_build_support/swift_build_support/products/`);
SE-0352 vs SE-0346/0353; SE-0430 implemented as `sending`;
`docs/SIL/Ownership.md`, `docs/LibraryEvolution.rst`,
`docs/ABI/TypeMetadata.rst`, `docs/HowToUpdateDebugInfo.md`,
SE-0176.

Proposed + Accepted (execution-gated GitHub tree listing + seating
replay):
- Stale test/doc globs in briefs, `seats.json`, pipeline-map,
  cookbook, cross-cutting playbook.
- SE numbering in generics/concurrency; `sending` not `transferring`.
- Specialist defaults: OSSA exactly-once lifetime-ending uses,
  exclusivity, metadata identity, LibraryEvolution closed-world ABI,
  debug salvage/undef.
- Conditional sit/abstain aligned with primary-file seating.

Gate: execution (paths exist on main) + replay (six roster chairs
unchanged).
Held-out: same six `seat.py` chairs as epoch 9.

Rejected: claiming any seat is now stronger than a human specialist.
This epoch only removes false paths and adds documented invariants.

## 2026-08-29 epoch 11 (specialist-bar panel rewrite)

Evidence: local swift docs `docs/TypeChecker.md` (subtype not
transitive; `ConformsTo` stricter than `X < any P`; solution
application cannot fail), `docs/SIL/Ownership.md` (lexical lifetimes,
deinit barriers, guaranteed interior pointers),
`docs/SIL/SILMemoryAccess.md` (SE-0176 access markers),
`docs/ABI/TypeMetadata.rst` (complete vs abstract; never backtrack),
`docs/LibraryEvolution.rst` (closed-world; `@frozen` add/remove
forbidden; ABI-public defaults are `@_alwaysEmitIntoClient`),
`docs/HowToUpdateDebugInfo.md` (never speculate; salvage on delete).
Seating mismatches: `docs/SIL/` was silgen-primary (stole
`Ownership.md`); `test/Generics/inverse*` was ownership-primary
(stole signature-only inverse tests); `DWARFImporter*` vs
`clang-importer`; driver-primary serialization without abstain.

Proposed + Accepted:
- Fail-closed specialist bar in `swift-expert-panel/SKILL.md`,
  `chair-protocol.md`, `ballot.md`, and workflow prompts: named
  `Protects` / `Reject unless` violations are `block` unless the
  artifact cites the exception in the same official doc.
- Remaining closed-world invariants encoded in domain briefs.
- All 18 briefs now have Protects / Plan review / PR review /
  Reject unless / Evolution / Forum / Abstain (conditionals no longer
  merge Plan/PR).
- `seats.json`: silgen primary is specific `docs/SIL/*.md` files;
  ownership owns `Ownership.md` + `SILMemoryAccess.md`; inverse tests
  chair as generics; debug-info neighbor `clang-importer`; ARC SIL
  docs to sil-optimizer.

Gate: execution (`python3 -m json.tool seats.json`; workflow
`swift-expert-panel` `validate_only` canned-host path passed) +
replay (`seat.py` on nine roster rows: original six chairs unchanged,
plus Ownership.md → ownership, DWARFImporter.cpp → debug-info,
`test/Generics/inverse.swift` → generics). Extra: Types.md → silgen,
Casting.cpp under `stdlib/public/runtime/` → runtime not stdlib.

Held-out: original six roster chairs identical to epochs 9–10.

Rejected: a measured claim that these seats outperform a human
specialist. The bar is fail-closed application of documented
invariants that a hurried human pass skips, not a SkillOpt win in
this domain.

## 2026-08-30 epoch 12 (Horizon 1: scorecard, producing-pass, paths)

Evidence: merged PRs with `CHANGES_REQUESTED` or a rejected first PR
(#90931/#90945, #81054, #84975, #74641, #86573, #91581/#91566,
#77522, #86312, #85644); in-tree `docs/DebuggingTheCompiler.md`;
execution of `$B/bin/sil-opt -O --sil-print-pass-name` and
`--sil-opt-pass-count=5` on this machine.

Proposed + Accepted:
- Panel scorecard: `knowledge-base/expert-panel/scorecard.md` +
  `scorecard-corpus.json` + `scripts/score_pr.py`. Offline seating
  10/10 chairs match. Ballot: 7 hit, 1 hit-after-rule, 1 seating
  glob fix, 1 partial (review invariant not fully extracted).
- Seating from misses: `TypeCheckDeclObjC.cpp` clang-importer
  primary; `SILIsolationInfo*` concurrency primary;
  `TypeCheckStmt.cpp` + `inlinable` keyword library-evolution.
- Briefs: PackageCMO skip is package-CMO-only (#74641); Embedded
  `witness_method` ABI-more-generic (#91581).
- Producing-pass cookbook (`stage-playbooks/producing-pass.md`);
  pipeline-map heuristic 9 points at it.
- Path contract: `swift-local-build-test/references/paths.json`.
  Triage/fix-loop no longer point at a stale absolute KB path.
- Panel loads cited official docs from `swift_checkout`.

Gate: execution (sil-opt pass-name + pass-count) + replay (nine
roster chairs unchanged; corpus 10/10).
Held-out: original six roster chairs identical to epochs 9–11.

Rejected: treating this 10-case scorecard as proof the panel is
better than a human specialist. It is a start of measurement.
