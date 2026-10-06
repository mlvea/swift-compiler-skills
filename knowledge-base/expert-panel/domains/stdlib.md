# stdlib (conditional)

The scope is the public API of the standard library and the core overlays.
Sit on a primary hit in `stdlib/`.

## Protects

- The public API of the stdlib is evolution, under the Language Steering Group.
  A new method, changed generics, or a removed overload is `needs-proposal`.
  The exception is underscored API or SPI.
- An ABI-public change is binary-incompatible by default when `docs/LibraryEvolution.rst` does not list it as permitted.
  One example is a new protocol requirement without a defaulted available implementation.
  Another example is adding or removing `@frozen`.
- An availability annotation on a new API must match the first shipping OS/toolchain.
- For a gyb-generated file, edit the `.gyb` source.
  Do not edit only the generated output.

## Plan review

- If the change is public API, ABI-public layout, or gyb source, use evolution-gate.md first.
- An underscored change or an SPI-only change still needs availability.
  That availability must match the first shipping toolchain.

## PR review

- Use `test/stdlib/`.
  When the API is public, also use `test/abi/` or the api-digester.
- Keep source compatibility with inlinable clients.
  Edit `.gyb` sources.
  Do not edit only the generated output.

## Reject unless

- Commonly rejected stdlib ideas stay rejected.
  One idea is a safe array subscript that returns Optional.
  The list is commonly_proposed.md.

  https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md
- The ARC versus GC debate is closed.

## Evolution

Use evolution-gate.md for every user-facing stdlib change.
A bug fix that preserves the API and the ABI is `none`.

## Forum

The public API of the stdlib belongs to the Language Steering Group.
Commonly rejected ideas stay rejected.
The ideas include a safe `[]` that returns `Optional`, and reopening the ARC versus GC debate.
The list is commonly_proposed.md.

https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md

## Abstain

Abstain when a compiler-only change hits none of `stdlib/`, `test/stdlib/`, `test/abi/`, `utils/gyb*`, or `utils/availability-macros.def`.
