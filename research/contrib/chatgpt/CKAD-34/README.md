# CKAD34 — Select a native causal class from public source consequences

**External research-only; not accepted-model training or a new controller.**

Predecessor CKAD33R in [draft PR #1248](https://github.com/spoonman136668-ai/Yggdrasil/pull/1248) demonstrated that the existing numeric checkpoint/weight substrate can perfectly represent held out source consequences **when the correct quadratic class is supplied**. An equivalent conventional GF(2) model and exact Bayesian posterior also had Brier 0. CKAD34 removes that per-world class oracle, not the general family of conventional polynomial classes.

## Frozen question

Can Yggdrasil choose the smallest *consistent* native degree (1, 2, 3) using **only intervention outcomes** and compile its selected numeric representation into the pre-existing immutable `NativeContextAccumulator`, retaining it under interference and cold restore?

Four synthetic families: affine, two quadratic interactions, two cubic interactions, and cubic with an unknown quartic perturbation. Three independent native slots per family. No hidden class ID or hidden law coefficient is presented to the candidate.

Inputs: six non-token numeric bits (five observed context and one action). A full rank-42 cubic input design, generated *without outcomes*, selects 42 source intervention IDs from 64, six additional distinct source-only calibration IDs, 16 held IDs. Public source records are identical across every control. Four independent new slots each receive 42 source interventions for memory-pressure qualification.

Native class selection attempts `stage_update(max_degree=1)`, then 2, then 3. The first consistent degree is used to persist native coefficients and outcome-free support. Six calibration consequences can veto the slot (it then **abstains**, scored at probability 0.5); they never tune numeric coefficients. The admission decision is research metadata, not production authenticated source authority.

## Mandatory strong controls

- Independently implemented conventional minimum-degree GF(2) source/validation model on identical 42+6 public interventions.
- More-capable **fixed full degree-3** conventional GF(2) baseline, trained on the exact same source actions and outcomes.
- Existing unmodified `NativeCumulativeLearner`, 48 public witnessed interventions/slot, existing provisional degree model, same limited family knowledge.
- Fully fitted cubic-polynomial logistic baseline, source-only frequency, 0.5 sham and an **ungated compiled-native** negative ablation.
- Three independent quartic out-of-class negative slots plus complete checkpoint cold restoration, 64/64 old input retention after four fresh pressure slots, source ledgers, atomic contradiction rejection.

At each original seed: **744** source outcomes = 12 × (42 fit + 6 calibration) + 4 × 42 pressure. **192** held composite cases = 4 families × 16 held actions × 3 graphs. Two disjoint original pilot seeds **13741, 13742**, and reserved primary **23741, 23742, 23743** never automatically used.

## Frozen stop

Both original pilots must select the correct in-family degree in all nine slots, show ≤0.01 compiled-native Brier on the 3 in-class families with ≥95% primitive coverage, exactly match conventional selected-degree AND stronger full degree3 Brier, improve ≥0.10 over original native on at least one nonaffine family, and reduce selected-degree profile bytes for affine/quadratic by ≥10% versus forced degree3. Quartic admission must reject ≥2/3 slots with no confidently incorrect accepted predictions and Brier no worse than ungated. All source/cold/retention/contradiction controls must PASS.

**Even ENGINEERING_FEASIBLE cannot mean SCIENTIFIC_PASS:** choosing among 1, 2, 3 is a supplied conventional portfolio, and the strongest conventional baseline uses the same source data and features. No unrestricted class discovery, independent transfer, real-world intervention truth, or general intelligence is demonstrated.

## Evidence discipline

Preregistration commit `2bcd8d5927732caa4c71acf361d7f0a9daf54e47` was committed before this source. The original campaign Git blob, tests, independent audit and workflow must be locked BEFORE eligible pilots. `seal_pilot.py` independently recomputes **every held Brier and primitive confidence error** using only the original immutable evaluator captures, without importing the generator or native code. The two pilot results must be preserved byte-for-byte on the PR. No rerun of consumed seeds, no post-result threshold tuning, no automatic protected primary, merge, deployment, owner/Forge dispatch, or scheduled tasks.
