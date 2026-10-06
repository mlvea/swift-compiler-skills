# silgen

The scope is checked AST to raw SIL.
If Sema should have rejected the program, this seat votes to move the fix.
This seat does not invent SILGen error nodes.

## Protects

- SILGen is allowed to assume a well-typed and valid AST.
  An invalid program that crashes in SILGen is a Sema hole (fix-loop heuristic 1).
- Cleanups and `ManagedValue` ownership must match the formal convention of the lowered type.
  "It runs at -Onone" is not enough.
- SIL type lowering (`docs/SIL/Types.md`) preserves abstraction.
  An unconstrained generic parameter stays indirect.
  It stays indirect after substitution with a loadable type.
  Lowering of a declaration need not equal lowering of the formal type of that declaration.
- Bridging rules and error-conversion rules are language rules.
  The forms include `E2→E1` typed throws and NSError.
  Unimplemented lowering of a valid AST is a bug.
  Unimplemented lowering of an invalid AST is a Sema miss.
- Do not call `unimplemented()` on user-reachable syntax.
- Formal access to a variable must emit `begin_access` and `end_access`.
  The rules are SE-0176 and `docs/SIL/SILMemoryAccess.md`.
  A missing marker is accepts-invalid exclusivity.
  That miss is not an optimizer problem.

## Plan review

- The flag ladder is `-typecheck`, then `-emit-silgen`.
  If `-typecheck` is clean and `-emit-silgen` crashes, this seat chairs only after you show that Sema is correct on **THIS** reducer.
- For result builders, property wrappers, lazy, and defer, is the AST already expanded incorrectly?
- For typed throws and typed errors, does Sema check the thrown-error destination (`ThrownErrorDestination`)?

## PR review

- Use `test/SILGen/` FileCheck on the relevant instruction sequence.
  Do not check only that the compiler does not crash.
- New apply conventions and new closure conventions must match `docs/SIL/SIL.md` and `docs/SIL/SILFunctionConventions.md`.
  They must also match OSSA in `docs/SIL/Ownership.md`.
  The `ownership` seat is adjacent.
- Concurrency emission in `SILGenConcurrency.cpp` is in scope here.
  Isolation checking is `concurrency`.
  `@isolated(any)` must survive as SIL function-type ABI.
  The forms are `partial_apply [isolated_any]` and `function_extract_isolation`.

## Reject unless

- Do not add a user-facing diagnostic in SILGen.
  The exceptions are definite lowering impossibilities of valid code.
  Those cases are rare.
  Prefer Sema.
  Do not source-break via ASSERT (swift#87352).
- ObjC lowering, async lowering, and typed-throws lowering must not special-case a single stdlib type.

## Evolution

- Result builders are SE-0289.
  Typed throws are SE-0413.
  Isolation in closures belongs to `concurrency`.
- Send a new SIL calling convention that escapes into the ABI to `irgen-abi`.
  If the convention is resilient, it also needs evolution.

## Forum

Borrowing in SIL verifies transformations.
It is not a substitute for language-level borrow checking.

https://forums.swift.org/t/proposal-sil-implementation-of-ownership-and-borrowing/7296

## Abstain

Abstain when there is no AST→SIL emission change.
Abstain for an optimizer-only change, a runtime-only change, or a parse-only change.
