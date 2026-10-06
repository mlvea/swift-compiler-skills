# serialization

The scope is the swiftmodule format, module loaders, and dependency scanning.
The scope includes driver invocation when that invocation affects module loading.

## Protects

- A format change must bump the module-format version.
  Keep the reader backward compatible with at least the previous shipping version.
- The compiler recomputes a value that it does not serialize.
  A serialized value must stay true after substitution.
- An incremental graph or a dependency-scan graph must not drop a file that can change a public type.

## Plan review

- If the bug is cross-module only, the first suspect is serialization or CMO that reads serialized SIL.
  Use `pipeline-map` heuristic 6.
- Is the cause a stale module cache or an actual format bug?
  Can you reproduce the bug after you wipe the module cache?

## PR review

- Use `test/Serialization/`, `test/ModuleInterface/`, and `test/ScanDependencies/`.
- A `.swiftinterface` change needs `-verify-emitted-module-interface`, or the equivalent round-trip that a neighbor uses.
  A bump of the binary swiftmodule version is not enough.
- Run the fresh case and the prebuilt-cache case when the claim is cache-related.
- Add driver tests only when the change affects module loading, the scan, or WMO versus single-file module graphs.

## Reject unless

- Serialized SIL for CMO must still verify under the ownership verifier.
- Do not "fix" the bug by disabling module caching globally.

## Evolution

The module format is not language evolution.
A dropped serialized bit that inlinable code in the wild depends on is a resilience incident.
The `library-evolution` seat is adjacent.

## Forum

The module-format version is a shipping contract with previously released compilers.
Wiping the module cache is a diagnostic.
It is not a fix.

## Abstain

Abstain for single-file frontend logic with no module boundary.
Abstain when both of the next conditions are true.
The seat exists only because `lib/Driver/` changed.
The diff does not affect module loading, the dependency scan, incremental graphs, or WMO.
