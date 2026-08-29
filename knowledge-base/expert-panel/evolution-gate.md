# Evolution Gate

Source of truth for "is this a compiler bugfix or a language change?"
Applied by every sitting expert and by the chair. Process text:
https://github.com/swiftlang/swift-evolution/blob/main/process.md

## The rule (process.md, Scope)

- Bug fixes, optimizations, and diagnostic improvements may land through
  ordinary code review.
- A patch that **changes a design covered by evolution** must not merge
  without the Language Steering Group (language/stdlib) even if it is
  framed as a bug fix.
- That includes fixes that **allow additional programs to be expressed**
  or **change user-visible behavior** of an accepted feature.
- Bugs in **features not yet officially released** may be fixed freely.
- **Experimental** features may change behind an experimental flag;
  they must not leak into default language mode.

Pitches: https://forums.swift.org/c/evolution/pitches/5
Reviews: https://forums.swift.org/c/evolution/proposal-reviews/21
Commonly rejected language ideas: https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md

## Classify the change

| User-visible effect | Gate |
| --- | --- |
| Crash/assert on invalid or valid code, no new accepted programs | `none` |
| Miscompile / wrong SIL / wrong IR, result matches existing rules | `none` |
| Accepts-invalid: restore an already-accepted rule (SE or book) | `none` |
| Rejects-valid: code that the accepted proposal already allowed | `none` |
| Better diagnostic / note / fix-it for an existing rule | `none` |
| Optimizer change, same language semantics | `none` |
| New accepted programs, new surface syntax, new stdlib API | `needs-proposal` (or `needs-pitch` if tiny/obvious) |
| Existing programs change meaning (source-breaking) | `needs-proposal` unless gated as upcoming-feature |
| ABI / mangling / layout change for resilient types | `needs-proposal` plus `irgen-abi` / `library-evolution` block. Closed-world: if `docs/LibraryEvolution.rst` does not list the change as permitted, it is a break. |
| Tightening a hole in an **unreleased** or experimental feature | `none` if still flag-gated |
| Implementing an **accepted** SE that is not in the tree | compiler work, not a new proposal; cite the SE |

When uncertain, chair sets `needs-pitch` and `block` until a forum
thread exists. Close cases should not silently `approve`.

## What is not evolution

IDE/SourceKit behavior, debugger output, compiler flags that are not
language configuration, and purely internal SIL/IR representation
changes. Language configuration flags (`Features.def`, upcoming-feature
flags) *are* evolution (Language Steering Group).
