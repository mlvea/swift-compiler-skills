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

## Common Bug Classes And Fix Patterns

### Class R1: IRGen assertion during emission

The assert names a broken lowering assumption (witness table not bound,
unexpected representation). Trace which SIL construct reached the emitter;
either normalize earlier (SILGen/mandatory pass should have canonicalized)
or teach IRGen the missing case mirroring a sibling.

Worked examples from harvest: #55299 root witness table assertion;
typed-throws nested-error generics (#86347 merged #86387: thread the
mapped in-context error type into `emitAsyncReturn`, do not re-query
maximal expansion at the crash site; #87030). Embedded existential
crash #91566 asserts in IRGen `setArgs` but the fix is SIL specialization
(`specializeWitnessMethodInst` in `Generics.cpp`, #91581) — do not patch
`GenCall`.

### Class R2: Undefined symbols / link errors

Usually a missing thunk/accessor emission for some declaration combination,
or an availability/back-deploy mismatch. TBD vs IRGen mismatch is often a
*symptom* of SILDeclRef identity, not a TBD list hole: #85557 / #90287
(review on #90287: add `SILDeclRef::Kind::DistributedThunk`; do not keep
`asDistributed()` as a boolean on the original isolated decl).

### Class R3: Miscompile visible only when running (-O or specific target)

Reproduce with `%target-run-simple-swift`. Compare `-Onone` vs `-O`
emitted IR (`swiftc -emit-ir`) to isolate the pass boundary. Platform-only
failures (watchOS, wasm, embedded) usually mean a layout/representation
special-case was missed — check `TargetInfo`/`LinkerInfo` branches.

### Class R4: Runtime crash in correct code (EXC_BAD_ACCESS at runtime)

Compiled cleanly; crash inside `swift_` runtime functions. Suspect
retain/release pairing, actor hop correctness, or bridge casts.
Use lldb on the built test binary; check
`test/Runtime/`, `test/Casting/`, `test/Concurrency/runtime*` for neighbors.

Worked examples from local cases: 85500 (isolated deinit cleanup executor
hop), 85663 (task-local suppression lifetime), 89581 (Embedded `-Onone`
pack init SIGSEGV: `projectTupleElementAddressByDynamicIndex` loads
`.Elements` from thin `{vwt,kind}` tuple metadata; `-O` unrolls first).

### Class R5: stdlib behavior wrong

Pure Swift sources under `stdlib/public/core`. Tests use
`%target-run-simple-swift` and need the rebuilt stdlib
(`ninja ... swift-stdlib-macosx-arm64`). Note HOSTTOOLS bootstrap skew risk:
see environments reference before blaming your patch.

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
