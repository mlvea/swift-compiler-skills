# Cross-Cutting Playbooks

Stages that do not sit on the single forward pipeline.

## ClangImporter / C++ Interop

Sources: `lib/ClangImporter/`; APINotes data lives in `apinotes/*.apinotes`
and APINotes handling inside ClangImporter; C++ interop tests
`test/Interop/Cxx/`, ObjC tests `test/ClangImporter/`, `test/APINotes/`.

Bug classes:
- Missing import of a valid C/C++ decl: the importer filters it out
  (unsupported construct, name mapping). Teach the importer or record an
  intentional unsupported case with a diagnostic.
- Bridging unsoundness: bridged types must not implicitly prove Swift
  protocol conformance — precedent 85111 (`any Equatable` via NSError).
- Synthesized C++ members must pass Clang-Sema viability before use —
  precedent 86478.
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
Bug classes: derivative registration crashes (#55882), pullback dominance,
implicit differentiability attributes skipping generic validation
(precedent 86522), IRGen linear-map structs (#55245).

## DebugInfo

Sources: `lib/SIL/IR/SILDebugInfoExpression.cpp` +
`include/swift/SIL/SILDebugInfoExpression.h`, verifier
`lib/SIL/Verifier/DebugInfoVerifier.cpp`, emission in `lib/IRGen/IRGenDebugInfo.cpp`;
docs: `swift/docs/HowToUpdateDebugInfo.md`.
Bug classes: wrong variable values in debugger after SROA/optimization;
DWARF piece assertions. Tests: `test/DebugInfo/*.sil|*.swift`.
Worked local example: the debug-value-type-chain fix currently staged in
the swift worktree (SROA + DeadObjectElimination interaction).

## Driver / Build / Platforms

Legacy driver: `lib/Driver/`. New driver + build system live in sibling
checkouts `swift-driver/`, `swift-build/`, `llbuild/`, `swiftpm/`.
Bug classes: flag forwarding differences between driver paths, WMO vs
file-by-file divergence, SDK/platform-specific flags.
Tests: `test/Driver/` in swift repo; package-level tests in each sibling.

## Embedded / Wasm / WatchOS Special Cases

Embedded Swift uses a restricted SIL subset and no runtime by default —
verifier failures there are often missing embedded-mode support for a new
feature (harvest example #90072). Wasm lacks ObjC runtime and has different
error lowering (#89320 typed-throws async on Wasm). Always check whether a
repro is target-gated before assuming general breakage.
