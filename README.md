# swift-compiler-skills

<p align="center">
  <img src="docs/suite-overview.svg" alt="The flow is triage, locate, plan, an optional page, patch, and a pull request. Notes and the curator are optional. seat.py selects a chair brief and up to three briefs. The reviewer returns approve, request-changes, or block." width="100%">
</p>

These agent skills help you fix bugs in the Swift compiler
([`swiftlang/swift`](https://github.com/swiftlang/swift)).

This project is not affiliated with Apple or the Swift project.

## Status

No change from this suite is a merged pull request in `swiftlang/swift`.

The regression corpus has 15 merged pull requests.
After the seat rules were edited, all 15 chairs match.
The same person wrote the chair labels and the file patterns.

A check with source files only matches 12 of 15 chairs.
That check uses the files in the merged pull request.
A planner has only the files that triage names.
Thus 12 of 15 is an upper limit.

Title tags on merged pull requests are a separate local report.
The numbers, the misses, and the empty held-out file are in the
[scorecard](knowledge-base/expert-panel/scorecard.md).

## What goes wrong

An agent often changes the wrong compiler stage.
It can lose hours on a build tree that is out of date.
It can put a test in the wrong directory.
Then the session ends, and the lesson is lost.

This repository keeps that lesson.
One skill takes one issue from the report to the patch.
The other skills each do one task.
The knowledge base holds the maps, the procedures, and the review briefs.

After a fix, the curator can make one small edit.
A seating edit must keep `score_pr.py --corpus` correct.
A brief edit or a playbook edit needs a named counterexample, or a command that you ran.
There is no separate replay tool.

## Start here

[`swift-compiler-fix-loop/`](swift-compiler-fix-loop/SKILL.md) is the
entry skill.

**Fast path.** Use this path only for a small patch.
Triage has already named the stage.
The patch is in the function that causes the bug.
The patch does not change the set of programs that compile.
A new diagnostic is not a fast path.
A change to ABI, ownership, isolation, or a language rule is not a fast path.
A guard at the crash site is the full loop.

1. Run triage, so `seat.py` receives `--stage`.
2. Reproduce this issue.
3. Run `seat.py` with that stage.
4. Ask one reviewer to read the diff. The reviewer does not see your reasoning.
5. Make the smallest patch in that function.
6. Add a test in the directory that the cookbook names.
7. Run the reproducer, the new test, and the nearest neighbors.

`request-changes` means this: apply the named changes, then review that diff again.
Skip the teaching page, the plan review, and the case notes.

**Full loop.** Use this path for every other change.

1. Read this issue. Read the body, the comments, and the linked pull requests. That read needs the network, or a local copy.
2. Run triage from the stack for this issue, or from the flag ladder.
3. Open the playbook for that stage.
4. Take every build command and every test command from [`swift-local-build-test/`](swift-local-build-test/SKILL.md).
5. Write the plan.
6. Ask one reviewer to read the plan before you edit compiler source. The reviewer does not see your reasoning.
7. Make the patch and add the tests.
8. Ask one reviewer to read the diff before you mark the pull request ready.
9. Write case notes if you keep a case-notes repository.
10. Call the curator only when a durable fact changed.

The teaching page is optional.
A panel with one reviewer for each domain is optional.
A similar bug can name a file. It is not the patch for this issue.
If this issue already has pull requests, read those pull requests.

## The other skills

| Skill | Task |
| --- | --- |
| [`swift-issue-triage/`](swift-issue-triage/SKILL.md) | Name the compiler stage for this stack or this reproducer. Do this before you edit compiler source. |
| [`swift-local-build-test/`](swift-local-build-test/SKILL.md) | Build, run tests, use worktrees, and repair the build tree. |
| [`swift-expert-panel/`](swift-expert-panel/SKILL.md) | One reviewer reads the briefs that `seat.py` selects. A separate ballot for each domain is optional. |
| [`swift-issue-explainer/`](swift-issue-explainer/SKILL.md) | An optional page that explains this bug. |
| [`swift-knowledge-curator/`](swift-knowledge-curator/SKILL.md) | When a durable fact changed, make one small checked edit. |

Read these files when you need them. Do not load all of them at the start.

- [`knowledge-base/pipeline-map.md`](knowledge-base/pipeline-map.md) tells parse from Sema, SILGen, and IRGen.
- [`knowledge-base/stage-playbooks/`](knowledge-base/stage-playbooks/) names the files for a known stage.
- [`knowledge-base/regression-test-cookbook.md`](knowledge-base/regression-test-cookbook.md) names the `RUN:` line and the `test/` directory.
- [`knowledge-base/resolved-issue-patterns.md`](knowledge-base/resolved-issue-patterns.md) names extra directories (A1-A10). These are files, not patches.
- [`knowledge-base/expert-panel/`](knowledge-base/expert-panel/) holds the seat table, the briefs, the chair rules, the scorecard, and [`evolution-gate.md`](knowledge-base/expert-panel/evolution-gate.md).
- [`knowledge-base/sibling-repos.md`](knowledge-base/sibling-repos.md) applies when the bug is in llvm, swift-driver, swift-syntax, or sourcekit-lsp.

The change log is [`optimization/edit-log.md`](optimization/edit-log.md).

## Install

Run these commands from the repository root.
Set `SKILL_DIR` to the directory where your agent reads skills.

```bash
SKILL_DIR=~/.agents/skills
for s in swift-compiler-fix-loop swift-issue-triage swift-local-build-test swift-expert-panel swift-issue-explainer swift-knowledge-curator; do
  ln -sfn "$PWD/$s" "$SKILL_DIR/$s"
done
```

The scripts are written for Python 3.9 or newer.
The check workflow is set to Python 3.9 and Python 3.12.

Copy the path template. Edit the copy. Then load it.
An unedited copy still contains `/path/to` placeholders.
`export-env.py` rejects those placeholders.

```bash
cp swift-local-build-test/references/paths.example.json \
   swift-local-build-test/references/paths.json
# Edit paths.json. wiki_checkout may stay an empty string.
eval "$(python3 swift-local-build-test/scripts/export-env.py)"
```

`paths.json` is gitignored.
A filled file always exports `$B`, `$LLVM`, `$LIT`, `$FE`, `$SO`, `$IDE`, `$SUFFIX`, `$CFG`, and `$SWIFT`.
`$WIKI` is set only when `wiki_checkout` is not empty.
`$B_SECONDARY` and `$TOOLCHAINS` are set only when those fields are not empty.

`$SUFFIX` is the text after `swift-` in the `build_swift` directory name.
On the tested setup, that directory is `swift-macosx-arm64`.
The stdlib target that was run is `swift-stdlib-macosx-arm64`.
A directory named `swift-linux-x86_64` would give the suffix `linux-x86_64`.
Linux suffixes have not been run off macOS arm64.
`$CFG` is `$B/test-$SUFFIX/lit.site.cfg`.

You need a `swiftlang/swift` checkout.
A case-notes repository is optional.
Its layout is [`case-notes.md`](swift-compiler-fix-loop/references/case-notes.md).
When you have one, set `wiki_checkout` to that checkout.
It is your repository. It is not a Swift project repository.
When `wiki_checkout` is empty, pass `--wiki` to `new_explainer.py`.
The script does not write into the current directory.

The tested setup is macOS arm64, the MacOSX26.2 SDK, and swift `main` as of August 2026.
The build-failure signatures were recorded on that setup.
That pin used llvm `stable/21.x`.
swift `main` fetched on 2026-10-07 (`e9581097859`) uses llvm `stable/23.x` in `update-checkout-config.json`.
Read that key before you build.
[`environments.md`](swift-local-build-test/references/environments.md) holds the pin and the signatures.

After you install the skills, run `python3 scripts/check_repo.py`.

## Review

`seat.py` selects the briefs.
The reviewer is one read-only subagent.
Give the reviewer the plan or the diff, the seated briefs, and the official documents that those briefs name.
Do not give the reviewer your reasoning.
A block from the chair brief is final.
A block from another brief needs a written rebuttal.
The reviewer writes that rebuttal and decides it.
`request-changes` means this: apply the named changes, then review again.

You can skip review only for a comment, a document, or a test expectation.
Skip review only when that edit does not encode a language rule.

```bash
python3 swift-expert-panel/scripts/seat.py --stage <triage-stage> \
  --text-file <plan-or-pr-body> -- <files relative to the swift checkout>
```

When `chair` is `unseated`, you select the briefs and you say why.
When the script seats any domain, do not add a domain and do not drop a domain.

The verdicts are:

- `approve`: continue.
- `request-changes`: apply the named changes, then review again.
- `block`: do not implement the plan, and do not mark the pull request ready.

A full panel uses one subagent for each seated domain, and then a chair.
Use a full panel only when you ask for separate writeups.
This repository does not show that several reviewers beat one reviewer who reads the same briefs.
The procedure is [`swift-expert-panel/SKILL.md`](swift-expert-panel/SKILL.md).

## House rules

Keep each entry skill short.
Put the long material in the knowledge base.

A build command or a test command is a fact only for the setup where it ran.
The commands in the build skill ran on the August 2026 macOS arm64 setup.
The skill marks the commands that did not run.

Use the evidence from this issue.
Do not copy a patch from a different issue.

The curator can change a few rules and a few dozen knowledge-base lines in one pass.
Those numbers limit churn. They are not a measured optimum.
Put a rejected idea in the change log.

Do not weaken a verifier to hide an assert.
That rule applies to the compiler and to these files.

## What was checked

The full record is [`docs/validation.md`](docs/validation.md).

On the August 2026 setup, `test/DebugInfo` was 336 of 337 tests.
The miss is `modulecache.swift`.
That test already failed.
It checks the SDK module-cache format.
The smoke tests in the validation record passed.
One local SIL debug-value fix was completed under lit.
That fix is a local example in the validation record.

On 2026-10-07, `probe_globs.py --checkout` ran on a sparse checkout of `github/main` at `e9581097859`.
It printed `OK 223 globs`.
That run also checks the 11 official-document paths.

Older issue notes now name files. They do not prescribe a patch.

## More

- [`docs/design.md`](docs/design.md) says why the pieces have this shape.
- [`docs/validation.md`](docs/validation.md) says what ran, and what the run showed.

## Check

```bash
python3 scripts/check_repo.py
python3 -m unittest discover -s tests -v
python3 swift-expert-panel/scripts/score_pr.py --corpus
python3 swift-expert-panel/scripts/score_pr.py --sources-only
python3 swift-expert-panel/scripts/score_pr.py --heldout
```

`--corpus` is the regression check. It must pass.
On 2026-10-07 it was 15 of 15.
`--sources-only` prints the plan-time report and exits 0.
On 2026-10-07 it was 12 of 15.
`--heldout` prints a report and exits 0 when a chair does not match.
The held-out file is empty today.

The check workflow runs on push and on pull request.
It is set to Python 3.9 and Python 3.12.
It also makes a sparse checkout of `swiftlang/swift` `main` and runs the glob probe once.
A weekly schedule runs the same probe.
The schedule stops after 60 days with no commit.
A later commit does not start that schedule again.
The push job is the job that continues to run.

Title tags are a local report. They are not a CI job.
One month of `git log` needs more history than a depth-1 clone.

```bash
python3 swift-expert-panel/scripts/score_titles.py \
  --checkout <swiftlang/swift> --since 2026-09-06 --until 2026-10-06
```

Git keeps commits that are newer than `--since` and older than `--until`.
That window ends at the start of 2026-10-06.
The recorded run printed 121 of 165, 91 of 165, and 104 of 165.

## License

[Apache-2.0](LICENSE). Copyright 2026 mlvea.
