# Checks that ran

This page records checks from one setup.
The machine is macOS arm64.
The SDK is Xcode's MacOSX26.2.sdk.
The compiler is swift `main` as of August 2026.
The change log is [`optimization/edit-log.md`](../optimization/edit-log.md).
It starts with this publication.

No merged pull request in `swiftlang/swift` is recorded for an issue that this suite worked.
The five open issues below have no merged answer.
On 2026-10-07, all five issues were still open.
The closed-issue checks are misses.
The suite then put those misses into the docs.
Seating on the regression corpus is measured.

Multi-agent review is not measured.

## The toolchain

The August 2026 pin paired swift `main` with llvm `stable/21.x`.
That row is in [`environments.md`](../swift-local-build-test/references/environments.md).
The pairing is the `llvm-project` value under `branch-schemes.main.repos`.
That value is in [`update-checkout-config.json`](https://github.com/swiftlang/swift/blob/main/utils/update_checkout/update-checkout-config.json).
On `github/main`, fetched on 2026-10-07 at `e9581097859`, that value is `stable/23.x`.
An earlier idea, that `main` needed llvm `next`, failed at link time on the August setup.

The August pin produced the failure signatures.
The table below comes from that same pin.
No later run repeated those signatures on `stable/23.x`.

After the forward migration, these checks ran.

| Check | Result |
| --- | --- |
| `test/DebugInfo` | 336/337 passed |
| `Constraints/argument_matching.swift` | pass |
| `Constraints/calls.swift` | pass |
| `SILGen/consume_operator_trivial_value_of_nontrivial_type.swift` | pass |
| this fix's own tests (`sroa_mem2reg_tuple.sil`, `dead-obj-elim.sil`) | pass |

The one DebugInfo miss is `modulecache.swift`.
The test asserts the clang module-cache format against the installed SDK.
The failure is not a SIL bug.
That test already failed before this work.

`appendTupleFragmentIfValid` is an in-flight fix for a SIL debug value.
The fix survived a four-month rebase.
Lit then made the fix better.
The fix is not a merged pull request in `swiftlang/swift`.
`dead-obj-elim.sil` showed that the guard rejected valid chains.
Those chains go from a struct fragment to a tuple fragment.

The guard now walks the recorded DIExpr.
One test improved that patch.
The case is one example, not a measure of the loop.

## Environment failures

Each failure below happened on a live run.
A follow-up edit fixed each failure.
Each check ran again.

1. The fault is HOSTTOOLS module skew.
   The compiler reports `module compiled with Swift 6.5 cannot be imported by the Swift 6.4 compiler`.
   Rebuild the stdlib.
   Rebuild the frontend.
2. Swift was too old for the llvm `next` beside it.
   The signs are `Integer_Width`, the arity of `maybeAddDependency`, and a missing override at link time.
3. Swift was too new for that llvm.
   That llvm build did not provide `DenseMapInfo::getEmptyKey`.
   That llvm build did not provide `Triple::NaCl`.
4. Tablegen output was stale.
   llvm-tblgen reports `The class 'SubCommand' is not defined`.
   Rebuild llvm-tblgen and the generated headers.
   Do that rebuild before you rebuild swift.
5. Tools were stale, or the rebuild covered only the embedded slice.
   `lldb-moduleimport-test` shows dyld misses.
   A partial tree rebuild causes module-version skew.
   A later run verified the one-line rebuild for both faults.

The signatures are in the [environment skill](../swift-local-build-test/SKILL.md).

## Five local cases, then GitHub

The first routes used only the title and the reproducer.
The five issues were still open.
They were not merged work.
No merged patch can check those routes.
A later pass read the closing pull requests.
That pass also read the `CHANGES_REQUESTED` reviews.

That later read is the ground truth.
A local case file is not ground truth.

| Issue | First route | What GitHub showed |
| --- | --- | --- |
| [#86472](https://github.com/swiftlang/swift/issues/86472) | sema, A2 | Still open. No merged pull request. |
| [#87540](https://github.com/swiftlang/swift/issues/87540) | sil-mandatory, A4 | Still open. No merged pull request. |
| [#85111](https://github.com/swiftlang/swift/issues/85111) | importer, A10 | Still open. The review flags a compat risk. |
| [#85557](https://github.com/swiftlang/swift/issues/85557) | irgen, A7 | Still open. [#90287](https://github.com/swiftlang/swift/pull/90287) is `SILDeclRef` identity, not a TBD-list hole. |
| [#85646](https://github.com/swiftlang/swift/issues/85646) | tooling, A6 | Still open. The gap is missing completion (T2), not a stale buffer. |

Closed issues used as a check:

- [#91566](https://github.com/swiftlang/swift/issues/91566) is an embedded crash on an existential generic.
  The first guess was the verifier or IRGen.
  The landing patch is [#91581](https://github.com/swiftlang/swift/pull/91581).
  The patch is in `lib/SILOptimizer/Utils/Generics.cpp`.
  The test is in `test/embedded/`.
  The crash site was IRGen `setArgs`, and that site is not where you patch.
- [#90916](https://github.com/swiftlang/swift/issues/90916) is LICM over a weak availability check.
  The stage was sil-opts.
  Review rejected the first pull request, [#90931](https://github.com/swiftlang/swift/pull/90931).
  The merge is [#90945](https://github.com/swiftlang/swift/pull/90945).
  The merge stops a speculative hoist of a scoped `load_borrow`.
  The stage was right, and the documented fix shape was the rejected patch.
- [#86347](https://github.com/swiftlang/swift/issues/86347) landed as [#86387](https://github.com/swiftlang/swift/pull/86387).
  The first approved commit did not compile.
  The real change threads the in-context typed-error type into `emitAsyncReturn`.
- An early note put [#80929](https://github.com/swiftlang/swift/issues/80929) under A2 by mistake.
  The issue is parse.
  The sibling issues are [#80927](https://github.com/swiftlang/swift/issues/80927) and [#80928](https://github.com/swiftlang/swift/issues/80928).
  The author rejected a `parseExprPrimary` one-off.
- [#89581](https://github.com/swiftlang/swift/issues/89581) is embedded pack IRGen.
  Use static tuple offsets.
  Do not use thin-metadata `.Elements`.
  The failure is a SIGSEGV at `-Onone`.
  The crash looks `-O`-only because unrolling hides the query.

## Rules from this evidence

Do not call a command a fact until that command has run here.

A new triage claim must re-route cases that are already solved.
Show at least one case that the current docs get wrong.

Only this issue can show that a patch is correct.
Use its reducer, its stack, its thread, and its pull requests.
A similar issue may name a file.
An archetype, a case file, or a wiki lesson may name a file.
None of those items is the patch.

Search families A1 through A10 name directories to open.
A family does not name the function to change.
A family does not give an anti-recipe from a rejected pull request.
A family does not diagnose an open issue.

If the stack does not settle the stage, run the flag ladder.
Do not skip the flag ladder.

The crash site is not the fix site.
Restore the check that the producing pass already has.
Do not encode the source symptom.

A worked example needs a merged pull request.
Record `CHANGES_REQUESTED` as a change that you must not copy.
Do not record that review as the recipe.

## Expert panel

`seat.py` replayed the file maps in [`roster.md`](../knowledge-base/expert-panel/roster.md).
These chairs matched: type-system, sil-optimizer, concurrency, silgen, embedded, and irgen-abi.
Later rows matched too.
Those chairs are ownership, debug-info, generics, and macros.

The [scorecard](../knowledge-base/expert-panel/scorecard.md) lists 15 merged pull requests.
Each request has a rejected first patch or a `CHANGES_REQUESTED` review.
The scorecard is a regression corpus.
Misses in that corpus caused edits to rules and globs.
The offline grades follow the known review outcome.
The same person wrote the `expected_chair` labels and the globs.

After those edits, seating is 15/15.
Plan-time seating uses only source files, and the result is 12/15.
The 12/15 figure is an upper bound.
It uses source files from the merged pull request.
A planner has only the files that triage guessed.

Title tags on merged pull requests are a separate report.
The script is `score_titles.py`.
The script prints the rates and exits 0.
`heldout-corpus.json` stays empty until a pull request is scored before any edit that it motivates.
`--heldout` does not fail the process.

The corpus does not prove that the review beats a human specialist.
Nothing here shows that several agents beat one reviewer who reads the same briefs.

`probe_globs.py` checks seating globs on a swift checkout.
It also checks the paths in `official-docs.md`.
On 2026-10-07 the command used `--checkout` on a sparse checkout.
That checkout was `github/main` at `e9581097859`.
The command printed `OK 223 globs`.
The same command checks the 11 official-doc paths.

A missing glob is the same class of bug as a stale `test/Module/` path.

## Where to look next

The change log starts with this publication.
Read the [environment skill](../swift-local-build-test/SKILL.md) for the commands and the failure signatures.
Read the [scorecard](../knowledge-base/expert-panel/scorecard.md) for the 15 pull requests.
