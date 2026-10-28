# V25 locked execution schedule and detector — before executable code

This supplementary specification extends existing preregistration in V25 draft PR #610, head d3af4f93f6a34f7685a4fb0fd1afe007041de538, parent V24 671d8c3def0ef6cbe60e52eaf66d28ead8475e66. No executable V25 model or audit existed at freeze time.

**Prospective observed-reward detector:** start selected SOURCE. After each real selected public terminal reward, record only `sign(abs(reward-slow_preupdate_prediction)-abs(reward-fast_preupdate_prediction))` with deadband 0.10; retain the most recent 4 signs in {-1,0,+1}. At least 3 of the most recent 4 signs favoring fast (slow error bigger) selects FAST; at least 3 favoring source selects SOURCE; otherwise retain selection. Ties never force a switch. No stage, source/target identity, hidden law, task timer or true returns sent to predictor. Fast model alone updates after every public feedback; frozen source does not update. One deterministic source-trained bank: 576 original V23 public observations, no retraining after cold restore. 326 stored learned scalars and max 12288-byte dual checkpoint. This hand-designed CENTRAL comparator is not native cell-autonomous cognition.

**Predeclared legal public event schedule**: within each segment event i=0..len-1, rotate by given fixed offset o, put index j=i+o; cue PUBLIC_CUES[j%4]; first ACTIONS[(2*j+1)%3]; selected second ACTIONS[(j+j//4)%3]. Every event observes exactly one actual selected action and reward, no feedback from withheld alternatives. Source-law and T1/T2 reward functions are external-only and unchanged V18/V23.

**Independent unlabeled streams (the regime names are OFFLINE EVALUATOR ONLY):**
- S→T1(12)→S(12), offset 0
- S→T2(12)→S(12), offset 3
- S→T1(8)→T2(10)→S(12), offset 6
- S→T2(10)→T1(8)→S(12), offset 9
- unchanged S(12)→S(12), offset 0
- unchanged T1(12)→T1(12), offset 3 (after first target warmup 4; inspect false returns)
- unchanged T2(12)→T2(12), offset 6 (after first target warmup 4; inspect false returns)

Use separate identical cold source starts for each stream; do not signal a stage change to detector, don't reset its four-value window, do not select tasks after seeing data. Evaluation snapshots at return events 1,4,8,12 from *frozen clones*, all 12 cue×first legal contexts and 3 candidate second actions, score against external law only. Measure first 4/8/12 return prediction errors, exact return latency, false switches, action regret, old source SHA, total scalar ring messages, host-specific timing/memory, checkpoint, and immutable original native pins.

**Strong controls required to claim final result**: original V24 always-fast and source-only, V23 destructive learner, matched online conventional CUSUM/Page-Hinkley plus 80-feature ridge, conventional two-expert source/ridge error selection; privileged boundary-aware chooser marked inadmissible upper-bound. Same sequence and reward budget, no hidden target counterfactual training. Source bank frozen and target-only reward updates must be provably legal. If conventional matched controls or cross-platform CI are missing, classify engineering BLOCKED rather than report return success.

Decision thresholds and negative classes are exactly those frozen in original PR #610 preregistration: detection <=4 observed return events in BOTH basic sequences without false source reactivation on unchanged-target controls; >=10% return error improvement versus both always-fast and strong conventional AND reduced return regret, neither T1/T2 adaptation >10% worse than matched fresh fast, all longer sequence/unchanged controls; never science/first-use. No merge, model promotion, original-world training, CKB/FORGE/controller change or G29 waiver.
