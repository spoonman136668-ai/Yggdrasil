# WSCM-01 — Wake–Sleep Causal-Signature Memory (research-only preregistration)

Status: PROTOCOL CANDIDATE; SCIENTIFIC FIRST-USE NOT AUTHORIZED OR EXECUTED.
Date: 2026-11-21.
Source baseline: `spoonman136668-ai/Yggdrasil` accepted `main` commit `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
Related but NOT inherited: coordinator PR #1278; functional retention PR #1329; stopped CASP-01/02 PR #1362.
Architecture contract: `research/architecture/yggdrasil-north-star.ice` (main blob `84358ec54c0e7eba6b6f830e0b4d2755920281cb`).
This document does not amend the existing learner, Genome, source-world evidence, accepted branch, owner state, or deployment interfaces.

## Falsifiable objective
Test whether fixed-capacity phenotype role signatures coupled to bounded sleep consolidation preserve old causal functions when action IDs and environment regimes change.
Aim: >=30% fewer charged steps-to-competence on unseen action-ID mappings than the strongest fully trained matched control; <=0.01 Brier degradation across 10x evaluation horizon / 5+ regime shifts; per-step latency <=1.15x matched baseline; zero spurious Genome promotions in 10% random sensor/action noise negative control. At most two *charged* probes per new action is a separate secondary gate, not an assumed property.

## Semantics and complexity corrections
A binary Hamming-distance signature is NOT conventional MinHash. Select and freeze either (a) a true minwise sketch with an appropriate estimator, or (b) a deterministic binary interventional-delta signature with exact Hamming/collision analysis. Do not call (b) MinHash without defining a valid minwise construction.
`do(a)` is an actual interventional probe only if action selection is controlled, the outcome is charged and logged, and confounding / unobserved state assumptions are stated; an observed action-delta correlation is not automatically a do-calculus estimate.
O(1) applies only relative to *fixed maximum* signature bits, local blanket cells, probe basis, ring size, per-bucket occupancy, eligible entry capacity, and bounded eviction/promotion work. A 128/256-bit signature does not alone guarantee constant-time candidate search. Fixed limits plus deterministic overflow/fail-closed behavior are mandatory.
The 12-cell blanket yields C(12,1)+C(12,2)+C(12,3)+C(12,4)=793 possible nonempty conjunctions before value assignments; selecting subsets and hashing at most a fixed budget is necessary. Counting Bloom filters support approximate membership, not exact conjunctive causal identification; test false positives and count saturation.
A 512-transition reservoir caps evidence, not automatically O(N^2) anti-unification over every bucket/trajectory. Cap number of candidates and comparisons and account for worst-case charged compute.

## Candidate mechanisms (development only)
Wake: phenotype-only role binding from a fixed 128/256-bit interventional signature; <=4-way conjunction candidates limited to <=12 local cells; W=16 fixed eligibility ring with integer decay and surprise-trigger-only bounded retrospective attribution. All online mutations confined to phenotype. Unknown or ambiguous role -> unbound, charge an authorized probe or abstain; no optimistic Genome alteration.
Sleep: deterministic trigger every 100 surprises or at episode boundary; surprise reservoir <=512 and historical charged anchor buffer <=256, with regime-stratified coverage and unbiased selection within each stratum. Historical anchors are mandatory for the retention gate.
For each bounded phenotype entry, compare masked/unmasked charged prediction loss on identically frozen replay samples; decrement TTL only for <=epsilon degradation. Protect historical high-charge rare exceptions from eviction. Counterfactual eviction measures *model dependence under masking*, not a physical intervention or proof of causal necessity.
For survivors, optionally anti-unify typed *acyclic* causal trees of depth <=6 with fixed candidate and tree-size caps, excluding concrete action IDs. Genome promotion requires all three: compression delta MDL < 0 including operator+index+exception costs; invariant success on >=2 genuinely distinct action mappings or seeds with held evidence; candidate masking causes >=delta_min deterioration on held multi-regime evidence. Training/replay data must not also be counted as held confirmation. Contradicted existing operators are marked CONTESTED, never silently overwritten.
Sleep writes are **disabled by default** in all source-free prototypes; promotion to real Genome requires separate owner authorization and the frozen qualification gate. Phenotype-only reset/prune must preserve old functional readouts.

## Required exact pre-first-use freeze (BLOCKER until recorded)
Freeze before **any** scored or protected world use: SHA/tree; dependency/env/runner versions; original source custody; exact fields/encoding of signatures; probe basis and charged observation contract; LSH hash family, Hamming threshold, collision resolution and fixed bucket capacities; blanket selection and Bloom geometry / false-positive budget; eligibility likelihood-ratio estimator and surprise threshold; TTL/epsilon; candidate caps and deterministic overflow policy; MDL code lengths; delta_min; genuine regime mapping definitions; seeded stratified reservoir policy; adaptive/sleep timing cost charges; seeds; train/hold/test partitions; stopping/consumed-trial ledger; strongest baseline hyperparameters; fixed paired statistical comparison and minimum sample size. Do not choose values after seeing held scores.

## Three-arm matched design
A: Existing tournament/action-indexed Yggdrasil baseline.
B: Wake routing + Bloom + W16 hindsight, sleep disabled.
C: Full B with bounded counterfactual eviction, skeleton promotion, and reset.
Run on same source, seed splits, charged probes, environment transitions, information exposure, wall-clock / compute accounting and retention query budgets. Include fully fitted conventional and exact symbolic controls if they are stronger than A; strongest control defines scientific pass/fail.
Tasks: ygg-act01 action-identifier remapping; ckad47 four-way composition; ygg-cap02 delayed/long-horizon retention. Verify exact task implementations and interfaces against current source before integration: these labels in the handoff are NOT evidence that a callable benchmark exists at the pinned main.
Per regime, measure: charged probes until stable competence, held Brier (initial and after 1/5/10 shifts), four-way conjunction held accuracy, historical catastrophic regression count, peak and steady-state bytes/bucket sizes, p50/p95/p99 and worst-case step time, sleep wall time amortized per step, Genome promotions/spurious promotions, old-regime cold restore and 10% noise negative control.

## Veto and disposition
Any old mastered regime Brier delta >+0.01 at the specified 10x horizon, violation of a previously accepted stricter safety fence, unbounded growth, source-custody ambiguity, permission drift, or spurious noise-triggered Genome promotion -> NO-GO, retain baseline. Do not retroactively narrow the population or tune on held test results. All negative outcomes remain recorded.
Research-only source-free unit tests are NOT scientific success and are NOT permission for first-use, accepted branch updates, merge, Genome writing, autonomous dispatch, CI runner registration, or deployment.

## Qualification and reporting
ENGINEERING: exact candidate SHA/tree/platform runner, negative/focused tests, *mandatory complete final regression on candidate*, memory and latency profile; PASS/FAIL/UNVERIFIED.
SCIENTIFIC: cohort/seed and matched A/B/C/strongest-control raw metric receipts; cold retention, transfer, composition, promotion/noise and budget gates; PASS/FAIL/UNVERIFIED. No claims before verified runs.
DEPLOYMENT: .ice/source manifest/digests and owner sign-off/authority, accepted-ref custody; PASS/FAIL/UNVERIFIED. Research PR is draft, unmerged by default.
