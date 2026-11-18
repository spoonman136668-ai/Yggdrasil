# CKAD29 — Compositional causal structure and cumulative retention

**FROZEN DEVELOPMENT_MIXED / SCIENTIFIC_PASS=false / UNMERGED / NO DEPLOYMENT**

The accepted Yggdrasil main is unchanged at `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. The source is the same native cumulative learner carried on CKAD28; this isolated external synthetic experiment does not alter the accepted model.

## Experiment and original receipt

Before evaluating, the exact protocol was committed at `022d7477de56bb2793b52d2ae3a02e86bbf73bdd` and source was locked to Git blob `f32f523766368f1c7ea6cc387c5bb663e6a17282`. The first scored result came from [run 44321333682](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44321333682): focused non-B native qualification, three-seed primary Linux run, then independent cross-OS Windows replay, all successful. `result.json` is preserved from the original Linux scoring log without retuning or rerunning the source cohort to choose a winner.

Three independent seeds supplied 432 total public primitive action/outcome observations to existing native slots. At a fixed previously unseen set of 96 composite examples, the task publicly disclosed XOR-of-three or majority-of-three composition. No held outcome was supplied for training. Six subsequent native primitive fits created memory pressure; old forecasts, a cold checkpoint restore, and local contradiction quarantine were checked. Conventional and exact-Bayesian arms saw the same public primitive training witnesses.

| Arm | Mean held Brier (lower better) |
|---|---:|
| Native composition | **0.2395833333** |
| Fully trained conventional polynomial logistic | 0.3131535851 |
| Fully trained conventional smoothed frequency | 0.2500000000 |
| Zero-information sham | 0.2500000000 |
| Fully inferred exact Bayesian grammar | **0.0000000000** |

The native learner gained **0.0104166667 absolute Brier** against the stronger fully fitted conventional control, insufficient for the +0.03 required improvement. It beat the strongest conventional control in just **one of three seeds**. Its held primitive forecast coverage was **0%, 33.3%, 33.3%** by seed; untouched primitive forecasts, cold restore and scoped contradiction quarantine nevertheless passed across three cases. This is a narrow memory-safety signal, **not generalization to reliably unfamiliar causal rules**.

The exact Bayesian control predicted every held outcome correctly within the declared 704-rule grammar. Yggdrasil's representational abstentions are a substantive gap, not an excuse to weaken the control. The original classification is **DEVELOPMENT_MIXED**, but the preregistered **DEVELOPMENT_GO gates FAILED** and this candidate must not be promoted or tuned on the consumed cohort.

Independent scoring/accounting audit: `python -B research/contrib/chatgpt/CKAD-29/independent_audit.py` (checks saved result without rerunning B). Original source: `campaign.py`, preregistration: `prereg.json`, provenance: `provenance.json`, sealed score: `result.json`.

**Scientific implication:** Preserve the learned native memory foundation, but prioritize supported extrapolation/representation of latent causal structure with genuinely unfamiliar operators, grounded knowledge and exact model controls. Additional trials require a new preregistered disjoint cohort, not post-hoc modifications of this experiment. No protected native first-use, automatic controller promotion, deployment, merge or scientific acceptance occurred.
