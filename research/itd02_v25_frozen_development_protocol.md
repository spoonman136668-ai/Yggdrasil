# V25 sealed development protocol — fixed BEFORE candidate/audit implementation

**Parent:** V25 prereg-only commit `d3af4f93f6a34f7685a4fb0fd1afe007041de538` on V24 exact `671d8c3def0ef6cbe60e52eaf66d28ead8475e66`.
This is an additional **pre-executable** protocol freeze. No V25 results have been observed. All cases are public synthetic development, never unseen first-use.

## Frozen controller decision function

Each independently initialized wrapper has a protected trained SLOW V22 bank (163 learned scalars) and separately initialized FAST V22 bank (163). Pretraining source uses original V23 `train_source()["pretrained_shared"]` frozen after 576 observations. The live feedback stream begins after that historical initialization, with **no further stage constructor/callback**. Both heads predict the same selected public terminal outcome *before* the reward; only fast updates. Repeated output predictions during nonlearning evaluation do not alter the controller.

Controller may see last **three** observed selected-action per-bank absolute prediction errors, never nonselected counterfactuals, and no ground-truth regime label. Let `Ls` and `Lf` be the sums of the three most recent absolute residuals and `margin=0.15`. With SLOW active, count a FAST-win when `Lf+0.15<=Ls` and switch to FAST after **two consecutive** qualifying observations with a full three-element window. With FAST active, count a SLOW-win when `Ls+0.15<=Lf` and switch to SLOW after **three consecutive** qualifying observations with a full window. Reset opponent streak on a failed condition and both streaks on switching. Ties keep current head. No learning of detector thresholds; this is a fixed *central controller*, NOT an endogenously learned native detector. No change to original local ring.

## Frozen synthetic case orders and segment budgets

Use exactly the existing 12 V23 `target_split()[0]` legal selected feedback tuples. For 0-based position `j`, the five immutable observation orders are:
- `target_one[j] = observed[(5*j+3)%12]` for `j=0..11`
- `target_two[j] = observed[(7*j+1)%12]` for `j=0..11`
- `return_a[j] = observed[(5*j+7)%12]` for `j=0..11`
- `return_b[j] = observed[(7*j+9)%12]` for `j=0..11`
- `return_c[j] = observed[(5*j+1)%12]` for `j=0..11`

All public tuples have the same cue/first/selected-second format, irrespective of environmental target law. The controller is NOT passed segment name, length, order code, wall-clock segment position, family identifier, or future switch-time information.

Six primary streams (the prefix S means already-finished common 576-event source pretraining; **it does not inject a new live stage marker**):
1. S→T1(12 in target_one order)→S(12 in return_a order)
2. S→T2(12 in target_two order)→S(12 in return_b order)
3. S→T1(8 in target_one order)→T2(10 in target_two order)→S(12 in return_c order)
4. S→T2(8 in target_two order)→T1(10 in target_one order)→S(12 in return_c order)
5. S→T1(12 in target_one order)→T1(12 in return_a order), **unchanged target false-reactivation control**
6. S→T2(12 in target_two order)→T2(12 in return_b order), **unchanged target false-reactivation control**

Separate unchanged-source control: S→S(12 in target_one order)→S(12 in return_a order). No false switch from slow should be counted as genuine correct behavior. Each actual terminal selected reward comes from V23 external `new_target` for T1/T2 or original V18 external `source_target(*case,nonlinear=True)` for S. Nobody passes law labels to the candidate.

## Frozen audit windows, comparators and thresholds

Before every live episode freeze prospective **active** score for selected second action and all three predicted-action scores (same legal public tuple); read actual selected reward only after predictions are recorded; no hindsight correction to action choice. Actual observed rewards update only on selected action. Return metrics use all 12 prospective selected-action predictions, plus first 4/8/12 errors and **12 cue/first action-choice regrets** on after-segment frozen heldout evaluations. Follow V23/V24 24 withheld second-action outcomes per family, never learning from those withheld outcomes.

Compare to V24-style always-fast bank and protected slow-only bank from the **same** source checkpoint and public history; to original V23 destructive single-bank continuous adaptation; to pre-committed conventional 80-feature online ridge (fixed update step `0.25/(1+||features80||²)`, source-pretrained on the same 576 samples) with a frozen original-source ridge expert and three-residual-window change detector matching the candidate's 0.15 margin and 2/3 streak requirements; and to conventional ridge single-bank continuous adaptation, zero and running observed mean. Report both a conventional detector that may switch experts and a single conventional online learner. The detached V24 boundary-aware selected model is a privileged oracle control only.

**Primary gate**: both basic return streams must reactivate SLOW by the fourth return reward with zero false return switches in both unchanged-target controls. Require >=10% lower 12-event **prospective** return absolute prediction error than always-fast and conventional two-expert detector, plus lower 12-context action regret than both. No source checkpoint changes, no counterfactual target reward learning, no 12-event return stage identifier. Secondary long streams must also reactivate without false detections and match these gains. At most 10% relative degradation in 12 withheld target-outcome prediction error versus matched always-fast (pre-return) on both T1/T2. Exact 326 learned native scalars; checksum canonical full checkpoint <=12,288 bytes; deterministic event SHA cross-host excludes runtime measurements; one final V24→V12 inherited native regression.

Return/false-positive failure: `V25_RETURN_REACTIVATION_NOT_ESTABLISHED__NO_SCIENCE`. A basic return or strong-control improvement failure after reactivation: `V25_REACTIVATION_WITHOUT_STRONG_CONTROL_GAIN__NO_SCIENCE`. A resource/target adaptation failure: `V25_RETURN_GAIN_WITH_TARGET_OR_RESOURCE_REGRESSION__NO_SCIENCE`. Full developmental positive only when **all** primary/secondary controls and resources pass: `V25_BOUNDED_SYNTHETIC_RETURN_REACTIVATION_ENGINEERING_POSITIVE__NO_SCIENCE`. Any broken provenance/leakage/checkpoint/frozen native boundary is `V25_ENGINEERING_BLOCKED__NO_SCIENCE`.

**No thresholds, order, family, event selection or outcome definition may be changed after results.** This does not authorize model adoption, merge, FORGE changes, independent scientific first-use, genuine unfamiliar-world cognition or retail-PC acceptance.
