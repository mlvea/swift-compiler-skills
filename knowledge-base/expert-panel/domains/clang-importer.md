# clang-importer

The scope is import of C, Objective-C, and C++ into Swift.
The scope includes PrintAsClang reverse interop, APINotes, and foreign reference types.

## Protects

- An imported declaration must be Clang-Sema viable.
  Synthesized C++ members that fail Clang lookup must not appear in Swift.
- Do not use a foreign reference type (`swift_shared_reference`) as a value when that use breaks the FRT contract.
  Forums show this with `std::string` import diagnostics.
- `@objc` representability is `isRepresentableInLanguage` and the related functions.
  This check includes **inferred** `@objc`.
  A check of only an explicit attribute in `InterfaceTypeRequest` misses inference (#81054).
- Do not consult `TypeRepr` for an imported declaration or a deserialized declaration.
  The repr is missing when there is no Swift source.

## Plan review

- Put a minimal header repro under `test/ClangImporter/Inputs/` or `test/Interop/Cxx/`.
- Is the filter intentional because the case is unsupported, or is it a missed mapping?
- Reverse interop (PrintAsClang) must not emit C++ that Clang rejects.

## PR review

- Put ObjC tests in files that require objc-interop.
  Follow the `test/attr/attr_objc.swift` pattern.
  When the change has effects, cover the sync case and the async case.
- A C++ test must specify `-cxx-interoperability-mode`.
- Suppress `Copyable` when an imported C++ value type is not copyable.
  This is the #86573 class of change.

## Reject unless

- Diagnostics must match neighboring importer diagnostics.
  Use `limitBehavior` where that API is used.
  Use `softenIfAccessNote` where that API is used.
- A new implicit Swift conformance from a bridged ObjC type is adjacent to `runtime`.
  The verdict is usually `block`.
- Do not add a process-global cache for in-process compiler instances.
  Prefer the request evaluator (swift#77522).

## Evolution

C++ interop is still changing quickly.
Experimental flags matter.
A new user-facing import of a C++ feature that changes the default Swift API surface can need a pitch on the C interoperability forum.

https://forums.swift.org/c/development/c-interoperability

Typed throws are not representable in ObjC (SE-0413 and #81054).

## Forum

https://forums.swift.org/t/c-interop-function-uses-foreign-reference-type-error-with-std-string/69626

FRT-as-value is a contract break.
It is not a missing convenience.

## Abstain

Abstain when the change has no import, no `@objc` representability, no APINotes, and no PrintAsClang change.
Send a `DWARFImporter*` debug-type import to `debug-info`.
