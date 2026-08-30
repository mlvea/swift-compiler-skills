# Environment Reference (verified facts)

This file records the machine's actual state and every verified failure
mode. Update it whenever a command in the skill proves wrong. Checkout
and build-tree paths: `paths.json` (edit that file to relocate).

## Repo Pinning Contract

Sibling repos must be mutually compatible. Re-verified 2026-08-25 after a
full forward migration:

| Repo | State | Notes |
| --- | --- | --- |
| `swift` | branch `main` @ Aug-2026 tip `9f2c97b7c8f`, which carries the rebased debug-value-type-chain fix; original preserved on branch `debug-value-type-chain-fix` @ `cca5c934393` | |
| `llvm-project` | branch `swift-main-compat-next` @ `origin/stable/21.x` tip (`98631a845ece`) | see pairing rule below |

**Pairing rule (authoritative):** read
`swift/utils/update_checkout/update-checkout-config.json`,
`branch-schemes["main"]["repos"]["llvm-project"]`. As of 2026-08 that is
**`stable/21.x`** — swift `main` pairs with the llvm **release train**
branch named there, NOT with llvm `next`, and NOT with llvm `main`
(frozen upstream at 2025-12). Release schemes pair with the matching
`stable/2026*` branch.

Verified failure signatures when mispaired:
- swift too OLD for llvm: `no member named 'Integer_Width' in 'llvm::Intrinsic::IITDescriptor'`;
  `too few arguments ... maybeAddDependency`; link error missing
  `ClangImporterDependencyCollector::maybeAddDependency` symbol.
- swift too NEW for llvm: `no member named 'getEmptyKey' in 'llvm::DenseMapInfo<const char *>'`
  (LLVM removed it 2026-06-06); `no member named 'NaCl' in 'llvm::Triple'`.
- Stale tblgen/generators after moving either checkout:
  `The class 'SubCommand' is not defined` from llvm-tblgen; undeclared
  identifiers in generated `TypeNodes.inc`. Fix by building tablegen tools
  + headers in the LLVM tree FIRST:
  ```bash
  ninja -C ./Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64 llvm-tblgen llvm-min-tblgen clang-tblgen \
        llvm-headers clang-tablegen-targets \
        include/llvm/Analysis/analysis_gen include/llvm/IR/intrinsics_gen
  ```

Rule: after ANY repo move, compile a few probe objects before long
rebuilds. Never move the user's existing branches; use a dedicated compat
branch. Note: `$var:path` in zsh needs braces (`${var}:path`) — zsh treats
`:l` etc. as history modifiers.

## Build Tree Facts

- Primary tree bootstraps with HOSTTOOLS (`CMakeCache.txt`:
  `BOOTSTRAPPING_MODE:STRING=HOSTTOOLS`): all targets compile with the
  installed Xcode toolchain. Xcode updates can therefore skew already-built
  objects against newly built ones.
- `swift-frontend --version` reports the *source* version (6.4-dev);
  `.swiftmodule` files report the *compiling toolchain* version. A module
  newer than the reading frontend is rejected at import time.
- Useful ninja target names (verified via `ninja -t targets`):
  `swift-frontend`, `swift-stdlib-macosx-arm64`, `swift-ide-test`,
  `check-swift`, `stdlib/public/embedded-libraries`.
  IMPORTANT: `bin/sil-opt` is a SYMLINK to `swift-frontend` in this tree —
  there is no separate ninja target; rebuilding `swift-frontend` updates it.
- Full stdlib rebuild after long drift ≈ 600–1500 steps; budget tens of
  minutes. Full LLVM-tree rebuild ≈ 5200 steps (needed once after llvm
  branch moves; swift links against its libraries).
- The LLVM build dir (`llvm-macosx-arm64`) generates headers on demand.
  After switching llvm checkouts, fatal errors like
  `'llvm/Analysis/TargetLibraryInfo.inc' file not found` or generated
  intrinsics missing mean the tablegen outputs are stale/absent. Regenerate
  (verified):
  ```bash
  ninja -C ./Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64 include/llvm/Analysis/analysis_gen \
        include/llvm/IR/intrinsics_gen
  ```
  Note: at this revision `Intrinsics.inc` does not exist by design —
  `Intrinsics.h` includes only `IntrinsicEnums.inc` + `IntrinsicImpl.inc`.

## Verified Test Invocation

```bash
LIT=./Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64/bin/llvm-lit
CFG=./Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/test-macosx-arm64/lit.site.cfg
$LIT -sv --param swift_site_config=$CFG <path under swift/test/>
```
Note: the lit site config has NO `.py` extension in this tree.

## Verified Failure Modes (post-migration, 2026-08-25)

### Stale test tools after sibling-repo updates

Symptom: a group of tests fails with `dyld: Symbol not found:
_$s27_CompilerSwiftLexicalLookup...` inside `bin/lldb-moduleimport-test`
(or similar tools) while the compiler itself works. Tools link against
swift-syntax-derived dylibs that moved on.
Fix (verified): `ninja -C $B lldb-moduleimport-test` — or the specific
tool target.

### Embedded stdlib skew

Symptom: ONLY embedded tests fail with `module compiled with Swift 6.4
cannot be imported by the Swift 6.5 compiler: lib/swift/embedded/Swift.swiftmodule`.
The embedded stdlib slice builds separately from the macosx stdlib.
Fix (verified): `ninja -C $B stdlib/public/embedded-libraries`.

### Known-pre-existing failure on this tree

`test/DebugInfo/modulecache.swift` fails independently of any SIL-level
patch (asserts clang module-cache format details against the installed
Xcode SDK). Treat as environmental unless upstream says otherwise.

Validation record 2026-08-25: after full migration + rebuild,
`test/DebugInfo` = 336/337 passed (only modulecache.swift failing);
`Constraints/argument_matching.swift`, `Constraints/calls.swift`,
`SILGen/consume_operator_trivial_value_of_nontrivial_type.swift`,
and the rebased fix's own `DebugInfo/sroa_mem2reg_tuple.sil` +
`DebugInfo/dead-obj-elim.sil` all pass.
