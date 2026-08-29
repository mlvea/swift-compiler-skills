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

- `test/Serialization/`, `test/Module/`, `test/ScanDependencies/`.
- Fresh and prebuilt-cache runs when the claim is cache-related.
- Driver tests only when flag forwarding / WMO vs single-file
  diverges.

## Reject unless

- Serialized SIL for CMO still verifies under the ownership verifier.
- No "fix" that disables module caching globally.

## Evolution

Module format is not language evolution, but dropping a serialized
bit that inlinable code in the wild depends on is a resilience
incident (`library-evolution`).

## Abstain

Single-file frontend logic with no module boundary.
