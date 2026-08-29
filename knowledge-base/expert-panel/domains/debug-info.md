# debug-info

SIL debug values, DWARF, debugger-visible locations after
optimization.

## Protects

- Optimizations may delete code; they may not leave `debug_value`
  pointing at a dead SSA value of the wrong type.
- `docs/HowToUpdateDebugInfo.md` is mandatory reading for SROA /
  mem2reg / DSE / LICM patches that touch debug intrinsics.
- Line tables must not claim user source for compiler-synthesized
  thunks without a reasonable location.

## Plan review

- Fails `test/DebugInfo` or LLDB, but `-O` still computes the right
  value? This seat chairs; `sil-optimizer` is adjacent.
- Verifier `debug_value undef` → producing pass, not the verifier.

## PR review

- `test/DebugInfo/*.sil` or `*.swift` in the existing style.
- Both `-Onone` and `-O` when the bug is opt-only.

## Reject unless

- Stripping debug info to silence the verifier.

## Evolution

None. Debugger behavior is outside Swift evolution (process.md).

## Abstain

No debug intrinsic, DI location, or DWARF change.
