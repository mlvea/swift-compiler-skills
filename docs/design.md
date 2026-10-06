# Design

## Problem

Work on the Swift compiler fails in four known ways when no compiler rule guides the edit.

1. The edit assigns the symptom to the wrong pipeline stage.
   The edit then changes the wrong layer.
2. Known environment traps waste hours.
   The traps are repo skew, HOSTTOOLS drift, and stale tablegen outputs.
3. The regression test does not match the layer of the fix.
   CI then disagrees with the local result.
4. Each fix teaches a lesson.
   That lesson disappears with the chat session.

This suite gives each failure its own skill.
The skills share one knowledge base.
The knowledge base records commands that ran.
It records review invariants from specific pull requests.
No issue worked with this suite is a merged pull request in `swiftlang/swift`.
The five open triage cases in `validation.md` have no merged answer to check.

## Architecture

```
swift-compiler-skills/
├── swift-compiler-fix-loop/     orchestrator (default entry)
│   └── references/              case-file checklist, PR/CI notes
├── swift-issue-triage/          stage classifier (not the patch)
├── swift-local-build-test/      build and test commands
│   ├── references/paths.example.json
│   ├── references/paths.json    gitignored, your machine
│   ├── references/environments.md
│   └── scripts/export-env.py    $B $SUFFIX $CFG $SWIFT
├── swift-expert-panel/          clean-context reviewer. Panel is opt-in
│   ├── scripts/seat.py          which briefs to load
│   └── scripts/score_pr.py      regression corpus, not a held-out set
├── swift-issue-explainer/       optional teaching page
├── swift-knowledge-curator/     one checked edit when a fact changed
│   └── references/harvest.md
├── knowledge-base/
│   ├── pipeline-map.md          symptoms, stage, files, tests
│   ├── stage-playbooks/         one playbook per compiler stage
│   ├── regression-test-cookbook.md
│   ├── resolved-issue-patterns.md   search families A1-A10 (files, not patches)
│   ├── sibling-repos.md         llvm, driver, syntax, sourcekit-lsp
│   └── expert-panel/            briefs, seats.json, evolution-gate.md
├── scripts/check_repo.py        prose, links, skill names, briefs
└── optimization/edit-log.md     append-only journal
```

Playbook commands use `$B`, `$LIT`, and `$FE`.
Copy `paths.example.json` to `paths.json`.
Load that file with `export-env.py`.
`export-env.py` takes `$SUFFIX` from the name of the build directory.
A second copy of a home-directory path is a bug.

One fix follows this flow.

```
issue ──▶ stack/flag-ladder stage ──▶ playbook ──▶ plan ──▶ reviewer ──▶ patch
                          └ optional search family (directories only)
                                                                  │
        curator ◀── durable fact ◀── review-on-diff ◀── tests ◀───┘
           │
           └─ checked edits ▶ knowledge-base / SKILL.md files
```

The explainer is an optional page.
The page sits off to the side.
The patch does not wait for that page.

The fast path still starts with triage.
Use the fast path only when the patch is in the function that causes the bug.
That patch must not change what compiles.
Reproduce the bug.
Run `seat.py` with `--stage`.
Do one clean-context review of the diff.

Apply the patch.
Run the tests.

A playbook says where to look.
A seated brief says whether a plan is acceptable.
A seated brief says whether a patch is acceptable.

## The triage model

Identify the stage from signals in strict order.
Use stack frames and assertion text first.
Then use how the reproducer behaves on the flag ladder.
The ladder is `-typecheck`, then `-emit-silgen`, then `-emit-sil` without `-O`, then `-O`, then run.
A failure at `-emit-sil` without `-O` is sil-mandatory.
That set includes region-isolation diagnostics.

Use title keywords and labels last.
Write the output as a fixed-shape record.
Later steps read that record.

Ten search families, A1 through A10, match the failure families.
A search family names extra files to open.
A search family does not predict the patch.
Only this issue shows what to change.
Use its reproducer, its stack, and the code that the reducer reaches.
Other issues, case files, and wiki lessons only hint at which file to open.

A merged or rejected pull request is in scope only when it belongs to this issue.

## How the suite learns

Keep each skill as a directory.
Keep the YAML file visible.
Load `SKILL.md` when the skill triggers.
Load the knowledge base on demand.
Give one real fix attempt one bounded edit.

| Piece | This repo |
| --- | --- |
| State | `SKILL.md` files, `knowledge-base/`, and scripts |
| Rollout | One real fix attempt. The attempt can pass or fail. |
| Signal | Did the reproducer get fixed? Did the tests pass? Did a regression appear? Was time lost? Was a path stale? |
| Update | Change 3 or fewer rules in one epoch. Change 30 or fewer lines in the knowledge base. The budget caps churn. It is not a measured optimum. |
| Accept | A seating edit must keep `score_pr.py --corpus` passing. A brief or playbook edit needs a named counterexample or a command that ran. |
| Never | Do not rewrite a whole playbook because one issue hurt. |
| Rejected edits | Record the edit in the journal. Read it again after two confirming instances. |
| Epochs | An epoch is a finished fix, repeated friction, or 50 or more new closed issues. |

A seating edit must keep `score_pr.py --corpus` passing.
A new triage sentence must name the resolved issue that the old text got wrong.
A command edit must be a command that ran.
A second read of two known cases is not a separate harness.
No script scores a triage corpus yet.

## Expert panel

`seat.py` chooses the chair and up to three other domains from `seats.json`.
The script uses file globs, keywords, and the pipeline stage.
No match reports `unseated`.

The default reviewer is one read-only subagent.
It receives the plan or the diff.
It receives the seated briefs.
It receives the official docs that those briefs name.
It does not receive the author's reasoning.

The reviewer writes a rebuttal of a `block` in another brief.
The reviewer decides that rebuttal.
A `block` in the chair brief is final.
`request-changes` means this.
Apply the named changes.
Review the artifact again.

Do not average ballots.
A multi-agent sitting is opt-in.
No one has compared panel sizes yet.
Nothing here shows that several agents beat one reviewer who reads the same briefs.

`evolution-gate.md` separates a bug fix from a language change.
`score_pr.py --corpus` checks the regression corpus.
After edits to the rules, seating on that corpus is 15/15.
The same person wrote the `expected_chair` labels and the globs.

`--sources-only` is a plan-time report and an upper bound.
It uses the source files of the merged pull request.
A planner has only the files that triage guessed.
The re-check on 2026-10-07 is 12/15.

Title tags on merged pull requests are an independent report.
`score_titles.py` only prints that report.
Put a new pull request in `heldout-corpus.json` before any edit that the pull request motivates.
`--heldout` reports the score and does not fail the process.

## Non-goals

- Do not give generic advice on how to write code.
  Keep the material specific to the Swift compiler.
- A read of the GitHub issue needs the network or a local copy.
  A read of its comments needs the same access.
  A read of a linked pull request needs the same access.
  The patch commands do not need that access.
  A harvest may stay cached under `data/` in the case-notes repo.
- Do not change this suite in silence.
  Record every epoch in the journal, with the evidence.
- Do not use an external skill-file trainer as the production store.
  Make one bounded edit for each fix.
  Check that edit into this repo.
