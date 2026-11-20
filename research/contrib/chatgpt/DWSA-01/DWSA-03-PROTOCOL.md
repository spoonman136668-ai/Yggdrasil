# DWSA-03 — zero-teacher functional signal from archival engineering fixtures

Status: **prospectively frozen *development* negative-control check**. This is
not protected original-world source first-use, source-actor replay, accepted
learner training, nor independent scientific evaluation.

## Source and authorization fence

Inherit DWSA-02's single, already-consumed, training-archive Linux ZIP
artifact 14517860401, producing run 44499793023.
ZIP SHA-256 `b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d`.
Exact member `amalgam-joint-state.json`, 2,921,047 bytes, SHA-256
`576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`.
Extract **only the already-recorded 1,025 native engineering episodes** from
the nested `native_ascii -> experience_ascii -> episodes` field.
Require `source_mode == "engineering_fixture_only"` and schema
`yggdrasil.ckad.native-episode-experience.v6`.
No CausalGym, protected pilot, historical DTR replay, new original-world
action, private owner host, new trained checkpoint, teacher execution,
or real model prediction is allowed.

The experiment is **TRAIN-REUSE / RETROSPECTIVE**: the donor is already
trained on these very episodes, so even the final chronological 205 observations
are not independent unseen heldout data for donor. Call those observations
`late_training_recheck`, NOT heldout transfer, genuine generalization or
retention. The experiment cannot yield SCIENTIFIC_PASS.

## Frozen, task-specific metric

Compile archived trained donor solely from its 4 recorded weight heads using
DWSA-02 `compile_routes` and `restore`, a **320-byte fixed footprint** of
200 stored affine routing coefficients; do not import or execute donor.
This model loses the donor's tanh hidden layers.

Observe only historical public six-field episode tuples in chronological
order: `(opaque_id, (view_a, view_b), x1, s2, x2, y)` where all public
bits are 0 or 1. Predict *observed* s2 from the two transition heads, and
observed terminal y from the two reward heads. Both labels already exist in
the archive; no counterfactual effect inference. Use the recorded state from
strictly earlier rows for each temporal history vector; do not leak a
row's observed label into its own prediction features.

For action heads, for both 2-bit public views project all public bits and
extras as `2*bit-1`: transition extras=(x1,), reward=(x1,s2,x2).
For temporal heads, append 8*5 past-event context/action/state/reward signed
features with age decay 1/(age+1), precisely as the archived research source
`yggdrasil/native_jepa_temporal.py::_features` at
`86264b41a08d49f558418c0fba367f3a2636befa`:
for previous events in reverse order, append (view0-context alignment,
previous-x1-current-x1 alignment, previous s2 signed, previous x2 signed,
previous y signed), scaled by 1/(age+1). Empty history uses five zeros.
Both public views get independently computed context alignment.

Given route head's two outputs `a0(x),a1(x)`, define averaged score contrast
`z=(sum over views [a0(x)-a1(x)])/2` and `p=sigmoid(2*z)`.
Compute Brier loss `(p-label)^2`, mean binary correct at >=0.5 (ties
predict 0), and log loss diagnostic with clipping at 1e-12.
No donor hidden activation, tanh forward, teacher query, or model import.

## Controls, fairness and locked splits

Use all 1,025 historical witnessed rows **once** in original order.
Pre-fixed baseline fitting prefix first 820 rows; diagnostic last 205 rows,
without any split selection or tuning. This is a chronological descriptive
diagnostic, NOT honest independent donor HELD.

For each of four head tasks report:

- DWSA-02 stored 320-byte trained structural projection.
- Exact same affine projection computed algebraically from donor weights;
  a quantization ceiling control (not a donor forward pass).
- Untrained initialization route at the *same source architecture* built
  deterministically using published `sin/cos` initializers, then compiled
  at the same native footprint; source uses salt [3,7,13,17] and scales
  [0.075,0.075,0.055,0.055] per original code. This is not a fully
  trained control.
- Zero/0.5 Brier baseline, and Laplace-smoothed constant prevalence
  `(positives_in_prefix+1)/(820+2)` fitted only on the first 820.
- Stronger direct supervised logistic-regression baseline trained from
  the first 820 archived engineering episodes, with *identical fixed
  feature coordinates and memory footprint*. Independent conventional
  training only for this control; do not run a donor. Freeze 200 iterations
  of batch gradient descent, initial weights zero, logistic
  `p=sigmoid(2*(w·x_mean+b))`, learning rate 0.1, L2=0.001,
  batch average cross entropy gradient, no stochasticity/shuffle.
  No feature preprocessing fitted from late data. Quantize baseline to
  the same 320-byte format (200 int8 records and four scales, checksum).
- Deterministic readout-shuffled sham; exact extraction but wrong routing
  in each head, and quantized to 320 bytes.

The **primary falsification** for useful weight-only structural signal:
on late_training_recheck, trained DWSA Brier must beat BOTH fixed
prevalence control and zero-0.5 control by at least 0.0100 absolute,
**on each of four head tasks**. Pass of this narrow DEV criterion is
not scientific superiority, because donor training reused all data
and controls have unequal access to that data. If it fails for even
one head, classify DWSA-03 `RETROSPECTIVE_SIGNAL_NO_GO` and
preserve per-head negative outcomes, not tune a new threshold.

Always report stronger directly fitted conventional control separately
regardless of its result, and mean of four task metrics. Report timing,
resident RSS, exact hashes, count / source-mode / replay actions=0,
fixed 320 bytes, cold checks, strongest Brier comparator, heldout flags
all FALSE, and seed independence NOT ESTABLISHED.

Allowed: Python standard library, local read-only archived fixture, existing
DWSA-02 compiler/restore only; static program analysis, independent
recipient predictions, baseline fitting. No network/model calls, scheduler,
new source actions, accepted state mutations, training continuation, or
controller access. The user authorization is for contributor research-only.

## Disposition

ENGINEERING: measure exact source/static evidence, native footprint and
reproducible test receipt, candidate Linux + Windows final regression is a
separate requirement. SCIENCE: DEV descriptive signal only / NO-GO if
primary metric misses; SCIENTIFIC_PASS prohibited. DEPLOYMENT: NONE.

An actual scientific test needs owner-cleared *new* evidence, frozen disjoint
worlds, real meaningful outcomes, fully trained controls and independent
qualification, entirely separately from this retrospective training reuse.
