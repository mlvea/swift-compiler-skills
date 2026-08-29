# stdlib (conditional)

Standard library public API and core overlays. Sit on `stdlib/`
primary hits.

## Protects

- Public stdlib API is evolution (Language Steering Group). New
  methods, changed generics, removed overloads → `needs-proposal`
  unless they are underscored / SPI.
- Availability annotations on new API must match the first shipping
  OS/toolchain.
- gyb-generated files: edit the `.gyb` source, not only the output.

## Plan / PR

- `test/stdlib/` and `test/abi/` / api-digester when the API is
  public.
- Source-compatibility with inlinable clients.

## Reject unless

- Commonly rejected stdlib ideas (safe array subscript returning
  Optional) stay rejected
  (https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md).
- ARC vs GC debates are closed.

## Evolution

Always run the evolution gate for user-facing stdlib changes. Bug
fixes that preserve API and ABI are `none`.

## Abstain

Compiler-only changes that do not touch `stdlib/`.
