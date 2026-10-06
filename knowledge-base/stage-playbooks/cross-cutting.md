# Cross-Cutting Playbooks

These stages do not sit on the single forward pipeline.

## ClangImporter / C++ Interop

Sources are in `lib/ClangImporter/`.
APINotes data is in `apinotes/*.apinotes`.
APINotes handling is inside ClangImporter.
C++ interop tests are in `test/Interop/Cxx/`.
ObjC tests are in `test/ClangImporter/` and `test/APINotes/`.

What to inspect:

- If a valid C or C++ declaration does not import, inspect the importer filter. The filter can reject an unsupported construct. The filter can apply a name mapping.
- For bridging unsoundness, inspect the exact bridge or cast that THIS reducer takes. Ask whether that bridge is allowed to imply a Swift protocol conformance.
- For synthesized C++ members, inspect the Clang-Sema viability of the operator. That operator is the one THIS lookup produced.
- Reproduce the failure with a minimal header. Use the style in `test/ClangImporter/Inputs/`. Or use inline reproducers with `-cxx-interoperability-mode=default`.

## Serialization / Modules

Sources are in `lib/Serialization/`.
Behavior of the module cache is in the frontend options.

One bug class is a deserialization crash on a valid module.
That crash is format skew.

One bug class is missing cross-module references.
In that class, CMO reads serialized SIL.

One bug class is a false error from a stale cache.

Test directories are `test/Serialization/` and `test/ModuleInterface/`.

When you change the serialization format, bump the format version.
Keep the reader backward compatible.
Run cross-module tests both fresh and with a prebuilt module cache.

## AutoDiff

Sources are in `lib/SILOptimizer/Differentiation/`.
The files include `PullbackCloner.cpp`, `JVPCloner.cpp`, and `LinearMapInfo.cpp`.
Tests are in `test/AutoDiff/`.

Inspect derivative registration.
Inspect pullback dominance.
Inspect implicit differentiability attributes against generic validation.
Inspect IRGen linear-map structs.
Decide from THIS reducer.
Do not decide from the patch of a listed issue.

## DebugInfo

One source is `lib/SIL/IR/SILDebugInfoExpression.cpp`.
The header is `include/swift/SIL/SILDebugInfoExpression.h`.
The verifier is `lib/SIL/Verifier/DebugInfoVerifier.cpp`.
Emission is in `lib/IRGen/IRGenDebugInfo.cpp`.
The document is `swift/docs/HowToUpdateDebugInfo.md`.

Inspect variable values after SROA or after optimization.
Inspect DWARF piece assertions.
Tests are `test/DebugInfo/*.sil|*.swift`.

## Driver / Build / Platforms

The legacy driver is `lib/Driver/`.
The new driver and the build system are in sibling checkouts.
Those checkouts are `swift-driver/`, `swift-build/`, `llbuild/`, and `swiftpm/`.

One bug class is a difference in flag forwarding between driver paths.

One bug class is WMO versus file-by-file divergence.

One bug class is an SDK flag or a platform-specific flag.

Tests in the swift repo are in `test/Driver/`.
Each sibling has package-level tests.

## Embedded / Wasm / WatchOS Special Cases

Embedded Swift uses a restricted SIL subset.
Embedded Swift has no runtime by default.

Wasm has no ObjC runtime.
Wasm has a different error lowering.

Always check whether THIS repro fails only on that target before you assume general breakage.
