# Expert Panel Roster

Seats are domains. The machine table is `seats.json`. This file is the
seating algorithm and the charter list.

Run `python3 swift-expert-panel/scripts/seat.py` to seat a change. Do not
hand-pick a chair when the script returned one.

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
| `runtime` | Casts, refcounting, metadata, bridging entrypoints |
| `clang-importer` | C/ObjC/C++ import, PrintAsClang, FRT |
| `parser-diagnostics` | Parse, recovery, diagnostic wording |
| `sourcekit-ide` | Completion, cursor info, index, refactoring |
| `library-evolution` | Availability, resilience, inlinable, feature flags |
| `serialization` | swiftmodule, dependency scan, driver module loading |
| `debug-info` | SIL debug values, DWARF, debugger after opts |

## Conditional seats

Sit only on a **primary** file hit (script enforces this):
`autodiff`, `distributed`, `embedded`, `stdlib`.

## Seating algorithm

1. For each changed file, pick the domain whose **primary** glob is the
   most specific match (longest literal pattern). That domain scores +3.
2. Unmatched files may score +1 on **adjacent** globs (several domains
   allowed).
3. Keywords in the plan/PR body add +1 (capped). Stage adds +1 only to
   domains that already scored on files or keywords.
4. Conditional domains with no primary hit are dropped even if keywords
   matched.
5. Chair = highest score. Ties break by domain id (stable, arbitrary).
6. Seated = chair + up to 3 others that scored, preferring the chair's
   `neighbors`, then remaining by score. Cap 4.
7. If that yields a single seat, add one neighbor (stage-matched if
   possible, else first core neighbor) so a cross-layer objection can
   still be raised. That neighbor may abstain.

When files span two primaries (e.g. Sema + SILGen), the higher-scoring
primary chairs; the other sits if it scored. That is the intended
split-brain case: SILGen often wants the diagnostic in Sema.

## Seating examples (replay)

`python3 swift-expert-panel/scripts/seat.py --stage <stage> -- <files>`
must keep these chairs:

| files | stage | chair | also seated |
| --- | --- | --- | --- |
| `lib/Sema/CSSimplify.cpp` | sema | type-system | generics |
| `lib/SILOptimizer/Transforms/LICM.cpp` | sil-opts | sil-optimizer | debug-info |
| `lib/Sema/TypeCheckConcurrency.cpp` + `lib/SILOptimizer/Mandatory/SendNonSendable.cpp` | sema | concurrency | type-system |
| `lib/SILGen/SILGenExpr.cpp` + `lib/Sema/CSSimplify.cpp` | silgen | silgen | type-system |
| `test/embedded/existential-generic-error.swift` + `lib/SILOptimizer/Utils/Generics.cpp` | irgen | embedded | sil-optimizer |
| `lib/IRGen/GenCast.cpp` | runtime | irgen-abi | runtime |

## Not in the panel

Build-system/Windows/CMake files are out of scope for a compiler-fix
review unless the patch is itself a build change. Use the environment
skill for that.
