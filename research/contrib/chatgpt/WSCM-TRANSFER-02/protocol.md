# WSCM-TRANSFER-02 — Distinct causal-function and action-identity transfer (research-only protocol candidate)

Date: 2026-11-22  
Status: DESIGN-PREPARED; NO SCIENTIFIC FIRST-USE; NO NEW TRIALS EXECUTED  
Owner lineage: [Yggdrasil Amalgam #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278); contributor [WSCM #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364).

## Immutable starting evidence and why this is a new test

- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Amalgam base: `86264b41a08d49f558418c0fba367f3a2636befa`, tree `ac2a2596555b490fc3ebdf16c1b5039ebb13d8b5`.
- WSCM previous result: `f68659aaaafeced6951b2d72d6d5d8a658003d4b`, tree `da4c5681fa615acc32bbeb54ecc49e2c7f4b65c5`. Frozen evidence is in `WSCM-PROBE-01/`; the 288/288 exact HMM parity is a negative novelty result, not a basis for a new selector claim.
- Prior WSCM-EPOCH-02 cohort is incomplete/invalid (three completed negative seeds and one STARTED-without-COMPLETED seed); do not resume or reuse it. Existing W16 epoch selector was stopped. OBS-01 established public observability limitations. Two binary probes cannot uniquely identify sixteen arbitrary equiprobable roles.
- The accepted `main` does not contain the Amalgam native episode learner. Native episode implementation on the Amalgam lineage is `yggdrasil/native_episode_experience.py` Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`; it accepts only binary `x1`/`x2` and paired binary views. Its `engineering_fixture_only` observations are not authenticated controlled interventions, and it cannot currently admit arbitrary external action IDs. **This is a hard interface and source-custody gate.** An external ID wrapper is not proof of native ID transfer.
- North-star contract: `research/architecture/yggdrasil-north-star.ice` blob `84358ec54c0e7eba6b6f830e0b4d2755920281cb`. No conventional model, external teacher, Genome writer or competing learner may replace the native developmental substrate.

## Distinct falsifiable hypothesis

A **native-compatible, bounded causal-role/function representation**, trained from real public action-consequence witnesses rather than preloaded role labels or a two-state regime codebook, can (i) preserve separate learned functions through an A -> B -> A return, (ii) identify changed action identities using charged discriminating interventions, and (iii) transfer constituent causal operators to a *new composed law*, with lower held predictive loss and less charged adaptation than the strongest equally informed, fully fitted non-oracle comparator.

A positive result requires native learned state, an independently verified action-identity interface, genuine compositional transfer, cold preservation, matched evidence, and the preregistered performance gates below. Simply choosing between two already-specified laws, source-free deterministic routing, recalling a supplied old ID, or running an exact Bayesian HMM is not novel transfer.

## Pre-first-use study design (not yet frozen for execution)

- Start with paired public binary views and two-stage action/consequence episodes. Define a finite, typed grammar of learned causal relations (e.g., conjunction, parity, conditional gating, one-step transition and delayed reward dependency); **freeze the allowed grammar and operator cost before generating scored data**. Expose identical raw public features/outcomes to every arm, with no hidden regime labels, true role mapping, future outcome or generator code in model inputs.
- Training law A: acquire at least two learnable independent local causal operators, with multiple controlled observations each. Law B must alter the dependency graph or function truth table, not just rename action IDs or change a Bernoulli base rate. At A-return use a *different public action-ID permutation*; this is not permission to pass an ID-to-role map into the learner. Held C must contain an unseen **composition** of learned primitives with a distinct dependency pattern. Hold out further shifted/scrambled views for interference checks.
- Before any scored outcome, independently verify that the laws are functionally different by enumerating all input/controlled-action truth-table entries, their identifiable differences, and a set of informative witness probes. Retain observationally indistinguishable/no-identification cases as abstention negatives; impossible-to-identify cases cannot be declared failures of an otherwise information-limited learner.
- The execution harness may know the law and mapping **solely** to generate outcomes and calculate evaluation truth. Candidate/controls see only time-ordered public features, selected actions, outcomes and charged resource usage. Every proposed action must be executable within a source-authenticated interface; otherwise classify only as source-free DEV, not native transfer.
- Explicitly bridge externally numbered actions to native binary `x1`/`x2` **without revealing role semantics or silently collapsing distinguishable IDs**. If that cannot be done with a verified native interface, stop native qualification and use an isolated development adapter only, keeping its evidence separate. Do not modify the accepted learner to make the benchmark appear to pass.

### Required matched arms

1. **N:** Existing native cumulative learner, fully trained on the same public observations, with its original memory/repair behavior.
2. **T:** New bounded causal-role/function representation linked to native learned state, learning role bindings from witnessed differences, with explicit unknown/ambiguous abstention; no baked-in action roles.
3. **C:** Independently implemented exact Bayesian change-point/HMM control **when its hypothesis family is admissibly learned from training data**; if its laws are provided by an oracle, report as an evaluation-only information bound, never a normal comparator.
4. **F:** Fully fitted per-action/context and hierarchical Bayesian controls, and a conventional causal rule/decision-tree or symbolic grammar learner with equal representation budget and matched tuning allowance.
5. **Ablations:** T without historical readouts, T without compositional role matching, T without targeted interventions, and T without bounded retention protection.

Choose the **strongest non-oracle eligible control on validation** before seeing held results. For any adaptive arm, charge identical available information and action selection opportunities, including probes used for role identification; charge compute, hyperparameter search and stored model bytes. If a baseline requires capabilities unavailable to native, report this as an architectural capability gap rather than suppressing the control.

## Frozen decision thresholds (criteria now, exact implementation parameters still pending)

A scientific **PASS** requires all of:
- Unfamiliar C held **prequential transition Brier** at least `0.02` absolutely lower than the strongest non-oracle comparator, with paired 95% uncertainty interval strictly below zero; no selection of comparator after inspecting held outcomes.
- At least **30% fewer charged informative interventions to a pre-frozen competence threshold** than that comparator, across held action-ID mappings. The competence threshold, statistical unit and sample size must be frozen before any first use.
- Old A-return and 10x-horizon cold retention no worse than **+0.01 Brier** relative to the original frozen A readout, and no pre-existing stricter source safety fence violation, including the 10% sensor/action noise negative.
- Exact byte-identical model/readout checkpoint and functional forecasts after cold restore, deterministic provenance, no spurious Genome promotion, no unbounded growth, and a pre-frozen peak/per-step compute budget (target <=1.15x comparable baseline).
- Native interface validity and same complete source/witness custody on **both** supported OS platforms, followed by mandatory final full regression on the exact candidate SHA/tree. Owner acceptance and protected first-use are separate gates.

Failure to beat the strongest non-oracle control on either primary measure, leakage through action mapping, unsupported source provenance, insufficient identification information without abstention, or a breached retention/compute/safety fence -> **SCIENTIFIC NO-GO or INVALID**, never an automatic retune.

## Trial isolation and stopping policy

1. **Preparation only in this document.** Before generating any new scored evidence, commit a final machine-readable preregistration containing: exact source SHA/tree and dependency blobs, real source/runner authority, complete input field/interface mapping, learned-grammar definitions, laws/truth tables, action permuter, intervention/witness charge rules, training/validation/held partitions and independent random seeds, consumed-seed ledger, minimum paired sample size and confidence method, baseline fitting/search budget, all thresholds, checkpoint hashes, CPU/OS versions, timeout limits and immutable write-once STARTED/COMPLETED evidence paths. Reject unknown or previously consumed seeds.
2. Split by **law family, causal graph, action permutation and source cohort**, not just RNG seed, so C cannot be a renamed A/B case. Require a held fresh family never used in template selection or hyperparameter fitting. Freeze the evaluator/scorer and test its ability to reject label leakage and a deliberately non-transferable baseline.
3. Do not score, probe, dispatch a runner, access a protected world or call native Genome APIs until the final freeze and independently verified owner first-use authority. Source-free *static* contract tests may be prepared, but must not consume held trial outcomes.
4. Enforce pre-set maximum number of trials and interventions, memory/compute/time limits, one-shot seed consumption and fail-closed interruption. A STARTED seed with no terminal receipt stays consumed/UNKNOWN until independent custody resolution; **no silent replay, padding or fresh seed substitution**.
5. Report all per-seed/per-phase losses, abstentions, action counts, empirical evidence overlap, collision/false-binding errors, held transfer, 10x old-task drift, all ablations, controls and raw receipts, including negatives. Tests passing alone never means scientific learning.

## Explicit phase status and next implementation gate

- **ENGINEERING:** Protocol prepared and a separate illustrative static preflight implemented; 7/7 isolated source-free contract tests PASS on Linux CPython 3.13.5, with both original tested files verified against exact GitHub blob hashes in `static-test-result.json`. No T native interface adapter, scored source generator, final first-use freeze, source-qualified local training, or complete exact-SHA dual-OS regression. **FOCUSED STATIC PASS; FULL INTEGRATION UNVERIFIED.**
- **SCIENTIFIC:** No new experiment run; no superiority, general retention or unfamiliar transfer established. **UNVERIFIED.**
- **DEPLOYMENT:** No native production, accepted main, Genome, `.ice`, controller, runner, queue, CI, first-use or merge changes. **NOT DEPLOYED.**

**Next authorized preparation gate:** In a research-only seam, verify actual native episode and action-ID interfaces and implement the source-free falsification fixtures/negative controls; freeze complete scorer and candidate source **before** a first scored development trial. If action IDs cannot be represented without semantic leakage or unsupported native mutation, explicitly stop and report `NATIVE_ACTION_ID_INTERFACE_BLOCKED` rather than manufacturing a positive transfer result.

## Subsequent source-free static qualification checkpoint (2026-11-22)

The added `contract.py` is an **illustrative law-isomorphism negative test**, not a protected-world law generator or candidate-visible held cohort. Its A/B/C truth functions are genuinely unequal under every action-role permutation; `A_return` has fresh external IDs but the same underlying A law. The public request omits hidden roles, laws, and phase. Seven isolated static tests PASS, including a deliberately permuted-A false-novelty guard and invalid-ID refusal. Complete provenance is in `static-test-result.json`; both files' Git blob IDs match the locally tested bytes. **Do not train on these disclosed example laws and then treat the same functions as held transfer.** The real scored law families, source adapter, frozen hyperparameters, seeds, action budget, information-control boundary and owner authority remain unqualified. No new scored trial or protected first-use occurred.


## Subsequent source-free falsification hardening (2026-11-22)

The previous static contract accepted a falsified phase table where `C_composition` reused law A despite a separate unused C truth-function family being present. This is a **real preflight false-positive defect**, not evidence that a model learned or failed to learn. The source-only correction binds actual phase-to-law assignments, rejects nonbinary functions and action-ID type aliases, and applies a strict whitelist to the learner-facing request payload. A new deliberately adversarial suite rejects injected hidden `role`, `law`, `phase`, action-to-role mapping and future outcome, as well as a C family that is merely permuted A.

**ENGINEERING:** Original 7 plus new 7 isolated contract/falsification tests = **14/14 PASS** on Linux CPython 3.13.5; exact tested source and new test bytes are Git-blobs pinned in `falsification-preflight-result.json`. These are source-free and illustrative, not a protected scored cohort. **SOURCE-FREE FOCUSED PASS; full Linux/Windows regression UNVERIFIED.**

**NATIVE INTERFACE:** Original pinned `NativeEpisodeExperience.observe` still accepts binary `x1`/`x2` only, and its ledger is `engineering_fixture_only` without independently authenticated charged interventions. Strict external action IDs cannot be learned through this native API without a new, separately qualified interface. **NATIVE_ACTION_ID_INTERFACE_BLOCKED**. Do not smuggle a private role map through a wrapper or import this illustrative harness into a candidate.

**SCIENTIFIC / DEPLOYMENT:** No new scientific trial, new held seed, owner runner use, protection first-use, native mutation, or deployment. No measured retention/transfer gain; first use remains owner gated. Do not merge or promote from these tests.
