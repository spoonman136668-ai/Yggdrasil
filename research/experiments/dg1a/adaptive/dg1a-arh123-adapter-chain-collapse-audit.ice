TITLE: DG-1A-AR-H123 — Adapter-Chain Collapse / Validated Direct-Bridge Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE STAGED DIRECT-BRIDGE RESULT + NON-TRANSITIVE-COMPOSITION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh122-interface-shim-development-audit.ice

PURPOSE
H122 permits:
temporary interface shims.

A new scaling problem appears when:
multiple adapters form:
A -> B -> C
chains.

Question:

SHOULD THE ORGANISM
COLLAPSE
THE CHAIN
INTO:
A -> C

to save:
translation cost?

The failure to avoid is:
assuming:

A->B valid
and
B->C valid

therefore:
A->C valid.

BOUNDARY
This is synthetic.

It does not:
- freeze one adapter representation;
- prove transitivity of real semantic interfaces;
- freeze joint canary size;
- establish runtime bridge generation;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BASE ADAPTER CHAIN
Two already validated temporary shims:

A -> B

and

B -> C.

Per-message overhead:

first shim:
0.04..0.12.

second shim:
0.04..0.12.

Traffic horizon:
5..180 messages.

CHAIN BASELINE
Keep:
both adapters.

The chain is:
semantically valid

because:
each local interface
has already passed:
its own validation.

DIRECT BRIDGE
Candidate:

A -> C.

Build cost:
2..12 synthetic units.

Per-message overhead:
0.025..0.07.

If:
semantically valid,

the direct bridge:
removes:
one translation layer
and:
reduces:
per-message cost.

NON-TRANSITIVE COMPOSITION
Approximately:
22%
of candidate direct bridges
are:
semantically non-transitive.

In these cases:

A -> B
is valid.

B -> C
is valid.

But:
skipping B's intermediate semantics
changes:
meaning / state
and:
the direct bridge fails.

Failure penalty:
25..85 synthetic value units.

PRIMARY COMPARATORS

KEEP CHAIN

ALWAYS COLLAPSE

VALIDATE-EVERY-DIRECT-BRIDGE

STAGED COST-AWARE DIRECT BRIDGE

Stage 1:
estimate whether:
expected traffic savings
can repay:
bridge build
and
validation cost.

Only then:
run:
joint A:C semantic validation.

Stage 2:
if validated,
collapse only when:
expected savings
still exceed:
semantic risk
and:
construction cost.

JOINT CANARY
12 direct A:C validation trials.

Compatible bridge:
canary success probability
~0.92.

Non-transitive bridge:
~0.38.

Primary acceptance:
9 or more successes.

Canary cost:
0.15 per trial.

PRIMARY CONFIRMATION
200,000 synthetic adapter chains.

KEEP CHAIN

mean value:
77.63.

10th percentile:
18.52.

1st percentile:
5.18.

ALWAYS COLLAPSE

mean:
55.64.

10th:
-36.96.

1st:
-74.02.

PRIMARY NON-TRANSITIVE FAILURE
Blind chain collapse is:
catastrophic in the tail.

Local interface validity
does NOT imply:
transitive semantic validity.

VALIDATE EVERY DIRECT BRIDGE

mean:
78.18.

10th:
13.05.

1st:
-3.75.

compatible direct bridge acceptance:
~98.85%.

non-transitive false acceptance:
~1.10%.

PRIMARY VALIDATION POSITIVE
Joint semantic testing removes:
most:
false direct shortcuts.

But:
validating every possible direct bridge
is itself:
wasteful.

Short-lived chains often:
cannot repay:
the bridge test
and:
construction cost.

SHORT-HORIZON STRESS
Traffic horizon:
less than 30 messages.

KEEP CHAIN

mean:
14.27.

VALIDATE-EVERY

8.38.

PRIMARY AUDITION-COST NEGATIVE
Even:
a semantically valid optimization

can be:
economically wrong
when:
its useful lifetime is short.

Thus:
interface optimization
should not:
automatically trigger:
more evidence collection.

STAGED COST-AWARE DIRECT BRIDGE

mean:
79.93.

10th:
18.48.

1st:
5.16.

Bridge auditioned:
~53.73%
of candidate chains.

Direct bridge chosen:
~35.31%.

Of chosen direct bridges:
~99.92%
are:
truly transitive
in the synthetic ground truth.

PRIMARY STAGED POSITIVE
The staged controller improves:
mean value
without:
sacrificing:
the lower tail.

It avoids:
most testing
for:
chains too short
to:
repay:
the experiment.

SHORT HORIZON

staged:
14.27.

essentially identical to:
keep-chain baseline.

LONG HORIZON
80 or more messages.

KEEP CHAIN:
109.17.

VALIDATE-EVERY:
112.93.

STAGED:
113.09.

PRIMARY TRAFFIC-LIFETIME RESULT
Direct bridge synthesis
becomes:
more valuable
as:
translation traffic
persists.

Therefore:
adapter-chain collapse should depend on:

SEMANTIC COMPATIBILITY

and

EXPECTED LIFETIME / TRAFFIC.

Not:
structure alone.

ADAPTER CHAIN OBJECT
A temporary interface graph
should plausibly track:

SOURCE STATE

+

TARGET STATE

+

TRANSLATION COST

+

SEMANTIC CANARY SUPPORT

+

EXPECTED TRAFFIC

+

EXPECTED REMAINING LIFETIME

+

DIRECT-BRIDGE CANDIDATES

+

NATIVE-COMPATIBILITY EXPIRY.

RELATION TO H101
H101 established:

valid module
+
valid module

does not imply:
valid composition.

H123 finds the same rule for:
temporary interfaces.

The intermediate state may carry:
essential semantics.

RELATION TO H84
H84:
spend experiments
where:
information value
repays:
cost.

H123:
even bridge validation
must be:
value-gated.

First ask:

IS THE OPTIMIZATION
WORTH TESTING?

Then:
test:
whether it is true.

RELATION TO H122
H122:
temporary shims can:
buy developmental continuity.

H123:
several shims can:
sometimes be compressed,

but:
only while:
preserving semantics.

GENERAL PRINCIPLE
DO NOT OPTIMIZE:

ADAPTER COUNT

IN ISOLATION.

Optimize:

SEMANTIC CORRECTNESS

+

TRANSLATION COST

+

BRIDGE BUILD COST

+

VALIDATION COST

+

EXPECTED LIFETIME.

DECISION
AR-H123 is POSITIVE
for:
STAGED VALIDATED ADAPTER-CHAIN COLLAPSE

WITH:
a NON-TRANSITIVE-COMPOSITION LIMIT.

Supported synthetically:

- direct bridges can reduce repeated translation overhead;
- valid local adapters do not imply a valid transitive shortcut;
- blind collapse has severe failure tails;
- joint semantic validation sharply reduces false shortcut creation;
- validating every possible shortcut is wasteful for short-lived chains;
- a cheap economic prefilter before semantic testing improves net value;
- long-lived adapter chains are the best candidates for direct collapse.

Not demonstrated:

- multi-hop chains beyond two adapters;
- graph-wide shortcut selection;
- semantic preservation under stateful protocols;
- bridge invalidation after context shift;
- distributed adapter construction;
- quadratic shortcut-state control.

NEXT HIGH-VALUE MOVE
AR-H124 — TEMPORARY-INTERFACE ECOLOGY / SHORTCUT MEMORY BUDGET

H122-H123 can create:
many temporary adapters
and:
some direct shortcuts.

Question:

HOW MANY
INTERFACE BRIDGES
SHOULD REMAIN
AVAILABLE
AT ONCE?

Potential failure:

every pair of partially transitioned states
accumulates:
a direct compatibility shortcut.

Temporary glue becomes:
a dense interface graph.

Compare:

A.
retain every validated shortcut;

B.
strict bridge-count cap;

C.
traffic/value-per-memory bridge retention;

D.
shared translator modules;

E.
rare bridge later reused;

F.
context shift invalidates:
an old direct bridge.

Desired:

TEMPORARY INTERFACE KNOWLEDGE
should remain:
sparse,
reusable,
and:
revalidatable

rather than:
growing:
quadratically
with:
state variants.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_chains = 200000
chain_mean = 77.63383
always_direct_mean = 55.64179
validated_direct_mean = 78.17825
staged_direct_mean = 79.93418
