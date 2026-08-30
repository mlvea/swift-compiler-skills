---
name: swift-local-build-test
description: Use when building Swift compiler targets, running lit tests, managing worktrees, or diagnosing build-tree problems (version skew, stale stdlib, module cache) in the local swiftlang checkout at /Users/madushan/Documents/Github/swiftlang. Contains verified commands for this machine's build trees.
---

# Swift Local Build & Test Environment

Verified commands for THIS machine. Paths: `references/paths.json`
(`swift_checkout`, `build_swift` `$B`, `build_llvm`). If a command
here fails, fix it in this file and `references/environments.md`, not
just your shell. Relocate by editing `paths.json` first.

Before blaming your patch for build failures, read
`references/environments.md` — sibling-repo version skew and HOSTTOOLS
bootstrap drift have both bitten here already.

## Build Trees

| Tree | Path | Notes |
| --- | --- | --- |
| Primary (arm64) | `/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64` | RelWithDebInfo + assertions; use this |
| LLVM/lit tools | `./Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64/bin` | `llvm-lit`, `FileCheck` |
| Secondary | `/Users/madushan/Documents/Github/swiftlang/build/buildbot_osx/swift-macosx-arm64` | older bot-style tree; only if primary is broken |
| Toolchains | `./Users/madushan/Documents/Github/swiftlang/toolchains/*.xctoolchain` | issue-87765 experiment artifacts |

Swift source checkout: `/Users/madushan/Documents/Github/swiftlang/swift`.
This tree bootstraps with HOSTTOOLS: everything is compiled by the installed
Xcode toolchain, so an Xcode update can silently skew modules — see
Troubleshooting.

## Everyday Commands

```bash
B=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64

# rebuild frontend after compiler-source edits (~fast)
ninja -C $B swift-frontend

# rebuild other common targets
ninja -C $B swift-ide-test sil-opt swift-demangle swift-parse-test

# rebuild stdlib+runtime (needed for %target-run tests / stdlib edits; slow first time)
ninja -C $B swift-stdlib-macosx-arm64
```

## Running Tests

```bash
LIT=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64/bin/llvm-lit
CFG=$B/test-macosx-arm64/lit.site.cfg

# focused test(s) — always do this first
$LIT -sv --param swift_site_config=$CFG <file-or-dir>

# full suite target exists but is slow; prefer directories:
ninja -C $B check-swift   # everything; use sparingly
```

Direct tool invocation for fast iteration:

```bash
FE=$B/bin/swift-frontend
$FE -typecheck -verify -swift-version 5 /tmp/repro.swift          # Sema
$FE -emit-silgen -target arm64-apple-macosx13.0 /tmp/repro.swift  # SILGen
$FE -O -emit-ir -target arm64-apple-macosx13.0 /tmp/repro.swift   # IRGen
$B/bin/sil-opt -enable-sil-verify-all case.sil                    # SIL unit
```

Note the SDK comes from Xcode (`MacOSX26.2.sdk` at last verification);
lit injects `-sdk` automatically. When invoking manually add
`-sdk $(xcrun --show-sdk-path)`.

## Worktrees For Fix Work

Keep main checkout clean; do fixes in worktrees or commit to branches:

```bash
git -C /Users/madushan/Documents/Github/swiftlang/swift status --short   # check state first!
git -C /Users/madushan/Documents/Github/swiftlang/swift worktree add /tmp/swift-fix-<n> <base>
```

Existing convention: `/tmp/swift-fix-<issue>` and `/tmp/swift-fix-round3`
(see `tracker/active.md`). Never stash someone else's dirty worktree.

## Troubleshooting (verified failure modes)

### Sibling-repo skew (swift vs llvm-project) — SEEN 2026-08-25

Symptom: compiler sources fail to compile with missing LLVM members
(`Integer_Width`, changed `maybeAddDependency` arity).
Fix + contract: see `references/environments.md`.

### Module version skew — SEEN 2026-08-25

Symptom: every test fails instantly with
`module compiled with Swift 6.5 cannot be imported by the Swift 6.4 compiler: ./Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/lib/swift/macosx/Swift.swiftmodule`.

Cause: HOSTTOOLS bootstrap; stdlib objects were built by a different Xcode
than the current ninja state expects.

Fix:
```bash
ninja -C $B swift-stdlib-macosx-arm64 swift-frontend
```
then rerun one known-good smoke test before continuing.

### Stale module cache

Symptom: weird "no such module" or stale-interface errors after switching
branches.
```bash
rm -rf $B/swift-test-results/*/clang-module-cache
```

### Test passes locally, fails in CI (or vice versa)

Check `-target` triples and availability defines differ per platform;
lit prints the exact command on failure — read it before theorizing.
