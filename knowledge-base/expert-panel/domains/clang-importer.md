# clang-importer

Import of C, Objective-C, and C++ into Swift; PrintAsClang reverse
interop; APINotes; foreign reference types.

## Protects

- Imported declarations must be Clang-Sema viable. Synthesized C++
  members that fail Clang lookup must not appear in Swift.
- Foreign reference types (`swift_shared_reference`) cannot be used as
  values in a way that breaks the FRT contract (seen with `std::string`
  import diagnostics on forums).
- `@objc` representability is `isRepresentableInLanguage` and friends,
  including **inferred** `@objc`. Checking only an explicit attribute
  in `InterfaceTypeRequest` misses inference (#81054).
- Do not consult `TypeRepr` for imported or deserialized declarations;
  the repr is missing when there is no Swift source.

## Plan review

- Minimal header repro under `test/ClangImporter/Inputs/` or
  `test/Interop/Cxx/`.
- Is the filter intentional (unsupported) or a missed mapping?
- Reverse interop (PrintAsClang) must not emit C++ that Clang rejects.

## PR review

- ObjC tests in files that require objc-interop (`test/attr/attr_objc.swift`
  pattern). Cover sync and async when effects are involved.
- C++ tests specify `-cxx-interoperability-mode`.
- Copyability of imported C++ value types: suppress `Copyable` when
  the C++ type is not copyable (#86573 class of change).

## Reject unless

- Diagnostics match neighboring importer diagnostics
  (`limitBehavior`, `softenIfAccessNote` where that API is used).
- New implicit Swift conformances from bridged ObjC types — `runtime`
  adjacent, usually `block`.
- No process-global caches (in-process compiler instances). Prefer the
  request evaluator (swift#77522).

## Evolution

C++ interop is still rapidly moving; experimental flags matter. New
user-facing import of a C++ feature that changes default Swift API
surface may need a pitch on
https://forums.swift.org/c/development/c-interoperability

Typed throws are not representable in ObjC (SE-0413 + #81054).

## Forum

https://forums.swift.org/t/c-interop-function-uses-foreign-reference-type-error-with-std-string/69626
— FRT-as-value is a contract break, not a missing convenience.

## Abstain

No import, `@objc` representability, APINotes, or PrintAsClang change.
