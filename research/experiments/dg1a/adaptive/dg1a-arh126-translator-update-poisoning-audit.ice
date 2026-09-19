TITLE: DG-1A-AR-H126 — Shared Translator Update Poisoning / Versioned Interface-Family Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DUAL-PATH SHARED-TRANSLATOR UPDATE RESULT + STRICT-FIT FREEZE / IN-FAMILY POISON LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh125-translator-family-collision-audit.ice

PURPOSE
H125 protects:
which bridges belong to:
a translator family.

H126 asks a different question:

HOW SHOULD
THE SHARED TRANSLATOR ITSELF
BE UPDATED?

Because:
shared interface state
has:
high leverage.

One bad member
can:
poison
many bridges.

BOUNDARY
This is synthetic.

It does not:
- freeze the translator parameterization;
- freeze residual thresholds;
- freeze canary cadence;
- prove one update rule solves every poison mode;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SHARED TRANSLATOR
Six-dimensional synthetic family state.

Base vector:

[0.2,
 0.4,
 0.6,
 0.8,
 0.5,
 0.3].

Member observations contain:
ordinary noise.

Three separate stress families
are tested.

STRESS A — OBVIOUS OUTLIER POISON
20%
of member updates
receive:
large multi-dimensional semantic corruption.

The corruption is:
far outside:
ordinary family residuals.

COMPARATORS

NAIVE EMA

FIT-WEIGHTED UPDATE

SHADOW / CANARY UPDATE.

200 matched runs.

FINAL HELD-OUT MSE

NAIVE:
~0.01338.

FIT-WEIGHTED:
~0.00160.

SHADOW / CANARY:
~0.00248.

PRIMARY OUTLIER RESULT
Obvious off-family corruption
is best handled by:
local robust admission.

Residual weighting
prevents:
large bad updates
from:
moving:
shared family state.

This is:
cheap
and:
effective.

But:
this mechanism alone
is not sufficient.

STRESS B — LEGITIMATE POPULATION-WIDE SEMANTIC SHIFT
At:
block 40

the entire translator family
changes coherently.

Shift magnitude:
large enough
to:
look off-manifold
to:
the old family model.

STRICT FIT GATE
Accept:
only member updates
within:
a tight residual threshold
of:
the old translator.

Result:

FINAL MSE:
~0.04661.

The family effectively:
freezes.

PRIMARY STRICT-FIT FAILURE
A rule designed to reject:
bad outliers

can also reject:
real developmental change.

If:
every member changes together,
the old model should not:
retain permanent veto authority.

SHADOW FAMILY CANDIDATE
All coherent new observations
can update:
a provisional family version.

The live family remains:
unchanged.

Fresh independent current-context canaries
compare:

LIVE
vs
SHADOW.

Promotion requires:
four consecutive strong candidate wins.

300 matched runs.

mean first promotion:
~47.69 blocks.

The true shift begins:
block 40.

FINAL MSE AFTER PROMOTION:
~0.0000056.

PRIMARY COHERENT-SHIFT POSITIVE
The shared translator can:
change dramatically

without:
giving:
raw new traffic
immediate live authority.

The correct architecture is:

QUARANTINE / SHADOW

->
PERSISTENT COHERENCE

->
INDEPENDENT CANARY

->
VERSION PROMOTION.

After:
promotion,

ordinary live adaptation
can resume
around:
the new family state.

STRESS C — SLOW IN-FAMILY POISON
40%
of incoming member updates
carry:
small structured bias

on:
two translator dimensions.

The bias remains:
inside:
the ordinary family fit envelope.

Thus:
residual weighting
does NOT:
identify:
the updates as:
outliers.

300 matched runs.

FINAL PARAMETER MSE

NAIVE:
~0.001587.

FIT-WEIGHTED:
~0.001575.

SHADOW / INDEPENDENT CANARY:
~0.000227.

PRIMARY IN-FAMILY POISON RESULT
Fit confidence
is:
not the same as:
functional correctness.

An update can:
look:
perfectly family-like

and still:
move:
the shared translator
in:
a harmful direction.

Independent canaries
provide:
a separate authority channel.

DUAL-PATH UPDATE ARCHITECTURE
H126 does NOT support:
one universal family-update rule.

The useful stack is:

PATH 1 — LOCAL ROBUST ADMISSION

reject / downweight:
obvious member outliers.

PATH 2 — VERSIONED SHARED WRITE

candidate shared translator
lives in:
shadow.

Promotion requires:
independent functional evidence.

PATH 3 — COHERENT SHIFT RECOGNITION

if:
many members
systematically disagree with:
the old family

do not:
freeze forever.

Allow:
a new family version
to:
compete.

SHARED-STATE AUTHORITY PRINCIPLE
The more members
a state update can affect,

the stronger:
its write evidence
should be.

One member may:
change:
its own provisional adapter

with:
weak evidence.

Changing:
the family translator

requires:
stronger,
independent
support.

RELATION TO H38-H40
H38-H40 found:
the same leverage problem
for:
shared generative lineage memory.

H126 reproduces it at:
interface grammar.

The recurrence is important.

Shared state
across:
different architecture layers
appears to need:

- provisional update;
- lower live write authority;
- independent canary;
- versioning;
- rollback;
- provenance diversity.

RELATION TO H125
H125 protects:
family membership.

H126 protects:
family state.

These are:
separate questions.

A bridge can:
correctly belong to:
the family

while:
its update
still should not:
rewrite:
the shared translator.

GENERAL PRINCIPLE
SHARED STRUCTURE
SHOULD BE:
EASIER TO READ
THAN:
TO WRITE.

And:

ROBUST OUTLIER FILTERING
CANNOT REPLACE:
VERSIONED FUNCTIONAL VALIDATION.

DECISION
AR-H126 is POSITIVE
for:
DUAL-PATH SHARED TRANSLATOR UPDATES

WITH:
STRICT-FIT FREEZE
AND
IN-FAMILY POISON LIMITS.

Supported synthetically:

- obvious translator outliers are strongly reduced by fit-weighted update;
- strict fit gating can freeze a legitimate population-wide semantic shift;
- coherent shift can be learned safely in shadow and promoted by independent canaries;
- small in-family poison bypasses ordinary fit filtering;
- independent canaries strongly reduce in-family shared-state drift;
- shared translator writes should have lower authority than member-local adaptation.

Not demonstrated:

- real interface canaries;
- asynchronous family version rollout;
- partial member adoption;
- rollback after delayed semantic failure;
- multiple competing candidate family versions;
- cross-family shared translator dependencies.

NEXT HIGH-VALUE MOVE
AR-H127 — STAGGERED FAMILY VERSION ROLLOUT / MIXED-VERSION INTERFACE AUDIT

H126 promotes:
one new shared translator version.

A real distributed tissue
may not:
switch every member
at the same instant.

Question:

WHAT IF
SOME BRIDGES
USE:
VERSION N

while:
others already use:
VERSION N+1?

Potential failures:

- mixed-version incompatibility;
- cascading translation shims;
- rollback ambiguity;
- temporary double-memory cost;
- one member lags indefinitely.

Compare:

A.
atomic family-wide cutover;

B.
uncoordinated rollout;

C.
staggered rollout with version leases;

D.
mixed-version compatibility shim;

E.
canary subset first;

F.
rollback after:
new version fails late.

Desired:

SHARED TRANSLATOR UPDATE
should:
roll out
without:
requiring:
one global stop-the-world switch

and without:
letting:
mixed-version state
become:
permanent.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
outlier_runs = 200
legitimate_shift_runs = 300
in_family_poison_runs = 300
outlier_naive_mse = 0.01338
outlier_fit_mse = 0.00160
legitimate_strict_fit_mse = 0.04661
legitimate_shadow_mse = 0.0000056
in_family_fit_mse = 0.001575
in_family_shadow_mse = 0.000227
