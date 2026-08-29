# Cross-Cutting Playbooks

Stages that do not sit on the single forward pipeline.

## ClangImporter / C++ Interop

Sources: `lib/ClangImporter/`; APINotes data lives in `apinotes/*.apinotes`
and APINotes handling inside ClangImporter; C++ interop tests
`test/Interop/Cxx/`, ObjC tests `test/ClangImporter/`, `test/APINotes/`.

What to inspect:
- Missing import of a valid C/C++ decl: importer filter (unsupported
  construct, name mapping).
- Bridging unsoundness: the exact bridge/cast THIS reducer takes, and
  whether it is allowed to imply a Swift protocol conformance.
- Synthesized C++ members: Clang-Sema viability of the operator THIS
  lookup produced.
- Reproduce with a minimal header: `test/ClangImporter/Inputs/` style, or
  inline `-cxx-interoperability-mode=default` reproducers.

## Serialization / Modules

Sources: `lib/Serialization/`, module cache behavior in frontend options.
Bug classes: deserialization crash on valid module (format skew),
missing cross-module references (CMO reading serialized SIL), stale-cache
false errors. Test dirs: `test/Serialization/`, `test/Module/`.
Rule: when changing serialization format, bump format version and keep the
reader backward compatible; run cross-module tests both fresh and with a
prebuilt module cache.

## AutoDiff

Sources: `lib/SILOptimizer/Differentiation/` (`PullbackCloner.cpp`,
`JVPCloner.cpp`, `LinearMapInfo.cpp`), tests `test/AutoDiff/`,
`validation-test/AutoDiff/`.
What to inspect: derivative registration, pullback dominance, implicit
differentiability attributes vs generic validation, IRGen linear-map
structs. Decide from THIS reducer, not from a listed issue's patch.

## DebugInfo

Sources: `lib/SIL/IR/SILDebugInfoExpression.cpp` +
`include/swift/SIL/SILDebugInfoExpression.h`, verifier
`lib/SIL/Verifier/DebugInfoVerifier.cpp`, emission in `lib/IRGen/IRGenDebugInfo.cpp`;
docs: `swift/docs/HowToUpdateDebugInfo.md`.
What to inspect: variable values after SROA/optimization; DWARF piece
assertions. Tests: `test/DebugInfo/*.sil|*.swift`.

## Driver / Build / Platforms

Legacy driver: `lib/Driver/`. New driver + build system live in sibling
checkouts `swift-driver/`, `swift-build/`, `llbuild/`, `swiftpm/`.
Bug classes: flag forwarding differences between driver paths, WMO vs
file-by-file divergence, SDK/platform-specific flags.
Tests: `test/Driver/` in swift repo; package-level tests in each sibling.

## Embedded / Wasm / WatchOS Special Cases

Embedded Swift uses a restricted SIL subset and no runtime by default.
Wasm lacks ObjC runtime and has different error lowering. Always check
whether THIS repro is target-gated before assuming general breakage.
