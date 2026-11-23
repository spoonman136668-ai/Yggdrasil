# Y2-CCE06 Statistical Successor Design B (PRE-DATA PROPOSAL)

**Status:** proposal only; NOT frozen, NOT authorized for sample generation, NOT a scientific result.  
**Target:** existing draft research PR #1369 branch `research/y2-cce06-calibration-protocol-20261123`.  
**Parent candidate:** `4d4fdd209fc0a3d461d958810df901082774eca6`.  
**Accepted main:** `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` (unchanged).  
**Supersession rule:** this document does not modify or reinterpret Amendment A. If adopted, it must become a new, versioned study/protocol identity. Old plan, generator and amendment remain immutable historical evidence.

## 1. Narrow the first claim, not its effect threshold

The first study should test **one nominated predictive-state split**, not simultaneous autonomous split/merge/edge discovery.

- Preserve the 0.08 minimum action-conditioned channel-difference threshold, 0.002 predictive-utility complexity threshold, alpha=0.01 family-wise error target, action-null and observational-alias controls.
- Use an isolated TRAIN discovery cohort to nominate exactly one parent, one child-history predicate, one action, and one output channel. Candidate choice and all model/threshold selection stop before confirmation data are created or viewed.
- The confirmation cohort evaluates only that fixed candidate/contrast in each of the two positive topology families: `local_reversible` and `gated_nonlocal`. This yields **M=2 confirmatory split contrasts** globally. Other actions/channels are reported as prespecified diagnostics, not additional opportunities to declare success.
- The contrast is child versus the **disjoint parent-complement**, never child versus the parent aggregate. One independent episode contributes one bounded episode-level contrast D in [-1,1] for the nominated action/channel, computed only when both context supports satisfy the frozen occupancy rule.
- The learner and its nomination process receive only public events. Family labels, latent state, graph template and evaluator diagnostics remain evaluator-only.

This is a narrower claim than the original all-action/all-channel structural test. It is a proposed new study identity, not a post-hoc relaxation of an existing result.

## 2. Independent episodes and discovery/confirmation

Each episode must be a genuinely independent reset unit:
- Fresh evaluator initial-state, action and sensing-noise streams derived from an immutable episode key using domain-separated derivation.
- Reset latent environment state at episode start. Do not continue one latent trajectory across episodes.
- Freeze a fixed episode horizon H before any registered sample. H must be selected by source-free occupancy simulation, not tuned from CAL outcomes.
- The same episode must provide adequate child and parent-complement support for the nominated action. Episodes failing a predeclared support/validity rule are counted as failures/ineligible in the denominator report; they are not silently replaced.
- TRAIN discovery episodes, calibration confirmation episodes and any later primary episodes have disjoint key spaces and independently sealed manifests.
- The learner may carry its learned memory across episodes for the later A→B→A retention study. However, the **structural confirmation statistic** is computed from immutable, independently reset evaluator episodes with the nominated structure frozen before confirmation. Retention is a separate sequential experiment and is not treated as independent split-test replicates.

Five seeds × 5,000 transitions is not an episode design. Count independent reset episodes, episode horizons, eligible-support rates and total transitions separately.

## 3. Split-confirmation power floor

For M=2 simultaneous two-sided confirmatory contrasts, family-wise alpha=0.01, an episode-level contrast D in [-1,1], and a minimum effect 0.08 above the decision threshold, a conservative Hoeffding planning rule targeting 80% probability that the lower confidence bound clears the threshold is:

`n >= 2 * (sqrt(ln(2*M/alpha)) + sqrt(ln(1/(1-0.80))))^2 / 0.08^2`

This gives **4,319 independent eligible confirmation episodes per positive family** (M=2 globally). This is a conservative concentration-bound planning floor under ideal independent episode assumptions, not a substitute for the exact frozen test or for occupancy feasibility. TRAIN discovery episodes are additional. The current five-trajectory generator cannot satisfy this unit/count.

A lower count may only be adopted if a new pre-data design proves its coverage and power using a justified, independently validated episode-level variance model and source-free simulations. The minimum practical effect, alpha and negative controls must not be weakened.

## 4. The 0.002 Brier requirement is a separate gate

Do not pretend a 32-event rolling window can confirm a 0.002 effect. Do not bundle six channel/action checks into a single uncorrected claim.

- Freeze one episode-level paired Brier contrast comparing the nominated split learner with its **same-information no-split ablation** on identical externally fixed action schedules.
- Keep the 0.002 minimum improvement and complexity charge.
- Use a mathematically specified, anytime-valid empirical-Bernstein confidence sequence for independent bounded episode contrasts, or a fixed-N method with a justified episode-level variance bound. Freeze its exact formula, alpha allocation, variance assumptions, stopping and max-episode cap in the successor amendment.
- Run source-free design simulations under null, boundary and alternative variance/effect scenarios before choosing H or the maximum episode count. Report the attainable-power envelope; if no affordable cap gives 80% power, record a pre-data no-go. No CAL data may be used to estimate variance for this design decision.

For perspective only: a worst-case distribution-free Hoeffding confirmation of a 0.002 bounded-episode effect would require millions of independent episodes. The 0.002 gate therefore needs a defensible variance-aware design, not an unsupported assertion that a short rolling window is enough.

## 5. Structural scope and hard limits

For this first study:
- Exactly one nominated split; at most one child state.
- No merge decisions and no edge admission.
- Keep deterministic 128-state / 256-edge / history-8 ceilings in the later learner contract, but they are not exercised as discovery search degrees of freedom in this first experiment.
- Action-null and aliased-probe controls remain mandatory; no hidden labels, oracle messages, true topology, generator code or latent cardinality reach any candidate/control.
- Split admission must pass both independent structural confirmation and the separate 0.002 Brier/complexity gate. Any missing support, convergence, custody, power, or negative-control failure is NO-GO.

## 6. Pre-data design-only gates

Before freezing this successor:
1. Specify H, the exact eligible-episode rule, episode-key derivation, reset semantics and manifests.
2. Implement a source-free analytical simulator for support/occupancy and the exact statistical procedure. It must not import `calibration_worlds.py`, use registered seeds, or write CAL/CAL-EVAL samples.
3. Verify family-wise coverage under the null and boundary; verify at least 80% power at the frozen alternative; test adaptive nomination leakage, episode dependence, missing context support and invalid/duplicate keys.
4. For the Brier gate, validate the empirical-Bernstein/variance-aware procedure mathematically and by coverage/power simulations over a declared variance envelope. Freeze a maximum independent-episode budget and stop as NO-GO/inconclusive if it is exceeded.
5. Cost the design in total episodes, transitions, wall-clock, memory and runner capacity. If the episode budget is not feasible, stop before registered sample generation.

**Do not generate registered TRAIN, CAL-EVAL, or PRIMARY samples during this design phase.** Source-free synthetic design simulations are allowed only after their own code and assumptions are versioned and hashed. No protected primary source or evaluator may be created or accessed as a side effect.

## 7. Current disposition

- Existing Amendment A and `calibration_plan.json`: **PRE-DATA NO-GO**, unchanged.
- Existing `calibration_worlds.py`: five continuous trajectories per family/split; not a qualifying independent-episode generator.
- CCE-06 split/merge learner: not implemented.
- CAL/CAL-EVAL/PRIMARY data: not generated or consumed.
- PR #1369: draft/unmerged; accepted main unchanged.
- This document: design proposal only, no sampling authority and no scientific claim.
