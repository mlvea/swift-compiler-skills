# Panel scorecard

This file is the regression corpus for seating.
The data file is `scorecard-corpus.json`.

```bash
python3 swift-expert-panel/scripts/score_pr.py --corpus
python3 swift-expert-panel/scripts/score_pr.py --sources-only
python3 swift-expert-panel/scripts/score_pr.py --heldout
```

This corpus is not a held-out measure.
It is not a claim that the panel beats a human specialist.
Nothing here shows that several agents beat one reviewer who reads the same briefs.
Tuning used the rows below to add rules and globs.
Four rows are `hit-after-rule`.
One row is `seating-hit-after-glob`.

`#86312` records a seating miss that then gained a glob.
The offline grades follow the known review outcome.
After those edits, seating replay is 15/15.

Plan-time seating passes only the source files.
It passes no `test/` path.
It passes no stage.
It passes no keyword text.
Tests often do not exist when someone writes the plan.
Tuning chose the keyword text.

The re-check on 2026-10-07 is 12/15.
That figure is an upper bound.
The figure uses the source files from the merged pull request.
A planner has only the files that triage guessed.
The same person wrote the `expected_chair` labels and the globs.

| PR | Expected | Source files only |
| --- | --- | --- |
| #84975 | library-evolution | parser-diagnostics. The word `inlinable` in the keyword text seats library-evolution. |
| #91581 | embedded | sil-optimizer. `test/embedded/` chairs embedded. Plan text that names Embedded seats the brief without that test. |
| #73158 | concurrency | generics. The concurrency test seats concurrency. |

One run on 2026-10-07 kept the keyword text and dropped the tests.
That run is 13/15.
`#84975` then matches.
`#91581` seats `embedded`.
The chair stays `sil-optimizer`.

With the corpus stage added, that chair matches.
That cut is 14/15.
`#73158` remains the chair miss.

## Held-out set

`heldout-corpus.json` starts empty.
Add a pull request only after you score seating.
Add it before you edit a brief or a glob because of that pull request.
Do not add a rule in the same epoch as the first score.
If you later tune on a case, move it to `scorecard-corpus.json`.
Say so in the edit log.

`--heldout` scores that file.
`--heldout` exits 0 on a miss.
A miss is not a reason to edit the globs.
Zero cases is an honest empty set.
Zero cases is not a pass of the regression corpus.

Title tags on merged pull requests are the independent set.
The authors of those titles did not write the globs.
`score_titles.py` prints three match rates.
The script exits 0.
Run the script on a local checkout.
CI uses a depth-1 sparse clone of swift.

That clone cannot walk a month of history.

```bash
python3 swift-expert-panel/scripts/score_titles.py \
  --checkout <swiftlang/swift> --since 2026-09-06 --until 2026-10-06
```

The recorded run of those flags printed 121/165, 91/165, and 104/165.
Git keeps a commit that is newer than `--since`.
Git keeps a commit that is older than `--until`.
That window ends at the start of 2026-10-06.
The move of `github/main` to `e9581097859` on 2026-10-07 added no first-parent merge in the window.
No one ran `score_titles.py` again for that move.

The rates from that run still stand.
The script counted 359 merge commits that have a title in the body.
Of those commits, 165 matched the tag map.
The map sends `[Sema]` to one domain, type-system.
The map sends `driver` to serialization.
The map sends `diagnostics` to parser-diagnostics.

The map sends `wasi` to embedded.
The set is wider than a hand list of about 50 tags.

## How to score a case

1. Take the first diff that received `CHANGES_REQUESTED`.
   If that diff does not exist, take the rejected pull request.
   Also take the merged diff.
2. Run `seat.py --stage <triage-stage> --text-file <PR body> -- <files>`.
3. Apply the seated briefs offline and fail-closed to that first diff.
   Expect `block` or `request-changes`.
   The verdict must name the same invariant as the review.
   Then apply the briefs to the merged diff.
   Expect `approve`, or `request-changes` only for leftover tests or wording.
4. Record the row.
   Put a miss that you fix in the same epoch into the regression corpus.
   Do not put that miss into the held-out set.
   Before you delete a rule, get a counterexample.
   Do that when a merged pull request got a false `block`.

Do not use an open issue as ground truth.
Do not name a reviewer in a brief.
Cite the pull request number and the invariant.

## Results (2026-08-30)

| PR | Chair (replay) | First-diff expected | Merged expected | Offline ballot | Lesson |
| --- | --- | --- | --- | --- | --- |
| #90931 (rejected) / #90945 | sil-optimizer | `block` weakly-imported `load_borrow` guard | `approve` scoped-inst hoist | **hit** | Already in sil-optimizer Reject unless. |
| #81054 | clang-importer | `request-changes` InterfaceTypeRequest / TypeRepr / missing async tests | `approve` `isRepresentableInLanguage` | **hit** | Already in clang-importer Protects + PR tests. |
| #84975 | library-evolution | `request-changes` hardcoded inlinable attr | `approve` `getFragileFunctionKind` | **hit** | Seating: `TypeCheckStmt.cpp` + `inlinable` keyword. |
| #74641 | sil-optimizer | `request-changes` disable AST mutation for all CMO | `approve` package-CMO-only skip | **hit** | Tightened Reject unless: aggressive CMO still mutates AST. |
| #86573 | clang-importer | - | `approve` suppress Copyable | **hit** | Already in clang-importer PR review. |
| #91581 (issue #91566) | embedded | - | `approve` shared `Generics.cpp` | **hit-after-rule** | Added: do not specialize `witness_method` when the requirement is ABI-more-generic than the protocol. |
| #77522 | clang-importer | `request-changes` if process-global FRT cache | `approve` request evaluator | **hit** | Already: no process-global caches. |
| #86312 | concurrency | `request-changes` until RBI model matches | isolation-info as concurrency | **seating-miss-before-glob** | `SILIsolationInfo*` is concurrency primary, not a SILBuilder drive-by. |
| #85644 | sil-optimizer | `request-changes` until shared utility / convention | embedded witness + IRGen | **partial** | Review threads exist. The invariant is not fully extracted. Seating is correct. The optimizer chairs, and `embedded` sits on `test/embedded/`. |
| #64215 | irgen-abi | hide noncopyable metadata from old runtimes | `approve` separate section | **hit-after-rule** | `RuntimeResolvableTypes2` / extra metadata section. |
| #72416 | distributed | thunk/getter mangling | seating + mangling rule | **seating-hit-after-glob** | `DistributedDecl.cpp` primary. |
| #73158 | concurrency | `@preconcurrency` override sendability | `approve` strip then match | **hit-after-rule** | Not a hard type mismatch that also bans mutable overrides. |
| #75745 | library-evolution | package UFI from interface is public | `approve` | **hit** | `accessibility_package*` primary. |
| #86148 | irgen-abi | skip explosion schema on huge types | `approve` keep indirect | **hit-after-rule** | `IsVeryLargeType`. |

The score is 8 hit, 4 hit-after-rule, 1 seating glob fix, 1 seating-hit-after-glob, and 1 partial.
Corpus seating is 15/15.
No merged diff got a false `block`.

## Adding a case

Put a case that you will tune into `scorecard-corpus.json`.
Give it `files`, `stage`, `text`, `expected_chair`, and `review_invariant`.
Re-run `--corpus`.
Then fill the table.

Put a case that you will not tune into `heldout-corpus.json` first.
Re-run `--heldout` before you edit a brief or a glob.
Score a new pull request before you change the suite because of that pull request.
