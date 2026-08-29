# serialization

swiftmodule format, module loaders, dependency scanning, driver
invocation as it affects module loading.

## Protects

- Format changes bump the module format version and keep the reader
  backward compatible with at least the previous shipping version.
- What is not serialized will be recomputed; what is serialized must
  still be true after substitution.
- Incremental / dependency-scan graphs must not drop a file that can
  change a public type.

## Plan review

- Cross-module only? Then serialization or CMO reading serialized SIL
  is the first suspect (pipeline-map heuristic 6).
- Stale module cache vs actual format bug: can wiping the cache
  reproduce?

## PR review

- `test/Serialization/`, `test/ModuleInterface/`, `test/ScanDependencies/`.
- `.swiftinterface` changes need `-verify-emitted-module-interface`
  (or the neighbor's equivalent round-trip), not only binary
  swiftmodule version bumps.
- Fresh and prebuilt-cache runs when the claim is cache-related.
- Driver tests only when the change affects module loading, scan, or
  WMO vs single-file module graphs.

## Reject unless

- Serialized SIL for CMO still verifies under the ownership verifier.
- No "fix" that disables module caching globally.

## Evolution

Module format is not language evolution, but dropping a serialized
bit that inlinable code in the wild depends on is a resilience
incident (`library-evolution`).

## Forum

Module format version is a shipping contract with previously released
compilers. Wiping the module cache is a diagnostic, not a fix.

## Abstain

Single-file frontend logic with no module boundary. Seated only
because `lib/Driver/` changed, and the diff does not affect module
loading, dependency scan, incremental graphs, or WMO → abstain.
