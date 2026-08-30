# Producing-pass cookbook

The crash/assert site is the observation. The producing pass is the first
transform that created the illegal SIL (or the Sema hole if `-typecheck`
already fails). Official dump flags: `docs/DebuggingTheCompiler.md`.

Machine binaries: `swift-local-build-test/references/paths.json`
(`build_swift` → `$B`, `build_llvm` → `$LLVM`).

```bash
B=<paths.json build_swift>
FE=$B/bin/swift-frontend
SO=$B/bin/sil-opt          # symlink to swift-frontend in this tree
```

`sil-opt` takes the flags **without** `-Xllvm`. `swift-frontend` needs
`-Xllvm` for the same names. Verified 2026-08-30 on this machine.

## 1. Flag ladder first (this reducer)

```bash
$FE -typecheck -verify -sdk $(xcrun --show-sdk-path) repro.swift
$FE -emit-silgen -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 repro.swift
$FE -emit-sil -Onone -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 repro.swift
$FE -O -emit-sil -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 repro.swift
```

If `-typecheck` fails, Sema produced the bug. Stop. Do not patch SILGen
or a later assert.

## 2. Name the passes that ran

```bash
# frontend (source)
$FE -O -emit-sil -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 \
    -Xllvm -sil-print-pass-name repro.swift -o /dev/null

# sil-opt (already-lowered .sil)
$SO -O --sil-print-pass-name --enable-sil-verify-all case.sil -o /dev/null
```

Each line is `Run #<n>, stage …, pass …: Name (sil-name), Function: …`.
`(Skip)` means the pass declined this function.

## 3. Bisect the producing pass

Binary-search the run index. `--sil-opt-pass-count=N` stops after N
pass runs (verified: `-O --sil-opt-pass-count=5` ends during
EarlyModulePasses on a trivial function).

```bash
$SO -O --sil-opt-pass-count=<N> --sil-print-pass-name --enable-sil-verify-all \
    case.sil -o /tmp/after.sil
```

Find the smallest N where the verifier fires or the bad SIL appears.
That pass is the producer unless the SIL was already illegal at N−1
→ the earlier pass (or SILGen) is the producer; this pass only
observed it.

Dump around one named pass (frontend):

```bash
$FE -O -emit-sil -sdk $(xcrun --show-sdk-path) -target arm64-apple-macosx13.0 \
    -Xllvm -sil-print-around=<sil-name> \
    -Xllvm -sil-print-function=<mangled> \
    repro.swift
```

`sil-name` is the parenthesized token from step 2 (`licm`,
`sil-mem2reg`, `send-non-sendable`). Filter with
`-Xllvm -sil-print-function=` or the SIL is huge.

## 4. Decide the layer

| What you see | Layer |
| --- | --- |
| Illegal SIL *before* the suspect pass | That pass is adjacent. Find the earlier producer. |
| Legal SIL in, illegal SIL out | That pass owns the bug. |
| Verifier on `load_borrow` / borrow / exclusivity | `ownership` + the producing pass |
| Only `-O`, `-Onone` clean | optimizer (this cookbook) |
| `-emit-silgen` already wrong, `-typecheck` clean | SILGen, after Sema validity is known |

Do not patch the verifier or add a symptom `#available` / weakly-
imported / embedded guard at the assert. Generalize the instruction
class (`#90931` vs `#90945`).

## 5. Unit-test the named pass

Copy RUN flags from a neighbor of that pass under `test/SILOptimizer/`.
The new `.sil` must fail on the producing pass alone, not only via
`swiftc -O`.
