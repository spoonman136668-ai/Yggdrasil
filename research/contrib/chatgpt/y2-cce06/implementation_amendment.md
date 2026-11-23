# CCE-06 implementation amendment A — frozen before calibration sampling

**Study:** `Y2-CCE06-CAL` (calibration only). **Parent protocol:** `c2927c3b864e0514b8aeb47c83a72a593bddba01`. This is a design commitment, not an observation, fitted result or authorization to consume `Y2-CCE06-PRIMARY`. Existing CCE01–05 trial identities and reports are immutable.

## A. Independently generated calibration families

The generator is a separate evaluator-owned module, not imported by the learner or controls. It may use latent factors internally to create public experiences; no hidden factors, state cardinality, equations or family identifiers appear in training/evaluation event payloads. Each event contains only a bounded observation bit-vector, an integer action and the next observation. Family labels are manifest metadata for clustering/identifiability analysis, never features.

- Public action IDs `0,1,2`: 0 is no-action, 1 and 2 are priced interventions. Observations are 2 binary channels; hidden state contains 3 binary factors. Probe cost = 1 for actions 1 and 2, zero for action 0.
- `local_reversible`: public actions perturb local factor 0/1; causal influence propagates with bounded noise.
- `gated_nonlocal`: one intervention affects a distant factor only when an unobserved gate is active; its dependencies differ from the local topology.
- `action_null`: action choice has no effect on latent transition or observation; it is an explicit negative control, not one of the two positive families.
- `aliased_probe`: two latent configurations share the same passive observation while intervention 2 creates an observable consequence contrast; evaluator-only diagnostic verifies the contrast.
- Seeds: exactly `13,29,53,71,97`. For each seed/family, TRAIN has 5000 transitions, CAL-EVAL has 1000 transitions. Independent random streams keyed by (family,seed,split), no shared evolving RNG state. Actions are externally randomized and fixed independently of candidate predictions.
- All sample generation is disallowed until source code and manifests are committed and their SHA/tree recorded. A fixture-only seed `997`, at most 32 transitions, is reserved for unit tests and is **not** an experimental or selected calibration seed.
- Train/calibration are separated by independent RNG states; this is split disjointness, not proof of statistical independence of all consecutive transitions. Evaluation Brier clustering is by seed **and family**, not transition.

## B. Candidate predictive-state dynamics (implementation specification, NOT implemented)

The learner sees only histories of public (observation,action,next-observation). No latent label, graph, template, state count, generator module or evaluator API is available to it.

- Prediction: independent Beta(1,1) Bernoulli posterior for each of 2 observed output channels and each public action, computed **before** observing its target. State contexts are suffixes of the last <=8 completed public pairs, including an empty root. Storage is hard bounded by 128 committed states, 256 edges, 16 pending candidates per committed state.
- Split candidate: a child public-history context with at least 32 outcomes for every action under test and a parent with at least 32; a channel/action posterior difference >=0.08; both the child-parent difference and an improvement >=0.002 in average prequential multi-channel Brier over the most recent 32 *pre-split* child witnesses. Admit only if a simultaneous two-sided Hoeffding confidence bound at alpha=0.01 (Bonferroni over currently pending tests) excludes zero difference and the Brier improvement exceeds a 0.002 complexity charge. Failed tests remain as counterexamples, not admitted states.
- Merge: only if both contracts have at least 64 witnesses **per action**, each channel/action posterior difference <=0.03 and the two one-sided 95% equivalence intervals fit wholly inside +/-0.05; a recorded prequential non-inferiority check must show no increase >0.002 Brier over at least 32 held-out-in-time witnesses. Insufficient evidence means **do not merge**.
- Directed edge: record only a public observed action-conditioned transition between admitted contracts. Admit after >=16 public transition witnesses and positive predictive gain >=0.002 over a matched no-edge message ablation; never infer hidden graph truth from generator metadata.
- When full, evict the lowest accepted *prequential gain per byte*, break ties by witness count then lexicographic public-history key; never evict mandatory root state. Deterministic sort, caps, counters and rejection on malformed events. These choices may be falsified by calibration; do not retroactively change them within this experiment identity to rescue outcomes.
- Checkpoint: canonical sorted UTF-8 JSON fields `schema,version,states,edges,pending,witnesses,policy,events`; SHA-256 integrity envelope; strict schema/range/aggregate semantic checks; cold restoration must reproduce predictions and policy choices exactly. Integrity digest alone is not authorization to trust a forged semantic payload.
- Selection policy: actions from 0/1/2, priced at 0/1/1; action utility from public predictive uncertainty reduction minus an explicitly metered action cost, no true latent-state access. Include no-intervention and action-shuffle ablations. No reward oracle.

**Capacity is a bound, not proof of computational advantage.** Future candidate implementation must exactly realize this amendment, or a new experiment identity must be preregistered before any calibration look.

## C. Fully fitted strongest comparator obligations

The CAL feasibility decision MUST include, all trained only on matched public TRAIN data and evaluated on identical externally fixed actions:
1. Action-conditioned HMM with learned transition/emission parameters, >=3 deterministic independent TRAIN-only EM restarts per candidate hidden dimension 2–8, convergence traces, no true latent initialization, TRAIN-only dimension selection.
2. Learned PSR action-observation operator control with train-fitted state rank/capacity selection and genuinely recurrent operator updating, not a relabeled suffix table.
3. Full-context suffix table with TRAIN-only depth selection from 1..8.
4. Compact recurrent neural state estimator fully fit on public streams with TRAIN-only early stop, not a fixed/random reservoir or fixed features.
5. Active Bayesian costed intervention policy with posterior updates, matched budgets, TRAIN-only policy calibration and a cost/accuracy Pareto frontier, not uniform random probing.

Controls may use greater resources when justified. Matched-byte and matched-compute variants are **additional**, not replacements. Do not score CAL-EVAL until all applicable strong controls and identifiability checks exist.

## D. Qualification and stop conditions

A code commit alone is ENGINEERING UNVERIFIED until focused, negative, full final Windows/Ubuntu, source-atlas and exact-SHA checks pass. A working generator or a single baseline is **not** the calibration gate. If source custody, sealed primary disjointness, strong controls, intervention identifiability, training convergence or feasible headroom are missing: `CALIBRATION_NOT_READY`; do not create or access protected primary data. No runner dispatch, merge or promotion is authorized by this amendment.
