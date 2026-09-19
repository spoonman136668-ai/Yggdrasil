TITLE: DG-1A-AR-H45 — Persistent Local Specialization vs Generative-Family Split Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE MEMORY-PRICE CROSSOVER RESULT + TRANSIENT/PERSISTENT IDENTIFIABILITY LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh44-local-template-version-lease-audit.ice

PURPOSE
H44 established a reversible local lease for unpromoted template versions during partition.

H45 asks:

WHEN SHOULD A REPEATEDLY USEFUL LOCAL SPECIALIZATION REMAIN:
LOCAL AND REVERSIBLE

vs

EARN:
A COMPACT GENERATIVE FAMILY BRANCH?

BOUNDARY
This is synthetic.

It does not:
- freeze a split duration;
- freeze a branch-memory price;
- define semantic lineage families;
- assume future recurrence is known;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

HORIZON
3,000 synthetic blocks.

LOCAL SPECIALIZATION LOSS
When the specialization is active
but no adapted local lease/branch is available:

mismatch cost:
0.64 per block.

LOCAL LEASE
Local lease maintenance / revalidation cost:

0.015 per active specialization block.

Lease reacquisition latency:

3 blocks
per specialization episode.

COMPACT FAMILY BRANCH
One-time branch-creation cost:

1.2 synthetic units.

Permanent branch storage cost is swept.

Once created,
the branch eliminates future lease reacquisition for the specialization.

This is a coarse resource model,
not a biological constant.

SCENARIO POPULATION
20,000 synthetic specialization histories.

Mixture:

SHORT TRANSIENT
40%.

one episode:
60..180 blocks.

LONG TRANSIENT
20%.

one episode:
300..700 blocks.

PERSISTENT
15%.

specialization remains for almost the full remaining horizon.

RECURRENT
15%.

eight episodes,
approximately 60..100 blocks each,
spaced through the horizon.

RARE RECURRING
10%.

four episodes,
approximately 40..60 blocks each,
widely separated.

No policy receives:
the scenario class
or
future duration.

COMPARATORS

LEASE ONLY
Never create a new generative family branch.

IMMEDIATE SPLIT
Create a branch at the first specialization appearance.

PERSISTENCE / RECURRENCE GATE
Split only if either:

one specialization episode persists for at least T blocks

or

the specialization has recurred at least R times.

Tested:

T:
200
400
600
800
1000.

R:
3
4
5.

These are synthetic discriminating gates only.

PRIMARY MEMORY-PRICE SWEEP

LOW BRANCH STORAGE PRICE:
0.0035 per block.

BEST TESTED POLICY:
IMMEDIATE SPLIT.

mean total cost:
10.0701.

Best gated competitor:
T=800
R=3.

cost:
10.2272.

INTERPRETATION
When permanent generative memory is cheap enough,
waiting for strong persistence evidence costs more than simply branching early.

This is an important negative against:
always delaying family formation.

MODERATE BRANCH STORAGE PRICE:
0.0045.

BEST TESTED POLICY:
PERSISTENCE / RECURRENCE GATE.

T=800
R=3.

mean cost:
11.0254.

Immediate split becomes more expensive because:
many short/transient specializations pay unnecessary long-lived branch storage.

PRIMARY MODERATE-PRICE POSITIVE
At intermediate memory price,
reversible local leasing should serve as a provisional stage.

Only:
persistent
or
recurrently useful
specializations
earn permanent generative branching.

HIGHER STORAGE PRICE:
0.006.

Best tested:
T=800
R=5.

mean cost:
12.0826.

The preferred gate becomes more conservative.

AT STORAGE PRICE:
0.008

best tested:
T=800
R=5.

mean:
13.1867.

AT STORAGE PRICE:
0.010

best tested:
T=800
R=5.

mean:
14.2907.

VERY HIGH STORAGE PRICE:
0.015.

BEST TESTED:
LEASE ONLY.

mean cost:
15.0243.

No tested family-split rule improves enough to justify permanent branch storage.

PRIMARY MEMORY-PRICE CROSSOVER
The correct structural decision is not:

LOCAL SPECIALIZATION PERSISTED
SO CREATE A FAMILY.

It is closer to:

EXPECTED FUTURE REUSE VALUE

vs

PERMANENT GENERATIVE MEMORY PRICE.

The same observed specialization can rationally produce different structural outcomes under different resource envelopes.

SCENARIO DETAIL AT PRIMARY MODERATE WORKING POINT
Memory price:
0.0035
for descriptive policy comparison.

T=800
R=3 gate.

SHORT TRANSIENT

lease/gated mean:
approximately 3.72.

immediate split:
approximately 10.07.

Thus:
early split wastes permanent memory on brief specialization.

LONG TRANSIENT

gated:
approximately 9.49
under the tested duration distribution.

immediate:
10.07.

PERSISTENT

gated:
approximately 22.46
because the conservative 800-block gate pays a long provisional period.

immediate:
10.07.

PRIMARY PERSISTENCE-LATENCY NEGATIVE
A gate conservative enough to avoid long transients
can react too slowly to genuinely persistent specialization.

Before enough history accumulates,
the two cases are observationally identical.

This is not fixable by choosing a sharper threshold.

It is a genuine:
FUTURE-DURATION IDENTIFIABILITY LIMIT.

RECURRENT SPECIALIZATION

T=800
R=3 gated cost:
approximately 15.27.

lease-only:
approximately 24.96.

The recurrence path can justify family branching even when:
no single episode is long.

Thus:
RECURRENCE
carries structural evidence distinct from:
CONTINUOUS DURATION.

RARE RECURRING SPECIALIZATION
A low recurrence threshold can over-promote rare specializations.

At R=3,
the tested rare 4-episode class branches and can pay more permanent cost than continued local leasing.

Increasing recurrence requirement toward:
R=5

prevents this branch in the tested four-episode class.

Thus:
RECURRENCE COUNT ALONE
IS NOT
EXPECTED FUTURE VALUE.

It must be priced by:
- branch cost;
- recurrence spacing;
- functional stake;
- reconstruction latency.

GENERAL STRUCTURAL DECISION
A local specialization should conceptually move through:

LOCAL LEASE

->

REPEATED UTILITY / RECURRENCE EVIDENCE

->

ESTIMATED FUTURE VALUE

compared with

PERMANENT FAMILY-BRANCH PRICE

->

REMAIN LOCAL
or
CREATE GENERATIVE BRANCH.

RELATION TO H34/H35
H34:
retain dormant lineages according to expected future value.

H35:
retirement depth depends on recurrence urgency and reconstruction cost.

H45 extends the same economics to:
CREATING NEW GENERATIVE FAMILY STRUCTURE.

Creation
and
retirement
should use compatible value accounting.

RELATION TO H37
H37:
existing families merge/split according to memory price and persistent fit cost.

H45 adds:
a local specialization should not become a new family merely because it differs.

It must earn:
future reusable structural value.

RELATION TO H44
H44's reversible local lease is essential because:
the system cannot know future specialization duration at onset.

Lease supplies:
fast local adaptation

while delaying:
permanent memory commitment.

PRIMARY ARCHITECTURAL PRINCIPLE
REVERSIBLE LOCAL EXPRESSION
SHOULD PRECEDE
IRREVERSIBLE / LONG-LIVED STRUCTURAL COMMITMENT
WHEN FUTURE VALUE IS UNCERTAIN.

But:

PERMANENT COMMITMENT SHOULD NOT BE DELAYED FOREVER
WHEN MEMORY IS CHEAP
AND
REUSE VALUE IS HIGH.

DECISION
AR-H45 is POSITIVE WITH A FUTURE-DURATION IDENTIFIABILITY LIMIT.

Supported synthetically:

- immediate family split can be optimal when permanent memory is cheap;
- persistence/recurrence gating becomes preferable as memory price rises;
- very high memory price can make lease-only behavior optimal;
- short transients strongly favor reversible local leasing;
- persistent specializations expose a cost of conservative split latency;
- recurrence supplies evidence beyond continuous duration;
- low recurrence thresholds can still over-promote rare specializations.

Not demonstrated:

- real Yggdrasil branch-memory price;
- learned recurrence-value estimator;
- optimal split thresholds;
- continuous niche geometry;
- branch sharing across several local specializations;
- online interaction with global resource reserve.

NEXT CLEAN QUESTION
AR-H46 — ENDOGENOUS GENERATIVE-MEMORY PRICE

H45 sweeps memory price externally.

Question:

Can the organism derive a useful local structural-memory price from its own current resource envelope?

Candidate inputs:

- total compact memory occupancy;
- active/dormant maintenance load;
- recent regeneration demand;
- reserve/runway pressure;
- expected branch reuse;
- structural write backlog.

Desired:

memory abundant
->
lower threshold for useful branch creation.

memory scarce
->
prefer local leases / compressed templates.

after old branches retire
->
memory price should fall again
and
new useful structure should become affordable.

This connects:
H45 family creation
with
H31 resource envelope
H34 retirement
H37 merge/split
H26 shared evidence economics.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
scenario_histories = 20000
horizon_blocks = 3000
tested_storage_prices = 0.0035,0.0045,0.006,0.008,0.010,0.015
tested_persistence_thresholds = 200,400,600,800,1000
tested_recurrence_thresholds = 3,4,5
