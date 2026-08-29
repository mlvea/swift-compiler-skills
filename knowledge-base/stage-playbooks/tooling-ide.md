# Tooling / IDE / Driver Playbook

Stages beside the batch pipeline: IDE services, SourceKit, LSP, driver.

## Key Sources

| Area | Files |
| --- | --- |
| Code completion | `lib/IDE/CodeCompletion.cpp`, `Completion*`, Sema side `lib/Sema/TypeCheckCodeCompletion.cpp` |
| Refactoring / local rename | `lib/IDE/Refactoring.cpp` (verify with `ls lib/IDE | grep -i refactor`); SourceKit side in `tools/SourceKit/lib/SwiftLang/` |
| Syntax highlighting / structure | `lib/IDE/SyntaxModel.cpp`; SourceKit structure in `SwiftSourceDocInfo.cpp` |
| Cursor info /USR | `tools/SourceKit/lib/SwiftLang/SwiftSourceDocInfo.cpp` |
| Semantic tokens | SourceKit `SwiftSourceDocInfo.cpp` |
| Compiler driver (C++) | `lib/Driver/FrontendUtil.cpp`, `lib/DriverTool/`; new Swift driver: sibling repo `swift-driver/` and `swift-build/` locally |
| Module interface printing | `lib/IDE/ModuleInterfacePrinting.cpp` and `lib/PrintAsClang/` |

## Common Bug Classes (what to inspect)

### Class T1: Editor-only crash or wrong result that batch compile handles

Inspect: stale ASTs/offsets, request cancellation, cache invalidation
*and* whether batch mode never enters this request. Stale buffers are
one cause, not the only one.

### Class T2: Completion missing results

Inspect: completion solver pruning, expected type, and whether the
parser entered type-completion context for THIS token. Repro via:
```bash
IDE=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/bin/swift-ide-test
$IDE -code-completion -source-filename /tmp/repro.swift -code-completion-token LINE:COLUMN
```
Open `lib/IDE/CodeCompletion*` and the parser handoff.

### Class T3: Driver misbehaves (flags, batching, module resolution)

Compare direct frontend invocation vs driver invocation on THIS flags.
Inspect `lib/Driver/` (legacy) or the swift-driver sibling. Tests:
`test/Driver/*.swift`.

### Class T4: LSP-only issues

Live in the sourcekit-lsp sibling checkout `/Users/madushan/Documents/Github/swiftlang/sourcekit-lsp`,
not the compiler. Route there; its tests are Swift Package based
(`swift test --filter <TestSuite>`).

## Verification Loop

```bash
ninja -C /Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64 swift-ide-test sourcekitd

LIT=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/llvm-macosx-arm64/bin/llvm-lit
CFG=/Users/madushan/Documents/Github/swiftlang/build/Ninja-RelWithDebInfoAssert/swift-macosx-arm64/test-macosx-arm64/lit.site.cfg
$LIT -sv --param swift_site_config=$CFG test/IDE/<file>.swift
```

## Regression Test Placement

- Completion/refactoring/highlighting: `test/IDE/*.swift` with
  `%target-swift-ide-test -code-completion ... | %FileCheck`
- SourceKit request behavior: `test/SourceKit/<request>/**` using
  sourcekitd-test style RUN lines copied from neighbors
