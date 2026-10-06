---
name: swift-issue-explainer
description: Use this skill to write an optional teaching page for one Swift issue. The page does not block the patch.
---

# Swift issue explainer

Write a teaching page for this issue.
The page is not a status report. It is not a patch to copy.
Write it when you want a page that someone can open.

The reviewer reads the written plan. This page does not block a compiler edit.

## Output

Take `wiki_checkout` and `explainers_rel` from `paths.json`.
Copy `swift-local-build-test/references/paths.example.json` to create that file.
The page path is `issues/explainers/<issue-number>/index.html`.
`explainers_rel` in `paths.json` names that relative path.

That tree is gitignored. Scaffold the folder. Then fill the page.

```bash
python3 swift-issue-explainer/scripts/new_explainer.py --issue <N>
```

Pass `--wiki` and a case-notes directory when `wiki_checkout` is empty.
`new_explainer.py` refuses an empty wiki, `.`, `..`, and a `/path/to` placeholder.
The script does not write into the current directory.

Use one folder for each issue. The script copies the CSS next to the page.
Open `index.html` in a browser. Read it as a stranger.

Rewrite a section that only you would understand.

## Inputs

Use these inputs.

- This issue: the body, the comments, and the pull requests for this number
- The reducer that failed
- The written plan: the invariant, the broken assumption, the path, and the intended change
- The triage record: the stage and the files
- The seating JSON and the review verdict, after a review
- The compiler files that this reducer reached. Open those files.

Other issues, case files, and harvested plans may name a file.
They do not explain this bug.

## Page

Follow `references/page-structure.md`.
Start from `references/shell.html`. Every heading on that page is required.
Say so when you do not know a fact.

Draw each diagram by hand as SVG in the HTML. Give each diagram one claim.
Mark the caption `schematic` when the figure is a schematic.

Build each diagram in markup. Do not generate an image.

## Hard rules

State the language rule first. Then state the compiler fact.
Take each path and function name from this reducer, not from a similar issue.
A reader who stops after the claim must still have the point.

Do not put a home-directory path on the page.
Write `lib/...` or the repository name.
Add a short note about the change after the diff review.
You do not need the patch before the diagnosis page.

You do not need the page before the patch.
