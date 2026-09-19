TITLE: DG-1A-AR-H72 — Continuous / Polyfunctional Phenotypes vs Discrete Roles Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SPECIALIZATION-PLASTICITY TRADEOFF / NO UNIVERSAL ROLE DISCRETENESS
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh71-manycell-role-ecology-audit.ice

PURPOSE
H70-H71 treat role expression as discrete:

ROLE A
or
ROLE B.

H72 asks a more fundamental question:

DO CELLS NEED DISCRETE ROLES AT ALL?

A cell could instead express:

70% A
30% B

and continuously adjust that mixture.

Potential benefit:
- smoother response;
- less phenotype switching;
- graceful handling of mixed demand.

Potential cost:
- weaker specialization efficiency;
- every cell becoming a mediocre generalist;
- loss of stable division of labor.

BOUNDARY
This is synthetic.

It does not:
- freeze continuous role representation;
- prove specialization efficiency has this exact form;
- establish final phenotype dimensionality;
- test more than two role axes;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL TISSUE
16 x 16 cells.

256 local cells.

Two work types:
A
and
B.

Four separate synthetic workloads are tested independently to avoid cross-phase backlog contamination.

WORKLOAD 1 — STABLE BALANCED HIGH LOAD

A:
0.575 / cell-step.

B:
0.575.

Total:
1.15 work units / cell-step.

WORKLOAD 2 — STABLE A-HEAVY HIGH LOAD

A:
0.90.

B:
0.25.

Total:
1.15.

WORKLOAD 3 — RAPIDLY ALTERNATING LOWER LOAD

Every 5 steps demand switches between:

A 0.70 / B 0.20

and

A 0.20 / B 0.70.

Total:
0.90.

WORKLOAD 4 — SPATIAL HETEROGENEITY

upper-left:
A 0.90 / B 0.25.

lower-right:
A 0.25 / B 0.90.

other quadrants:
A 0.575 / B 0.575.

COMPARATORS

DISCRETE LEASED SPECIALISTS
Cells are:
A
or
B.

Specialization efficiency:
1.30 work units / step
for the selected role.

Local work-demand fields
+
10-step role lease
control switching.

CONTINUOUS POLYFUNCTIONAL
Each cell stores:

f in [0,1].

A capacity:
f.

B capacity:
1-f.

Total capacity:
1.

Thus:
full plasticity

but
no specialization bonus.

CONTINUOUS + SPECIALIZATION BONUS
Total capacity grows as phenotype becomes more extreme.

Primary tested form:

capacity
=
1
+
0.30
*
(2 * abs(f - 0.5))^2.

STRONGER CONTINUOUS SPECIALIZATION
Same form with:

0.45

maximum specialization bonus.

This asks whether:
continuous phenotype
can recover most discrete specialization benefit
without a hard role switch.

PRIMARY CONFIRMATION
16 matched synthetic populations per comparator and workload.

Late stable evaluation window:
steps 300..499.

DISCRETE LEASED SPECIALISTS

STABLE BALANCED HIGH LOAD

served:
294.40 work units / step.

New arrivals:
approximately 294.4.

A-role fraction:
0.500.

Thus:
essentially complete service.

STABLE A-HEAVY

served:
294.88.

A-role fraction:
0.698.

Again:
essentially complete service.

RAPIDLY ALTERNATING

served:
230.40.

New arrivals:
approximately 230.4.

Global A-role fraction:
approximately 0.500.

SPATIAL HETEROGENEITY

served:
293.39.

PRIMARY DISCRETE POSITIVE
When specialization itself increases processing efficiency,
discrete leased roles can exploit stable workloads extremely well.

The tissue behaves as:
many specialized workers
rather than:
every cell splitting capacity.

CONTINUOUS POLYFUNCTIONAL

STABLE BALANCED HIGH LOAD

served:
256.0.

backlog:
approximately 15,378 work units
in the late evaluation window.

A fraction:
approximately 0.500.

STABLE A-HEAVY

served:
256.0.

A allocation:
approximately 0.750.

backlog:
approximately 15,597.

PRIMARY CONTINUOUS-CAPACITY NEGATIVE
Continuous phenotype tracks:
the correct local mix

but
cannot exploit:
specialization efficiency.

Its total per-cell capacity remains:
1.

Under 1.15 work units / cell-step,
backlog grows without bound.

Thus:

PLASTICITY
DOES NOT REPLACE
SPECIALIZATION ECONOMICS.

CONTINUOUS + 30% SPECIALIZATION BONUS

STABLE BALANCED

served:
256.0.

Because:
f remains near 0.5,

the specialization bonus is almost zero.

STABLE A-HEAVY

served:
278.46.

A allocation:
approximately 0.770.

Phenotype extremity:
approximately 0.540.

Thus:
continuous specialization recovers some efficiency when demand itself pushes cells toward an extreme.

But:
balanced high load still lacks:
symmetry breaking into complementary specialists.

STRONG 45% CONTINUOUS SPECIALIZATION

STABLE A-HEAVY

served:
292.25.

This approaches:
discrete specialist performance:
294.88.

However:
stable balanced load still remains near:
256.

PRIMARY SYMMETRY RESULT
A continuous phenotype that only follows:
local demand ratio

does not spontaneously split:
balanced tissue
into
complementary specialists.

This is exactly where:
H70 lateral symmetry breaking
adds value.

RAPIDLY ALTERNATING DEMAND
Continuous phenotype behaves very differently in the volatile workload.

CONTINUOUS

served:
230.378
of approximately 230.4 arrivals.

late backlog:
approximately 224.

mean fractional phenotype movement:
approximately 13.82 total cell-fraction units / step
across the 256-cell tissue.

CONTINUOUS 30% SPECIALIZATION

served:
230.378.

CONTINUOUS 45%

served:
230.378.

DISCRETE LEASED

served:
230.400.

But discrete role switching:

approximately 25.6 cell role changes / step

in the late volatile window.

PRIMARY VOLATILITY RESULT
Both architectures can service the lower-load volatile workload.

But:

CONTINUOUS PHENOTYPE
moves capacity smoothly.

DISCRETE SPECIALIZATION
uses repeated phenotype switching.

Thus:
continuous roles can provide:
plasticity

without:
full identity flips.

SPATIAL HETEROGENEITY
DISCRETE

served:
293.39.

CONTINUOUS

256.0.

CONTINUOUS 30%

257.64.

CONTINUOUS 45%

259.04.

PRIMARY SPATIAL SPECIALIZATION RESULT
Persistent local spatial niches strongly favor:
discrete or near-discrete specialization

when:
specialization increases local processing efficiency.

Continuous generalism wastes:
potential niche advantage.

PHENOTYPE-CHANGE COST INTERPRETATION
The continuous policy does not need:
cell-type replacement

or
full role switching.

Its state moves:
gradually.

The discrete policy changes:
roughly 6–10% of cells per step

in some volatile synthetic working points.

If role switching carries:
real migration,
cache,
state,
or
developmental cost,

continuous phenotype gains:
additional value.

H72 does not freeze that cost.

CORE RESULT
The correct question is not:

ARE ROLES DISCRETE
OR
CONTINUOUS?

The evidence supports:

ROLE DISCRETENESS
IS ITSELF
AN ADAPTIVE TRADEOFF.

Stable high-load environments:
favor stronger specialization.

Fast-changing mixed environments:
favor polyfunctionality.

GENERALIST vs SPECIALIST
is therefore:
a phenotype axis

not:
a one-time architecture choice.

RELATION TO H70
H70 showed:
lateral inhibition can break symmetry
and create complementary discrete specialists.

H72 shows:
that symmetry breaking is useful primarily when:
specialization efficiency is worth the rigidity.

Without a specialization gain,
continuous mixtures are much more attractive.

RELATION TO H68
H68 allowed one cell to change:
its computational implementation mode.

H72 changes:
how narrowly the cell commits
to one functional role.

Both are forms of:
metabolic phenotype plasticity.

GENERAL PRINCIPLE
Yggdrasil should preserve:
the ability to become strongly specialized

without requiring:
permanent hard cell types.

A cell may need to:

CRYSTALLIZE
under stable demand

and

MELT BACK
toward polyfunctionality

when:
the environment becomes volatile.

DECISION
AR-H72 is POSITIVE FOR AN ADAPTIVE SPECIALIZATION-PLASTICITY TRADEOFF.

Supported synthetically:

- discrete specialization exploits stable high-load niches strongly;
- continuous phenotype tracks mixed demand smoothly;
- continuous generalism loses specialization efficiency;
- continuous demand following alone does not create balanced complementary specialists;
- rapidly changing demand reduces the advantage of discrete commitment;
- spatially persistent niches favor stronger specialization;
- role discreteness should be treated as adaptive state rather than a fixed architecture constant.

Not demonstrated:

- adaptive learning of phenotype discreteness;
- more than two role axes;
- real switching cost;
- lineage inheritance of specialization;
- rare critical third roles;
- continuous causal credit between mixed phenotypes.

NEXT HIGH-VALUE MOVE
AR-H73 — ADAPTIVE PHENOTYPE CRYSTALLIZATION / MELTING

Question:

Can each cell learn:
HOW DISCRETE ITS ROLE SHOULD BE

from local environmental volatility?

Candidate state:

PLASTICITY / COMMITMENT
parameter.

Stable predictable local demand
->
increase specialization strength
and
crystallize toward role extremes.

High prediction error / rapid demand reversal
->
reduce commitment
and
melt toward polyfunctional mixtures.

Compare:

A.
fixed discrete specialist;

B.
fixed continuous phenotype;

C.
local volatility-controlled commitment;

D.
stable -> volatile transition;

E.
volatile -> stable transition;

F.
false transient volatility.

Desired:

SPECIALIZATION STRENGTH
itself becomes:
reversible developmental state.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 16x16
primary_matched_populations = 16
discrete_role_lease = 10
