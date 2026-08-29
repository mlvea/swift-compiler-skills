# stdlib (conditional)

Standard library public API and core overlays. Sit on `stdlib/`
primary hits.

## Protects

- Public stdlib API is evolution (Language Steering Group). New
  methods, changed generics, removed overloads → `needs-proposal`
  unless they are underscored / SPI.
- ABI-public change not enumerated as permitted in
  `docs/LibraryEvolution.rst` is binary-incompatible by default
  (adding a protocol requirement without a defaulted available
  implementation; adding or removing `@frozen`).
- Availability annotations on new API must match the first shipping
  OS/toolchain.
- gyb-generated files: edit the `.gyb` source, not only the output.

## Plan review

- Public API, ABI-public layout, or gyb source? Evolution gate first.
- Underscored / SPI-only changes still need availability that matches
  the first shipping toolchain.

## PR review

- `test/stdlib/` and `test/abi/` / api-digester when the API is
  public.
- Source-compatibility with inlinable clients. Edit `.gyb` sources,
  not only generated output.

## Reject unless

- Commonly rejected stdlib ideas (safe array subscript returning
  Optional) stay rejected
  (https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md).
- ARC vs GC debates are closed.

## Evolution

Always run the evolution gate for user-facing stdlib changes. Bug
fixes that preserve API and ABI are `none`.

## Forum

Public stdlib API is Language Steering Group territory. Commonly
rejected ideas (safe `[]` returning `Optional`, reopening ARC vs GC)
stay rejected:
https://github.com/swiftlang/swift-evolution/blob/main/commonly_proposed.md

## Abstain

Compiler-only changes that hit none of `stdlib/`, `test/stdlib/`,
`test/abi/`, `utils/gyb*`, or `utils/availability-macros.def`.
