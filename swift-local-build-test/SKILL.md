---
name: swift-local-build-test
description: Use this skill to build Swift targets, run lit tests, or diagnose a local build tree. The commands expand from references/paths.json.
---

# Swift local build and test

These commands were run on macOS arm64 with the MacOSX26.2 SDK.
The compiler was swift `main` as of August 2026.
Copy `references/paths.example.json` to `references/paths.json`.

`paths.json` is gitignored. Edit it for this machine.
Load `paths.json` before any command below.

`export-env.py` refuses a `/path/to` placeholder. `wiki_checkout` may be empty.
`$WIKI` is optional.
If a command in this file fails, correct this file and `references/environments.md`.

Do not correct only the shell history.
Edit `paths.json` when you move a tree. Then run one smoke test again.

```bash
eval "$(python3 swift-local-build-test/scripts/export-env.py)"
```

Run that command from the skills repository root.
The script finds `paths.json` next to its own file. A call by path also works.

## Variables

| Variable | Source | Notes |
| --- | --- | --- |
| `$B` | `build_swift` | Primary tree. The build is RelWithDebInfo with assertions. Use this tree. |
| `$B_SECONDARY` | `build_swift_secondary` | Older tree in the bot style. Use it only when the primary tree is broken. |
| `$LLVM` | `build_llvm` | Build directory for LLVM and Clang. It holds `llvm-lit`, `FileCheck`, and tblgen. |
| `$LIT` | `$LLVM/bin/llvm-lit` | Lit driver. |
| `$FE` | `$B/bin/swift-frontend` | Frontend. |
| `$SO` | `$B/bin/sil-opt` | Symlink to `swift-frontend`. There is no separate ninja target. |
| `$IDE` | `$B/bin/swift-ide-test` | Completion tests and other IDE requests. |
| `$SUFFIX` | derived | `macosx-arm64` on the tested setup. It is the part after `swift-` in the `build_swift` directory name. |
| `$CFG` | `$B/test-$SUFFIX/lit.site.cfg` | Lit site config. The file name has no `.py` suffix. |
| `$SWIFT` | `swift_checkout` | Compiler sources. |
| `$WIKI` | `wiki_checkout` | Optional. The case-notes repository, when you set one. |
| `$TOOLCHAINS` | `toolchains_dir` | Local experiments with `.xctoolchain`. |

This tree bootstraps with HOSTTOOLS.
The installed Xcode toolchain compiles every target.

An Xcode update can skew modules. It gives no warning. See Troubleshooting.

## Commands for a normal edit

```bash
# Rebuild the frontend after an edit to compiler source.
ninja -C "$B" swift-frontend

# Rebuild other common targets.
ninja -C "$B" swift-ide-test swift-demangle swift-parse-test

# Rebuild the stdlib and the runtime for a %target-run test or a stdlib edit.
ninja -C "$B" swift-stdlib-$SUFFIX
```

On the tested setup, `$SUFFIX` is `macosx-arm64`.
The stdlib target that was run is `swift-stdlib-macosx-arm64`.
Linux suffixes have not been run off macOS arm64.
Those suffixes are `linux-x86_64` and `linux-aarch64`.

`swift-stdlib-$SUFFIX` has not been run off macOS arm64.
A rebuild of `swift-frontend` updates `$SO`.

## Run tests

```bash
# Run a focused test first.
"$LIT" -sv --param swift_site_config="$CFG" <file-or-dir>

# The full suite is slow. Prefer one directory.
ninja -C "$B" check-swift
```

Call a tool directly when you want a fast cycle.

```bash
"$FE" -typecheck -verify -swift-version 5 /tmp/repro.swift
"$FE" -emit-silgen -target arm64-apple-macosx13.0 /tmp/repro.swift
"$FE" -O -emit-ir -target arm64-apple-macosx13.0 /tmp/repro.swift
"$SO" -enable-sil-verify-all case.sil
```

The hand frontend triple `arm64-apple-macosx13.0` is the tested setup.
On another machine, use the triple for that platform.
The SDK comes from Xcode. The last check used `MacOSX26.2.sdk`.

Lit adds `-sdk` for you.
Add `-sdk $(xcrun --show-sdk-path)` when you call the frontend by hand.

## Worktrees

Keep the main checkout clean. Do the fix in a worktree or on a branch.

```bash
git -C "$SWIFT" status --short
git -C "$SWIFT" worktree add /tmp/swift-fix-<n> <base>
```

The usual path is `/tmp/swift-fix-<issue>`.
Read `tracker/active.md` in the case-notes repository before you add a worktree, when that file exists.
Do not stash a dirty worktree that belongs to someone else.

## Troubleshooting

These failure modes were checked. The pairing contract is in `references/environments.md`.

- On 2026-08-25 the build showed skew between sibling repositories. LLVM had no member `Integer_Width`, or `maybeAddDependency` had a new arity.
- On 2026-08-25 the build showed a skew in module versions. The Swift 6.4 compiler cannot import a module that Swift 6.5 compiled. Rebuild the stdlib and the frontend.

```bash
ninja -C "$B" swift-stdlib-$SUFFIX swift-frontend
```

- The module cache can go stale after a branch switch.

```bash
rm -rf "$B"/swift-test-results/*/clang-module-cache
```

A test can pass on the local machine and fail in CI. The reverse can also happen.
Compare `-target` and availability.

Lit prints the command that it ran. Read that command before you form a theory.
