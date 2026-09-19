TITLE: DG-1A-AR-H120 — Change-Debt Scheduling / Incomplete Self-Change Liability Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DEBT-PORTFOLIO SCHEDULING RESULT + RESOURCE-SCARCITY DEBT-SPIRAL LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh119-change-debt-audit.ice

PURPOSE
H119 gives:
one interrupted developmental transition
an explicit:
change-debt state.

H120 asks:

WHAT IF
A RESOURCE SHOCK
LEAVES:
MANY PARTIALLY COMPLETED SELF-CHANGES
AT ONCE?

These debts compete for:
the same recovery capacity.

The question is:
how should they be scheduled?

BOUNDARY
This is synthetic.

It does not:
- freeze one debt-priority score;
- prove developmental debt is financially analogous in all respects;
- freeze the tested debt types;
- implement distributed scheduling;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

DEBT TYPES

REPAIR MIGRATION

remaining work:
5..11 units.

unresolved interest / blockage:
1.0..1.8 per step.

mature value:
0.8..1.3 per step.

useful horizon:
35..58 steps.

rollback:
expensive.

ROLE REALLOCATION

work:
2..5.

interest:
0.10..0.35.

mature value:
0.35..0.75.

horizon:
10..24.

rollback:
cheap.

MACRO / CACHE MIGRATION

work:
4..9.

interest:
0.25..0.65.

value:
0.65..1.15.

horizon:
18..38.

SENSOR RESTRUCTURING

work:
3..7.

interest:
0.18..0.50.

value:
0.45..0.90.

horizon:
15..32.

UNRESOLVED INTEREST
Every unresolved transition
charges:
functional loss
per step.

This represents:
blocked downstream function,
degraded capacity,
or:
maintenance burden.

COMPLETED DEBT
Once:
transition work reaches zero,

the new state earns:
its mature functional value
until:
the current niche expires.

ROLLBACK
A debt may be:
abandoned
at:
a type-specific rollback cost.

Rollback:
stops future debt interest

but:
forfeits:
the mature-state value.

PRIMARY MODERATE-SCARCITY STREAM
18 incomplete debts
after:
a shared shock.

Recovery horizon:
60 steps.

Available transition work / step:

steps 0..14:
3.

15..29:
5.

30..59:
8.

Each work unit also carries:
small synthetic resource opportunity cost.

COMPARATORS

FIFO
complete:
oldest debt first.

SMALLEST DEBT FIRST
maximize:
number of finished transitions.

HIGHEST IMMEDIATE VALUE
prioritize:
mature value / remaining work.

INTEREST / BLOCKAGE PRIORITY
include:
unresolved debt interest
in:
priority.

DEBT PORTFOLIO
combine:
unresolved blockage,
future mature value,
remaining transition work,
time-to-expiry,
and
rollback economics.

The portfolio can:
proactively roll back:
low-payback debt.

PRIMARY MODERATE-SCARCITY CONFIRMATION
1,200 matched debt portfolios.

FIFO

mean net:
55.48.

10th percentile:
14.15.

completed debts:
14.72 / 18.

rolled back:
3.28.

unresolved-interest cost:
165.01.

SMALLEST FIRST

mean:
44.60.

10th percentile:
-0.23.

completed:
17.55.

rolled back:
0.45.

interest:
183.08.

PRIMARY COMPLETION-COUNT NEGATIVE
Finishing:
the most transitions

does NOT:
maximize:
functional recovery.

Small role/sensor debts
can be completed rapidly

while:
expensive high-interest repair obligations
continue:
damaging the organism.

Thus:

DEBT COUNT
IS NOT
DEBT IMPORTANCE.

HIGHEST IMMEDIATE VALUE

mean:
110.83.

10th percentile:
68.52.

completed:
11.81.

rolled back:
6.19.

interest:
129.33.

INTEREST / BLOCKAGE PRIORITY

mean:
110.42.

10th percentile:
68.29.

completed:
11.79.

rolled back:
6.21.

interest:
126.98.

DEBT PORTFOLIO

mean:
113.19.

10th percentile:
70.68.

completed:
11.25.

rolled back:
6.75.

interest:
122.77.

PRIMARY PORTFOLIO POSITIVE
The strongest tested controller
completes:
FEWER total transitions

than:
FIFO
or:
smallest-first.

But:
it produces:
approximately 2x
their net value

because:
it resolves:
the obligations that matter
and:
abandons:
low-payback developmental commitments.

This is:
a liability-management problem.

REPAIR DEBT
All moderate-scarcity policies
eventually complete:
approximately 4.50
repair debts
per portfolio.

The value difference comes from:
WHEN
high-interest debt is serviced

and:
which lower-value debts
are:
allowed to expire / roll back.

DEBT-INTEREST PRINCIPLE
An unfinished transition can:
become more expensive
the longer:
it blocks downstream function.

Therefore:
priority should depend on:

REMAINING WORK

and

CURRENT BLOCKAGE RATE.

Not merely:
creation time
or:
transition size.

SEVERE-SCARCITY STRESS
24 incomplete debts.

Recovery capacity:

steps 0..19:
2 work units / step.

20..39:
4.

40..59:
6.

The total debt load is intentionally:
too large
for:
clean full recovery.

1,000 matched portfolios.

FIFO

mean net:
-132.21.

10th percentile:
-210.92.

interest:
316.03.

SMALLEST FIRST

mean:
-188.33.

10th:
-283.22.

interest:
360.03.

VALUE PRIORITY

mean:
-23.94.

10th:
-81.57.

INTEREST PRIORITY

mean:
-24.82.

10th:
-80.52.

DEBT PORTFOLIO

mean:
-16.04.

10th:
-71.47.

interest:
235.01.

PRIMARY DEBT-SPIRAL RESULT
Under:
sufficiently severe resource scarcity,

EVERY tested controller
goes:
net negative.

This is important.

The experiment contains:
a real infeasible regime.

No scheduling trick can:
manufacture enough recovery resource.

The debt portfolio is:
least bad

but:
still loses value.

Thus:

CHANGE-DEBT MANAGEMENT
DOES NOT
ELIMINATE
RESOURCE INSOLVENCY.

SEVERE-SCARCITY SELECTIVITY
DEBT PORTFOLIO average completions:

repair:
~5.95.

role:
~0.06.

macro:
~2.66.

sensor:
~0.96.

The controller:
protects:
high-interest repair state

and:
rolls back:
most low-value role changes.

This is the desired behavior
under:
triage.

SMALLEST-FIRST FAILURE
Smallest-first completes:

~19.68
of 24 transitions,

including:
~6.37 role debts.

Yet:
it has:
the worst mean value.

This is:
developmental busywork.

The system is:
finishing many things
while:
the important unresolved liabilities
continue:
accruing loss.

CURRENT CHANGE-DEBT OBJECT
A debt portfolio entry should plausibly contain:

TRANSITION ID

+

STATE FAMILY

+

REMAINING WORK

+

CURRENT BLOCKAGE / INTEREST

+

DOWNSTREAM DEPENDENCIES

+

MATURITY VALUE

+

NICHE EXPIRY

+

ROLLBACK COST

+

RESOURCE VECTOR

+

SAFETY PRIORITY.

The scheduler allocates:
recovery metabolism
across:
these liabilities.

RELATION TO H55
H55:
acute repair can:
dominate
resource allocation

while:
slow learning retains:
bounded access.

H120:
incomplete repair transitions
also deserve:
high debt priority

when:
their unresolved burden
is:
actively damaging capacity.

RELATION TO H67
H67:
compute,
memory,
and
communication
are:
different resource species.

H120 currently collapses:
transition work
into:
one synthetic recovery resource.

A later integration must:
vectorize:
change debt
by:
resource species.

RELATION TO H119
H119:
one partial transition
must be:
resumed
or:
rolled back.

H120:
many partial transitions
must:
compete.

The correct question becomes:

WHICH SELF-CHANGE
DO I FINISH FIRST?

GENERAL PRINCIPLE
INCOMPLETE ADAPTATION
CAN ACCUMULATE:

DEVELOPMENTAL DEBT.

Do not schedule it by:

AGE

SIZE

or:
COMPLETION COUNT
alone.

Price:

BLOCKAGE

PAYBACK

ROLLBACK

and:
SCARCITY.

And:
admit:
when:
the debt load is:
temporarily insolvent.

DECISION
AR-H120 is POSITIVE
for:
CHANGE-DEBT PORTFOLIO SCHEDULING

WITH:
a RESOURCE-SCARCITY DEBT-SPIRAL LIMIT.

Supported synthetically:

- several incomplete self-changes should compete for recovery resources explicitly;
- FIFO is substantially suboptimal;
- shortest-debt-first can maximize completions while minimizing functional value;
- unresolved blockage/interest is a useful scheduling signal;
- proactive rollback of low-payback debt improves recovery;
- debt-aware scheduling improves mean and lower-tail value;
- sufficiently severe debt load remains insolvent under every tested scheduler;
- triage should protect high-interest repair debt over cheap low-value adaptation.

Not demonstrated:

- multi-resource-vector debt;
- debt dependencies / cycles;
- debt created while older debt remains unresolved;
- distributed scheduling;
- starvation prevention for slow low-interest development;
- real runtime migration queues.

NEXT HIGH-VALUE MOVE
AR-H121 — CHANGE-DEBT DEPENDENCY GRAPH / DEVELOPMENTAL DEADLOCK AUDIT

H120 treats:
debts
as:
mostly independent.

But:
one unfinished transition
may require:
another transition
to complete first.

Question:

WHAT IF
CHANGE DEBTS
FORM:
A DEPENDENCY GRAPH?

Potential failure:

A waits for B.

B waits for C.

C waits for A.

Development enters:
DEADLOCK.

Compare:

A.
priority scheduling
without:
dependency awareness;

B.
dependency-aware topological scheduling;

C.
cycle detection;

D.
rollback one low-value edge / transaction
to:
break the cycle;

E.
high-value repair inside:
a dependency cycle;

F.
new debt arriving
during:
recovery.

Desired:

PARTIAL DEVELOPMENT
should have:
dependency structure

and:
deadlock should become:
detectable state

rather than:
permanent unexplained stagnation.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
moderate_portfolios = 1200
severe_portfolios = 1000
moderate_portfolio_mean = 113.19484
moderate_fifo_mean = 55.47742
severe_portfolio_mean = -16.03505
