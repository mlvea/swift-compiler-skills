# autodiff (conditional)

Differentiation transforms, pullback/JVP cloning, derivative
registration. Sit only on a primary file hit.

## Protects

- Registered derivatives must match the original function's generic
  signature; skipping generic validation is a known hole.
- Pullback dominance: generated adjoint code must be well-formed SIL
  (verifier on).
- Linear-map structs have IRGen layout constraints (`irgen-abi`
  adjacent).

## Plan review

- Sit only if differentiation files or attributes are in the change.
- Does the registered derivative's generic signature match the
  original, or did validation get skipped?

## PR review

- Tests in `test/AutoDiff/`.
- `@differentiable` / `derivative(of:)` reducers, not only SIL dumps.

## Reject unless

- Implicit differentiability attributes do not skip generic checks.
- No `sil-verify-none` to hide differentiation SIL.

## Evolution

AutoDiff is still partially experimental; flag-gated behavior may
change without LSG, but public stdlib differentiation API cannot.

## Forum

SIL transform / pullback bugs are compiler defects. New public
`Differentiation` stdlib API is evolution (`stdlib` adjacent).

## Abstain

No differentiation files or attributes.
