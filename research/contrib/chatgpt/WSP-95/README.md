# WSP95 — noisy, partially observed causal sensor learning

**Isolated development. No accepted Yggdrasil model, no FORGE loop integration, no merge or deployment.**

WSP94 (draft PR #1012, exact qualified source `602ab9ca8b0033fb3873d113826f9f730119379c`) achieved 400/400 unseen two/three-intervention composition goals, **tied both independent symbolic and fully trained conventional controls**, and learned trivially observable XOR action effects. This pilot deliberately removes the clean observability of effects while keeping the cost small.

## Frozen prospective experiment

Preregistration-only commit: `5b9bf6780a2073ed3223892ca0582cfdc1288d8f`, before any WSP95 generator/learner code or public/reserved generation. Original seeds, all source definitions, selection policies, matching budgets, strong controls and pass/fail metrics are fixed in `prereg.json`.

Each synthetic world has six opaque actions, a hidden group of five stable causal sensor channels among seven total channels, and two exogenous nuisance channels whose before/after values may change spontaneously. The observer does **not know which five are causal**. Each action has a concealed five-bit XOR effect projected into the stable sensors. During every intervention, stable after-measurements are corrupted independently with 12% bit-flip probability, and nuisance after-measurements are randomized. Every policy sees only the chosen action ID and seven-bit *before/after* sensor readings. No learner is passed the causal mask, true hidden effect mapping, world generator state or target-originating action subset.

**Important causal claim boundary:** These are randomized experimental *observation errors and exogenous sensor drift*, not a latent variable that confounds choice of treatment and outcome. WSP95 does **not** establish causal identification under unknown confounding.

## Matched-action-budget learners

All three probe policies conduct **exactly 30 original interventions per world**:

- **Direct numerical learner with bounded active selection:** Writes integer flip-count weights for each action/sensor from actual observations. Initially samples each action, then chooses the least sampled action, breaking equal-coverage ties by empirical sensor uncertainty. After sampling it ranks all seven sensor channels by average stable response across actions, chooses five putatively causal ones, and estimates per-action XOR effects by majority vote. A frozen subset planner picks at most three actions to reach target states; exact goals preferred, then minimal Hamming error as a fallback.
- **Uniform-coverage policy:** Identical direct writer but one observation per action in round-robin, five each. Given this symmetric design, the active learner also tends to allocate five per action; **there is no honest expected active-learning sample-efficiency gain over uniform**. Report both. Do not call an exact tie an improvement.
- **Random-coverage policy:** Identical direct writer but draws actions pseudorandomly with replacement under the same total 30-intervention budget. All three policies access **common potential outcomes** keyed by (world seed, action, within-action trial number), so choosing the same action trial produces identical noisy evidence. This isolates the difference in probing strategy rather than artificially different sensor-noise worlds.

Controls with the **identical active-policy observations**: an independently implemented symbolic histogram and parser; a fully trained 120-pass, seven-head, one-hot logistic-gradient model with no additional observations; and deliberately wrong action-ID association. There is an evaluator-only exact oracle ceiling, never passed to a model. Both fully trained and independent symbolic controls are permitted to tie or outperform the direct candidate. No supervised vocabulary/token decoder, transformer or next-token foundation is used.

## Unseen consequence test

After each policy finishes 30 probes, each model receives **35 fresh goals** made from every pair and triple of the six actions. The generating action subset stays hidden. Model responses are source-free action plans, not predicted correctness labels; the evaluator executes these plans in the *real hidden noiseless world* to determine whether the stable target is achieved. All methods' plans, source observation hashes and goal request hashes are SHA256-frozen **before any hidden truth is inspected or outcomes are scored**. Each world's candidate weights are checksum-snapshotted and restored exactly. Replayed/unknown trials and tampered states must fail closed.

Public original development: seeds 95011–95022, **12 worlds ×35 goals =420**, 30 probes per policy/world (360 per policy). Passing requires ≥270/420 direct, ≥76% learned true effect-bit agreement across worlds, correctly identify all stable channel IDs in at least 8/12 worlds, fully trained conventional ≥230/420, candidate ≥5 above random probing and ≥90 above wrong action binding, within 80 of the conventional, exact independent symbolic parity, exact cold/tamper/unknown source qualification and full CPU/source budgets. Any failed check is **`PUBLIC_NOISY_CAUSAL_SLOTS_NEGATIVE`**; the 20 reserved worlds must remain untouched.

Only if both Ubuntu and Windows public reports qualify as positive may the source-controlled original receipt be created. Then source-only G29 reanchor changing exactly the three atlas files, mandatory all WSP80–WSP95 tests and full Yggdrasil root regression on the exact tree on both OS, and a once-only reserved development test (seeds 95101–95120, **700 goals**) are eligible. The reserved DEV condition remains limited to original workflow attempt 1 and exactly precommitted seeds, not independent scientific acceptance.

## What passing would and would not show

A positive demonstrates that direct numerical evidence counts support **noisy effect denoising, hidden channel selection and compositional planning** in a small, stationary XOR simulator, not causal learning in an open physical world. The planner is algebraic and fixed. The strong conventional model and exact symbolic histogram are expected to match if noise is adequately averaged. Whole-process, model-fit and planning CPU are separately recorded; training epochs alone do not establish matched-compute superiority.

WSP92 and WSP93 broad language-QA development **negative findings remain unchanged** and their original SQuAD DEV questions remain unconsumed. WSP94 reserved synthetic seeds are consumed. No user Library artifact, paid API, new runner, scheduled task, controller, accepted-main update or production promotion is authorized.
