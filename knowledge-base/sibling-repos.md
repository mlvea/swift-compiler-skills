# Sibling repos (leave `swiftlang/swift` when the bug is here)

Leave the `swiftlang/swift` checkout when the bug is in one of these repos.

Machine roots are `siblings` in `swift-local-build-test/references/paths.json`.
That file is gitignored.
Copy `paths.example.json`.

The panel seats compiler domains inside `swift`.
These products are other checkouts.
Do not invent a frontend patch for a driver bug.
Do not invent a frontend patch for an LSP bug.
Do not invent a frontend patch for a syntax bug.

| Sibling | Owns | Stay in `swift` only if |
| --- | --- | --- |
| `llvm-project` | LLVM, Clang, and LLD. The frontend links these tools. | Stay in `swift` only if IRGen already emitted the wrong LLVM IR. The related area is `irgen-abi`. |
| `swift-driver` | This repo owns the job graph, incremental builds, WMO scheduling, and the `swiftc` CLI. | Stay in `swift` only for flag parsing of this frontend in `lib/Driver/` or `lib/Frontend/`. |
| `swift-syntax` | This repo owns the SwiftSyntax library and the host types for macro expansion. | Stay in `swift` only for lowering into the compiler through `lib/ASTGen/` or `lib/Sema/TypeCheckMacros*`. |
| `sourcekit-lsp` | This repo owns the LSP server and background indexing. | Stay in `swift` only for a request in `lib/IDE/` or `tools/SourceKit/` that `swift-ide-test` reproduces. |
| `indexstore-db` | This repo owns the index store on disk. | Stay in `swift` only for the `lib/Index/` writer in the compiler. |

Do not invoke `swift -frontend` from a product build system.
That rule is in `docs/Driver.md`.
That bug is a driver-integration bug.
That bug is not a Sema fix.
