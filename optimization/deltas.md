# Curator deltas

One bullet per accepted epoch. `helpful` when a later trajectory used
it; `harmful` when it misrouted. Do not rewrite a whole playbook
because one issue hurt. Never cite `D_test` ids here.

Format: `- (helpful:N harmful:M) <home>: <rule>`

- (helpful:1 harmful:0) seating: `TypeCheckDeclObjC.cpp` is clang-importer primary; inferred `@objc` is `isRepresentableInLanguage`
- (helpful:1 harmful:0) seating: `SILIsolationInfo*` is concurrency primary
- (helpful:1 harmful:0) seating: inverse generic tests chair generics, not ownership
- (helpful:1 harmful:0) seating: `docs/SIL/Ownership.md` chairs ownership
- (helpful:1 harmful:0) sil-optimizer: generalize missing hoist checks to the instruction class; PackageCMO skip is package-CMO-only
- (helpful:1 harmful:0) embedded: do not specialize `witness_method` when the requirement is ABI-more-generic than the protocol
- (helpful:1 harmful:0) irgen-abi: noncopyable metadata not discoverable by old runtimes; no explosion schema just to count registers on huge types
- (helpful:1 harmful:0) debug-info: salvage on delete; never drop a variable; never speculate
- (helpful:1 harmful:0) type-system: subtype is not transitive; solution application cannot fail
- (helpful:1 harmful:0) library-evolution: closed-world ABI; `getFragileFunctionKind` not a hardcoded attribute list
- (helpful:0 harmful:0) eval: train/selection/test splits; seating `--corpus` is D_tr regression, `--sel` is the accept gate; specialist numbers need a D_test run that has not happened
