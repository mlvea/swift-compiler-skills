# Expert panel roster

Seats are domains.
The machine table is `seats.json`.
This file gives the seating algorithm and the charter list.

Run `python3 swift-expert-panel/scripts/seat.py` to seat a change.
Do not choose the chair by hand when the script returned one.
If `chair` is `unseated`, choose the briefs.
Say why you chose the briefs.

## Core seats

| id | Charter |
| --- | --- |
| `type-system` | Constraint solver, overloads, argument matching, solver diagnostics |
| `generics` | Requirement machine, generic signatures, conformances, existentials, packs |
| `concurrency` | Isolation, Sendable, region-based isolation, sending |
| `silgen` | AST → raw SIL |
| `ownership` | OSSA, borrow/consume, move-only, ownership verifier |
| `sil-optimizer` | Pass soundness, specialization, ARC opts |
| `irgen-abi` | LLVM IR, layout, witness tables, mangling, ABI |
| `runtime` | Casts, refcounting, metadata, reflection, threading, backtrace, bridging |
| `clang-importer` | C/ObjC/C++ import, PrintAsClang, FRT |
| `parser-diagnostics` | Parse, recovery, diagnostic wording, ASTGen |
| `sourcekit-ide` | Completion, cursor info, index, refactoring |
| `library-evolution` | Availability, resilience, inlinable, feature flags |
| `serialization` | swiftmodule, dependency scan, driver module loading |
| `debug-info` | SIL debug values, DWARF, debugger after opts |

## Conditional seats

These seats sit only on a primary file hit.
The script enforces that rule.
The seats are `autodiff`, `distributed`, `stdlib`, and `macros`.

`embedded` also sits when the plan hits its keywords.
`embedded` also sits when the title hits its keywords.
The flag for that rule is `text_may_seat`.
A SILOptimizer path alone does not seat `embedded`.
An IRGen path alone does not seat `embedded`.

## Seating algorithm

1. For each changed file, the most specific primary glob wins.
   A longer glob is more specific.
   A more literal glob is more specific.
   Equal specificity keeps the later domain in `seats.json`.
   That domain scores +3.
2. An unmatched file may score +1 on an adjacent glob.
   More than one domain may score.
3. Each keyword hit adds `keyword_weight`.
   At most three hits count.
   The weight is 1, so the keyword total is at most +3.
   Stage adds +1 only when the domain already scored on a file or a keyword.
4. The script drops a conditional domain that has no primary hit.
   A keyword match does not keep that domain.
   The script keeps `embedded` when `text_may_seat` is set.
5. If no domain remains, `chair` is `unseated`.
   `seated` is empty.
   The script does not substitute `type-system`.
6. The chair is the highest score.
   A tie breaks by domain id, in alphabetical order.
7. `seated` holds the chair and up to three other domains that scored.
   The script prefers the `neighbors` of the chair.
   The script then takes the rest by score.
   The cap is 4.
8. If that set has one seat, the script adds one neighbor.
   The script uses a stage-matched neighbor when one exists.
   Otherwise the script uses the first core neighbor.
   The added neighbor lets someone raise a cross-layer objection.
   The script skips a conditional neighbor that is not eligible.
   That neighbor may abstain.

When files hit two primary globs, the higher score chairs.
One example is Sema plus SILGen.
The other primary sits if it scored.
The split is intended.
SILGen often wants the diagnostic to be in Sema.

## Seating examples

Keep these chairs when you run `python3 swift-expert-panel/scripts/seat.py --stage <stage> -- <files>`.

| files | stage | chair | also seated |
| --- | --- | --- | --- |
| `lib/Sema/CSSimplify.cpp` | sema | type-system | generics |
| `lib/SILOptimizer/Transforms/LICM.cpp` | sil-opts | sil-optimizer | debug-info |
| `lib/Sema/TypeCheckConcurrency.cpp` + `lib/SILOptimizer/Mandatory/SendNonSendable.cpp` | sema | concurrency | type-system |
| `lib/SILGen/SILGenExpr.cpp` + `lib/Sema/CSSimplify.cpp` | silgen | silgen | type-system |
| `test/embedded/existential-generic-error.swift` + `lib/SILOptimizer/Utils/Generics.cpp` | irgen | embedded | sil-optimizer |
| `lib/IRGen/GenCast.cpp` | runtime | irgen-abi | runtime |
| `docs/SIL/Ownership.md` | silgen | ownership | silgen |
| `lib/ClangImporter/DWARFImporter.cpp` | importer | debug-info | clang-importer |
| `test/Generics/inverse.swift` | sema | generics | type-system |
| `lib/Sema/TypeCheckMacros.cpp` + `test/Macros/attached_macros_diags.swift` | sema | macros | parser-diagnostics |

## Not in the panel

Files for the build system, Windows, or CMake are out of scope for a compiler-fix review.
Review those files when the patch itself is a build change.
Use the environment skill for that work.
