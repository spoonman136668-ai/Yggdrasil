# DG1-SL10 pre-execution arithmetic clarification

This note is committed **before the first prospective PR experiment** and does not change the frozen source, seeds, policy, metrics, numerical thresholds or the physical budget.

The original `prereg.json` budget item `actions_after_cold` mistakenly says **18 causal choices, two flips**. The frozen list of ten charged flips is `[6,14,22,30,38,46,54,62,70,78]`; in the 20-step interval with zero-based indices **60 through 79**, there are exactly **three** charged flips (62, 70, 78), hence **17** legal learner-selected causal actions. All other frozen totals remain unchanged: 80 charged steps per arm/world, 10 flips, 70 causal observations; 32 worlds × 9 arms = 23,040 paid steps, 2,880 charged flips and 20,160 observed causal consequences.

The physical policy is not permitted to select an action for any of the three flip steps. Preserve the originally committed preregistration and this independently timestamped clarification; no post-result adjustment to the experiment is allowed.

The phrase "independently implemented Bayesian memory" means a separate `ExactBayes` implementation using the same fully disclosed public program grammar and paid observations; it does not imply independently qualified scientific replication, identical compute, or matched information between *different* active policies. Within each replay pair, the separately charged action/state/outcome sequence must be identical.

No CI result or primary scientific outcome has been observed as of this pre-execution clarification.
