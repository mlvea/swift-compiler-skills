# Panel scorecard

Held-out measure of whether the specialist bar matches real review.
Corpus: `scorecard-corpus.json`. Seating replay:
`python3 swift-expert-panel/scripts/score_pr.py --corpus`.

This is **not** a claim that the panel outperforms a human specialist.
It records hit / miss / seating-miss against merged PRs that had
`CHANGES_REQUESTED` or a rejected first PR. Scorecard rows are **`D_tr`**.
Specialist numbers use locked `D_test` only (`docs/eval-protocol.md`).

## How to score a case

1. Take the **first** diff that received `CHANGES_REQUESTED` (or the
   rejected PR), and the **merged** diff.
2. `seat.py --stage <triage-stage> --text-file <PR body> -- <files>`.
3. Offline, apply the seated briefs fail-closed to that first diff.
   Expected: `block` or `request-changes` naming the same invariant as
   the review. Then apply them to the merged diff: `approve` (or
   `request-changes` only for leftover tests/wording).
4. Record in the table. A miss writes one `Reject unless` (or a seating
   glob) same epoch. A false `block` on a merged PR needs a
   counterexample before deleting the rule.

Do not use open issues as ground truth. Do not name reviewers in
briefs; cite the PR number and the invariant.

## Results (2026-08-30)

| PR | Chair (replay) | First-diff expected | Merged expected | Offline ballot | Lesson |
| --- | --- | --- | --- | --- | --- |
| #90931 (rejected) / #90945 | sil-optimizer | `block` weakly-imported `load_borrow` guard | `approve` scoped-inst hoist | **hit** | Already in sil-optimizer Reject unless. |
| #81054 | clang-importer | `request-changes` InterfaceTypeRequest / TypeRepr / missing async tests | `approve` `isRepresentableInLanguage` | **hit** | Already in clang-importer Protects + PR tests. |
| #84975 | library-evolution | `request-changes` hardcoded inlinable attr | `approve` `getFragileFunctionKind` | **hit** | Seating: `TypeCheckStmt.cpp` + `inlinable` keyword. |
| #74641 | sil-optimizer | `request-changes` disable AST mutation for all CMO | `approve` package-CMO-only skip | **hit** | Tightened Reject unless: aggressive CMO still mutates AST. |
| #86573 | clang-importer | — | `approve` suppress Copyable | **hit** | Already in clang-importer PR review. |
| #91581 (issue #91566) | embedded | — | `approve` shared `Generics.cpp` | **hit-after-rule** | Added: do not specialize `witness_method` when the requirement is ABI-more-generic than the protocol. |
| #77522 | clang-importer | `request-changes` if process-global FRT cache | `approve` request evaluator | **hit** | Already: no process-global caches. |
| #86312 | concurrency | `request-changes` until RBI model matches | isolation-info as concurrency | **seating-miss-before-glob** | `SILIsolationInfo*` is concurrency primary, not a SILBuilder drive-by. |
| #85644 | sil-optimizer | `request-changes` until shared utility / convention | embedded witness + IRGen | **partial** | Review threads exist; invariant not fully extracted. Seating OK (optimizer chairs, embedded sits on `test/embedded/`). |
| #64215 | irgen-abi | hide noncopyable metadata from old runtimes | `approve` separate section | **hit-after-rule** | `RuntimeResolvableTypes2` / extra metadata section. |
| #72416 | distributed | thunk/getter mangling | seating + mangling rule | **seating-hit-after-glob** | `DistributedDecl.cpp` primary. |
| #73158 | concurrency | `@preconcurrency` override sendability | `approve` strip then match | **hit-after-rule** | Not a hard type mismatch that also bans mutable overrides. |
| #75745 | library-evolution | package UFI from interface is public | `approve` | **hit** | `accessibility_package*` primary. |
| #86148 | irgen-abi | skip explosion schema on huge types | `approve` keep indirect | **hit-after-rule** | `IsVeryLargeType`. |

**Score:** 8 hit, 4 hit-after-rule, 1 seating glob fix, 1 seating-hit-after-glob, 1 partial. Corpus seating **15/15**. No false block on a merged diff.

## Adding a case

Append to `scorecard-corpus.json` with `files`, `stage`, `text`,
`expected_chair`, `review_invariant`. Re-run `--corpus`. Then fill the
table row. Calendar trigger: same as curator harvest (≥50 closed
issues) or any panel miss vs a landed `CHANGES_REQUESTED`.
