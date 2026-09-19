TITLE: DG-1A-AR-H121 — Change-Debt Dependency Graph / Developmental Deadlock Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DEADLOCK-DETECTION + VALUE-AWARE CYCLE-BREAK RESULT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh120-change-debt-scheduling-audit.ice

PURPOSE
H120 schedules:
multiple incomplete self-change debts.

But H120 treats:
those debts
as:
mostly independent.

H121 asks:

WHAT IF
ONE INCOMPLETE CHANGE
REQUIRES
ANOTHER
TO COMPLETE FIRST?

The resulting dependency graph
can contain:
cycles.

Question:

CAN DEVELOPMENTAL DEADLOCK
BECOME:
EXPLICIT,
DETECTABLE,
AND
RECOVERABLE?

BOUNDARY
This is synthetic.

It does not:
- freeze a graph representation;
- freeze cycle-breaking policy;
- prove real Yggdrasil change dependencies are pairwise;
- implement distributed consensus;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CHANGE-DEBT GRAPH
14 incomplete developmental transactions.

Debt types:
repair,
role,
macro,
sensor.

Each debt carries:

remaining transition work,

unresolved blockage / interest,

mature functional value,

rollback cost,

and:
zero or more:
dependency edges.

BASE GRAPH
Most dependencies
are:
acyclic.

In approximately:
55%
of portfolios,
one synthetic 3-node dependency cycle
is inserted.

Roughly half
of inserted cycles
are constructed
to include:
a repair debt
when:
one is available.

DEPENDENCY SEMANTICS
A debt can:
consume transition work
only after:
all prerequisite debts
have:
resolved.

Resolution can be:
completion

or:
explicit rollback to:
the old compatible interface.

Thus:
rollback can:
break a dependency cycle.

RECOVERY HORIZON
55 steps.

Transition recovery capacity:
4 work units / step.

Unresolved debt continues:
accruing:
functional interest.

Completed transitions:
earn:
mature-state value.

COMPARATORS

DEPENDENCY-AWARE ONLY
Process:
ready debts.

If:
no unresolved debt is ready,
the scheduler:
waits.

RANDOM CYCLE BREAK
When:
no debt is ready,
detect:
a dependency cycle

and rollback:
one random cycle member.

SMALLEST-DEBT CYCLE BREAK
Rollback:
the cycle member
with:
least remaining transition work.

VALUE-AWARE CYCLE BREAK
Rollback:
the cycle member
with:
lowest projected future importance,
combining:

rollback cost,

forgone mature value,

ongoing blockage importance,

and:
type-specific abandonment consequence.

High-value repair debt
therefore:
usually survives.

PRIMARY CONFIRMATION
5,000 matched synthetic dependency portfolios.

DEPENDENCY-AWARE ONLY

mean net value:
288.59.

10th percentile:
109.33.

mean unresolved debts at horizon:
2.21.

mean rolled back:
0.

PRIMARY DEADLOCK NEGATIVE
A scheduler can:
understand every dependency

and still:
make no progress.

When:
the ready set is empty
but:
unresolved debt remains,

the system is:
DEADLOCKED.

Unused recovery capacity
does not:
solve:
a cyclic dependency.

RANDOM CYCLE BREAK

mean:
392.05.

10th percentile:
341.45.

mean rollback transactions:
0.552.

unresolved at horizon:
0.

repair rollbacks:
0.191 / portfolio.

PRIMARY CYCLE-BREAK POSITIVE
Explicitly recognizing:

NO READY WORK
+
UNRESOLVED GRAPH

as:
a deadlock condition

allows:
recovery.

One explicit rollback
is often enough
to:
restore:
topological progress.

SMALLEST-DEBT CYCLE BREAK

mean:
396.67.

10th:
350.68.

repair rollback:
0.0438.

PRIMARY SMALL-DEBT RESULT
Avoiding:
large transitions

is:
better
than:
random sacrifice

because:
large/high-interest repair state
is:
less likely
to be discarded.

But:
remaining work alone
is not:
the right rollback value.

VALUE-AWARE CYCLE BREAK

mean:
398.68.

10th:
354.36.

mean rollback:
0.552.

unresolved:
0.

repair rollback:
0.0134.

PRIMARY VALUE-AWARE POSITIVE
The strongest tested policy
breaks:
the same number of cycles

as:
random rollback

but:
sacrifices:
far less:
high-value repair state.

Compared with:
random cycle breaking,

repair rollback falls by:
approximately 93%.

The gain in:
mean value
is modest

but:
the semantic difference is important.

DEADLOCK RESOLUTION
SHOULD NOT
SACRIFICE:
ARBITRARY STATE.

CYCLE BREAK AS:
LOSS-MINIMIZATION
A deadlock forces:
a choice.

At least one:
dependency obligation
must:
change.

The system should select:
the smallest expected loss
compatible with:
restoring progress.

This can mean:

rollback a role change,

abandon a low-value sensor restructure,

or:
restore an old macro interface

rather than:
throwing away:
urgent repair.

DEPENDENCY GRAPH STATE
A change-debt entry now needs:

TRANSITION ID

+

REMAINING WORK

+

DEPENDENCIES

+

DEPENDENTS

+

CURRENT BLOCKAGE COST

+

ROLLBACK / ABANDONMENT COST

+

MATURE VALUE

+

SAFETY PRIORITY.

The portfolio additionally needs:

READY SET

and

DEADLOCK / CYCLE STATE.

RELATION TO H118
H118:
coupled change
can:
share transaction staging.

H121:
coupled change
can also:
create:
mutual waiting.

Composition requires:
both:
transaction benefit

and:
dependency discipline.

RELATION TO H119-H120
H119:
partial self-change
becomes:
explicit debt.

H120:
many debts
must be:
scheduled.

H121:
their dependencies
must also be:
represented.

The progression is:

PARTIAL CHANGE

->
DEBT

->
DEBT PORTFOLIO

->
DEPENDENCY GRAPH.

RELATION TO DISTRIBUTED SYSTEMS
The useful analogy is:
wait-for graphs
and:
deadlock recovery.

This is:
architectural inspiration only.

H121 remains:
synthetic developmental research.

GENERAL PRINCIPLE
IF:
RECOVERY CAPACITY EXISTS

BUT:
NO DEVELOPMENTAL DEBT
CAN ADVANCE,

ASK:

AM I
RESOURCE-LIMITED

OR:

DEPENDENCY-DEADLOCKED?

Those are:
different failure modes.

And:

BREAK CYCLES
BY:
MINIMIZING LOST FUNCTION,
NOT:
BY:
ARBITRARY ROLLBACK.

DECISION
AR-H121 is POSITIVE
for:
EXPLICIT CHANGE-DEPENDENCY / DEADLOCK STATE

WITH:
a VALUE-AWARE CYCLE-BREAK REQUIREMENT.

Supported synthetically:

- change debts can form cyclic dependencies;
- dependency-aware scheduling alone does not solve cycles;
- an empty ready set with unresolved debt is a useful deadlock signal;
- explicit cycle breaking restores recovery progress;
- random rollback can sacrifice high-value repair state;
- value-aware rollback strongly reduces repair sacrifice;
- dependency graphs should be first-class developmental state.

Not demonstrated:

- distributed deadlock detection;
- dependency uncertainty;
- asynchronous updates;
- partial edge rollback;
- higher-order hypergraph dependencies;
- deadlock among live cell populations;
- starvation after repeated cycle breaking.

NEXT HIGH-VALUE MOVE
AR-H122 — SOFT DEPENDENCY / INTERFACE-SHIM DEVELOPMENT AUDIT

H121 breaks:
a dependency cycle
by:
rolling back
one transaction.

A more interesting alternative:

CAN THE ORGANISM
TEMPORARILY BUILD:
AN INTERFACE SHIM

that:
lets:
two partially transitioned states
communicate
without:
fully completing
or:
rolling back
either one?

Potential gain:

break:
deadlock

while:
preserving:
both developmental investments.

Potential failures:

- shim cost exceeds rollback value;
- shim hides semantic incompatibility;
- temporary compatibility becomes permanent technical debt;
- many shims create:
translation overhead.

Compare:

A.
transaction rollback;

B.
temporary compatibility shim;

C.
value-gated shim;

D.
shim expiry;

E.
multiple stacked shims;

F.
new state later becomes:
natively compatible.

Desired:

INTERFACE ADAPTATION
can:
buy time

but:
must not become:
unbounded permanent glue.

This would connect:
H101 interface validation
with:
H121 developmental deadlock.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
dependency_portfolios = 5000
cycle_probability = 0.55
dependency_only_mean = 288.593792
random_break_mean = 392.049515
value_break_mean = 398.680397
value_break_repair_rollback = 0.0134
