# NKR30: did selective feedback damage calibration?

Diagnostic:DIAG_SELECTIVE_CALIBRATION_DAMAGE_SUPPORTED

NKR29's actual negative remains frozen. This follow-up restores its saved
native checkpoints and computes analytic expected error under the published
source's nominal IID law. No training, new source action or earned reward.
The source oracle is evaluator-only and never reaches the learned bank.

| Maximum events | Memory | Expected Brier | Excess calibration error |
|---:|---|---:|---:|
| 28 | all_feedback | 0.159705184 | 0.012105184 |
| 28 | error_only | 0.169321416 | 0.021721416 |
| 28 | frozen | 0.166654494 | 0.019054494 |
| 28 | random_matched_701 | 0.167994567 | 0.020394567 |
| 28 | random_matched_702 | 0.166789530 | 0.019189530 |
| 28 | random_matched_703 | 0.167294685 | 0.019694685 |
| 14 | all_feedback | 0.160520949 | 0.012920949 |
| 14 | error_only | 0.169321416 | 0.021721416 |
| 14 | frozen | 0.166654494 | 0.019054494 |
| 14 | random_matched_701 | 0.166551721 | 0.018951721 |
| 14 | random_matched_702 | 0.167800942 | 0.020200942 |
| 14 | random_matched_703 | 0.168658930 | 0.021058930 |
| 7 | all_feedback | 0.163002466 | 0.015402466 |
| 7 | error_only | 0.169321416 | 0.021721416 |
| 7 | frozen | 0.166654494 | 0.019054494 |
| 7 | random_matched_701 | 0.166942954 | 0.019342954 |
| 7 | random_matched_702 | 0.166653436 | 0.019053436 |
| 7 | random_matched_703 | 0.166954845 | 0.019354845 |

Every checkpoint is scored on all32 world/target/state/action conditions
with equal weights, using exact fractions. Expected error decomposes exactly
into irreducible stochastic noise plus squared calibration error. The
source-kernel noise floor is0.1476. This oracle floor is an analytic reference,
not a learner supplied with hidden source laws and not an executed control.

## Meaning and limits

This distinguishes a diagnostic about learned probability quality from
relabeling individual stochastic outcomes as erroneous facts. Evidence from
previous negative results is unchanged. Neither future held-out worlds nor
the21.3M factual image were trained here. No claim of new relationship type,
native control superiority, unfamiliar-world transfer or general intelligence.
Expected values assume the same nominal IID structural equations; they are
not actual new-world trial scores, earned returns or pristine science.

Source SHA:29bb546e7cd9e0578c6b124dc64c9251a7b71653
Prereg SHA:09ff23a1eb094e0ac16ea3e02129520bd805d86a
Stable SHA256:d43a20e3d25f4b0df0d386fbe5ee0c26b7b3a40c1d478d255f0ffb8ea12fe580
Ubuntu audit:0.011954s; Windows audit:0.016000s.
All earlier evidence and saved checkpoints remain byte-identical.
Final-source mandatory full root/NKR05/independent G29 follows receipt commit.
Draft only, unmerged, undeployed, accepted native model unchanged.
