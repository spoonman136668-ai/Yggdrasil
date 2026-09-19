TITLE: DG-1A-AR-H23 — Shared Meta-Rule vs Collapsed Trust-State Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SHARED-UPDATE RESULT + HARD GLOBAL-TRUST-COLLAPSE NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh22-learned-context-challenge-value-audit.ice

PURPOSE
H5-H22 repeatedly introduced local state with the same functional motifs:

- recency;
- confidence;
- causal validity;
- resource cost;
- reversible authority.

Those motifs now appear in:
- inherited-prior expression trust;
- causal-control trust;
- nomination/search trust;
- context-routing trust;
- learned challenge-value trust.

H23 asks:

Can Yggdrasil reuse ONE COMPACT LOCAL TRUST UPDATE FORM
without collapsing all adaptive meanings into one global confidence scalar?

BOUNDARY
This is synthetic.

It does not:
- prove one production update equation is sufficient;
- freeze a trust threshold;
- freeze per-type timescales;
- authorize a global confidence controller;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SYNTHETIC TRUST DOMAINS
Five local adaptive trust channels:

D0:
inherited-prior expression.

D1:
causal-control validity.

D2:
structural nomination/search trust.

D3:
context-routing authority.

D4:
challenge-value policy trust.

Each domain has a hidden binary condition:

CURRENTLY VALID
or
CURRENTLY INVALID.

Each receives its own noisy local evidence stream.

VALID evidence success probability:

D0 0.90
D1 0.85
D2 0.80
D3 0.90
D4 0.75.

INVALID evidence success probability:

D0 0.20
D1 0.25
D2 0.30
D3 0.15
D4 0.35.

FUNCTIONAL WRONG-AUTHORITY WEIGHTS

D0:
3

D1:
4

D2:
2

D3:
5

D4:
1.

These are synthetic contrast weights only.

TRUST UPDATE MOTIF
Generic form:

trust_next
=
(1 - alpha)
*
trust
+
alpha
*
new_local_evidence.

Authority:

trust >= 0.50.

This is intentionally simple.

The question is not whether EMA is the final mechanism.

The question is whether:
ONE UPDATE FORM

can be reused while:
EACH ADAPTIVE MEANING KEEPS ITS OWN LOCAL STATE.

PRIMARY NONSTATIONARY STREAM
5,000 opportunities.

Domains become invalid and recover on different schedules.

D0 invalid:
1200..2199.

D1:
1800..3199.

D2:
700..1099
and
2400..2799.

D3:
1600..1899.

D4:
1000..2599.

No domain is given another domain's hidden validity state.

COMPARATORS

SEPARATE TUNED TIMESCALES
Same mathematical update form,
but each trust channel uses its individually best tested alpha from:

0.002
0.005
0.01
0.02
0.05
0.10
0.20.

Selected on separate training seeds:

D0:
0.10

D1:
0.10

D2:
0.05

D3:
0.10

D4:
0.02.

SHARED UPDATE / SINGLE ALPHA
Five distinct trust scalars.

One common update form.

One common alpha:

0.05.

SHARED UPDATE / SMALL TYPED TIMESCALE
Five distinct trust scalars.

Same update form.

Only a small type distinction:

D0-D3:
0.05

D4:
0.02.

COLLAPSED GLOBAL TRUST
One global trust scalar.

At each step:
average all five evidence channels

and update:

one trust value.

That single value controls authority for all five domains.

PRIMARY CONFIRMATION
40 fresh matched seeds.

WEIGHTED WRONG-AUTHORITY FRACTION

SEPARATE TUNED

mean:
0.005687

SD:
0.000728.

SHARED SINGLE-ALPHA

mean:
0.006937

SD:
0.000736.

SHARED SMALL-TYPED

mean:
0.006952

SD:
0.000561.

COLLAPSED GLOBAL

mean:
0.154951

SD:
0.001158.

PRIMARY POSITIVE
A single shared update form with distinct local trust state performs close to the individually tuned per-domain controllers.

Absolute weighted error difference:

0.00694
vs
0.00569.

The shared-form penalty is small in this synthetic population.

Thus:
CODE / RULE REUSE
DOES NOT REQUIRE
STATE COLLAPSE.

PRIMARY HARD NEGATIVE
Collapsing all trust meanings into one scalar increases weighted wrong-authority fraction to:

0.15495.

That is approximately:

27x

the separately tuned error

and over:

22x

the shared-form / separate-state error.

Therefore:

ONE META-RULE
MAY BE GOOD.

ONE GLOBAL CONFIDENCE NUMBER
IS NOT.

WHY COLLAPSE FAILS
Different trust channels can be valid at the same time that another is invalid.

For example:

context evidence may remain trustworthy
while
a causal-control source becomes contaminated.

Or:

a slow inherited prior may remain stored
while
its current expression should be suppressed.

A global trust scalar forces unrelated validity states to interfere.

ISOLATED-FAILURE STRESS
Separate diagnostic:

3,000 opportunities.

All five domains remain valid
except:

D0 invalid during:
1000..1999.

100 matched seeds.

SHARED UPDATE WITH SEPARATE STATE
alpha:
0.05.

Mean wrong-authority fraction by domain:

D0:
0.00899

D1:
0

D2:
0.000027

D3:
0

D4:
0.000513.

COLLAPSED GLOBAL TRUST
alpha:
0.05.

D0:
0.33333.

D1-D4:
0.

INTERPRETATION
The global scalar does not suppress the isolated invalid domain because the four still-valid domains keep the aggregate confidence high.

Thus:

GLOBAL CONFIDENCE CAN HIDE LOCAL FAILURE.

In other geometries the reverse can also occur:

one severe failure can suppress unrelated valid capabilities.

The problem is structural.

LOCAL STATE IS NOT DUPLICATE ARCHITECTURE
Maintaining five trust values does not imply:
five neural networks
or
five schedulers.

The supported abstraction is:

ONE SHARED TRUST UPDATE MOTIF

applied to:

TYPED LOCAL TRUST STATE.

A type identifies:
WHAT QUESTION THIS CONFIDENCE ANSWERS.

Examples:

EXPRESSION TRUST:
should this inherited prior currently bias phenotype?

CONTROL TRUST:
is this source currently a valid causal baseline?

NOMINATION TRUST:
should this heuristic receive expensive search budget?

CONTEXT TRUST:
should this fingerprint route delayed credit?

VoI-POLICY TRUST:
is this learned evidence-allocation rule currently calibrated?

These variables may share:
- update code;
- decay machinery;
- bounded state representation;
- causal-control utilities.

They should not automatically share:
one numeric authority state.

TYPE-SPECIFIC TIMESCALE RESULT
The separately tuned synthetic working point uses three distinct timescale classes:

FAST:
0.10

MEDIUM:
0.05

SLOW:
0.02.

This suggests a possible compact implementation:

one trust-update kernel

+
small trust-type metadata

+
per-instance trust value.

H23 does NOT establish those exact three classes.

It only shows:
some typed timescale flexibility can preserve most of the benefit of bespoke controllers.

GENERAL ARCHITECTURAL PRINCIPLE
Reuse:

THE UPDATE LAW.

Preserve:

THE SEMANTIC QUESTION
and
THE LOCAL STATE.

Do not confuse:
shared computation

with:
shared authority.

RELATION TO EXISTING YGGDRASIL THESIS
This is compatible with the standing goal:

ONE COMPACT SHARED DEVELOPMENTAL ENGINE.

Cells do not need:
separate bespoke networks
for memory,
control,
context,
and resource allocation.

The engine can execute a common meta-rule over small typed state.

That is materially closer to the original compact-developmental objective than a growing collection of independent controller architectures.

IMPORTANT LIMITATION
H23 uses only binary validity evidence and EMA-style trust.

Real Yggdrasil trust questions may need:
- asymmetric loss;
- continuous causal confidence;
- eligibility age;
- source provenance;
- model-fit residual;
- resource price.

Therefore H23 validates:
shared form with separate state

not:
this exact scalar EMA.

DECISION
AR-H23 is POSITIVE.

Supported synthetically:

- one generic trust-update motif can serve multiple adaptive domains;
- modest per-domain tuning improves performance but is not required for useful behavior;
- small typed timescale classes are plausible;
- trust variables must remain locally distinct;
- one collapsed confidence scalar causes severe cross-domain interference;
- a failure in one trust domain must not be hidden by unrelated healthy domains.

Not demonstrated:

- final common trust-state schema;
- optimal trust type count;
- continuous typed confidence vector;
- memory/resource savings in the current Yggdrasil implementation;
- shared causal-control substrate across all trust domains;
- emergent learning of trust type.

NEXT CLEAN QUESTION
AR-H24 — MINIMAL TYPED META-STATE

Question:

What is the smallest generic per-trust-instance state that can reproduce the major behaviors already required across H5-H23?

Candidate fields:

VALUE / TRUST MAGNITUDE

RECENCY / AGE

EVIDENCE COUNT OR EFFECTIVE SAMPLE SIZE

CAUSAL-CONTROL CONFIDENCE

MODEL-FIT / CONTEXT-FIT CONFIDENCE

RESOURCE COST / AUTHORITY WEIGHT.

Test ablations.

Desired:

identify which state dimensions are genuinely independent

and

which can be derived from one another

without recreating the global-scalar failures.

The goal is not to add fields.

The goal is to minimize the generic local meta-state
while preserving:
- fast suppression;
- slow reconsolidation;
- stale-control retirement;
- context-conditioned delayed credit;
- bounded evidence spending.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
trust_domains = 5
primary_stream_steps = 5000
primary_confirmation_seeds = 40
isolated_failure_seeds = 100
shared_alpha = 0.05
collapsed_global_weighted_error = 0.154951
