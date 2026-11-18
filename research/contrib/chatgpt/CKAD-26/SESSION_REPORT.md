# CKAD26 — Conditional causal evidence versus raw surprise

**DEVELOPMENT_SIGNAL_NO_GO** — frozen, prospective synthetic development.
Nine native 192-episode public-action streams start from exactly three
previously qualified 448-episode Yggdrasil checkpoints, using new
synthetic source namespaces. Every shadow detector received exactly
the same public action-consequence evidence. Neither shadow hypothesis
could alter the native learner, exploration actions or learned weights.

Candidate tests a Beta(1,1) split-versus-shared conditional transition
or reward distribution over the previous 32 observations (16+16).
Exact rational Bayes factor threshold=16, persistence=2, spacing=8.
The unconditional conventional detector has identical windows,
threshold and persistence but ignores intervention state/action keys.
Native joint surprise is the preserved CKAD23 comparator.
Random alarm is a label-free hash-rate control, not a learner.

| Schedule | Arm | Correct boundary 48 /3 | 96 /3 | 144 /3 | True detections | False alarms |
|---|---|---:|---:|---:|---:|---:|
| transition_flip | causal_bayes | 3 | 1 | 2 | 6 | 4 |
| transition_flip | unconditional_bayes | 1 | 0 | 0 | 1 | 2 |
| transition_flip | native_joint | 2 | 2 | 2 | 6 | 2 |
| transition_flip | random_alarm | 1 | 2 | 1 | 4 | 8 |
| reward_flip | causal_bayes | 0 | 1 | 0 | 1 | 0 |
| reward_flip | unconditional_bayes | 0 | 0 | 0 | 0 | 2 |
| reward_flip | native_joint | 1 | 2 | 3 | 6 | 1 |
| reward_flip | random_alarm | 1 | 0 | 1 | 2 | 5 |
| no_change | causal_bayes | — | — | — | 0 | 0 |
| no_change | unconditional_bayes | — | — | — | 0 | 0 |
| no_change | native_joint | — | — | — | 0 | 3 |
| no_change | random_alarm | — | — | — | 0 | 6 |

## Frozen gates

- recognize_each_boundary_2of3: FAIL
- plus_four_vs_native_joint: FAIL
- plus_two_vs_unconditional_bayes: PASS
- stationary_null_false_lte1_per_seed: PASS
- changed_false_lte2_per_seed: PASS
- source_and_checkpoint_custody: PASS

## Limitations

This is causal-*conditional* evidence in a known synthetic world
family, not independently verified causal discovery. All candidate
change alarms are shadow-only; an alarm cannot establish improved
learning, retained knowledge, transfer, planning or reward.

The nine native source checkpoints and full timestamp-ordered action
receipts were independently reproduced byte-for-byte on Linux and
Windows, preserved with deterministic lossless gzip in this folder.
Three independent pretrained parent groups; nine source draw namespaces
are not nine independent pretrained models. No protected first use.

Stable result SHA256: 68a11deda00b31c75e33656be09e97cd6e4f9569f5e08606d6c86695be792aaf

**ENGINEERING:** subject to mandatory full exact-candidate cross-OS regression.
**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**
