TITLE: DG-1A-AR-H127 — Staggered Translator-Family Version Rollout / Mixed-Version Interface Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE CANARY-FIRST LEASED ROLLOUT RESULT + MIXED-VERSION / STOP-THE-WORLD TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh126-translator-update-poisoning-audit.ice

PURPOSE
H126 permits:
versioned shared translator updates.

H127 asks:

HOW SHOULD
A NEW FAMILY TRANSLATOR VERSION
ROLL OUT
ACROSS:
MANY BRIDGES?

A distributed tissue may not:
switch every member
at:
one instant.

The resulting temporary state is:

MIXED VERSION.

BOUNDARY
This is synthetic.

It does not:
- freeze rollout batch size;
- freeze lease duration;
- prove real bridge families can share one deployment protocol;
- establish production rollback semantics;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FAMILY
80 translator-family members.

OLD VERSION:
N.

NEW VERSION:
N+1.

VALID NEW VERSION
When semantically correct:

N+1
improves:
per-member service
by:
approximately 8%.

LATENT BUG WORLDS
18%
of synthetic rollouts
contain:
a rare semantic defect
in:
N+1.

While:
a buggy member runs,
functional service is:
reduced.

The defect may be:
caught
during:
targeted canary challenge

or:
later
through:
live consequence.

POLICIES

ATOMIC FAMILY-WIDE CUTOVER
Stop:
the whole family
during:
one coordinated migration.

No mixed-version interval.

Primary cutover downtime:
approximately 6 steps.

UNCOORDINATED MEMBER ROLLOUT
Members switch:
independently
across:
approximately 50 steps.

No shared mixed-version discipline.

Cross-version interaction:
pays:
large incompatibility overhead.

CANARY-FIRST STAGGERED ROLLOUT
First:
8 members
receive:
N+1.

Canary period:
approximately 10..12 steps.

If:
canaries remain healthy,

remaining members move:
in small batches.

During mixed version:

temporary N<->N+1 compatibility shim
reduces:
interaction cost.

Each migrated member retains:
N rollback state
for:
a bounded lease.

PRIMARY STREAM
120 steps.

5,000 matched rollout worlds.

ATOMIC

overall mean utility:
9646.78.

10th percentile:
8888.80.

valid-version worlds:
9830.32.

latent-bug worlds:
8801.51.

mixed-version interaction events:
0.

temporary old/new double-memory:
~1575 member-steps.

PRIMARY ATOMIC RESULT
Atomic cutover eliminates:
mixed-version semantics.

But:
the entire translator family
pays:
global migration downtime.

A large shared update
therefore creates:
a stop-the-world tax.

UNCOORDINATED

overall:
9333.41.

10th:
9089.28.

valid:
9422.19.

bug:
8924.51.

mixed-version interaction events:
~1838.89.

PRIMARY UNCOORDINATED NEGATIVE
Independent adoption avoids:
global downtime

but:
creates:
a long mixed-version interval.

Without:
version-aware compatibility discipline,
cross-version interaction
consumes:
large functional value.

Thus:

NO GLOBAL BARRIER

does not imply:

NO COORDINATION.

CANARY-FIRST STAGGERED

overall:
9925.45.

10th:
9552.00.

valid:
10016.62.

bug:
9505.56.

mixed-version interactions:
~1468.37.

rollback members:
~2.36
averaged across:
all worlds.

temporary double-memory:
~1671.84 member-steps.

PRIMARY STAGGERED POSITIVE
The canary-first leased rollout
achieves:
the highest tested total value.

Compared with:
atomic rollout,

it avoids:
whole-family downtime.

Compared with:
uncoordinated rollout,

it controls:
mixed-version semantics.

LATENT-BUG CONTAINMENT
In bug worlds:

the initial canary subset
uses:
targeted semantic challenge.

Primary canary catch probability:
approximately 85%.

If:
the defect is found early,

only:
the small canary subset
needs:
rollback.

Broad rollout:
never begins.

PRIMARY BLAST-RADIUS POSITIVE
A candidate shared version
can:
fail

without:
immediately exposing:
the entire family.

This is:
versioned developmental containment.

BUG ESCAPE
Some rare defects
survive:
the initial canary.

They may be:
discovered later
during:
live use.

Version leases keep:
old translator state
temporarily available.

Rollback cost therefore depends on:
lease age.

Recent migration:
cheap rollback.

Old migration:
more expensive reconstruction.

This makes:
rollback capability
time-bounded

rather than:
permanent duplicate state.

MIXED-VERSION SHIM VALUE
Staggered rollout still experiences:
many cross-version interactions.

If:
the compatibility shim
were replaced by:
the uncoordinated mismatch penalty,

the tested staggered utility
would lose:
roughly 440
additional value units
on average.

Thus:
temporary mixed-version translation
is:
part of:
the rollout architecture,
not:
a cosmetic optimization.

DOUBLE-MEMORY TRADEOFF
Staggered rollout carries:
slightly more:
old/new duplicate-state time
than:
atomic rollout.

This is expected.

It buys:

- smaller failure blast radius;
- cheap rollback;
- no family-wide stop;
- gradual validation.

Thus:
temporary double memory
is:
an insurance cost.

It should:
expire
when:
the version lease closes.

CURRENT VERSION-ROLLOUT OBJECT
A family member may carry:

ACTIVE VERSION

+

CANDIDATE VERSION

+

VERSION LEASE EXPIRY

+

MIXED-VERSION SHIM

+

CANARY / FIT STATUS

+

ROLLBACK TARGET

+

CURRENT FAMILY PROMOTION GENERATION.

The family additionally needs:

ROLLOUT PHASE

and

PROMOTION / ABORT AUTHORITY.

RELATION TO H39
H39:
shared memory updates
benefit from:
shadow candidate
and:
promotion.

H127:
promotion itself
can be:
staged.

SHADOW
and
ROLLOUT
are:
different phases.

RELATION TO H44
H44 introduced:
local version leases.

H127:
version leases become:
critical
for:
shared translator rollout.

A bounded old-version lease
preserves:
rollback
without:
permanent duplicate state.

RELATION TO H122
H122:
temporary shims
bridge:
partially changed interfaces.

H127:
the same principle
bridges:
version skew
during:
family rollout.

GENERAL PRINCIPLE
A HIGH-LEVERAGE SHARED UPDATE
SHOULD NOT REQUIRE:

ONE GLOBAL INSTANTANEOUS SWITCH.

Prefer:

SHADOW VALIDATION

->
CANARY SUBSET

->
BOUNDED STAGGERED ROLLOUT

->
VERSION LEASES

->
FINAL RETIREMENT.

But:

MIXED VERSION
IS:
REAL STATE

and:
must be:
explicitly supported.

DECISION
AR-H127 is POSITIVE
for:
CANARY-FIRST STAGGERED TRANSLATOR ROLLOUT

WITH:
a MIXED-VERSION / TEMPORARY DOUBLE-MEMORY TRADEOFF.

Supported synthetically:

- atomic cutover avoids version skew but pays family-wide downtime;
- uncoordinated rollout avoids downtime but creates costly mixed-version interaction;
- canary-first staggered rollout gives the best tested total utility;
- canary subsets reduce failure blast radius;
- version leases reduce rollback cost after late failure;
- temporary cross-version shims materially improve staggered rollout;
- old/new duplicate state is a bounded insurance cost rather than permanent memory.

Not demonstrated:

- concurrent competing candidate versions;
- distributed promotion authority;
- network partition during rollout;
- canary-selection bias;
- member-specific version incompatibility;
- multi-family coordinated migration.

NEXT HIGH-VALUE MOVE
AR-H128 — CONCURRENT FAMILY UPDATES / VERSION-FORK CONFLICT AUDIT

H127 assumes:
one candidate family version
at a time.

Question:

WHAT IF
TWO LOCAL REGIONS
INDEPENDENTLY DEVELOP:

N+1a

and

N+1b

before:
either rollout finishes?

Potential failures:

- last-writer-wins destroys useful local adaptation;
- dual version branches diverge indefinitely;
- automatic merge creates invalid semantics;
- mixed-version shims explode;
- one branch is locally valid but globally harmful.

Compare:

A.
last-writer-wins;

B.
global lock / serialize updates;

C.
version-fork retention;

D.
functional merge challenge;

E.
region-specific branch authority;

F.
later reconciliation.

Desired:

SHARED FAMILY STATE
should support:
temporary version forks

without:
turning:
concurrent local adaptation
into:
silent overwrite
or:
permanent fragmentation.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
family_members = 80
rollout_steps = 120
matched_worlds = 5000
atomic_mean = 9646.778
uncoordinated_mean = 9333.406
staggered_mean = 9925.448
staggered_bug_mean = 9505.564
