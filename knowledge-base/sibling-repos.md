# Sibling repos (leave `swiftlang/swift` when the bug is here)

Machine roots: `swift-local-build-test/references/paths.json` `siblings`.
The panel seats compiler domains inside `swift`. These products are
**other checkouts**. Do not invent a frontend patch for a driver/LSP/
syntax bug.

| Sibling | Owns | Stay in `swift` only if |
| --- | --- | --- |
| `llvm-project` | LLVM/Clang/LLD the frontend links | IRGen already emitted wrong LLVM IR (then `irgen-abi`) |
| `swift-driver` | Job graph, incremental, WMO scheduling, `swiftc` CLI | `lib/Driver/` / `lib/Frontend/` flag parsing of *this* frontend |
| `swift-syntax` | SwiftSyntax library, macro expansion host types | `lib/ASTGen/` / `lib/Sema/TypeCheckMacros*` lowering into the compiler |
| `sourcekit-lsp` | LSP server, background indexing | `lib/IDE/` / `tools/SourceKit/` request that `swift-ide-test` reproduces |
| `indexstore-db` | Index store on disk | `lib/Index/` writer in the compiler |

`docs/Driver.md`: do not invoke `swift -frontend` from a product build
system. That is a driver-integration bug, not a Sema fix.
