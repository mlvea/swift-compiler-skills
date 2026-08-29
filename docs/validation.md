# Validation Record

Everything below was executed on the target machine (Apple Silicon macOS,
Xcode MacOSX26.2.sdk). Dates: 2026-08-25/26. Full narratives live in
`optimization/edit-log.md` (epochs 1–5).

## Triage Skill

Replay gate — 5 local cases re-triaged from title/reproducer only
(epoch 2). Epoch 7 review audit: these were *investigations of still-open
issues*, not merged-PR ground truth. Stage routing still holds except
85646 (A6 stale-buffer was wrong; it is T2 missing completion). Fix-shape
claims from those case files are not review-validated.

| Issue | Epoch-2 route | 2026-08-29 status |
| --- | --- | --- |
| 86472 | sema / wrong-diagnostic / A2 | still open; no merged PR |
| 87540 | sil-mandatory / false-sendable / A4 | still open; no merged PR |
| 85111 | importer / unsound-cast / A10 | still open; review flags compat risk |
| 85557 | irgen / undefined-symbols / A7 | still open; main #90287 is SILDeclRef identity |
| 85646 | tooling / completion / A6 | still open; T2 parse-context, not A6 |

Counterexample gate — fresh closed issue #91566 (embedded existential
generic crash): predicted verifier/IRGen; actual fix landed in
`lib/SILOptimizer/Utils/Generics.cpp` with test in `test/embedded/`.
Two documentation gaps found and fixed under gate: shared-SIL-utility
mechanism for embedded bugs, and `test/embedded/` test placement.

Fresh replay #90916 (SIL LICM hoist over weak availability gate) routed
correctly to sil-opts / A3. Epoch 7: the *merged* fix is #90945 (stop
speculative hoist of scoped `load_borrow`); first PR #90931 was rejected
as a weakly-imported special case. Stage was right; documented fix shape
was the rejected patch.

## Environment Contract (execution-gated facts)

All signatures below were reproduced live, then fixed and re-verified:

1. HOSTTOOLS module skew — `module compiled with Swift 6.5 cannot be
   imported by the Swift 6.4 compiler`. Remedy: rebuild stdlib+frontend.
2. swift↔llvm skew, swift too old — `Integer_Width`,
   `maybeAddDependency` arity, missing override symbol at link.
3. swift↔llvm skew, swift too new — `DenseMapInfo::getEmptyKey` removed,
   `Triple::NaCl` removed.
4. Authoritative pairing rule established from
   `swift/utils/update_checkout/update-checkout-config.json`: scheme `main`
   → llvm-project **stable/21.x**. (An earlier inference of "next" was
   falsified by build failures — recorded as a lesson.)
5. Stale tblgen layer — `The class 'SubCommand' is not defined`; fixed by
   rebuilding llvm-tblgen + generated headers before swift.
6. Stale tools / embedded slice — dyld symbol misses in
   lldb-moduleimport-test; embedded-only module version skew. Both have
   verified one-line remedies.

## Toolchain Validation After Forward Migration

swift main @ Aug-2026 + llvm stable/21.x tip + refreshed siblings:

| Check | Result |
| --- | --- |
| `test/DebugInfo` directory | 336/337 passed |
| `Constraints/argument_matching.swift` | pass |
| `Constraints/calls.swift` | pass |
| `SILGen/consume_operator_trivial_value_of_nontrivial_type.swift` | pass |
| rebased fix's own tests (`sroa_mem2reg_tuple.sil`, `dead-obj-elim.sil`) | pass |

The single DebugInfo failure (`modulecache.swift`) asserts clang
module-cache format details against the installed SDK and is unrelated to
any SIL-level change; classified pre-existing/environmental.

## Epoch 8 — issue-local evidence only

User-requested correction: agents must not derive patch correctness from
other issues, archetypes, case files, or wiki lessons. Sweep applied:

- Triage/fix-loop: THIS issue's reducer, stack, and code are the only
  patch evidence. Other issues name files. This issue's own PRs are in
  scope.
- Search families A1–A10 no longer have "Fix:" recipes.
- Playbooks renamed to "what to inspect"; historical worked-example
  patches removed.
- Curator must not write a rule that states the patch for a future,
  different issue.

Held-out: #90916 still routes sil-opts from `-O` + LICM in the title;
#86347 still routes IRGen from `emitAsyncReturn`; #80929 still routes
parse from skip-until recovery. None of those records now include a
copy-this-patch instruction.

## Epoch 9 — leftover analogical recipes

Flag ladder is required when the stack does not settle stage. Search
family comes last and maps issue→stage only (no function names, no
rejected-PR anti-recipes, no root-cause claims for open issues).
Harvested plans/wiki are optional hints after reproduce, not the
diagnosis. Heuristic 9 no longer forbids `#available` / weakly-imported
as a class of check.

## Live Patch Under Lit Feedback

A real in-flight fix (SIL debug-value type chains:
`appendTupleFragmentIfValid`) was preserved through a 4-month forward
migration, rebased across upstream rewrites, and then *improved by lit
evidence*: `dead-obj-elim.sil` proved the guard rejected valid
struct-fragment→tuple-fragment chains. The guard now walks the recorded
DIExpr to compute the narrowed running type. This is the curator loop's
thesis demonstrated end-to-end: validation data improved both the patch and
the skills that produced it.

## Expert panel seating (epoch 9)

`python3 swift-expert-panel/scripts/seat.py` replayed six file maps
from `knowledge-base/expert-panel/roster.md`. All chairs matched:
type-system, sil-optimizer, concurrency, silgen, embedded, irgen-abi.
Workflow `swift-expert-panel` passed `validate_only` (canned host;
not a live panel run).
