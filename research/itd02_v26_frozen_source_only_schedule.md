# ITD-02 V26 exact source-only experiment schedule (pre-executable freeze)

**Chronology:** V26 initial prereg commit `9eb4e7305cbd55e146ff64c8f82f06edb87a5350` precedes this exact event schedule. This file is committed BEFORE V26 executable candidate or auditor, and is frozen regardless of result. Source foundation: V25 `7f3d16b542e83c87abdacdf8e8988ca20c1e215e`, untouched. No protected original-world test.

## Legal observed event generator

For each segment, zero-based selected feedback index i, fixed integer shift s and offset o:

`k=(5*i+s)%12`; `j=k+o`;
`cue=PUBLIC_CUES[j%4]`;
`actual_first=ACTIONS[(2*j+1)%3]`;
`actual_selected_second=ACTIONS[(j+j//4)%3]`.

Reward depends on evaluator-only regime `source`, `cue_second` or `triple_parity` (unchanged V18 and V23 source/target functions); the candidate sees **only** cue, actual_first, selected_second, selected terminal reward, in that order. The integer s/o, stage length, stage ID and regime name are **not** candidate inputs. Index i restarts at 0 in each stage; there is no corresponding model callback, reset, memory swap or control message. No dummy training feedback.

The eight independent exact streams are:

| Stream key | Offline stages (selected terminal feedback count) | s | o |
|---|---|---:|---:|
| basic_t1 | cue_second:12; source:12 | 1 | 0 |
| basic_t2 | triple_parity:12; source:12 | 4 | 3 |
| long_t1_t2 | cue_second:8; triple_parity:10; source:12 | 7 | 6 |
| long_t2_t1 | triple_parity:10; cue_second:8; source:12 | 10 | 9 |
| unchanged_source | source:12; source:12 | 2 | 0 |
| unchanged_t1 | cue_second:12; cue_second:12 | 5 | 3 |
| unchanged_t2 | triple_parity:12; triple_parity:12 | 8 | 6 |
| confusable_target_only | cue_second:12; triple_parity:10; cue_second:12 | 11 | 9 |

Before these streams, instantiate identical independently restored source-trained banks using the ORIGINAL V23 source 16 passes ×36 histories = 576 legal terminal source rewards; freeze source weights and initialize new fast learning bank with zero native learned scalars. Do not train from the eight streams while building any separate initial source checkpoint. Each stream gets its own cold start. Original V22 native learning weights (163 per bank) and edge channels/hops unchanged.

## Strict outcome measurement

Record for every individual observed episode a pre-feedback active prediction, source-only prediction, fast-only prediction, conventional RLS/CUSUM prediction, and comparator predictions; record the corresponding actual reward only after predictions. Update every learner from exactly that selected public reward, except for frozen source banks.

Do not confuse score-side output-message counters with training or parameter updates. Audit-only per-context scores after event 1,4,8,12 must operate on **frozen clones** with 12 public cue/actual-first combinations and all three possible second choices. True counterfactual rewards are evaluator-only and may be used solely to compute regret/errors, never to train. Freeze V23's 24 withheld target action outcomes per target law for secondary target error after adaptation. Return latency means first SLOW selection *after an observed return reward*; return prospective pre-feedback errors use the policy active **before** that reward; ignore non-return source stages when calculating return benefit. False reactivation counts a transition FAST→SLOW in a target segment (with separate measurement of any SLOW policy still active at target start). For unchanged-target second stages, report both count of mistaken FAST→SLOW reactivations and number of observations under SLOW; success requires **both zero after initial 4 target warmup observations**. For the confusable target-only final stage, require zero source reactivation/selection after first 4 of that final target stage. Independent source-unchanged controls must not be interpreted as proof of return detection.

Comparators: V25 original selector exactly unchanged; always FAST; always SLOW; source-destructive single V22; full 80x80 RLS + disclosed sequential CUSUM and separate two-expert public-error selector; constant zero/observed-mean; equal-action/same-information V26 ablation without cross-cue confirmation, with all other V26 conditions identical. Privileged stage-aware is report-only oracle and inadmissible for primary gain claims.

V26 must preserve 326 learned scalars in native banks (163 target-trainable), checkpoint <=12,288 bytes including selector, checksum/corruption safeguards, exact source parameter SHA unchanged, and complete selector trace. Evaluate both simple returns FIRST, then longer/false-positive controls. A software regression or missing strong comparator means ENGINEERING_BLOCKED; never reinterpret a negative outcome as PASS. The full exact-source Linux/Windows workflow must preserve canonical case+regret SHA and one final inherited V25→V12 original-native regression before qualified developmental result.

No V26 thresholds, stage mappings, schedules, candidate window size, cue corroboration criterion or outcome classification may be changed after executing the candidate. This schedule cannot establish independent first-use or original unfamiliar causal-world transfer. No other controller, FORGE, CKB-plane, science authority, runtime or accepted source is modified.
