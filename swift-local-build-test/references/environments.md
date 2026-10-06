# Environment reference

This file records one tested setup and each failure mode that was checked.
The setup is macOS arm64, the MacOSX26.2 SDK, and swift `main` as of August 2026.
The `macosx-arm64` directory names below belong to that setup.

`export-env.py` sets `$SUFFIX` from the `build_swift` directory name (`swift-<os>-<arch>`).
It sets `$CFG` to `$B/test-$SUFFIX/lit.site.cfg`.
Set `lit_platform` only when that directory name is not `swift-<os>-<arch>`.

`export-env.py` refuses a `/path/to` placeholder. `wiki_checkout` may be empty.
Copy `paths.example.json` to `paths.json` when you move a tree. Then edit the paths.

Update this file when a command in the skill proves wrong.

## Pin for sibling repositories

Sibling repositories must be compatible with each other.
A second check on 2026-08-25 confirmed this pin after a full forward migration.

| Repo | State | Notes |
| --- | --- | --- |
| `swift` | branch `main` at the August 2026 tip `9f2c97b7c8f` | This tip carries the rebased debug-value-type-chain fix. The original remains on branch `debug-value-type-chain-fix` at `cca5c934393`. |
| `llvm-project` | branch `swift-main-compat-next` at the `origin/stable/21.x` tip `98631a845ece` | August pin. Read the pairing rule below. |

Read `swift/utils/update_checkout/update-checkout-config.json` before a build.
Use the branch at `branch-schemes["main"]["repos"]["llvm-project"]`.
The August llvm pin is `stable/21.x`. That is the pin in the table.

The `github/main` fetch on 2026-10-07 (`e9581097859`) pairs scheme `main` with `stable/23.x`.
In August 2026, a build that used llvm `next` failed at link time.
A build that used llvm `main` failed at link time on that same attempt.
On that fetched main, a release scheme pairs `llvm-project` with `swift/<scheme>`.

For example, `release/6.2` pairs with `swift/release/6.2`.
The `next` scheme pairs with llvm `next`. `rebranch` pairs with `stable/23.x`.
The August pin hit the failure signatures below.

Checked failure signatures for a bad pair:

- swift is too old for llvm. The errors are `no member named 'Integer_Width' in 'llvm::Intrinsic::IITDescriptor'`, `too few arguments ... maybeAddDependency`, and a link error for the missing symbol `ClangImporterDependencyCollector::maybeAddDependency`.
- swift is too new for llvm. The errors are `no member named 'getEmptyKey' in 'llvm::DenseMapInfo<const char *>'` and `no member named 'NaCl' in 'llvm::Triple'`. LLVM removed `getEmptyKey` on 2026-06-06.
- tblgen output is stale after either checkout moves. llvm-tblgen reports `The class 'SubCommand' is not defined`. Generated `TypeNodes.inc` has undeclared identifiers. Build the tablegen tools and the headers in the LLVM tree first.

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
ninja -C "$LLVM" llvm-tblgen llvm-min-tblgen clang-tblgen \
        llvm-headers clang-tablegen-targets \
        include/llvm/Analysis/analysis_gen include/llvm/IR/intrinsics_gen
```

After any move of a repository, compile a few probe objects before a long rebuild.
Do not move a branch that the user already has. Use a branch that exists only for this compatibility pin.
In zsh, `$var:path` needs braces, as in `${var}:path`.

zsh reads `:l` and similar suffixes as history modifiers.

## Build tree

The primary tree bootstraps with HOSTTOOLS.
`CMakeCache.txt` contains `BOOTSTRAPPING_MODE:STRING=HOSTTOOLS`.
The installed Xcode toolchain compiles every target.
An Xcode update can put an old object next to a new object and skew the build.

`swift-frontend --version` reports the source version, which is `6.4-dev` on this tree.
A `.swiftmodule` file reports the version of the toolchain that compiled it.
Import rejects a module that is newer than the frontend that reads it.
`ninja -t targets` on macOS arm64 checked these target names.

- `swift-frontend`
- `swift-stdlib-macosx-arm64`
- `swift-ide-test`
- `check-swift`
- `stdlib/public/embedded-libraries`

`swift-stdlib-$SUFFIX` has not been run for a Linux suffix.
`bin/sil-opt` is a symlink to `swift-frontend` in this tree.
There is no separate ninja target for it. A rebuild of `swift-frontend` updates the symlink.

A full stdlib rebuild after a long gap is about 600 to 1500 steps. Plan for tens of minutes.
A full rebuild of the LLVM tree is about 5200 steps.

Do that LLVM rebuild once after the llvm branch moves. swift links against those libraries.
The LLVM build directory `llvm-macosx-arm64` generates headers when a target needs them.
After an llvm checkout switch, a stale or missing tablegen output causes fatal errors.

One error is `'llvm/Analysis/TargetLibraryInfo.inc' file not found`.
Another error is a missing generated intrinsic. Regenerate the outputs. A run on this tree checked that command.

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
ninja -C "$LLVM" include/llvm/Analysis/analysis_gen \
        include/llvm/IR/intrinsics_gen
```

At this revision, `Intrinsics.inc` does not exist. That absence is by design.
`Intrinsics.h` includes only `IntrinsicEnums.inc` and `IntrinsicImpl.inc`.

## Checked test command

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
"$LIT" -sv --param swift_site_config="$CFG" <path under swift/test/>
```

The lit site config in this tree has no `.py` extension.

## Checked failures after the move on 2026-08-25

### Stale test tools after a sibling repository moves

A group of tests fails, and the compiler itself still works.
The failure is `dyld: Symbol not found: _$s27_CompilerSwiftLexicalLookup...` inside `bin/lldb-moduleimport-test` or a similar tool.
Those tools link against dylibs that come from swift-syntax. Those dylibs moved.

The checked fix is `ninja -C $B lldb-moduleimport-test`, or the ninja target for that tool.

### Skew in the embedded stdlib

Only the embedded tests fail.
The Swift 6.5 compiler cannot import a module that Swift 6.4 compiled.

The module path is `lib/swift/embedded/Swift.swiftmodule`.
The embedded stdlib slice builds apart from the macosx stdlib.
The checked fix is `ninja -C $B stdlib/public/embedded-libraries`.

### Failure that already existed on this tree

`test/DebugInfo/modulecache.swift` fails with no dependence on a SIL patch.
The test checks the clang module-cache format against the installed Xcode SDK.
Treat this failure as environmental, unless upstream says otherwise.
Check record for 2026-08-25, after the full move and the rebuild:

- `test/DebugInfo` passed 336 of 337 tests. Only `modulecache.swift` failed.
- `Constraints/argument_matching.swift` passed.
- `Constraints/calls.swift` passed.
- `SILGen/consume_operator_trivial_value_of_nontrivial_type.swift` passed.
- `DebugInfo/sroa_mem2reg_tuple.sil` for the rebased fix passed.
- `DebugInfo/dead-obj-elim.sil` for the rebased fix passed.
