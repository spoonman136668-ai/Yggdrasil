# ITD-02 V31 — prospective public-history detection / independent holdout preregistration

**Gate:** frozen design and data-separation boundary, before training, detector construction or test results. Stacked on unmerged V30 PR #617 exact head `94dbd1ccda2095eb2f087c244647ebfc9656e007`. V30 exact-source Windows/Linux run #40692513758 passed 2/2, but frozen V26 failed detection latency on all three previously untested synthetic mappings (H1=7,H2=5,H3=5 rewards; <=4 required). V25/V26/V28 negative classifications remain unchanged. V31 is *not* another rethresholding of the 4-event error-vote detector.

## Research question
Can a small prospective public-history change detector infer meaningful reward-regime changes, retain an independently protected original source bank, and recover old knowledge without explicit source/target labels, while surviving genuinely held-out synthetic regime laws? A central hand-engineered selector is not spontaneous native-cell cognition. No current test constitutes unknown-world scientific first-use.

## Freeze separate discovery and test partitions
Development may use only the original source law, synthetic T1/T2 and H1/H2/H3 regimes **already exposed by V23–V30**, plus predefined unchanged-regime and multi-change controls. Any model design, configuration, thresholds, feature transform, statistical calibration, stop rule, or parameter search must be decided entirely on this development partition.

The final held-out family is defined **now** but must not be executed, inspected for performance, or used for training/selection before the detector code and all acceptance choices have been committed and pinned:
- Q1: `0.15 + 0.37*(a-b) + 0.62*(1 if ((c+2*a+b)%4 in (0,3)) else -1) - 0.08*c*b`
- Q2: `-0.25 + 0.41*(b-1) + 0.57*(1 if ((2*c+a+3*b)%5 in (1,4)) else -1) + 0.19*(1 if c==a else -1)`
- Q3: `0.05 - 0.23*a + 0.31*c + 0.54*(1 if ((c+1)*(b+1)+a)%3==1 else -1) - 0.12*b*c`
Here `c` is index of legal public cue in the original four cues, `a` and `b` are indices of actual first and second legal actions in the original three actions. These are independent formulas but not independent unknown causal worlds: the same 36 familiar public context tuples are reused. Do not infer any novelty beyond unseen reward laws.

## Candidate information and causality
Candidate receives only cue, actual selected first action, actual selected second action, observed public terminal reward and its own predictions/checkpoint. No source/target identifiers, task boundary, evaluator outcomes, secret epoch length, unchosen action reward, future feedback, replay of hidden labels or oracle advice. Preserve the 576 public observation source-pretraining protocol, protected source SHA and an independently adaptable fast bank if used. Specify and report all extra stored history/parameter bytes, CPU time, Python peak memory and total scalar edge messages. Any additional history learner must be disclosed as a non-native controller, with a separate 80-feature full-matrix ridge/CUSUM baseline and two-expert residual comparator.

## Acceptance gates frozen now
On every Q1/Q2/Q3 S→Q→S sequence, with 12 real public target rewards and 12 source-return rewards, require source memory selected within **4 return rewards**, no false source selections in matched Q→Q unchanged control after target warmup, >=10% lower return absolute error versus BOTH always-fast and strong conventional, lower 12-context action regret versus both, and <=10% relative target-stage error regression versus matched scratch fast. Independently compare all 3 known development families, longer Q1→Q2→S sequences, source-only no-change controls and a conventional Page-Hinkley/RLS switch. If any held-out latency or false-positive condition fails: `V31_HELDOUT_RETURN_REACTIVATION_NO_GO__NO_SCIENCE`; if those pass but matched controls or regret fail: `V31_HELDOUT_STRONG_CONTROL_NO_GO__NO_SCIENCE`; if source/target resource or other long-sequence integrity fails: `V31_HELDOUT_INTEGRITY_OR_TARGET_REGRESSION__NO_SCIENCE`; positive only if all development, 3 independent withheld mapping families, conventional controls and full inherited V30→V12 regression pass: `V31_BOUNDED_HELDOUT_SYNTHETIC_RETURN_ENGINEERING_POSITIVE__NO_SCIENCE`. If sources, prereg chronology, cross-host identical canonical evidence, blindness or full strong controls are incomplete: `V31_ENGINEERING_INCOMPLETE__NO_SCIENCE`.

## Holdout governance
This gate only records prereg and immutable holdout contract, **no heldout executable, detector code, performance log or result**. The later implementation shall commit detector + dev-only tests first, freeze exact code hash, and only subsequently create a separate read-only heldout evaluator. Both Ubuntu 24.04 and Windows 2022 must verify an identical source exact head, same evidence SHA and chronological prereg. Do not change a failed V31 detector after inspecting Q outcomes and call it successful. A later V32 would need a completely new preregistration and unseen holdout partition.

No merge, first-use, original model weight promotion, FORGE/CKB-plane/control mutation, G29/write-proxy waiver, paid API or retail deployment.
