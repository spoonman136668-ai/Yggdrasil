TITLE: DG-1A-AR-U13 — Budgeted Active Evidence Collection Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE RESOURCE-TRADEOFF AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru12-confidence-weighted-plasticity-audit.ice

PURPOSE
AR-U12 showed that confidence-triggered evidence accumulation is much more robust than fixed one-pair consequence probing,
but it spends substantially more local observations.

This audit introduces an explicit local evidence budget.

QUESTION
Can a cell spend additional causal probes selectively when uncertainty is high while preserving enough budget for future regime changes?

BOUNDARY
This is synthetic.

It does not:
- freeze a biological energy accounting model;
- establish real Yggdrasil sensing cost;
- authorize unlimited perturbation;
- modify or execute STAB-18-R1;
- count as functional regeneration.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BENCHMARK
Same bounded one-dimensional local role-control task as AR-U12.

Role parameter:
x in [0,1]

Hidden optimum:
0.8 before episode 110
0.2 after episode 110

Episodes:
220

Primary population:
16,000 learners

Role perturbation:
epsilon = 0.06

Role step:
0.02

Primary consequence noise SD:
0.03

Confidence threshold:
1.5

Maximum probe pairs per decision:
8

COMPARATORS

FIXED-1
1 probe pair every episode.

FIXED-2
2 probe pairs.

FIXED-4
4 probe pairs.

FIXED-8
8 probe pairs.

UNBOUNDED-ADAPTIVE
Take additional independent probe pairs until:
confidence >= 1.5
or
8 pairs have been used.

TOKEN-BUCKET ACTIVE EVIDENCE
Each cell has a local evidence token budget.

Tokens refill gradually every episode.

A cell:
1. spends one pair if available;
2. evaluates confidence;
3. spends additional local probe pairs only while confidence is low;
4. stops at threshold or local episode maximum;
5. preserves unused tokens for later uncertainty/regime change.

Primary refill:
4 probe-pair tokens per episode.

Bucket capacity:
32 pairs.

This does not provide future knowledge.

PRIMARY RESULTS
noise SD:
0.03

FIXED-1
final role error:
0.03768

stable recovery:
95.23%

median switch latency:
45

false-update fraction:
26.35%

pairs per episode:
1.00

mature-state movement over 30 pre-switch episodes:
0.6000

FIXED-2
final:
0.03162

recovery:
98.71%

latency:
39

false:
23.65%

pairs:
2.00

mature movement:
0.6000

FIXED-4
final:
0.02676

recovery:
99.77%

latency:
33

false:
20.73%

pairs:
4.00

mature movement:
0.6000

FIXED-8
final:
0.02264

recovery:
100%

latency:
31

false:
17.54%

pairs:
8.00

mature movement:
0.6000

UNBOUNDED-ADAPTIVE
final:
0.01892

recovery:
100%

latency:
31

false:
11.48%

mean pairs:
4.93

mature movement:
0.25446

TOKEN-BUCKET / REFILL 4
final:
0.01979

recovery:
100%

latency:
31

false:
11.21%

mean pairs:
3.70

mature movement:
0.20731

PRIMARY POSITIVE
The token-bucket policy matches the unlimited adaptive collector's:

100% recovery
and
31-episode median switching latency

while using:

3.70 pairs/episode

instead of:

4.93 pairs/episode.

It also outperforms fixed-8 probing while spending less than half as many probe pairs on average.

The improvement comes from concentrating evidence when confidence is low,
not from uniformly increasing sensing.

BUDGET SWEEP
Fresh population:
10,000 per condition.

NOISE SD = 0.03

refill 2:
final error 0.02191
recovery 99.89%
latency 38
false 9.96%
pairs/episode 1.99
mature movement 0.1383

refill 3:
final 0.02058
recovery 99.97%
latency 32
false 10.81%
pairs 2.87
mature movement 0.1766

refill 4:
final 0.01978
recovery 99.99%
latency 31
false 11.23%
pairs 3.70
mature movement 0.2071

NOISE SD = 0.05

refill 2:
final 0.03078
recovery 91.14%
latency 63
pairs 2.04

refill 3:
final 0.02727
recovery 98.39%
latency 47
pairs 2.99

refill 4:
final 0.02576
recovery 99.76%
latency 41
pairs 3.89

NOISE SD = 0.08

refill 2:
final 0.06261
recovery 44.90%
latency 83
pairs 2.06

refill 3:
final 0.04045
recovery 78.62%
latency 70
pairs 3.06

refill 4:
final 0.03477
recovery 90.22%
latency 60
pairs 4.03

RESOURCE CURVE
Higher evidence budget:
- lowers role error;
- raises recovery rate;
- reduces switching latency;
- increases sensing / perturbation cost;
- modestly increases mature-state movement because more updates become authorized.

Therefore:
the evidence budget is a genuine adaptive resource.

It should not be hidden inside a fixed hyperparameter.

FIXED-VS-ACTIVE COMPARISON AT HIGH NOISE
noise SD = 0.08

fixed-2:
final 0.05199
recovery 76.02%
latency 61
pairs 2.0

fixed-4:
final 0.04343
recovery 89.07%
latency 53
pairs 4.0

fixed-8:
final 0.03692
recovery 95.79%
latency 45
pairs 8.0

unbounded adaptive:
final 0.03177
recovery 96.73%
latency 54
pairs 5.41

The fixed-8 strategy can switch faster under this very noisy condition,
but it pays a constant 8-pair cost in every episode and keeps mature plastic movement high.

The adaptive strategy spends evidence selectively and produces lower final error with substantially fewer probes.

TOKEN-BUCKET INTERPRETATION
The local evidence budget acts like a primitive:

ATTENTION / METABOLIC RESOURCE

for adaptation.

Low uncertainty:
few probes are needed.

High uncertainty:
the cell spends additional evidence.

Persistent uncertainty:
the local budget limits how aggressively the cell can keep probing.

This is directly relevant to the Yggdrasil end goal:

ADAPTIVE CAPABILITY
should increase without requiring every cell to remain maximally active all the time.

IMPORTANT DISTINCTION
The best budget depends on:
- consequence noise;
- urgency;
- mature-state risk;
- available energy;
- task value.

No single refill value is privileged by this toy.

Do not freeze:
2
3
4
or any tested number
as a biological constant.

ARCHITECTURAL CONSEQUENCE
The emerging local adaptation loop now includes an explicit resource dimension:

uncertainty
+
local consequence value
+
remaining evidence budget

->
how much causal evidence to collect

then

confidence-weighted bounded role update.

This is more compatible with:
hibernation
selective activity
resource-limited development

than a globally fixed learning schedule.

NEXT
AR-U14 — VALUE-OF-INFORMATION / URGENCY COUPLING

Question:
When evidence is costly,
should a cell spend its remaining probe budget now or preserve it?

Introduce:
- different functional stakes;
- different time urgency;
- damage vs maintenance;
- finite replenishment.

Ask whether a local value-of-information signal can allocate causal sensing preferentially to:
high-value
and
time-critical
adaptation.

PARALLEL FRONTIER
AR-C1 — repeated decentralized context ordering.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_population = 16000
budget_sweep_population_per_condition = 10000
