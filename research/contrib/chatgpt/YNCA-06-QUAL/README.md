# YNCA-06 — qualify four frontier ideas before tuning

**Status: EARLY-STOP ANALYTIC SCREEN COMPLETE. Four original toy fixtures show no unique gain over cheaper controls. No actual Yggdrasil native model training, no scientific pass.**

## Why this exists

Four novel mechanisms were proposed in a user-provided research memo:

1. Sheaf-Cohomological Defect Repair (SCDR): mint hidden state from contradictions on action loops.
2. Allosteric Chemical Reaction Network (CRN) Morphogenesis: context-dependent composition changes through reaction kinetics.
3. Internal Popperian Falsifier Co-Evolution (IPFC): an adversarial internal counterexample generator targeting indistinguishable causal hypotheses.
4. Localized Thermodynamic Melting (LTM): contradiction-local updates and memory protection via thermal annealing/cost routing.

Before building large new components, test whether their *provided minimum experiments* can show an advantage over a strong matched control. This source-free qualifier is a falsification of overstrong claims about those fixtures; **it does not implement or refute the full proposed mechanisms**.

## Results (original output unmodified)

| Proposal | Frozen screen | Result | Decision |
| --- | --- | --- | --- |
| IPFC | Exhaust all 64 YNCA05 Boolean laws; select up to 2 distinct noiseless probes by max disagreement or exact 1-step EIG, shared evidence and tie break | 64/64 same paths, residual 16 laws, no unique gain over EIG | Do not train IPFC on this same independent-bit world; require structured hypotheses/novel worlds and coevolved falsifier |
| SCDR | Fully visible deterministic 3-cycle graph; 5% independent sensor flip, 100 paired reads; compare naive ever-different flag with exact binomial noise gate | Graph cycle rank1 with no hidden state; naive null false alert 99.995%; calibrated binomial threshold16 null FPR 2.654% | Specify actual sheaf cohomology and distinguish non-Markov hidden state from observation noise before algorithm build |
| CRN | 3 hidden equiprobable contexts without cues; minimal multiplicative reaction concentrations vs same-information exact Bayesian update | No-cue context bound 1/3; Bayes/replicator difference zero | Specify reaction ODE, topological composition updates and measured benefit; a renamed Bayes update is not new intelligence |
| LTM | 100 independent binary causal rules; exactly 20 changed with direct addressed truthful feedback | Sparse direct edit: 20 writes, 0 changed errors, 0 untouched forgetting | No thermal optimization on this fixture; require coupled/noisy updates, full resource measurement and EWC/sparse controls |

**Clarifications:** SCDR's graph cycle rank is *not* the first cohomology group of a specified sheaf. The example refutes conflation of graph loops with hidden states; a genuine sheaf method needs formal stalks, overlap maps and proof of an obstruction. The 99.995% false alarm applies only to the explicitly tested naive repeated-outcome rule, not to all possible sheaf algorithms.

Landauer's physical bound pertains to logically irreversible erasure under thermodynamic conditions, not automatically to CPU operations or every modified model bit. A software-temperature coefficient is an algorithmic analogy until physical energy is measured.

### Qualifier for any expensive successor

**One shared prerequisite:** freeze hypothesis, source/grammar, seeds and unseen contexts; ensure full training of strong conventional baselines with same information, permitted actions, model capacity and whole-process compute. An exploratory diagnostic does not authorize owner integration.

- **IPFC:** genuinely structured, previously unrepresented causal rules; coevolving generator must produce fresh validated counterexamples. At matched action/information cost, target at least 20% fewer distinct probes than exact EIG, no >30% redundant actions, and no more than 5% downstream reward loss. Otherwise NO-GO.
- **SCDR:** define a real sheaf and its restriction maps, demonstrate obstruction not induced by 5% sensor noise; FPR <=5%, parity-state TPR >=95%, no more than 2x latent-state inflation. Compare fully trained two-state HMM/POMDP and history predictor on unseen worlds; absent improvement NO-GO.
- **CRN:** specify mass-action equations, kinetic constants, stability/cycle constraints, and a topology-changing reaction observable. Adapt within 20 observations; retain at least 95% reward of an exact Bayes permutation mixture *and* improve whole-process cost at least 1.5x, or exceed transfer under equal compute.
- **LTM:** frozen 6-world interference suite with coupled ambiguous rules; unmodified rule degradation <=5%, changed rule recovery <=2x strong sparse update/EWC controls, and >=1.5x total efficiency at matched reward. Record actual CPU/GPU process cost separately from physical erasure-energy claims.

These thresholds were frozen before analytic output in `prereg.json`. A successor must have its own independent prereg/source/heldout; do **not** tune this consumed screen.

## Exact audit and reproduction

- Accepted `main` fork: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; unchanged.
- Pre-result prereg commit: `559f84cb80f4e54e0de27eb3999bb2923645dd81`.
- Exact original source commit: `d935c1dcc545c3c5e90167372cd96d4be1865dea`; SHA-256 `8c606125e484ef8be7f669e56b6fd2d421730b31a0969d4cf1feaeb3cd84ee45`.
- [Linux and Windows frozen run #44289572607](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44289572607): **9/9 focused PASS each OS, byte-identical 3,834-byte output**, original result SHA-256 `8800a1c615cc831c3f46f7cbd4c7954bc23fd0bb27abfc45d844c921e003665f`.
- Result committed unchanged `2d88531f0a90aa7cd19f75022c157f36ce7bdd5b` at `result.json`.
- Run: `python -B -m unittest discover -s research/contrib/chatgpt/YNCA-06-QUAL -p 'test_*.py' -v` and `python -B research/contrib/chatgpt/YNCA-06-QUAL/qualify.py --run`.

## Disposition

This completes a **cheap early-stop gate**, not four independently trained algorithms. For actual native learning, prioritize strong grounded knowledge and structural concept invention in the independently owned CKAD learner. Keep this research unmerged unless separately qualified and explicitly admitted. No authority to mutate accepted research, native owner, schedulers, controllers or protected scientific first-use.
