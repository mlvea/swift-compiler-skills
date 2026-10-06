# sil-optimizer

The scope is performance SIL passes and mandatory SIL passes.
The scope includes specialization, ARC, mem2reg, LICM, SROA, and the SwiftCompilerSources optimizer.

## Protects

- Language semantics are not negotiable for speed.
  A miscompile at `-O` that `-Onone` does not show is still a `block`.
- Keep OSSA until the pass is allowed to run after OME.
  Do not strip ownership to make an analysis easier.
- After SROA, mem2reg, or DSE, debug info must still describe user variables.
  The `debug-info` seat is adjacent.
  Read `docs/HowToUpdateDebugInfo.md`.
- Specialization must not drop where-clause constraints.
  Specialization must not drop inverse-constraint requirements.
- A transform that assumes exclusivity without the matching enforcement is a miscompile (SE-0176).
  The enforcement is `begin_access`, static enforcement, or dynamic enforcement.
  OSSA lifetime-ending uses stay jointly post-dominating.
  The `ownership` seat is adjacent.
  The spec is `docs/SIL/Ownership.md`.
- `AccessPath` visitor customization is bookkeeping.
  It must not change the meaning of `AccessStorage`.
  The spec is `docs/SIL/SILMemoryAccess.md`.
- Do not shrink lexical lifetimes across deinit barriers.
  The `ownership` seat covers that rule.

## Plan review

- Bisect the pass.
  "Something in -O" is not a plan.
- If the illegal SIL appears before the suspect pass, abstain or vote adjacent.
- For LICM or speculation, do not treat `load_borrow` or `begin_access` as an ordinary load.
  Those instructions are side-effecting or scoped.

## PR review

- Add a `.sil` unit test that runs the named pass.
  Add a Swift test when the source-level trigger is the regression.
- Check `sil-opt` FileCheck.
  Do not check only the `swiftc -O` exit code.
- Keep a benchmark-only change in `benchmark/`.
  That change must not alter semantics.

## Reject unless

- Generalize the missing check to the instruction class.
  The review rejected #90931, a weakly-imported special case.
  The review accepted #90945, `load_borrow` speculation.
- An Embedded specialization hole belongs in a shared utility, with `test/embedded/` coverage.
  The `embedded` seat is conditional.
- Do not use `sil-verify-none` in a test to hide a verifier failure (swift#87916).
- Do not mutate the AST from an optimizer, except in a mode that already mutates the AST.
  PackageCMO must not stamp `@usableFromInline` (swift#74641).
  Do not disable `makeDeclUsableFromInline` for **all** CMO.
  Aggressive CMO still mutates the AST by design.
  Limit the skip to package-CMO only.

## Evolution

Optimizer internals are not evolution.
A change to what `-O` is allowed to assume about a language rule is evolution or a language mode.
For example, strict-concurrency at `-O` only.
That change is a `block` without a flag.

## Forum

Pass authors treat a verifier failure as a bug in the pass.

https://forums.swift.org/c/development/compiler

## Abstain

Abstain when the change has no pass change, no analysis change, and no specialization change.
Abstain for a SILGen-only change or an IRGen-only change.
