# Producing-pass cookbook

The crash site or the assert site is the observation.
The producing pass is the first transform that created the illegal SIL.
Or the bug is a Sema hole when `-typecheck` already fails.
Official dump flags are in `docs/DebuggingTheCompiler.md`.

Machine binaries come from `swift-local-build-test/scripts/export-env.py`.
That script sets `$B`, `$FE`, `$SO`, and `$LLVM`.
`$SO` is a symlink to `swift-frontend` in this tree.
A rebuild of `swift-frontend` updates `$SO`.

`sil-opt` takes these flag names without `-Xllvm`.
`swift-frontend` needs `-Xllvm` for the same flag names.
These flag forms were verified on 2026-08-30.
The tested setup was macOS arm64.
The `-target` triple below is for that setup.

## 1. Flag ladder first (this reducer)

Run the flag ladder on this reducer first.

```bash
$FE -typecheck -verify -sdk $(xcrun --show-sdk-path) repro.swift
$FE -emit-silgen -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 repro.swift
$FE -emit-sil -Onone -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 repro.swift
$FE -O -emit-sil -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 repro.swift
```

If `-typecheck` fails, Sema produced the bug.
Stop.
Do not patch SILGen.
Do not patch a later assert.

## 2. Name the passes that ran

Name the passes that ran.

```bash
# frontend (source)
$FE -O -emit-sil -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 \
    -Xllvm -sil-print-pass-name repro.swift -o /dev/null

# sil-opt (already-lowered .sil)
$SO -O --sil-print-pass-name --enable-sil-verify-all case.sil -o /dev/null
```

Each output line uses this form: `Run #<n>, stage …, pass …: Name (sil-name), Function: …`.
`(Skip)` means that the pass declined this function.

## 3. Bisect the producing pass

Binary-search the run index.
`--sil-opt-pass-count=N` stops after N pass runs.
One verified example is `-O --sil-opt-pass-count=5`.
That run ends during EarlyModulePasses on a trivial function.

```bash
$SO -O --sil-opt-pass-count=<N> --sil-print-pass-name --enable-sil-verify-all \
    case.sil -o /tmp/after.sil
```

Find the smallest N where the verifier fires or the bad SIL appears.
That pass is the producer unless the SIL at N-1 was already illegal.
In that case, the earlier pass or SILGen is the producer.
This pass only observed the bad SIL.

Dump the SIL around one named pass on the frontend.

```bash
$FE -O -emit-sil -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 \
    -Xllvm -sil-print-around=<sil-name> \
    -Xllvm -sil-print-function=<mangled> \
    repro.swift
```

`sil-name` is the token in parentheses from step 2.
Examples are `licm`, `sil-mem2reg`, and `send-non-sendable`.
Filter with `-Xllvm -sil-print-function=`.
If you do not filter, the SIL is huge.

## 4. Decide the layer

Decide the layer from what you see.

| What you see | Layer |
| --- | --- |
| Illegal SIL before the suspect pass. | That pass is adjacent. Find the earlier producer. |
| Legal SIL comes in and illegal SIL goes out. | That pass owns the bug. |
| The verifier reports `load_borrow`, a borrow, or exclusivity. | Open `ownership` and the producing pass. |
| The failure is only at `-O`, and `-Onone` is clean. | The layer is the optimizer. Use this cookbook. |
| `-emit-silgen` is already wrong, and `-typecheck` is clean. | The layer is SILGen, after Sema validity is known. |

Do not patch the verifier.
Do not add a symptom `#available` guard at the assert.
Do not add a weakly-imported symptom guard at the assert.
Do not add an embedded symptom guard at the assert.
Generalize the instruction class, as in #90931 versus #90945.

## 5. Unit-test the named pass

Copy the RUN flags from a neighbor of that pass under `test/SILOptimizer/`.
The new `.sil` file must fail on the producing pass alone.
It is not enough if the file fails only through `swiftc -O`.
