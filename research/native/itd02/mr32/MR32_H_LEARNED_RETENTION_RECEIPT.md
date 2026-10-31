# MR32-H — learned downstream-utility memory allocator qualification

Date: 2026-10-31
PR: #716 OPEN / DRAFT / UNMERGED
Source CI head: `fc5e3e43989353511890e93341896d1ce057e427`
Receipt/documentation head follows in branch history.

## Mechanism

`learned_memory_allocator.py` maintains exactly 16 positions from initialization, partitioned as seven active slots and nine retained slots. Empty positions are explicit. A linear utility predictor scores fixed metadata (evidence count, use count, recency, prediction-error summary and contradiction rate); its weights are updated only after explicit downstream usefulness feedback for a memory item that was marked as used. Unselected memory cannot receive utility credit. The learned ranking controls the active/retained partition and lowest-utility retained eviction. Pending feedback prevents checkpointing and eviction.

This is a source-only learned retention scorer. The metadata representation, linear model, update rate and feedback interface are fixed engineering choices; the memory-management weights are trainable. It is not a learned representation or end-to-end autonomous memory policy.

## Exact-head qualification

The first exact-head attempt run `41224230048` failed on both platforms because partition rebalancing did not update moved slots' `active` flags. The failure and correction are preserved in `MR32_A_QUALIFICATION_RECEIPT.md`. Source correction commit: `fc5e3e43989353511890e93341896d1ce057e427`.

Corrected exact-head run: `41224311049`
- Ubuntu job `124605152880`: PASS, 45 tests, syntax compilation, resource inventory and clean checkout.
- Windows job `124605153023`: PASS, 45 tests, syntax compilation, resource inventory and clean checkout.

Tests cover exact 16-position/7-active/9-retained partition from empty initialization, partition invariants through repeated inserts/evictions, weights changing only after downstream feedback, rejection of unselected feedback, pending-feedback checkpoint refusal, cold restore, and checkpoint tamper detection.

## Same deterministic 256-step software inventory

The allocator's development inventory uses synthetic labels `1.0 if step index mod 3 is zero else 0.0`, and only supplies a label when that memory is active and explicitly marked used. It is not original-world task reward or scientific training data.

| Model | Serialized bytes | Deep Python object bytes | Tracemalloc peak Windows/Linux | Wall seconds Windows/Linux |
|---|---:|---:|---:|---:|
| Memoryless mean | 63 | 852 | 166,320 / 166,312 | 0.00529 / 0.00969 |
| Additive diagonal Bayesian | 1,865 | 11,961 | 24,216 / 24,232 | 0.10090 / 0.11289 |
| Interaction Bayesian | 5,326 | 36,529 | 48,336 / 48,312 | 0.14560 / 0.36361 |
| Conventional prototype/EMA | 3,483 | 4,419 | 134,736 / 134,728 | 0.01029 / 0.02069 |
| Recurrent state-space | 3,170 | 5,808 | 114,584 / 114,592 | 0.11873 / 0.14210 |
| MR32 residual prototype | 3,853 | 7,335 | 178,512 / 178,408 | 0.04293 / 0.32442 |
| Learned allocator | 4,313 | 7,121 | 10,698 / 10,690 | 0.07497 / 0.22465 |

These are single-pass hosted runner diagnostics, not calibrated performance or fair total-resource parity. Python deep-size and tracemalloc are not process RSS; persistence schemas and feature/data structures differ. The allocator has slightly larger checkpoint bytes than MR32 but a similar estimated object footprint and lower traced peak in this stream. Its wall time varies substantially by runner. No resource or efficacy winner is established.

## Scientific status

- Learned retention weights update from explicitly attached post-usefulness feedback: SOFTWARE CONTRACT PASS.
- Synthetic software feedback path: EXECUTED.
- Original task outcome feedback: NOT EXECUTED.
- Prospective task reward, predictive loss or decision gain: NOT TESTED.
- Matched recurrent/Bayesian training efficacy: NOT TESTED.
- Cold restart under real distractor interference: NOT TESTED.
- Unfamiliar-family transfer: NOT TESTED.
- Equal total compute/resource parity: NOT ESTABLISHED.
- Original-world first use: BLOCKED by FSA-04 #83, still OPEN.

## Next admissible work

Keep MR32 residual prototype, conventional controls and learned allocator as separate candidates; do not merge their memory states or combine results after seeing tests. Prepare a preregistered three-to-five mechanism pilot under a fresh authorized source-birth epoch, with frozen FIT/CHECK/TRANSFER cohorts, same-information recurrent/Bayesian controls and a fixed total 16/7/9 state budget. Until FSA-04 authority is independently deployed and qualified, continue only source engineering and synthetic contract tests. Preserve negative and harness results. No source integration, merge, accepted-ref update or promotion is requested.
