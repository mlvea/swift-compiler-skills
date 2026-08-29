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
- Speculative `debug_value` (correct on only some paths) must become
  `undef`. Debug info never speculates. Deleting an instruction must
  call `salvageDebugInfo` (or `InstructionDeleter` /
  `replaceAllUsesWith`). A source variable is never dropped entirely:
  keep an undef `debug_value` unless the whole scope is unreachable.
- `lib/ClangImporter/DWARFImporter*` is this seat (more specific than
  `clang-importer`). Header / APINotes / PrintAsClang import is not.

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

## Forum

`docs/HowToUpdateDebugInfo.md` is the spec. Incorrect `debug_value` is
a compiler bug even when `-O` computes the right value. Debugger
output is not a language change.

## Abstain

No debug intrinsic, DI location, DWARF, or `DWARFImporter` change.
Clang header import without DWARFImporter → `clang-importer`.
