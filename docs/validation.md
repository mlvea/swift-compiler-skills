# Validation Record

Everything below was executed on the target machine (Apple Silicon macOS,
Xcode MacOSX26.2.sdk). Dates: 2026-08-25/26. Full narratives live in
`optimization/edit-log.md` (epochs 1–5).

## Triage Skill

Replay gate — 5 solved local cases re-triaged from title/reproducer only:

| Issue | Routed to | Recorded truth |
| --- | --- | --- |
| 86472 | sema / wrong-diagnostic / A2 | CSSimplify argument matching ✓ |
| 87540 | sil-mandatory / false-sendable / A4 | SendNonSendable region fix ✓ |
| 85111 | importer / unsound-cast / A10 | NSError bridging conformance ✓ |
| 85557 | irgen / undefined-symbols / A7 | distributed TBD symbols ✓ |
| 85646 | tooling / completion / A6 | IDE completion ✓ |

Counterexample gate — fresh closed issue #91566 (embedded existential
generic crash): predicted verifier/IRGen; actual fix landed in
`lib/SILOptimizer/Utils/Generics.cpp` with test in `test/embedded/`.
Two documentation gaps found and fixed under gate: shared-SIL-utility
mechanism for embedded bugs, and `test/embedded/` test placement.

Fresh replay #90916 (SIL LICM hoist over weak availability gate) routed
correctly to sil-opts / A3.

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

## Live Patch Under Lit Feedback

A real in-flight fix (SIL debug-value type chains:
`appendTupleFragmentIfValid`) was preserved through a 4-month forward
migration, rebased across upstream rewrites, and then *improved by lit
evidence*: `dead-obj-elim.sil` proved the guard rejected valid
struct-fragment→tuple-fragment chains. The guard now walks the recorded
DIExpr to compute the narrowed running type. This is the curator loop's
thesis demonstrated end-to-end: validation data improved both the patch and
the skills that produced it.
