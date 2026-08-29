# IRGen / Runtime / LLVM Playbook

Stages: SIL -> LLVM IR, ABI/layout emission, and the runtime+stdlib that the
generated code calls into. 17 `IRGen` labels in the 2026-08 harvest plus
most "undefined symbol" and run-time-crash reports.

## Key Sources

| Area | Files |
| --- | --- |
| Entry points | `lib/IRGen/IRGenModule.cpp`, `IRGen.cpp`, `GenDecl.cpp` |
| Types / layout | `lib/IRGen/GenType.cpp`, `TypeInfo.h` + per-representation headers (`FixedTypeInfo.h`, `ScalarTypeInfo.h`, ...), layout in `TypeLayout.h`, metadata visitors (`ClassMetadataVisitor.h`, `EnumMetadataVisitor.h`) |
| Witness tables / thunks | `lib/IRGen/GenProto.cpp`, `GenMeta.cpp` |
| Calls / functions | `lib/IRGen/GenCall.cpp`, `GenFunc.cpp`, `IRGenFunction.cpp` |
| Casts | `lib/IRGen/GenCast.cpp` |
| Reflection / metadata | `lib/IRGen/MetadataLayouts`, `lib/RuntimeAbi`? — reflection reader is in `stdlib/public/runtime/Reflection*.cpp` |
| Runtime | `stdlib/public/runtime/` (casting, concurrency runtime, objc interop), `include/swift/Runtime/` |
| Stdlib sources | `stdlib/public/core/` |
| ABI definitions | `docs/ABI/` in the swift repo |

Correction note: verify file names with `ls lib/IRGen/` at your base commit.

## Common Bug Classes (what to inspect)

### Class R1: IRGen assertion during emission

The assert names a broken lowering assumption. Trace which SIL construct
reached the emitter on THIS reducer. Ask whether an earlier pass should
have canonicalized it, or whether IRGen lacks a case THIS valid program
needs. Do not patch the assert site until that is known.

### Class R2: Undefined symbols / link errors

Inspect: thunk/accessor emission, availability/back-deploy, and TBD vs
IR mangling of the missing symbol.

### Class R3: Miscompile visible only when running (-O or specific target)

Reproduce with `%target-run-simple-swift`. Compare `-Onone` vs `-O`
emitted IR to isolate the pass boundary. For platform-only failures,
check `TargetInfo`/`LinkerInfo` *and* that THIS repro is actually
target-gated.

### Class R4: Runtime crash in correct code (EXC_BAD_ACCESS at runtime)

Compiled cleanly; crash inside `swift_` runtime functions. Inspect
retain/release pairing, actor hops, or bridge casts on THIS binary.
Neighbors: `test/Runtime/`, `test/Casting/`, `test/Concurrency/runtime*`.

### Class R5: stdlib behavior wrong

Pure Swift sources under `stdlib/public/core`. Tests use
`%target-run-simple-swift` and need the rebuilt stdlib
(`ninja ... swift-stdlib-macosx-arm64`). Note HOSTTOOLS bootstrap skew
risk: see environments reference before blaming your patch.

## Verification Loop

```bash
# IRGen changes may need frontend only; stdlib changes need the stdlib target
ninja -C /Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64 swift-frontend   # compiler-side
ninja -C /Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64 swift-stdlib-macosx-arm64   # stdlib/runtime side

# emit IR manually
FE=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/bin/swift-frontend
$FE -emit-ir -target arm64-apple-macosx13.0 /tmp/repro.swift | less
```

Executable tests require a runnable stdlib; after any stdlib rebuild rerun a
known-good executable smoke test first to rule out toolchain skew.

## Regression Test Placement

- IR shape: `test/IRGen/<topic>.swift`,
  `// RUN: %target-swift-frontend -emit-ir -primary-file %s | %FileCheck`
- Executable behavior: `%target-run-simple-swift` style tests in
  `test/<Area>/` or `test/stdlib/`
- ABI-sensitive: `test/ABI/` + api-digester baselines
- Crash reducers for runtime bugs: `test/stdlib/` named issue-<n> style
