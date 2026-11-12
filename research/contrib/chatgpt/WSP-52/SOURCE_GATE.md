# WSP52 source construction — pre-DEV engineering gate

Parent: qualified WSP47 at 9e6374119602ea57e479a1b36a35a5c0e932b4e1.
Original preregistration: 8cea083b5c230663b9a9dccfc8089a77f1c4c729, unchanged.

## Delivered and bounded

- source.py constructs deterministic synthetic undelimited binary utterances with a fifteen-word, variable-length, prefix-free codebook and two distinct hidden grammar permutations.
- An evaluator-owned SourceWorld holds 36 phase-A experiences, 6 phase-B experiences, and distinct heldout sets of 60/90 examples. Every source experience is charged one action, and its state transition is observable. This is a finite, preprogrammed physical simulator, not learned physics.
- Learner-visible Observation contains exactly (before, acoustic_bits, after, action_cost, reset_cost); the evaluator must only pass these records, never the SourceWorld, latent triples or hidden codebook.
- SourceWorld.audit() checks codebook prefix-freeness, lexical coverage, demonstration/heldout separation, no extra resets, action counts and grammar changes. source_receipt() produces source-set hashes without lexical labels or true grammar.
- No network, third-party models, GPU, paid API, production system or scheduled task is needed.

Reproducible local source-only fixture: cd research/contrib/chatgpt/WSP-52 && python -m unittest -v test_source.py.
This uses SELFTEST seeds 9001/9002 exclusively; it does not generate registered DEV or PRIMARY worlds. All 5 fixture tests passed locally on Python 3.13.5, 2026-11-12. This is not CI or cross-platform qualification.

Verified file blobs:
- source.py: Git blob 53ac7699f38070e13994aba42ab395fa363fc3c2, SHA-256 53d0123d0dc7fcc65f8c242446f7007a5e6632072ce81f8a93835ee827e79c85.
- test_source.py: Git blob 5af0ef1724c9420bdf5da0140d2a0530f7810454, SHA-256 458317caf3fe672619f0985ca626e62943fd02d0a15502043029ff696ce7ccda.

## Qualification risks and limits

1. Identifiability blocker: physical outcomes are location := (destination + verb) mod 4. Thus (destination=0, verb=1) and (destination=1, verb=0) give the same consequence for any current state. Without separate observational anchors, full independent meanings of destination and verb cannot be recovered, no matter how strong the learner. Source tests verify the collision. Do not label compositional performance as separately identifying both semantic factors.
2. Observation vs. evaluation: heldout transitions are evaluator-generated counterfactual tests, not additional learner experiences. Training exposure uses a continuous 42-action trajectory with no zero-cost reset. Heldout action count must be reported separately from training actions; the comparator must not use evaluator oracle fields.
3. Dataset interface: SourceWorld itself is intentionally evaluator-only and presently in the same module; the final harness needs explicit partitioned delivery and a leakage-negative test. A code-only convention is not a security boundary.
4. Source controls: DEV seeds, PRIMARY seeds and hypothesis model limits are still unexercised. Source generation has not been independently reviewed, nor its code/hash pinned in an accepted science ledger.
5. Incomplete scientific arms: direct weight writer, 64-step warmup, fully trained neural comparator, exhaustive symbolic learner, whole-process cost instrumentation, persistence/tamper negative and preregistered scoring remain unimplemented. This gate supplies no model performance result.
6. Prerequisite decision: before first DEV or PRIMARY run, either demonstrate that the target claims are invariant to the observational symmetry (score only observable consequences, no independent role semantics), or register a pre-DEV protocol amendment with an additional observable physical anchor. Preserve the original preregistration and disclose any change.

State: SOURCE_IMPLEMENTED_LOCAL_SELFTEST_PASS; ENGINEERING_CI_UNVERIFIED; SCIENTIFIC_NOT_RUN; PRIMARY_NOT_ADMITTED; MERGE_NOT_AUTHORIZED. No accepted ref was changed.
