# Tooling / IDE / Driver Playbook

These stages sit beside the batch pipeline.
The stages are IDE services, SourceKit, LSP, and the driver.

## Key Sources

| Area | Files |
| --- | --- |
| Code completion | `lib/IDE/CodeCompletion.cpp` and `Completion*`. The Sema side is `lib/Sema/TypeCheckCodeCompletion.cpp`. |
| Refactoring / local rename | One file is `lib/IDE/Refactoring.cpp`. The SourceKit side is in `tools/SourceKit/lib/SwiftLang/`. |
| Syntax highlighting / structure | The file is `lib/IDE/SyntaxModel.cpp`. SourceKit structure is in `SwiftSourceDocInfo.cpp`. |
| Cursor info /USR | `tools/SourceKit/lib/SwiftLang/SwiftSourceDocInfo.cpp` |
| Semantic tokens | Semantic tokens are in SourceKit `SwiftSourceDocInfo.cpp`. |
| Compiler driver (C++) | The C++ files are `lib/Driver/FrontendUtil.cpp` and `lib/DriverTool/`. The new Swift driver is the local sibling repos `swift-driver/` and `swift-build/`. |
| Module interface printing | `lib/IDE/ModuleInterfacePrinting.cpp` and `lib/PrintAsClang/` |

For the refactoring file, verify the name with `ls lib/IDE | grep -i refactor`.

## Common Bug Classes (what to inspect)

### Class T1: Editor-only crash or wrong result that batch compile handles

Inspect stale ASTs and stale offsets.
Inspect request cancellation.
Inspect cache invalidation.
Also check whether batch mode never enters this request.
A stale buffer is one cause.
A stale buffer is not the only cause.

### Class T2: Completion missing results

Inspect completion solver pruning.
Inspect the expected type.
Inspect whether the parser entered type-completion context for THIS token.
Reproduce the failure with this command.

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
"$IDE" -code-completion -source-filename /tmp/repro.swift -code-completion-token LINE:COLUMN
```

Open `lib/IDE/CodeCompletion*`.
Open the parser handoff.

### Class T3: Driver misbehaves (flags, batching, module resolution)

Compare a direct frontend invocation with a driver invocation on THIS flags.
Inspect `lib/Driver/` for the legacy driver.
Or inspect the swift-driver sibling.
Tests are `test/Driver/*.swift`.

### Class T4: LSP-only issues

These bugs live in the `sourcekit-lsp` sibling, not in the compiler.
The `paths.json` key is `siblings.sourcekit-lsp`.
Route the bug there.
The tests there are Swift Package based.
Run `swift test --filter <TestSuite>`.

## Verification Loop

```bash
# Load variables with swift-local-build-test/scripts/export-env.py
ninja -C "$B" swift-ide-test sourcekitd

"$LIT" -sv --param swift_site_config="$CFG" test/IDE/<file>.swift
```

## Regression Test Placement

- For completion, refactoring, or highlighting, use `test/IDE/*.swift`. The RUN line uses `%target-swift-ide-test -code-completion ... | %FileCheck`.
- For SourceKit request behavior, use `test/SourceKit/<request>/**`. Copy sourcekitd-test style RUN lines from neighboring tests.
