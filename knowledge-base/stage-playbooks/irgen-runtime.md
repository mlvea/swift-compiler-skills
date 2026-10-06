# IRGen / Runtime / LLVM Playbook

This playbook covers SIL to LLVM IR.
It covers ABI emission and layout emission.
It covers the runtime and the stdlib that the generated code calls.
The 2026-08 harvest has 17 `IRGen` labels.
Most reports of an undefined symbol also land here.
Most run-time crash reports also land here.

## Key Sources

| Area | Files |
| --- | --- |
| Entry points | `lib/IRGen/IRGenModule.cpp`, `IRGen.cpp`, `GenDecl.cpp` |
| Types / layout | See `lib/IRGen/GenType.cpp` and `TypeInfo.h`. Per-representation headers include `FixedTypeInfo.h`, `ScalarTypeInfo.h`, and others. Layout is in `TypeLayout.h`. Metadata visitors include `ClassMetadataVisitor.h` and `EnumMetadataVisitor.h`. |
| Witness tables / thunks | `lib/IRGen/GenProto.cpp`, `GenMeta.cpp` |
| Calls / functions | `lib/IRGen/GenCall.cpp`, `GenFunc.cpp`, `IRGenFunction.cpp` |
| Casts | `lib/IRGen/GenCast.cpp` |
| Reflection / metadata | One file group is `lib/IRGen/MetadataLayouts`. Is the path `lib/RuntimeAbi` real? This file does not confirm it. The reflection reader is in `stdlib/public/runtime/Reflection*.cpp`. |
| Runtime | See `stdlib/public/runtime/` for casting, the concurrency runtime, and objc interop. Headers are in `include/swift/Runtime/`. |
| Stdlib sources | `stdlib/public/core/` |
| ABI definitions | `docs/ABI/` in the swift repo |

Correction note: verify the file names with `ls lib/IRGen/` at your base commit.

## Common Bug Classes (what to inspect)

### Class R1: IRGen assertion during emission

The assert names a broken lowering assumption.
Trace the SIL construct that reached the emitter on THIS reducer.
Ask whether an earlier pass should have canonicalized that construct.
Or ask whether IRGen lacks a case that THIS valid program needs.
Do not patch the assert site until you know that answer.

### Class R2: Undefined symbols / link errors

Inspect thunk emission and accessor emission.
Inspect availability and back-deploy.
Inspect the TBD mangling and the IR mangling of the missing symbol.

### Class R3: Miscompile visible only when running (-O or specific target)

The miscompile shows only when the program runs.
The trigger is `-O` or a specific target.
Reproduce the bug with `%target-run-simple-swift`.
Compare the emitted `-Onone` IR with the emitted `-O` IR.
Use that comparison to isolate the pass boundary.

For a platform-only failure, check `TargetInfo` and `LinkerInfo`.
Also confirm that THIS repro really fails only on that target.

### Class R4: Runtime crash in correct code (EXC_BAD_ACCESS at runtime)

The program compiled cleanly.
The crash is inside `swift_` runtime functions.
Inspect retain and release pairing on THIS binary.
Inspect actor hops on THIS binary.
Inspect bridge casts on THIS binary.
Neighbor tests are `test/Runtime/`, `test/Casting/`, and `test/Concurrency/runtime*`.

### Class R5: stdlib behavior wrong

The sources are pure Swift under `stdlib/public/core`.
Tests use `%target-run-simple-swift`.
The tests need the rebuilt stdlib.
The build command is `ninja ... swift-stdlib-macosx-arm64`.
HOSTTOOLS bootstrap skew is a risk.
See the environments reference before you blame your patch.

## Verification Loop

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
# An IRGen change may need the frontend only.
# A stdlib change needs the stdlib target.
ninja -C "$B" swift-frontend   # compiler-side
ninja -C "$B" swift-stdlib-macosx-arm64   # stdlib/runtime side

# emit IR manually
"$FE" -emit-ir -target arm64-apple-macosx13.0 /tmp/repro.swift | less
```

Executable tests require a runnable stdlib.
After any stdlib rebuild, rerun a known-good executable smoke test first.
Use that test to rule out toolchain skew.

## Regression Test Placement

- For IR shape, use `test/IRGen/<topic>.swift`. The RUN line is `// RUN: %target-swift-frontend -emit-ir -primary-file %s | %FileCheck`.
- For executable behavior, use `%target-run-simple-swift` tests. Put them in `test/<Area>/` or `test/stdlib/`.
- For an ABI-sensitive change, use `test/ABI/` and the api-digester baselines.
- For a runtime-bug crash reducer, use `test/stdlib/`. Name the file in the issue-<n> style.
