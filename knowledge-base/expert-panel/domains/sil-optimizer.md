# sil-optimizer

Performance and mandatory SIL passes, specialization, ARC/mem2reg/
LICM/SROA, SwiftCompilerSources optimizer.

## Protects

- Language semantics are not negotiable for speed. A miscompile at `-O`
  that `-Onone` does not show is still a `block`.
- Preserve OSSA until the pass is allowed to run after OME. Do not
  strip ownership to make an analysis easier.
- Debug info after SROA/mem2reg/DSE must still describe user variables
  (`debug-info` adjacent, `docs/HowToUpdateDebugInfo.md`).
- Specialization must not drop where-clause constraints or
  inverse-constraint requirements.
- Transforms that assume exclusivity without matching
  `begin_access` / static / dynamic enforcement are a miscompile
  (SE-0176). OSSA lifetime-ending uses stay jointly post-dominating
  (`ownership` adjacent, `docs/SIL/Ownership.md`).
- `AccessPath` visitor customization is book-keeping; it must not
  change `AccessStorage` meaning (`docs/SIL/SILMemoryAccess.md`).
- Do not shrink lexical lifetimes across deinit barriers (`ownership`).

## Plan review

- Bisect the pass. "Something in -O" is not a plan.
- If the illegal SIL appears before the suspect pass, this seat
  abstains or votes adjacent.
- LICM/speculation: side-effecting or scoped instructions (`load_borrow`,
  `begin_access`) are not ordinary loads.

## PR review

- `.sil` unit test that runs the named pass, plus a Swift test if the
  source-level trigger is the regression.
- Check `sil-opt` FileCheck, not just `swiftc -O` exit code.
- Benchmark-only changes stay in `benchmark/` and must not alter
  semantics.

## Reject unless

- Generalize the missing check to the instruction class (rejected
  #90931 weakly-imported special case; accepted #90945
  `load_borrow` speculation).
- Embedded specialization holes belong in shared utilities with
  `test/embedded/` coverage (`embedded` conditional).
- No `sil-verify-none` in tests to hide a verifier failure
  (swift#87916).
- No AST mutation from an optimizer except modes that already do.
  PackageCMO must not stamp `@usableFromInline` (swift#74641). Do not
  disable `makeDeclUsableFromInline` for *all* CMO; aggressive CMO
  still mutates AST by design — gate the skip on package-CMO only.

## Evolution

Optimizer internals are not evolution. Changing what `-O` is allowed
to assume about language rules (e.g. strict-concurrency at -O only)
is evolution / language mode, `block` without a flag.

## Forum

Pass authors treat verifier failures as the pass's bug:
https://forums.swift.org/c/development/compiler

## Abstain

No pass/analysis/specialization change. SILGen-only or IRGen-only.
