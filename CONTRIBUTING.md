# Contributing

## Prose

Apply these rules in the README, the docs, the skills, the knowledge base, and other writing.

- Do not write a home-directory path.
  Put checkouts only in `swift-local-build-test/references/paths.json`.
  Git ignores that file.
  Copy `paths.example.json`.
  In other files, name the checkout `swiftlang/swift`.
  Use `$B`, `$LIT`, and `$FE` for a build path.
- Do not use a U+2014 dash or a U+2013 dash.
  Use a period, a comma, a colon, or a hyphen.
- Do not use filler from the list in `scripts/check-doc-prose.py`.
  The filename `evolution-gate.md` is allowed.
  The script allows a target compound, a flag compound, and a feature compound.
  The journal field is `Check:`.

## Checks

The Python scripts target Python 3.9 or newer.
The check workflow is configured for Python 3.9 and Python 3.12.

```bash
python3 scripts/check_repo.py
python3 -m unittest discover -s tests -v
python3 swift-expert-panel/scripts/score_pr.py --corpus
python3 swift-expert-panel/scripts/score_pr.py --sources-only
python3 swift-expert-panel/scripts/score_pr.py --heldout
```

`--corpus` must pass.
`--sources-only` is the plan-time report.
`--sources-only` exits 0.
The test checks a minimum ratio.
The test does not freeze the miss list.

`--heldout` scores `heldout-corpus.json`.
`--heldout` exits 0 on a miss.

Run the next commands against a swift checkout.
Use `--checkout` or `paths.json`.

```bash
python3 swift-expert-panel/scripts/probe_globs.py --checkout <swift-checkout>
python3 swift-expert-panel/scripts/score_titles.py --checkout <swift-checkout>
```

Push CI and pull-request CI run the probe on a sparse checkout of `swiftlang/swift` `main`.
The weekly schedule runs that probe too.
GitHub stops a schedule after 60 days with no commit.
A later commit does not start that schedule again.
The push and pull-request job is the durable glob check.

Keep `score_titles.py` local.
The CI clone has depth 1.

## What a change may do

Keep each entry skill short.
Put long material in the knowledge base or in that skill's `references/`.

A new triage claim must re-route cases that are already solved.
In that claim, explain at least one case that the current docs get wrong.

Read the edit budgets in `swift-knowledge-curator/SKILL.md`.

Do not weaken a check to silence a failure.
