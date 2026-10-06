# Bug fix or language change

This file answers one question.
Is the change a compiler bug fix, or is it a language change?
Every sitting expert applies this file.
The chair applies it too.
Process text: [process.md](https://github.com/swiftlang/swift-evolution/blob/main/process.md).

## The rule in process.md, under Scope

- A bug fix, an optimization, or a diagnostic improvement may land through ordinary code review.
- A patch that changes a design covered by evolution must not merge without the Language Steering Group.
  The group covers the language and the standard library.
  The ban holds when the patch is framed as a bug fix.
- The ban covers a fix that lets more programs be expressed.
- The ban covers a fix that changes the user-visible behavior of an accepted feature.
- You may fix a bug in a feature that is not officially released.
- An experimental feature may change behind an experimental flag.
  That change must not enter the default language mode.

Pitches: https://forums.swift.org/c/evolution/pitches/5

Reviews: https://forums.swift.org/c/evolution/proposal-reviews/21

Commonly rejected language ideas: https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md

## Classify the change

| User-visible effect | Result |
| --- | --- |
| Crash or assert on invalid code or valid code, with no new accepted programs | `none` |
| Miscompile, wrong SIL, or wrong IR, and the result matches existing rules | `none` |
| Accepts-invalid restoration of a rule that an SE or the book already accepted | `none` |
| Rejects-valid: the accepted proposal already allowed the code | `none` |
| Better diagnostic, note, or fix-it for an existing rule | `none` |
| Optimizer change with the same language semantics | `none` |
| New accepted programs, new surface syntax, or a new stdlib API | `needs-proposal`. Use `needs-pitch` when the change is tiny and obvious. |
| Existing programs change meaning. The change is source-breaking. | `needs-proposal`, unless an upcoming-feature flag hides the change. |
| ABI change, mangling change, or layout change for a resilient type | `needs-proposal`, plus a block from `irgen-abi` and from `library-evolution`. Closed-world: if `docs/LibraryEvolution.rst` does not list the change as permitted, the change is a break. |
| Tightening a hole in an unreleased feature or an experimental feature | `none` when an experimental flag still hides the feature. |
| An accepted SE that is not in the tree yet | Compiler work, not a new proposal. Cite the SE. |

When the class is uncertain, the chair sets `needs-pitch`.
The chair also sets `block` until a forum thread exists.
If the case is close, do not approve it in silence.

## What is not evolution

These items are not evolution.
IDE behavior is not evolution.
SourceKit behavior is not evolution.
Debugger output is not evolution.
A compiler flag that is not language configuration is not evolution.
A purely internal change of SIL representation is not evolution.

A purely internal change of IR representation is not evolution.
A language configuration flag is evolution.
`Features.def` is one of those flags.
An upcoming-feature flag is one of those flags.
The Language Steering Group owns those flags.
