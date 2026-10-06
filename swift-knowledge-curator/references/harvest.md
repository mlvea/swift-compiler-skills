# Harvest

Run this check when a family share may have drifted.
Also run it when 50 or more issues have closed since the last pass.
Change a count in `knowledge-base/resolved-issue-patterns.md` only when a family share moves by more than 10%.

```bash
curl -sG "https://api.github.com/search/issues" \
  --data-urlencode "q=repo:swiftlang/swift is:issue is:closed crash in:title" \
  --data-urlencode sort=closed --data-urlencode order=desc \
  --data-urlencode per_page=50 -o data/resolved-issues-<date>/crash.json
```

Repeat the query for assertion, diagnostic, SILGen, IRGen, and sendable.
Also repeat it for the type checker, the parser, completion, and sourcekit.
An unauthenticated search allows about 10 requests in one minute.
Sleep between calls.

Write the JSON under `data/` in the case-notes repository.
Do not write that JSON in this skills repository.
See `swift-compiler-fix-loop/references/case-notes.md`.

For a search-family claim, fetch the pull request that closed the issue.

Also fetch each linked pull request and each superseded pull request.
Do the same for a check of a solved case.
Record the merged pull request and the files that it changed.
Record each `CHANGES_REQUESTED` review on that issue.

An open issue is not solved. A patch in a local case file is not solved.
Name the issue that the old text got wrong.
A second reading of two known cases is not a separate harness.

If a panel sat, compare the chair verdict with those reviews.

- A `CHANGES_REQUESTED` review that the panel missed is a miss in the domain brief. Add a reject-unless line.
- A panel `block` that maintainers approved needs a counterexample. Get that counterexample before you delete the rule.

The procedure and the corpus are in `knowledge-base/expert-panel/scorecard.md`.

```bash
python3 swift-expert-panel/scripts/score_pr.py --corpus
python3 swift-expert-panel/scripts/probe_globs.py
```

`score_pr.py` does not need the swift checkout. `probe_globs.py` does need it.
Pass `--checkout` when a checkout is available. Otherwise copy `paths.example.json` to `paths.json`.

The check workflow makes a sparse checkout of `swiftlang/swift` `main`.
It does this on a push and on a pull request. It runs with `--checkout`.
The weekly schedule does the same run.

GitHub turns that schedule off after 60 days with no commit.
A missing glob is the same class of bug as a removed path such as `test/Module/`.
