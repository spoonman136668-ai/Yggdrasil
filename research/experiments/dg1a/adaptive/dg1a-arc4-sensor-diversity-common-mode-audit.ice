TITLE: DG-1A-AR-C4 — Sensor-Diversity / Common-Mode Failure Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DIVERSITY-AWARE CONSENSUS AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arc3-compressed-source-independence-audit.ice

PURPOSE
AR-C3 established that distinct provenance is necessary but not sufficient.

Several distinct sensors can still share one failure mode.

AR-C4 asks:

Can the organism estimate SENSOR ERROR DIVERSITY from local report history and discount groups of sensors that fail together?

BOUNDARY
This is synthetic.

It does not:
- prove current Yggdrasil sensors form clean families;
- authorize fixed sensor-family labels;
- freeze a clustering algorithm;
- solve arbitrary adversarial sensor corruption;
- replace AR-01 broadcast context;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SENSOR POPULATION
8 sensors.

Primary equal-family experiment:
4 latent error families
2 sensors per family.

Unequal-family stress:
family sizes:
4
2
1
1

Sensors in one family share:
family-level wrong-mode events.

Outside those events,
each sensor may also fail independently.

The selector does NOT observe the true family labels.

OBSERVABLE HISTORY
Before the scored context decision,
the system receives:

200 prior context transitions

containing only sensor mode reports.

No true error indicator is exposed to the clustering rule.

PAIRWISE AGREEMENT SIGNAL
For each pair of sensors,
measure historical mode-report agreement.

Sensors sharing one error family tend to show:
excess agreement,
because they make the same wrong report together.

A simple local research clustering rule:

1. compute all pairwise report-agreement rates;
2. sort the pairwise agreement values;
3. place a threshold at the largest observed agreement gap;
4. connect pairs above that threshold;
5. use connected components as estimated error families.

This is a deliberately simple identifiability probe,
not a production algorithm.

CONSENSUS COMPARATORS

RAW SOURCE MAJORITY
Every surviving sensor contributes one vote.

TRUE-FAMILY CONSENSUS
Each actual latent error family contributes at most one family vote.

This is an unavailable oracle diagnostic.

LEARNED-FAMILY CONSENSUS
Use the history-derived clusters.

Within each estimated family:
- if surviving members agree, the family contributes that mode;
- if members disagree, the family abstains.

Then:
each estimated family contributes at most one vote.

HIGH-RISK GATE
For raw source voting:

require:
>=4 source reports
and
>=75% agreement.

For family-aware voting:

require:
>=3 family votes
and
>=75% family agreement.

EQUAL 2/2/2/2 FAMILY RESULT
sensor loss:
25%

independent per-sensor error:
5%

family common-mode failure varied.

History:
200 transitions.

At family failure probability 0.05:

family clustering exact:
100% in the tested 5 fresh runs.

RAW SOURCE consensus:
overall correct non-tied decision:
98.52%

LEARNED-FAMILY:
98.14%

ORACLE FAMILY:
98.14%

At low balanced common-mode failure,
raw source voting can be slightly more accurate because:
two sensors per family provide useful repeated evidence when the family is behaving correctly.

Therefore:
FAMILY DISCOUNTING IS NOT ALWAYS FREE.

At family failure probability 0.10:

clustering exact:
100%.

RAW:
96.32%

LEARNED FAMILY:
95.85%

At 0.20:

RAW:
89.53%

LEARNED:
88.87%

In the equal-size-family case,
family collapsing mainly changes confidence rather than dramatically improving plain majority accuracy.

This is expected:
all families have equal representation,
so raw source majority does not structurally over-weight one family relative to another.

HIGH-RISK GATE — EQUAL FAMILIES
At family failure 0.10:

raw high-risk gate acceptance:
~74.1%

false adoption among all trials:
~0.06%

family-aware gate acceptance:
~78.4%

false adoption:
~0.02%

Thus diversity-aware gating can preserve strong safety while accepting more decisions,
because the family representation directly tracks independent evidence units.

UNEQUAL FAMILY STRESS
This is the discriminating experiment.

Latent family sizes:

F0:
4 sensors

F1:
2 sensors

F2:
1 sensor

F3:
1 sensor

If all 8 sensors are counted equally,
F0 can dominate the vote even though its four members share one common failure mode.

sensor loss:
25%

independent error:
5%

history:
200 transitions

fresh clustering runs:
5

FAMILY FAILURE = 0.05

learned clustering exactly recovered the true family partition:
80% of runs.

mean inferred cluster count:
4.2

RAW source majority:
overall correct:
95.89%

LEARNED family consensus:
97.24%

ORACLE family:
97.39%

RAW high-risk gate:
acceptance 86.23%
false adoption 0.257% of all trials
conditional accuracy ~99.70%

LEARNED-family gate:
acceptance 79.97%
false adoption 0.019%
conditional accuracy ~99.98%

FAMILY FAILURE = 0.10

learned family partition:
100% exact in tested runs.

RAW overall correctness:
91.47%

LEARNED FAMILY:
94.64%

ORACLE:
94.64%

RAW high-risk gate:
acceptance:
78.12%

false adoption:
0.604%

conditional accuracy:
99.23%

LEARNED-family gate:
acceptance:
71.17%

false adoption:
0.022%

conditional accuracy:
99.97%

PRIMARY POSITIVE
Once one correlated family has more members than others,
raw sensor count overstates the amount of independent evidence.

Learning and counting error families instead:

improves overall consensus

and

dramatically reduces false high-risk adoption.

FAMILY FAILURE = 0.20

RAW overall:
81.82%

LEARNED FAMILY:
86.81%

ORACLE:
86.81%

RAW high-risk gate:
acceptance:
62.94%

false adoption:
1.429%

conditional accuracy:
97.73%

LEARNED-family gate:
acceptance:
56.53%

false adoption:
0.112%

conditional accuracy:
99.80%

The safety gain becomes larger as common-mode family failures become more important.

PRIMARY DESIGN RULE
The relevant quantity is not:

NUMBER OF SENSORS

but:

EFFECTIVE NUMBER OF INDEPENDENT SENSOR FAMILIES.

This is the context-consensus analogue of the prior:

effective independent cue count

found in injury and role-credit research.

HISTORY LENGTH / IDENTIFIABILITY
At very low family common-mode failure,
there may be too little observable disagreement structure to identify families reliably from only 200 transitions.

This is not a defect in clustering alone.

If two sensors have not yet exhibited their shared failure mode,
their dependence may be statistically invisible.

Therefore:
INDEPENDENCE ESTIMATION REQUIRES EXPERIENCE.

A mature organism can become more confident about sensor diversity over time.

A new organism should begin with uncertainty about independence.

ARCHITECTURAL CONSEQUENCE
Context confidence should not be:

agreement fraction across raw sensors.

A better abstraction is:

agreement across ESTIMATED INDEPENDENT EVIDENCE FAMILIES

with uncertainty about the family model itself.

Candidate local state:

source provenance sketch

+
historical co-failure / co-disagreement summary

->
effective source diversity estimate.

Then:

effective diversity
+
agreement
+
freshness
+
epoch order
+
mode risk

->
context confidence.

IMPORTANT CAUTION
High historical agreement can arise because:
- sensors are both accurate;
- sensors share environment;
- sensors share one failure mode.

Agreement alone is ambiguous.

The clustering works in this synthetic benchmark because:
common wrong reports create an observable excess-agreement signature across varied true modes.

Real Yggdrasil sensing may require richer diagnostics.

RELATION TO LITERATURE
Distributed-consensus and sensor-network research treats correlated failures, node faults, and constrained communication as core reliability problems.

Recent decentralized swarm-state-estimation work likewise combines multiple local information sources to remain coherent under primary-sensor dropout.

AR-C4 adds a Yggdrasil-specific scientific question:
how much INDEPENDENT context evidence is locally available?

DECISION
AR-C4 is POSITIVE in the structured-family toy.

Supported:
- sensor-dependence structure can be statistically learnable from report history;
- family-aware evidence can prevent large correlated sensor groups from dominating consensus;
- high-risk context benefits strongly from diversity-aware confidence.

Not solved:
- arbitrary overlapping failure families;
- continuously changing sensor dependence;
- very sparse failure history;
- learned compression of the family model;
- adversarial correlated misinformation.

NEXT
AR-C5 — ONLINE SENSOR-DIVERSITY ADAPTATION

Introduce:
- sensor family relationships that change over time;
- new sensors;
- sensor death;
- environmental regime changes that alter correlations.

Question:
Can effective-independence estimates update online without either:
- forgetting real historical dependence too quickly;
or
- remaining permanently biased by obsolete sensor relationships?

PARALLEL
AR-U14 — value-of-information / urgency coupling.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
history_transitions = 200
scored_trials_per_condition = 50000
fresh_clustering_runs = 5
sensor_count = 8
