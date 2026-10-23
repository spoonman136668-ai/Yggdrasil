# Mass Research R10-I — Unknown-action-address information screen

**Frozen prereg FIRST.** This is a source-only symbolic challenge and not a new R10 causal environment. Base: Mass R10-F exact source `d31c8d00ccc2bb00f098b87097610329637a37f6` ([PR #423](https://github.com/spoonman136668-ai/Yggdrasil/pull/423)); independent Yggdrasil learner R10 remains separate [PR #422](https://github.com/spoonman136668-ai/Yggdrasil/pull/422). Commit this file alone before any proof/test implementation. Preserve previous frozen proofs and original R7/R9 negative outcomes byte-for-byte.

## Exact new question

Under the R10 prospective **32-public-probe budget**, is an environment feasible even if the learner is not told which of **two legally addressable probe actions** actually reveals a hidden causal distinction? Quantify the difference between a privileged policy knowing the active probe address in advance and a fixed legal plan that must be committed **before** that hidden address is revealed. Do not confuse known-address, source-law-aware Bayes error with a deployable learner.

## Frozen structural contrast

Two legal probe IDs: `probe_0` and `probe_1`. Two possible hidden address assignments: in setting `active=0`, `probe_0` yields independent Bernoulli consequences with probabilities `p` under structural hypothesis `H0` and `q` under `H1`; `probe_1` is completely non-diagnostic, probability 1/2 under both hypotheses. In setting `active=1`, swap the action IDs. The learner **does not see the active address**, and never receives the hypothesis label. Each legal probe consumes one episode and produces one delayed *public* binary consequence; the exact oracle calculation abstracts away the >=2-step delivery latency and therefore **cannot certify temporal credit assignment or action-dependent costs**.

For a specified fixed allocation `n0+n1=32`, use the optimal **privileged** likelihood-ratio oracle that knows `p,q` **and** the active address. Its equal-prior error in an active assignment is exactly

`R(n,p,q)=1/2 * sum_{k=0..n} min[Bin(n,p)[k],Bin(n,q)[k]]`

with `n = n_active`. Silent-probe observations provide zero mutual likelihood contrast. **This is an optimistic lower bound for a real unknown-address learner**, not its reachable accuracy. Evaluate the worst case `max(R(n0,p,q),R(n1,p,q))` over hidden address assignments. Exhaustively enumerate **all 33** fixed allocations to identify the minimax oracle-known-active bound; ties choose the closest-to-even split, then smaller n0. Compare to the oracle that *knows the active address before planning* and allocates all 32 probes to it. This is a fixed **non-adaptive** allocation screen only: do **not** call its optimum a lower bound on arbitrary adaptive policies, which might sequentially gather information and act differently. Do not claim source-level identifiability has been established merely because one idealized fixed plan passes.

Frozen exact contrast families (all abstract, **not actual R10 prospective cohort sources**):

- `STRONG`: p=1/4, q=3/4
- `MODERATE`: p=2/5, q=3/5
- `WEAK`: p=9/20, q=11/20
- `RARE`: p=0, q=1/64
- `NULL`: p=q=1/2

Use only exact `fractions.Fraction`, `math.comb` and Python standard library; no Monte Carlo simulation, PRNG, source generation, model training, supervised fit, source role consumption, protected holdout, first-use, or credentials. Report integer numerator/denominator, approximated decimal clearly marked, best allocation, per-address oracle lower bounds, and all-32-to-unknown-single-probe worst case.

**Predeclared explanatory screen:** ideal error <=5% after 32 probes. It is diagnostic context only, **not** an amended R10 native acceptance threshold. For the strong toy family, a near-even fixed split may satisfy 5%; moderate/weak/rare should fail. Even a strong-world symbolic PASS must not be represented as a genuine R10 source certificate.

## Required falsification tests / engineering qualification

- Prove identity and symmetry for swapping probe names; prove zero samples and silent-only samples leave a 50% prior error.
- Prove every candidate allocation sums to exactly 32, minimax minimization is exhaustive, and worst-of-two risk is no less than best-known-address 32-probe risk.
- Exact ideal strong/moderate/rare outcome checks; reject negative counts and non-Fraction probabilities.
- Assert no actual `source_generator_created`, `scientific_first_use`, `controller_admitted`, `observed_cohorts` or original data alteration.
- Frozen-file SHA/first-commit proof, four additive-path scope (protocol, proof, tests, dual-OS CI), clean checkout, original result logs archived and checked cross-OS. Preserve any failures; do not retune frozen test expectations.

**Authority and answer:** Only the live, authenticated CKB-plane may admit an independently born R10 causal source and run science. This entirely mathematical challenge cannot establish the actual source's causal structure, active probe address, delayed-feedback validity, identifiability with finite probes, cost budget, signed original first-use or model superiority. It must report `ACTUAL_R10_SOURCE_CERTIFICATE=NOT_ESTABLISHED` regardless of toy results.
