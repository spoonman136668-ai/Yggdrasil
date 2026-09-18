TITLE: DG-1A-AR-U3 — Local Utility Corruption / Delay Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX ROBUSTNESS AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru2-moving-demand-role-relocation-audit.ice

PURPOSE
Stress the local utility signal that drives role relocation.

Question:
How does the bounded utility market behave when local consequence estimates are:
- missing;
- noisy;
- delayed;
- semantically assigned to the wrong role?

This is a precursor to lifetime meta-rule credit.

BOUNDARY
This is synthetic.

It does not:
- train Yggdrasil;
- establish learned credit assignment;
- execute STAB-18-R1;
- alter AR-01 or R1 gates.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TASK
Use the AR-U2 horizontal -> vertical moving-demand transition.

Fresh synthetic seeds:
40..45
n = 6

Pre-switch route cost:
mean 20.60949

The role update uses normalized local utility q_i.

Recovery criterion:
vertical route cost returns to within 10% of the seed's pre-switch horizontal cost for 10 consecutive steps.

Evaluation horizon:
180 steps

CLEAN
Final last-20-step route cost:
20.47668

Recovery:
6/6

Median latency:
60.5 steps

DELAYED LOCAL UTILITY
The role rule uses q from a fixed number of steps in the past.

4-step delay:
final 20.47936
recovery 6/6
median latency 65

16-step delay:
final 20.48969
recovery 6/6
median latency 76.5

32-step delay:
final 20.51544
recovery 6/6
median latency 92

PRIMARY DELAY RESULT
Substantial local consequence delay slows role relocation predictably but does not destroy it in the tested range.

This supports using short temporal windows or locally accumulated consequence state.

NAIVE UTILITY DROPOUT — ZERO IMPUTATION
For each cell-role utility observation independently,
drop the observation with probability p
and replace the missing value with ZERO.

p = 0.25:
final 23.11542
recovery 0/6

p = 0.50:
final 27.72969
recovery 0/6

NEGATIVE
Treating missing feedback as evidence of zero usefulness is unsafe.

It systematically retires useful specialization.

This is a semantics error:
MISSING
is not the same observation as
NO BENEFIT.

HOLD-LAST MISSINGNESS
Repeat the same dropout,
but when utility is missing:

retain the cell's previous local utility estimate for that role.

No global information is introduced.

p = 0.25:
final 20.47457
recovery 6/6
median latency 61

p = 0.50:
final 20.47492
recovery 6/6
median latency 61.5

KEY RESULT
The exact same missingness rate changes from failure to near-clean performance when missing feedback is represented explicitly rather than collapsed into zero utility.

Therefore future Yggdrasil role-credit state should distinguish:

KNOWN LOW UTILITY

from

UTILITY NOT OBSERVED / NOT UPDATED.

GAUSSIAN UTILITY NOISE — NO FILTER
Independent noise is added to normalized q.

sigma = 0.10:
final 22.92656
recovery 2/6
median successful latency 81

sigma = 0.25:
final 25.20540
recovery 0/6

sigma = 0.50:
final 27.17750
recovery 0/6

The local utility market is materially more sensitive to persistent analog utility noise than it is to deterministic delay.

TEMPORAL EMA
Maintain a local utility estimate:

q_est(t) =
0.75 * q_est(t-1)
+
0.25 * q_observed(t)

sigma = 0.10:
final 22.94090
recovery 6/6
median latency 80

sigma = 0.25:
final 25.23760
recovery 0/6

EMA restores reliable threshold crossing at the mild-noise condition,
but does not solve larger corruption.

Note:
the final mean at sigma=0.10 remains slightly worse than clean despite all seeds achieving the 10-step recovery criterion at some point.
Do not hide this residual drift.

SEMANTICALLY WRONG ROLE CREDIT
For a fraction p of cells,
replace the four-role utility vector with a fixed wrong-role permutation.

This is intentionally more dangerous than simple missingness.

p = 0.10:
no-filter final 22.71742
recovery 3/6
median successful latency 87

p = 0.25:
no-filter final 26.05223
recovery 0/6

EMA alpha 0.25:

p = 0.10:
final 22.78001
recovery 4/6
median successful latency 101

p = 0.25:
final 26.18357
recovery 0/6

NEGATIVE
Temporal smoothing cannot reliably rescue semantically wrong role credit.

This mirrors the earlier AR-01 context result:

ANALOG NOISE / MISSINGNESS
is easier to tolerate than

CONFIDENT WRONG MEANING.

CROSS-RESEARCH PATTERN
The same distinction now appears in two adaptive layers:

SEASONAL CONTEXT
- missing/noisy context can be made more robust;
- wrong-mode context remains dangerous.

ROLE UTILITY
- missing utility can be handled by retained local state;
- delayed utility is manageable;
- wrong-role credit remains dangerous.

Therefore a general Yggdrasil design rule is emerging:

DO NOT COLLAPSE UNCERTAINTY INTO A FALSE CERTAIN STATE.

Useful local state should be able to represent:
- value estimate;
- freshness / observation availability;
- perhaps confidence/disagreement.

META-RULE CONSEQUENCE
A future bounded meta-rule should not update sensitivity from every instantaneous scalar consequence.

Prefer:

local consequence evidence
+
explicit freshness
+
temporal aggregation
+
possibly redundant partially independent cues

->
bounded sensitivity update.

The wrong-credit problem is not solved by more aggressive adaptation.

It requires better credit identity / causal evidence.

LITERATURE RELATION
The Growing Neural Cellular Automata information-dynamics work (Masumori, Sato, Ikegami, Entropy 2026) reports structured hidden fluctuations and changing information organization during maintenance and repair.

That literature does not provide this utility rule,
but it supports treating temporally structured local state as potentially functional rather than as noise to be averaged away blindly.

DECISION
Preserve three implementation principles for later meta-rule work:

1. missing utility != zero utility;
2. local consequence memory should be bounded and freshness-aware;
3. semantically wrong credit requires an identity/causal safeguard, not merely smoothing.

NEXT
AR-U4:
LOCAL UTILITY CUE ABLATION / CREDIT IDENTIFIABILITY.

Remove one local cue at a time and test whether:
- function can still recover;
- another cue substitutes;
- the system misattributes improvement to the wrong role.

Then connect the result to the existing partially-independent injury-cue research.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
fresh_seeds = 6
