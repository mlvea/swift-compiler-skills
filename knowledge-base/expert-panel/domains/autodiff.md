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

## Plan / PR

- Tests in `test/AutoDiff/` or `validation-test/AutoDiff/`.
- `@differentiable` / `derivative(of:)` reducers, not only SIL dumps.

## Reject unless

- Implicit differentiability attributes do not skip generic checks.
- No `sil-verify-none` to hide differentiation SIL.

## Evolution

AutoDiff is still partially experimental; flag-gated behavior may
change without LSG, but public stdlib differentiation API cannot.

## Abstain

No differentiation files or attributes.
