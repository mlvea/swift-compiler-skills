# autodiff (conditional)

The scope is differentiation transforms, pullback cloning, and JVP cloning.
The scope includes derivative registration.
Sit only on a primary file hit.

## Protects

- The generic signature of a registered derivative must match the original function.
  A skip of generic validation is a known hole.
- Pullback dominance means that generated adjoint code is well-formed SIL with the verifier on.
- Linear-map structs have IRGen layout constraints.
  The `irgen-abi` seat is adjacent.

## Plan review

- Sit only when the change has differentiation files or attributes.
- Does the generic signature of the registered derivative match the original?
  Did the change skip validation?

## PR review

- Put tests in `test/AutoDiff/`.
- Use `@differentiable` reducers and `derivative(of:)` reducers.
  Do not use only SIL dumps.

## Reject unless

- Implicit differentiability attributes do not skip generic checks.
- Do not use `sil-verify-none` to hide differentiation SIL.

## Evolution

AutoDiff is still partially experimental.
Behavior that a flag controls can change without LSG.
The public differentiation API in the stdlib cannot change without LSG.

## Forum

SIL transform bugs and pullback bugs are compiler defects.
A new public `Differentiation` API in the stdlib is evolution.
The `stdlib` seat is adjacent.

## Abstain

Abstain when the change has no differentiation files and no differentiation attributes.
