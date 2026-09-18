TITLE: DG-1A-AR-U2 — Moving-Demand Role Relocation Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE PRECURSOR
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-aru1-multirole-utility-market-audit.ice

PURPOSE
Test whether useful specialization can relocate when functional demand moves,
or whether cells remain permanently canalized into obsolete roles.

This is a direct precursor to the requirement:
same developmental genome
+
different local demand
->
different functional organization.

BOUNDARY
This is synthetic.

It does not:
- train Yggdrasil;
- establish cognitive specialization;
- execute STAB-18-R1;
- use global role targets.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BODY
149-node radius-7 four-neighbor disk.

MULTI-ROLE BACKGROUND
The same factorized local utility market from AR-U1 remains active:

relay
repair
inhibitor
growth
+
derived dormant state.

Only communication demand is moved for the primary relocation test.
The other synthetic local demands continue in the background.

DEMAND A — HORIZONTAL
Three message pairs traverse approximately:

left <-> right

at three vertical offsets.

DEMAND B — VERTICAL
Three message pairs traverse approximately:

bottom <-> top

at three horizontal offsets.

The geometric horizontal and vertical route skeletons contain:
41 nodes each

with only:
9 shared nodes.

Thus the task requires a substantial spatial reorganization.

CANALIZATION NEGATIVE FROM EARLIER UPDATE LAW
The earlier saturating logit role rule could learn the new vertical relay pattern,
but obsolete horizontal relay state retired extremely slowly.

After 180 steps on the new demand:
old horizontal corridor relay remained approximately 1.0.

Even after 600 steps:
old horizontal corridor relay remained approximately 0.84.

Therefore the first rule solved demand addition,
not true role relocation.

This negative motivated the bounded kinetic retirement term preserved in AR-U1.

KINETIC WORKING POINT
Exploratory retirement-coefficient sweep:

0.05
0.10
0.15
0.20
0.25
0.50
0.75
1.00

showed the expected trade-off:

too little retirement:
better static performance
but more obsolete specialization.

too much retirement:
cleaner de-specialization
but worse static functional performance.

A follow-up working point used:
retirement coefficient = 0.10

This is an exploratory synthetic choice.
It is not a Yggdrasil scientific hyperparameter.

FRESH RELOCATION TEST
Fresh seeds:
20..27
n = 8

Horizontal specialization:
220 steps

Then:
switch to vertical demand

Adaptation:
180 steps

RECOVERY CRITERION
New-demand route cost returns to within 10% of the seed's pre-switch horizontal route cost for 10 consecutive steps.

RESULTS

Pre-switch horizontal route cost:
mean 20.60619
sd   0.01037

Immediate vertical route cost using old organization:
mean 52.53964
sd   0.04268

Adaptive final vertical route cost:
mean 20.47480
sd   0.00329

Frozen-role final vertical route cost:
mean 54.08067
sd   0.04155

Recovery:
8/8 seeds

Median switching latency:
60 steps

Range:
57..62 steps

SPATIAL ROLE RELOCATION

Before switch:

relay on horizontal corridor:
0.89137

relay on vertical corridor:
0.22603

After 180 vertical-demand steps:

relay on horizontal corridor:
0.35787

relay on vertical corridor:
0.89365

Thus obsolete relay expression substantially retires while the new corridor becomes strongly specialized.

GLOBAL RELAY LOAD

before:
0.27401

after:
0.29525

The new solution does not require doubling total relay expression.

TOP-20% SPECIALIST TURNOVER
Jaccard overlap between:
top 20% relay nodes before switch
and
top 20% relay nodes after switch

mean:
0.115385

The spatial identity of the strongest relay specialists is therefore largely replaced.

PLACEMENT CONTROL
Randomly permute the final relay gate values across nodes while preserving:
- exact relay-value distribution;
- exact total relay mass;
- all non-relay state;
- graph;
- vertical demands.

20 permutations per seed.

Shuffled final vertical route cost:
mean 48.04496

Adaptive placement:
20.47480

Therefore:
the result depends on spatial placement,
not only total role mass.

REPEATED SWITCHING
Fresh seeds:
30..37
n = 8

After initial horizontal specialization,
alternate demand:

V
H
V
H

120 steps per phase.

Mean last-20-step route cost:

first V:
20.71222

first H return:
20.54654

second V:
20.57004

second H return:
20.53355

Mean corridor relay expression:

after first V:
H = 0.45678
V = 0.89101

after H return:
H = 0.89315
V = 0.45771

after second V:
H = 0.45928
V = 0.89287

after second H:
H = 0.89337
V = 0.46051

Global relay gate remained around:
0.319..0.325

No progressive relay accumulation was observed across these four switches.

PRIMARY POSITIVE
With explicit bounded role retirement,
the local utility market can:

- specialize;
- detect moved functional demand through local traffic;
- retire obsolete specialization;
- recruit a new spatial role pattern;
- restore function;
- reverse that organization repeatedly.

This is substantially stronger than:
"cells can switch labels."

The useful spatial substrate itself relocates.

INTERPRETATION
A plausible developmental-computation primitive is:

local functional demand
->
soft specialization
->
performance improvement

then when demand moves:

old utility disappears
->
old specialization decays

new utility appears
->
new specialization grows.

The retirement term is therefore not an implementation detail.

It is part of the adaptive architecture.

RELATION TO LITERATURE
Béna and Goodman (Nature Communications 2025) report that functional specialization can vary dynamically over time and depends on the timing and bandwidth of information flow.

This synthetic result is consistent with that general observation:
specialization should be evaluated as a time-dependent state,
not a permanent cell identity.

Sensor movement drives emergent attention and scalability in active neural cellular automata
Neural Networks 200 (2026), 108798

provides a contemporary NCA example in which changing where information is acquired can produce adaptive distributed behavior.

Neither work establishes the Yggdrasil mechanism tested here.

NEXT
AR-U3:
corrupt and delay the LOCAL UTILITY / consequence signal.

Test:
- missing feedback;
- noisy feedback;
- delayed feedback;
- semantically wrong role credit.

The purpose is to determine whether role adaptation remains stable when local consequence estimates are imperfect.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
fresh_relocation_seeds = 8
fresh_repeated_switch_seeds = 8
