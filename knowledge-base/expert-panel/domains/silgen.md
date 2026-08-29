# silgen

Checked AST → raw SIL. If Sema should have rejected the program, this
seat votes to move the fix — it does not invent SILGen error nodes.

## Protects

- SILGen may assume a well-typed, valid AST. Invalid programs that
  crash here are Sema holes (fix-loop heuristic 1).
- Cleanups and `ManagedValue` ownership must match the formal
  convention of the lowered type. "It runs at -Onone" is not enough.
- Bridging and error conversion (`E2→E1` typed throws, NSError) are
  language rules; unimplemented lowering of a *valid* AST is a bug,
  unimplemented lowering of an *invalid* AST is a Sema miss.
- No `unimplemented()` on user-reachable syntax.

## Plan review

- Flag ladder: `-typecheck` clean and `-emit-silgen` crashes → this
  seat chairs only after Sema is shown to be correct on THIS reducer.
- Result builders, property wrappers, lazy, defer: is the AST already
  expanded incorrectly?
- Typed throws / typed errors: is the thrown-error destination checked
  in Sema (`ThrownErrorDestination`)?

## PR review

- `test/SILGen/` FileCheck on the relevant instruction sequence, not
  only "doesn't crash".
- New apply/closure conventions must match `docs/SIL*.md` and OSSA
  conventions (`ownership` adjacent).

## Reject unless

- User-facing diagnostics are not added in SILGen except for definite
  lowering impossibilities of valid code (rare). Prefer Sema. Do not
  source-break via ASSERT (swift#87352).
- ObjC/async/typed-throws lowering does not special-case a single
  stdlib type.

## Evolution

- Result builders SE-0289; typed throws SE-0413; isolation in
  closures is `concurrency`.
- New SIL calling conventions that escape into ABI → `irgen-abi` +
  evolution if resilient.

## Forum

OSSA notes: borrowing in SIL verifies transformations; it is not a
substitute for language-level borrow checking.
https://forums.swift.org/t/proposal-sil-implementation-of-ownership-and-borrowing/7296

## Abstain

No AST→SIL emission change. Optimizer-only, runtime-only, or
parse-only.
