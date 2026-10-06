# Case notes

Case notes are optional.
They are the user's repository for plans, case writeups, and tracker notes.
They are not a Swift project repository.
This skills repository does not publish a case-notes repository.

The fix loop runs with no case notes.
A pull request description can hold the same facts.
Set `wiki_checkout` in `paths.json` when a checkout exists.
Copy `paths.example.json` to `paths.json` first.

`export-env.py` exports that path as `$WIKI`.

## Minimum layout

```
issues/cases/issue-<N>/README.md
issues/explainers/<N>/index.html
templates/issue-case.md
```

`issues/cases/issue-<N>/README.md` is the case file.
The checklist is `case-file-checklist.md` in this directory.
Write a case file when the pull request cannot rebuild the investigation.
`issues/explainers/<N>/index.html` is the optional teaching page from `swift-issue-explainer`.

Ignore that tree in git.
`explainers_rel` in `paths.json` is the relative path. The default is `issues/explainers`.
`templates/issue-case.md` is a starter file when you keep one.

This skills repository does not ship that template.

## Optional local notes

Create these paths only when you want them.
They are file-search hints after you reproduce the current issue.
They are not the diagnosis.

- `issues/plans-by-search-page/`
- `issues/guidance/README.md`
- `wiki/compiler-understanding.md`
- `tracker/active.md`

Put harvest JSON from `swift-knowledge-curator/references/harvest.md` under `data/` in the case-notes repository.
Do not put that JSON in the skills repository.
