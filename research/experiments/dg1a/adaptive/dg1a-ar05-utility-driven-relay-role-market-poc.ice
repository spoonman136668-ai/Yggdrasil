TITLE: DG-1A-AR-05/06 — Utility-Driven Relay Role Market Synthetic Precursor
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE PRECURSOR — NOT YGGDRASIL FUNCTIONAL REGENERATION
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT_NEGATIVE: dg1a-ar05-seasonal-role-mixture-negative-audit.ice

PURPOSE
Replace the failed fixed-global-role-quota idea with a local functional utility signal.

Question:

Can relay-like specialization emerge and recover after selective ablation when cells receive no target relay ratio and respond only to local communication traffic versus role cost?

This is a precursor to functional regeneration.

It is not a Yggdrasil task result.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BODY / COMMUNICATION GRAPH
Disk-like 2D grid.

live nodes:
149

connectivity:
4-neighbor local edges only.

communication demands:
6 fixed source-destination pairs placed approximately opposite each other around the boundary.

No node has access to the whole graph.

CELL ROLE STATE
Each node has one continuous scalar:

relay_propensity r in [0,1]

Initial value:
approximately 0.05 plus small random heterogeneity.

There is NO global relay target.

FUNCTION
Messages follow the current lowest-cost paths.

Edge traversal cost:

cost(u,v) =
1
+
4 * (
    1 - 0.5*(r_u + r_v)
)

Therefore:
high relay propensity locally reduces communication delay/cost.

LOCAL UTILITY SIGNAL
Each communication route contributes one local traffic count to every node it traverses.

Each cell sees only its experienced local traffic load.

Saturating local benefit:

benefit =
traffic / (traffic + 1.5)

Relay-role update pressure:

delta_r =
eta * (
    benefit * (1-r)
    -
    energy_cost * r
)

Frozen toy coefficients:

eta = 0.25
energy_cost = 0.12

stochastic cell update probability:
0.5

Interpretation:
- traffic rewards relay specialization;
- maintaining relay specialization has a local cost;
- unused relay decays;
- no global histogram or controller prescribes where relays belong.

ROUTING NOTE
The synthetic environment computes lowest-cost paths to generate message traffic.

That path solver is an evaluation/environment mechanism.

Cells do NOT receive:
- global shortest paths;
- global role counts;
- source-destination coordinates;
- target relay locations.

They receive only:
their local traffic count.

PRE-ABLATION DEVELOPMENT
50 adaptation steps.

SEEDS
12 per ablation severity.

SELECTIVE RELAY ABLATION
Sort established relay propensity from highest to lowest.

Remove enough highest-relay nodes' relay state to eliminate the declared fraction of TOTAL relay mass.

Morphological nodes remain present.

Ablation severities:
50%
70%
90%
100%

After ablation:
relay propensity of selected nodes = 0.

POST-ABLATION ADAPTATION
100 steps.

PRIMARY FUNCTIONAL METRIC
Mean shortest communication cost over the six message demands.

RECOVERY
Communication cost must return to within 5% of that seed's pre-ablation cost and remain there for 10 consecutive steps.

RESULTS — 12 SEEDS PER SEVERITY

50% relay-mass ablation:
pre-ablation mean route cost = 29.872
immediate damaged cost = 61.563
final adaptive cost = 29.389
recovery rate = 100%
median recovery step = 36
pre relay mass = 54.738
post-ablation relay mass = 27.055
final relay mass = 55.397

70% relay-mass ablation:
pre-ablation cost = 29.872
immediate damaged cost = 69.060
final adaptive cost = 29.155
recovery rate = 100%
median recovery step = 38.5
post-ablation relay mass = 16.069
final relay mass = 54.698

90% relay-mass ablation:
pre-ablation cost = 29.872
immediate damaged cost = 78.292
final adaptive cost = 29.257
recovery rate = 100%
median recovery step = 40
post-ablation relay mass = 5.077
final relay mass = 55.621

100% relay-mass ablation:
pre-ablation cost = 29.872
immediate damaged cost = 83.333
final adaptive cost = 28.739
recovery rate = 100%
median recovery step = 37.5
post-ablation relay mass = 0
final relay mass = 50.803

PRIMARY POSITIVE
A local utility rule restored communication function after even total removal of the established relay state.

No target relay fraction was provided.

The population reconstructed relay capacity where traffic demanded it.

FIXED-ROLE CONTROL
Without post-ablation role adaptation,
the damaged communication cost remains at the immediate damaged state.

Therefore the observed recovery requires role adaptation.

SPATIAL-PLACEMENT CONTROL
A critical question is whether recovery occurs merely because total relay mass grows back.

For every final adaptive organism:
randomly permute the exact final relay-propensity vector across nodes.

This preserves:
- total relay mass;
- distribution of relay values;
- number of nodes;
- graph;
- communication demands.

Only spatial placement is destroyed.

30 random permutations per seed.

Mean shuffled final route cost:

50% ablation:
46.724

70% ablation:
47.000

90% ablation:
46.502

100% ablation:
48.586

Adaptive placement:
approximately 28.7..29.4

Therefore:
RECOVERED RELAY MASS ALONE IS NOT ENOUGH.

The utility rule reconstructs functionally useful spatial placement.

This is the strongest result in this precursor.

INTERPRETATION
The successful pattern is:

local functional demand
->
role utility
->
soft specialization
->
environment reroutes work
->
new local demand
->
distributed adaptation

This forms a closed feedback loop without a fixed global role quota.

RELATION TO PRIOR NEGATIVE
The fixed seasonal role-mixture experiment failed because it asked local cells to reproduce a global histogram.

The utility-driven experiment instead asks:
"Is becoming more relay-like useful here?"

That is the more promising meta-rule.

RELATION TO FUNCTIONAL REGENERATION MILESTONE
This toy now contains four ingredients relevant to the future milestone:

1. a role has an actual function:
reducing communication cost;

2. role placement is spatially meaningful;

3. selective role ablation damages function;

4. unrelated nodes adapt and restore function.

However this still does NOT count as Yggdrasil functional regeneration because:

- roles are hand-defined;
- utility equation is hand-designed;
- routing task is synthetic;
- no NCA network learned the mechanism;
- relay state is not an emergent latent specialization;
- no real Yggdrasil cognitive task is restored.

Do not promote this result beyond:
SYNTHETIC PRECURSOR.

IMPORTANT SCIENTIFIC CONSEQUENCE
AR-05/06 should NOT begin by teaching a target role count.

The more discriminating route is:

task/local performance signal
->
bounded per-cell role utility
->
soft role adjustment

Then ask whether:
useful population ratios
and
spatial organization
emerge.

FUTURE CONTROL REQUIREMENTS
A real implementation must prevent trivial global leakage.

Cells may consume only locally available quantities such as:
- messages handled;
- prediction error;
- neighbor failures;
- local damage evidence;
- local energy/update cost;
- local improvement following prior actions.

No cell should receive:
- global task accuracy;
- global role histogram;
- target role coordinates;
unless the experiment explicitly tests such a signal.

NEXT EXPERIMENT
Generalize the utility-driven role market beyond a single relay function.

Candidate role utilities:
RELAY:
communication demand / bottleneck relief

REPAIR:
reduction in local predictive-error after damage

INHIBITOR:
reduction in runaway local growth / instability

DORMANT:
energy saved without degrading local function

GROWTH:
improvement in local task/morphology error per resource consumed

Then test whether:
- several roles coexist;
- roles relocate when demand moves;
- selective ablation of one role restores function through unrelated cells;
- no fixed role ratios are required.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
nodes = 149
communication_pairs = 6
seeds_per_severity = 12
shuffled_controls_per_seed = 30
