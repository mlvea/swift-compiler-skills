# debug-info

The scope is SIL debug values, DWARF, and debugger-visible locations after optimization.

## Protects

- An optimization is allowed to delete code.
  It is not allowed to leave `debug_value` pointing at a dead SSA value of the wrong type.
- Read `docs/HowToUpdateDebugInfo.md` before an SROA, mem2reg, DSE, or LICM patch that touches a debug intrinsic.
  That reading is mandatory.
- A line table must not claim user source for a compiler-synthesized thunk without a reasonable location.
- Speculative `debug_value` is correct on only some paths.
  Change that value to `undef`.
  Debug info never speculates.
- When you delete an instruction, call `salvageDebugInfo`, `InstructionDeleter`, or `replaceAllUsesWith`.
  Do not drop a source variable entirely.
  Keep an undef `debug_value` unless the whole scope is unreachable.
- `lib/ClangImporter/DWARFImporter*` is this seat.
  This seat is more specific than `clang-importer`.
  Import of a header, of APINotes, or of PrintAsClang is not this seat.

## Plan review

- Does `test/DebugInfo` or LLDB fail, while `-O` still computes the right value?
  This seat chairs.
  The `sil-optimizer` seat is adjacent.
- Send a verifier error for `debug_value undef` to the producing pass, not to the verifier.

## PR review

- Use `test/DebugInfo/*.sil` or `*.swift` in the existing style.
- Test both `-Onone` and `-O` when the bug is opt-only.

## Reject unless

- Do not strip debug info to silence the verifier.

## Evolution

The evolution answer is none.
Debugger behavior is outside Swift evolution (process.md).

## Forum

`docs/HowToUpdateDebugInfo.md` is the spec.
An incorrect `debug_value` is a compiler bug even when `-O` computes the right value.
Debugger output is not a language change.

## Abstain

Abstain when the change has no debug intrinsic, no DI location, no DWARF, and no `DWARFImporter` change.
Send Clang header import without `DWARFImporter` to `clang-importer`.
