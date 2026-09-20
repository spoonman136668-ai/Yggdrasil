TITLE: DG-1A-AR-H149 — Dual-Channel Structural Memory / Regional Re-Validation + Cohort-Proof Audit
DATE: 2026-09-19
STATUS: ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE / CHALLENGE-HISTORY SIGNAL CONFIRMED / HANDOFF-SPECIFICITY + REGIONAL-REVALIDATION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh148-nonfungible-repair-envelope-audit.ice
PREREGISTERED_FROM_HEAD: 63407904477c39bd4510f6de682a5301f39bdfe5

PURPOSE

H148 established:

1.
NON-FUNGIBLE
ACCEPTED-REPAIR HISTORY

is useful.

In:
ACCUMULATED-MICROPATCH,

the vector / scoped controller
materially outperformed:
H147 scalar repair debt.

2.
ACCEPTED REPAIR HISTORY
IS NOT:
TOTAL STRUCTURAL HISTORY.

MOVING-WOUND
and:
BOUNDARY-PING-PONG

can repeatedly challenge:
different or recurring structural relations

while:
the accepted topology
moves very little.

Therefore:

P
cannot be:
the only cumulative path state.

3.
REGIONAL RE-DEVELOPMENT
IS TOO LARGE
A RESPONSE

when:
a local repair has already become coherent

but:
the regional repair ledger
has exhausted.

A missing mode is:

REGIONAL RE-VALIDATION.

4.
FIXED INDIVIDUAL
4+2 CERTIFICATE WITNESSES

are:
too brittle.

One challenged witness
can:
fan invalidation
across:
many otherwise-stable certificates.

Yet:
dropping structural provenance
would recreate:
unsafe stale inheritance.

H149 asks:

CAN
YGGDRASIL
REMEMBER
BOTH:

WHAT IT CHANGED

AND:

WHAT CHALLENGED IT,

while:

re-validating
coherent local structure
before:
rebuilding it,

and:

carrying maturity
with:
aggregate structural proof objects

instead of:
fragile named witnesses?

BOUNDARY

Synthetic research only.

It does not:
- implement biological tissue;
- claim biological repair equivalence;
- establish production repair thresholds;
- execute or modify STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

STAB-18-R1 remains:
UNTOUCHED.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX
LONGITUDINAL
DUAL-CHANNEL-STRUCTURAL-MEMORY
REGIONAL-REVALIDATION
COHORT-PROVENANCE

CORE ARCHITECTURE

FOUR STRUCTURAL MODES

MODE 1 — PATCH

Bounded incremental membership repair.

MODE 2 — REGIONAL RE-VALIDATION

Retain:
the current repaired topology.

Acquire:
fresh bounded structural evidence

for:
the affected region / source-target pair.

If:
the repaired topology
is independently supported,

establish:
a new regional validation baseline

without:
scratch reconstruction.

MODE 3 — REGIONAL RE-DEVELOPMENT

If:
regional re-validation fails,

reconstruct:
the affected scope
from:
fresh evidence.

MODE 4 — GLOBAL RE-DEVELOPMENT

Reconstruct:
the family

when:
repair / challenge history
is:
structurally diffuse
or:
regional recovery repeatedly fails.

DUAL-CHANNEL STRUCTURAL MEMORY

CHANNEL A — ACCEPTED REPAIR HISTORY

Retain:
H148 non-fungible accepted-change ledgers.

P =
accepted membership-change path length / N.

U =
fraction of distinct members
moved by:
accepted repair.

C_P =
mass-aware normalized entropy
of:
accepted source-region touch mass.

P_r =
region-specific accepted-change path.

Primary bounds remain:

P <=0.15.

U <=0.15.

C_P <=0.45.

P_r <=0.35.

Successful local repair:
does NOT
refund:
these ledgers.

Only:
validated regional
or:
global
baseline establishment
may reset:
the corresponding scope.

CHANNEL B — CHALLENGE EXPOSURE HISTORY

Challenge exposure is:
structural contradiction
that was observed
and:
persisted,

even when:
no topology patch
was accepted.

CONFIRMED CHALLENGE EXPOSURE

At each:
3-episode structural checkpoint,

member i contributes:
one exposure incidence

only when:

- i is structurally challenged;
- i was structurally challenged
  at the immediately previous checkpoint;
- accepted source region is unchanged;
- observed candidate target region
  is the same at:
  both checkpoints.

Thus:

one noisy checkpoint
does NOT:
consume durable challenge authority.

A persistent:
source -> target
structural contradiction
does.

EXPOSURE PATH

q_i += 1

for:
each confirmed challenge incidence.

Q =
sum_i q_i / N.

This is:
member-checkpoint structural exposure.

Successful patch:
does NOT
reduce Q.

DISTINCT EXPOSURE

V =
fraction of members
with:
q_i >0

since:
their last validated scope reset.

EXPOSURE REGION LEDGER

For each confirmed exposure:

Q_r[source] +=
1 / baseline_region_size[source].

Q_r[target] +=
1 / baseline_region_size[target].

Primary regional exposure bound:

Q_r <=0.60.

EXPOSURE DIFFUSION

Maintain:
non-decaying confirmed-exposure source mass

challenge_touch[r].

Let:

H_Q =
normalized Shannon entropy
of:
challenge_touch.

Define:

C_Q =
H_Q
*
min(1, Q / 0.30).

Primary global exposure-diffusion bound:

C_Q <=0.45.

PRIMARY GLOBAL EXPOSURE BOUNDS

Q <=0.30.

V <=0.20.

C_Q <=0.45.

No weighted average.

No:
accepted repair success
may erase:
confirmed challenge exposure.

DUAL-HISTORY INTERPRETATION

P answers:

HOW FAR
DID
THE ACCEPTED SCAFFOLD
MOVE?

Q answers:

HOW MUCH
PERSISTENT STRUCTURAL CHALLENGE
DID
THE SCAFFOLD
EXPERIENCE?

A moving wound can therefore:

keep P low

while:
Q,
V,
and:
C_Q

continue to grow.

REGIONAL CONCENTRATION

Scope concentration uses:
combined non-fungible history.

For each region:

footprint[r] =

accepted touch mass[r]
+
confirmed challenge_touch[r]
+
current challenged mass[r].

The dominant:
one-region
or:
source-target two-region
scope

must contain:
>=70%
of total nonzero footprint

for:
regional handling.

Otherwise:
global handling.

PRIMARY HANDOFF RULE

PATCH remains admissible only while:

accepted-change envelope:
inside H148 bounds

AND

challenge-exposure envelope:
inside H149 bounds

AND

current quarantine <=25%

AND

single patch <=8%

AND

failed patch cycles <3.

When:
an envelope closes,

choose:

REGIONAL RE-VALIDATION

when:

- combined concentration >=70%;
- C_P <=0.30;
- C_Q <=0.30;
- no more than two regions dominate the footprint;
- current challenged fraction <=15%;
- no multi-region failed-repair condition exists.

GLOBAL RE-DEVELOPMENT

when:

- C_P >0.45;
- OR C_Q >0.45;
- OR V >0.20
  with:
  exposure spanning >2 regions;
- OR more than two regions
  each carry >=15%
  of combined structural-history mass;
- OR global quarantine >25%;
- OR two regional redevelopment attempts fail;
- OR failed repair cycles >=3
  across:
  multiple regions.

AMBIGUOUS ZONE

If:

0.30 < C_P <=0.45

or:

0.30 < C_Q <=0.45

while:
regional concentration remains >=70%,

freeze:
currently challenged / uncertified action

and:

acquire:
one additional structural checkpoint.

Then:

regional re-validation
if:
concentration remains >=70%
and:
neither diffusion ledger exceeds 0.45;

otherwise:
global re-development.

REGIONAL RE-VALIDATION

PURPOSE

Re-establish:
a local structural baseline

without:
rebuilding a topology
that is already coherent.

SCOPE

The dominant:
source-target region pair

selected from:
combined accepted-change
+
challenge-exposure
+
current-challenge history.

TOPOLOGY

Frozen:
during re-validation.

No membership changes.

FRESH EVIDENCE

For:
3 episodes,

members currently inside:
the regional scope

receive:

2 additional
region-identity observations
per episode

on top of:
the normal H148 evidence stream.

Thus:

6 extra observations
per scoped member
for:
one validation attempt.

These observations use:
the same sensor-error class
as:
the world at that episode.

No latent labels
are supplied to:
the controller.

PROMOTION CHECK

At:
launch +3 episodes,

regional validation succeeds only when:

- mean observed support
  for:
  current accepted assignments
  across scoped members
  >=0.90;

- >=90%
  of scoped members
  have:
  accepted-assignment support >=0.80;

- structurally challenged fraction
  inside scope
  <=5%;

- no member with:
  active certificate contradiction debt
  above the H146 invalidation threshold
  remains:
  action-eligible.

On success:

- no topology is changed;
- count:
  one regional-validation unit;
- establish:
  a new regional proof epoch;
- reset:
  P_r
  and:
  Q_r
  for:
  validated scope;
- reset:
  path_count
  and:
  q_i
  for:
  members currently inside:
  validated scope;
- reset:
  accepted touch
  and:
  challenge touch
  for:
  validated scope;
- recompute:
  P,
  U,
  C_P,
  Q,
  V,
  C_Q
  from:
  remaining non-validated history.

Do NOT reset:
unrelated scope history.

On failure:

handoff to:
REGIONAL RE-DEVELOPMENT.

REGIONAL RE-DEVELOPMENT

Reuse:
H148 scoped reconstruction.

Maturation:
4 episodes.

Mean support:
>=0.85.

Candidate-assignment stability:

>=90%
launch -> +2

and:

>=90%
+2 -> +4.

Each attempt:
1 scratch unit.

Two failed regional redevelopment attempts:

force:
GLOBAL RE-DEVELOPMENT.

GLOBAL RE-DEVELOPMENT

Reuse:
H148 / H147
global reconstruction.

Maturation:
6 episodes.

Mean support:
>=0.80.

Each attempt:
3 scratch units.

Validated global promotion:

resets:
all accepted-repair
and:
challenge-exposure
history

to:
the new global validation baseline.

COHORT / RELATION PROOF OBJECT

H149 removes:
fixed individual
4+2 witnesses

from:
the primary candidate.

A certificate instead depends on:

1.
its own:
accepted membership relation;

2.
a:
REGION PROOF OBJECT;

3.
the H146:
contradiction budget;

4.
its calibration class.

REGION PROOF OBJECT

For each:
currently validated accepted region,

store:

- proof_epoch_id;
- member cohort;
- cohort size;
- observed mean accepted-assignment support;
- observed 10th-percentile accepted-assignment support;
- challenged-member fraction;
- calibration class.

The primary simulator may use:
the exact accepted member cohort

to isolate:
proof semantics.

This is:
not a claim
that production must store:
a full bitmap.

Future work may compress:
the cohort proof
using:
sketches / hashes.

REGION PROOF VALIDITY

A region proof is:
locally valid

when:

- mean accepted-assignment support >=0.90;
- 10th-percentile accepted-assignment support >=0.75;
- challenged fraction <=5%;
- calibration class unchanged.

CERTIFICATE TRANSFER

A valid certificate may transfer
through:
patch,
regional validation,
regional redevelopment,
global redevelopment,
or:
numeric relabel

only when:

- the member itself
  is not structurally challenged;
- member accepted-assignment support >=0.80;
- H146 contradiction budget
  is not exceeded;
- calibration class is unchanged;
- its prior region proof
  can be matched to:
  a current region proof
  by:
  structural cohort overlap.

COHORT MATCHING

Match:
old accepted regions
to:
new accepted regions

by:
maximum Jaccard overlap
of:
accepted member cohorts.

A certificate may transfer
without deliberate revalidation

when:

- matched region Jaccard >=0.90;
- certificate member belongs to:
  the matched current cohort;
- current region proof is valid;
- the member's own accepted support >=0.80.

Numeric region IDs:
do not matter.

Therefore:

PURE RELABEL

with:
identical membership cohorts

has:
Jaccard = 1.0

and:
should transfer
without:
revalidation.

A true structural region change:

reduces:
cohort overlap

and/or:
region proof validity.

CERTIFICATE AFTER REGIONAL RE-VALIDATION

A successful:
regional re-validation

creates:
a new regional proof epoch.

Stable certificates
inside:
the scope

may:
transfer to:
the new proof epoch

without:
six-observation member revalidation

when:
the cohort-transfer rules above pass.

This is:
the key cost-saving hypothesis.

CERTIFICATE AFTER PATCH

Patched members:

invalidate.

Unmoved members:

do NOT:
invalidate

merely because:
a named witness changed.

Their certificates transfer only if:

current region proof
and:
own member support
remain:
valid.

H146 CONTRADICTION SEMANTICS

Retain:
corrected H146 behavior.

Every:
active valid certificate

receives:
one opportunistic feedback observation / episode.

Primary error:
5%.

Match:
debt -1
to:
minimum 0.

Conflict:
debt +1.

Keep:
recent six
active-feedback outcomes.

Invalidate before:
broad action

when:

debt >=3

AND

recent-6 contradictions >=3.

Successful deliberate revalidation:

resets:
debt
and:
recent contradiction history.

PRIMARY POLICIES

A — H148-SCOPED-WITNESS

Frozen H148 primary candidate.

Accepted-change vector envelope.

Regional redevelopment.

Fixed 4+2 individual witnesses.

No challenge-exposure ledger.

No regional re-validation.

This is:
the direct parent comparator.

B — DUAL-HISTORY-WITNESS

Add:
Q,
V,
C_Q,
Q_r

to:
H148.

Keep:
fixed 4+2 witnesses.

No:
regional re-validation.

This isolates:
challenge-exposure history.

C — DUAL-HISTORY-COHORT

Dual-history envelope.

Use:
cohort / relation proof objects.

On local envelope closure:

regional redevelopment.

No:
regional re-validation.

This isolates:
proof-object contribution.

D — DUAL-HISTORY-REVALIDATE-COARSE

Dual-history envelope.

Add:
regional re-validation.

Use:
coarse H147-style
region-bound certificate inheritance.

This isolates:
regional re-validation.

E — DUAL-HISTORY-REVALIDATE-COHORT

PRIMARY CANDIDATE.

PATCH
->
REGIONAL RE-VALIDATION
->
REGIONAL RE-DEVELOPMENT
->
GLOBAL RE-DEVELOPMENT.

Uses:
dual structural-history channels

and:
cohort / relation proof objects.

F — IMMEDIATE GLOBAL

Persistent structural disturbance
causes:
global redevelopment.

No patch.

Full certificate invalidation.

Reference for:
maximum caution / high cost.

G — ORACLE SCOPE

Synthetic reference only.

Uses:
true disturbance history

only to choose:
patch,
regional validation,
regional redevelopment,
or:
global redevelopment.

All topology / certificate validation:
still uses:
observed evidence.

Not deployable.

PRIMARY REGIMES

R0 — LOCAL-5

Single:
5% local disturbance.

Episode:
11.

R1 — LOCAL-10

Single:
10% local disturbance.

Episode:
11.

R2 — DIFFUSE-10

10%:
approximately even
across regions.

Episode:
11.

R3 — ACCUMULATED-MICROPATCH

Five:
5% local disturbances

inside:
the same original structural region

at:

11,
19,
27,
35,
43.

R4 — MOVING-WOUND

10% instantaneous local wound

relocates:
to a new region

at:

11,
19,
27,
35,
43,
51.

Before:
each new wound,

the previous wound
is restored.

Instantaneous changed mass:
approximately 10%.

Cumulative challenge footprint:
moves across:
the family.

R5 — BOUNDARY-PING-PONG

Matched:
5% cohort

alternates:
between:
one source-target pair

at:

11,
19,
27,
35,
43,
51.

Net displacement
may:
fall

while:
challenge / path history
continues.

R6 — TRANSIENT-LOCAL-NOISE

No true structural change.

Episodes:
11..15.

One accepted region:
45% observation error.

Episode 16 onward:
5%.

Tests:
whether
two-checkpoint / pair-consistent
challenge confirmation
rejects:
transient sensor disturbance.

R7 — PURE RELABEL

No structural relation change.

Episode:
21.

Consistently permute:

- true region IDs;
- accepted region IDs;
- accumulated evidence columns;
- region-indexed ledgers.

Tests:
cohort proof
relabel invariance.

R8 — STACKED

Episode 11:
LOCAL-10.

Episode 19:
LOCAL-5
same source.

Episode 27:
LOCAL-5
same source.

Episode 35:
DIFFUSE-10.

Then:
stable.

R9 — ROAMING-SUBPATCH

A:
5% local wound

is:
restored
and:
relocated

every:
6 episodes

at:

11,
17,
23,
29,
35,
41,
47,
53.

The wound moves:
before:
ordinary two-checkpoint patch persistence
can reliably convert:
all challenge
into:
accepted topology movement.

This directly tests:

CHALLENGE HISTORY
WITHOUT
ACCEPTED-REPAIR HISTORY.

PRIMARY HORIZON

60 episodes.

PRIMARY WORLD MODEL

Inherit:
H148.

Family:
80..120.

Regions:
4..6.

Initial accepted topology:
98% correct.

Initial vested certificates:
55%
of correctly assigned members,
value-biased.

Normal structural observations:
2 / member / episode.

Memory retention:
0.92 / episode.

Structural checkpoint:
every 3 episodes.

Structural challenge:

effective mass >=4

AND

candidate != accepted

AND

candidate support >=0.70

AND

candidate margin >=0.20.

Incremental patch candidate:

same source -> target
coherent challenge

present at:
2 consecutive checkpoints.

Patch cap:
ceil(0.08N).

PRIMARY SENSOR ERROR

5%.

COMMON-WORLD DISCIPLINE

Within each world:

all policies receive:

- identical initial topology;
- identical member values;
- identical activity;
- identical disturbances;
- identical normal structural observation potentials;
- identical opportunistic certificate-feedback potentials;
- identical deliberate member-revalidation potentials;
- identical regional-validation observation potentials.

PRIMARY METRICS

1.
final ARI.

2.
safe active-value coverage.

3.
false-promotion proxy.

4.
accepted path P.

5.
accepted distinct U.

6.
accepted diffusion C_P.

7.
max accepted region P_r.

8.
challenge exposure Q.

9.
distinct exposure V.

10.
challenge diffusion C_Q.

11.
max region exposure Q_r.

12.
patch count.

13.
regional-validation count.

14.
regional-validation pass rate.

15.
regional redevelopment count.

16.
global redevelopment count.

17.
scratch units.

18.
regional-validation observation cost.

19.
member revalidation observation cost.

20.
action downtime.

21.
certificate retention.

22.
false inherited-certificate rate.

23.
recovery latency.

24.
topology churn.

25.
false handoff rate.

26.
pure-relabel unnecessary invalidation.

27.
challenge-history handoff latency.

PRIMARY ACCEPTANCE SHAPE

H149 is supported if:

1.
E preserves:
LOCAL-5
and:
LOCAL-10

final ARI >=0.99.

2.
E uses:
global redevelopment
in:
<=5%
of LOCAL-5 worlds

and:
<=10%
of LOCAL-10 worlds.

3.
In LOCAL-10:

regional re-validation
is used:
more often
than:
regional redevelopment.

4.
In LOCAL-5 / LOCAL-10:

E uses:
fewer scratch units
than:
H148-SCOPED-WITNESS.

5.
In LOCAL-5 / LOCAL-10:

E uses:
fewer total deliberate observations

where:

total deliberate =
regional-validation observations
+
member revalidation observations

than:
IMMEDIATE GLOBAL.

6.
In ACCUMULATED-MICROPATCH:

E final ARI >=0.97

and:

regional validation / redevelopment
occurs
before:
accepted P reaches 0.25.

7.
In MOVING-WOUND:

E structural handoff rate:
>=90%.

8.
In ROAMING-SUBPATCH:

E structural handoff rate:
>=90%

despite:
low accepted-repair path.

9.
In TRANSIENT-LOCAL-NOISE:

false structural handoff:
<=5%.

10.
In PURE RELABEL:

>=95%
of previously valid certificates
transfer
without:
member revalidation,

with:

false inherited-certificate rate:
<1%

and:

structural handoff:
<=1%.

11.
For:
every true structural-damage regime,

E false inherited-certificate rate:
<1%.

12.
In STACKED:

E final ARI
is:
within 0.01

of:
the better of:
B
or:
C,

while:
using fewer scratch units
than:
IMMEDIATE GLOBAL.

13.
Challenge-exposure ledgers:

must:
increase materially
in:
MOVING-WOUND
and:
ROAMING-SUBPATCH

even when:
accepted P
remains low.

14.
Value / current safety terms
may:
freeze action

but:
may NOT
buy:
additional P
or:
Q
structural authority.

FAILURE CONDITIONS

Treat H149 as:
mixed / negative

if:

- challenge exposure
  triggers redevelopment
  on:
  transient noise;

- challenge exposure
  still misses:
  moving / roaming wounds;

- regional re-validation
  usually fails
  and:
  only delays inevitable redevelopment;

- regional re-validation
  costs as much as:
  regional scratch reconstruction;

- cohort proofs
  recreate:
  region-ID brittleness;

- cohort proofs
  transfer stale certificates
  above:
  1% primary;

- cohort proof refresh
  invalidates:
  most otherwise-stable members;

- stacked damage
  remains worse
  than:
  global-only dual-history repair;

- the controller needs:
  latent labels
  outside:
  the ORACLE comparator.

PRIMARY CONFIRMATION SIZE

400 held-out worlds / regime.

10 regimes.

7 policies.

28,000 policy-regime-worlds.

PRIMARY RANDOMNESS

Accepted primary seed blocks:

R0:
20260919300000..20260919300399.

Each next regime:
+1000.

These seeds are:
held out.

Do NOT use:
them for:
harness sanity,
threshold selection,
or:
debugging.

HARNESS / SANITY SEEDS

Use:
a disjoint non-evidence family
beginning at:

20260919250000.

Sanity outputs are:
NON-EVIDENCE.

No threshold may be tuned
from:
accepted primary worlds.

ROBUSTNESS — AFTER PRIMARY

Challenge Q bound:

0.20,
0.30,
0.40.

Distinct exposure V:

0.15,
0.20,
0.30.

Challenge diffusion C_Q:

0.30,
0.45,
0.60.

Regional exposure Q_r:

0.40,
0.60,
0.80.

Regional validation support:

0.85,
0.90,
0.95.

Cohort Jaccard transfer:

0.85,
0.90,
0.95.

Sensor error:

1%,
5%,
10%,
20%.

Family size:

40..60,
80..120,
160..240.

OUT-OF-BOX EXTENSION

H149 treats:
structural experience

as:
an EVENT-SOURCED HISTORY.

Accepted topology changes
are:
one event stream.

Persistent contradictions
that did not yet cause:
accepted changes

are:
another event stream.

Neither:
may erase the other.

This is analogous to:

a transactional system
that records:

COMMITTED WRITES

and:

CONFLICT / RETRY PRESSURE.

A database that records:
only successful commits

cannot tell:
whether:
one key
has been:
under continuous contention.

Similarly:

an organism
that records:
only accepted repair

cannot tell:
whether:
a wound
keeps moving
faster than:
repair can settle.

Regional re-validation
adds:
a checkpoint / compaction operation.

It can:
establish a new local baseline

without:
rebuilding
already-correct structure.

Cohort proof objects
turn:
maturity persistence

from:
a brittle list
of named dependencies

into:
a structural provenance object
that can:
survive renaming,
refresh locally,
and:
be revoked by:
real contradiction.

FROZEN BEFORE EXECUTION

Dual-channel ledgers,
challenge confirmation,
bounds,
regional re-validation,
cohort proof semantics,
handoff rules,
policies,
regimes,
metrics,
acceptance shape,
failure conditions,
primary size,
primary seeds,
sanity seeds,
and:
robustness dimensions above

are fixed before:
H149 accepted primary execution.

canonical_scientific_execution = false
canonical_r1_execution_spent = false


PRE-PRIMARY AMENDMENT 01 — FAST RESIDUAL EXPOSURE / ACTION SUSPENSION / PRIMARY-SEED ROLLOVER

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H149 PRIMARY EXECUTION.

WHY THIS AMENDMENT EXISTS

Post-H148 harness diagnosis,
performed before:
any H149 primary execution,
showed that:

the long-memory structural challenge channel

can:
attenuate a moving wound

before:
accepted repair
or:
two-checkpoint slow challenge persistence
captures it.

In the diagnostic realization:

MOVING-WOUND true structural path
was approximately:
1.15 family-equivalents,

while:
accepted-change P
captured only:
approximately 1.1%
of that path.

The existing slow structural-challenge exposure
also remained:
near background.

A separate:
short-timescale observable residual
did recover:
the missing signal.

Therefore:

H149 keeps:
DUAL STRUCTURAL HISTORY

but:
changes how
CHALLENGE EXPOSURE
is observed.

No latent labels
are introduced.

FAST RESIDUAL WINDOW

For each member:

retain:
the most recent
6 normal region-identity observations

corresponding to:
3 episodes
at:
2 observations / episode.

For each observation:

record:
MATCH

when:
observed region
equals:
the member's accepted region
at observation time;

otherwise:
MISMATCH.

FAST-SUSPECT STATE

A member becomes:

FAST-SUSPECT

when:

>=4
of:
the most recent 6 observations

are:
MISMATCH.

FAST-SUSPECT is:

an action-safety state,

not:
a topology decision
and:
not:
automatic permanent certificate invalidation.

ACTION SUSPENSION

Before:
broad action accounting,

a valid certificate held by:
a FAST-SUSPECT member

is:

SUSPENDED_FAST.

SUSPENDED_FAST:

- remains cached;
- is NOT action-eligible;
- may not contribute broad active value;
- does not require immediate deliberate member revalidation;
- clears when:
  the fast residual condition clears,
  provided:
  H146 contradiction invalidation
  has not separately fired
  and:
  structural proof state remains valid.

Thus:

CACHE RETENTION
DOES NOT EQUAL
ACTION AUTHORITY.

This state exists to:
prevent stale action
during:
fast structural nonstationarity

without:
forcing epistemic amnesia.

DURABLE CHALLENGE-EXPOSURE CONFIRMATION

The existing H149 two-checkpoint consistency rule
is retained,

but:
its input is now
FAST-SUSPECT evidence

rather than:
the slow 0.92 structural-candidate challenge alone.

At each:
3-episode structural checkpoint,

derive for every FAST-SUSPECT member:

- accepted source region;
- dominant non-accepted observed target region
  from:
  the same six-observation fast window.

Member i contributes:
one durable challenge-exposure incidence

only when:

- i is FAST-SUSPECT
  at:
  the current checkpoint;

- i was FAST-SUSPECT
  at:
  the immediately previous checkpoint;

- accepted source region
  is unchanged;

- dominant non-accepted target region
  is identical
  at:
  both checkpoints.

Then:

q_i += 1.

Q,
V,
Q_r,
challenge_touch,
H_Q,
and:
C_Q

retain:
their already-preregistered definitions
and:
numerical bounds.

NO H149
Q,
V,
C_Q,
or:
Q_r
threshold
is changed
by this amendment.

FAST RESIDUALS
THAT DO NOT
PASS
TWO-CHECKPOINT
SOURCE-TARGET CONSISTENCY

may:
temporarily suspend action,

but:

do NOT
consume:
durable challenge-history authority.

This is intended to:
reject:
transient sensor disturbance

while:
retaining sensitivity
to:
moving / roaming wounds.

RESET SEMANTICS

Accepted patch:

- reset the six-observation fast window
  for:
  members whose accepted region changes.

Validated regional re-validation
or:
regional redevelopment:

- reset:
  FAST-SUSPECT state
  and:
  fast-window history
  for:
  the validated scope;

- reset:
  durable Q state
  only according to:
  the already-preregistered regional validation rules.

Validated global redevelopment:

- reset:
  fast-window state
  and:
  all durable challenge-exposure history
  to:
  the new global validation origin.

CERTIFICATE METRICS

Retain:
the preregistered
false inherited-certificate rate.

Add:

FALSE ACTIONABLE INHERITED-CERTIFICATE RATE

A transferred / retained certificate counts
as:
false actionable

when:

- it is action-eligible;
- its current true functional region
  differs from:
  its accepted / certified region.

SUSPENDED_FAST certificates:

are:
not actionable

and therefore:
do NOT count as:
false actionable authority.

Also report:

STALE CACHED CERTIFICATE RATE

for:
cached certificates
whose current true structural relation
is stale
while:
action is suspended.

This prevents:
a safety improvement
from being hidden

and also prevents:
cached stale state
from being mislabeled
as:
authorized action.

EXPLORATORY RESULT THAT MOTIVATED THIS AMENDMENT

NON-EVIDENCE only.

A separate exploratory fast-residual ablation
used:

4-of-6 fast suspension

plus:
a provisional,
non-H149,
fast-diffusion global trigger.

On:
100 worlds / regime,

it reduced:
false active-value promotion

in:
MOVING-WOUND

from approximately:
3.81%

to:
0.82%,

while:
LOCAL-5
and:
LOCAL-10

kept:
final ARI 1.0

and:
unchanged global-redevelopment counts.

It also reduced:
STACKED false promotion

from approximately:
1.25%

to:
0.28%.

The exploratory global-trigger thresholds
used in that ablation

are:
NOT
adopted by H149.

H149 retains:
its preregistered
Q,
V,
C_Q,
and:
Q_r
handoff thresholds.

PRIMARY-SEED CONTAMINATION

The previously reserved H149 primary seed family:

R0:
20260919300000..20260919300399,

with:
+1000 per subsequent regime,

was unintentionally consumed by:
the separate exploratory fast-residual ablation
before:
H149 primary execution.

Therefore:

that entire seed family is:

CONTAMINATED
/
NON-EVIDENCE
FOR H149 PRIMARY.

It must NOT:
be reused
for:
accepted H149 confirmation.

REPLACEMENT H149 PRIMARY SEEDS

New held-out primary family:

R0:
20260919400000..20260919400399.

Each subsequent regime:
+1000 seed base.

These replacement seeds:

have not been used
for:
sanity,
debugging,
threshold selection,
or:
exploratory analysis.

HARNESS / SANITY SEEDS

Remain:

20260919250000 family.

They remain:
NON-EVIDENCE.

PRIMARY EXECUTION STATUS

H149 accepted primary execution:

HAS NOT STARTED.

This amendment is:
pre-primary.

No H149 accepted primary world
has been spent.

STAB-18-R1 remains:
UNTOUCHED.

AMENDMENT PROVENANCE

reason_1 =
slow structural memory can attenuate moving wounds before durable challenge capture.

reason_2 =
fast residuals recover an observable short-timescale injury signal.

reason_3 =
previously reserved H149 seed family was consumed by exploratory work and is no longer held out.

threshold_tuning_from_replacement_primary = false.
canonical_scientific_execution = false.
canonical_r1_execution_spent = false.


PRE-PRIMARY CORRECTION 02 — FINAL HARNESS LINEAGE FREEZE / PRIMARY-SEED ROLLOVER

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE ACCEPTED H149 PRIMARY EXECUTION.

BACKGROUND

After Amendment 01,
an H149 implementation audit found three remaining lineage mismatches
before:
any H149 result was accepted.

1.
ACCEPTED-CHANGE DIFFUSION C_P

The inherited H148 accepted-change diffusion ledger
must be:

the unattenuated normalized entropy
of:
accepted source-region touch mass.

A provisional harness still multiplied:
H_P
by:
min(1, P / 0.15).

That attenuation belonged to:
an obsolete H148 implementation path.

It is removed.

H149 now uses:

C_P = H_P

when:
accepted touch mass is nonzero.

The frozen H149 numerical bounds:

0.30 regional / ambiguous boundary
and:
0.45 global boundary

are unchanged.

2.
PURE-RELABEL COHORT TRANSFER

A provisional harness directly rewrote:
certificate numeric region IDs
for:
cohort-proof policies
during:
PURE RELABEL.

The frozen H149 rule requires:
ordinary cohort-proof transfer.

Therefore:
PURE RELABEL transfer now passes through:

- Jaccard cohort matching;
- current region-proof validity;
- own-member support;
- H146 contradiction validity.

Numeric IDs remain:
irrelevant.

No cohort threshold is changed.

3.
REGIONAL RE-VALIDATION COHORT TRANSFER

After:
successful regional re-validation,

cohort certificates now transfer
only when:

- member remains unchallenged;
- fresh member support passes;
- ordinary own-member support passes;
- the current region proof itself is valid.

This enforces:
the already-preregistered
cohort-proof contract.

No numerical threshold is changed.

AMENDMENT 01 FAST-RESIDUAL REALIZATION

The final frozen harness also implements:
the already-preregistered Amendment 01 semantics exactly.

FAST-SUSPECT:

>=4 mismatches
inside:
the most recent six normal structural observations.

Durable challenge exposure:

requires:
FAST-SUSPECT
at:
two consecutive structural checkpoints

with:
the same accepted source region
and:
the same dominant non-accepted target region.

FAST-SUSPECT:

suspends broad action

but:
does not itself
invalidate the cached certificate.

Accepted patch:

resets fast-window state
for:
moved members.

Validated regional scope:

resets fast-window state
for:
that scope.

Validated global redevelopment:

resets:
all fast-window state
and:
all durable challenge-exposure history.

PRIMARY FAMILY 20260919400000 DISPOSITION

The seed family beginning:

20260919400000

was touched by:
a provisional primary harness
before:
the implementation audit above
was fully closed.

Those outputs were not:
used to tune
Q,
V,
C_Q,
Q_r,
P,
U,
C_P,
P_r,
regional-validation,
cohort-Jaccard,
or:
any other numerical threshold.

Nevertheless,
for conservative evidence hygiene:

THE ENTIRE
20260919400000 PRIMARY FAMILY
IS:

CONTAMINATED /
NON-EVIDENCE.

No numerical result
from that family
may be used
for:
H149 acceptance.

FINAL HELD-OUT H149 PRIMARY SEEDS

R0:

20260919500000..20260919500399.

Each subsequent regime:

+1000 seed base.

This family was selected:
before inspecting
or accepting
H149 primary outcome metrics.

HARNESS / SANITY SEEDS

Remain:

20260919250000 family.

They are:
NON-EVIDENCE.

FINAL FROZEN HARNESS SHA-256

36408075f911e0a0ea4b44184f95f298198fd56a1228e39dd61368fd74a32b22

No execution-semantic change is permitted
after:
the first accepted 20260919500000-family world is executed.

H149 accepted primary execution status:

NOT STARTED
at the moment of this freeze.

STAB-18-R1 remains:
UNTOUCHED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.


ACCEPTED PRIMARY CHECKPOINT — PRIMARY CANDIDATE COMPLETE / COMPARATOR MATRIX IN PROGRESS

DATE:
2026-09-19.

STATUS:
PRIMARY IN PROGRESS.
DO NOT INTERPRET AS FINAL H149 CLOSURE.

FROZEN HARNESS

sha256:
36408075f911e0a0ea4b44184f95f298198fd56a1228e39dd61368fd74a32b22.

Accepted primary family:

R0:
20260919500000..20260919500399.

Each subsequent regime:
+1000.

PRIMARY CANDIDATE E

E —
DUAL-HISTORY-REVALIDATE-COHORT

has completed:

400 worlds / regime
across:
all 10 primary regimes.

Candidate-only accepted primary metrics:

R0 LOCAL-5

final ARI:
0.9910.

global redevelopment:
0.1200 / world.

regional re-validation:
1.0075 / world.

regional redevelopment:
0.3050 / world.

false inherited-certificate rate:
0.0056%.

structural handoff worlds:
92.25%.

R1 LOCAL-10

final ARI:
1.0000.

global redevelopment:
0.2150 / world.

regional re-validation:
1.1000 / world.

regional redevelopment:
0.8450 / world.

false inherited-certificate rate:
0%.

structural handoff worlds:
100%.

R2 DIFFUSE-10

final ARI:
1.0000.

global redevelopment:
1.0000 / world.

false inherited-certificate rate:
0.106%.

R3 ACCUMULATED-MICROPATCH

final ARI:
0.9121.

global redevelopment:
0.5650 / world.

regional re-validation:
2.5025 / world.

regional redevelopment:
2.1850 / world.

max accepted P:
0.0446.

false inherited-certificate rate:
0.0052%.

R4 MOVING-WOUND

final ARI:
0.8062.

global redevelopment:
1.3175 / world.

regional re-validation:
2.7575 / world.

regional redevelopment:
1.9600 / world.

structural handoff worlds:
100%.

max accepted P:
0.0108.

max challenge exposure Q:
0.4984.

false inherited-certificate rate:
0.0836%.

false actionable inherited-certificate rate:
1.379%.

R5 BOUNDARY-PING-PONG

final ARI:
0.9861.

global redevelopment:
0.0900 / world.

regional re-validation:
2.1475 / world.

regional redevelopment:
1.1325 / world.

false inherited-certificate rate:
0.0031%.

R6 TRANSIENT-LOCAL-NOISE

final ARI:
1.0000.

structural handoff worlds:
9.50%.

false inherited-certificate rate:
0%.

R7 PURE RELABEL

final ARI:
1.0000.

structural handoff worlds:
11.75%.

pure-relabel unnecessary invalidation:
0.174%.

false inherited-certificate rate:
0%.

R8 STACKED

final ARI:
0.9964.

global redevelopment:
1.4875 / world.

regional re-validation:
1.7375 / world.

regional redevelopment:
1.4375 / world.

scratch units:
5.9000 / world.

false inherited-certificate rate:
0.296%.

R9 ROAMING-SUBPATCH

final ARI:
0.8776.

structural handoff worlds:
100%.

max accepted P:
0.0127.

max challenge exposure Q:
0.2163.

false inherited-certificate rate:
0.178%.

false actionable inherited-certificate rate:
0.988%.

INTERIM GATE SIGNALS

These are:
candidate-batch observations only.

They are not:
a final H149 disposition.

POSITIVE SIGNALS

1.
MOVING-WOUND handoff:

100%.

2.
ROAMING-SUBPATCH handoff:

100%.

3.
Challenge history becomes:
material

while:
accepted repair path remains low.

MOVING-WOUND:

Q approximately:
0.498.

P approximately:
0.011.

ROAMING-SUBPATCH:

Q approximately:
0.216.

P approximately:
0.013.

4.
Cohort-proof false inherited-certificate rate
is below:
1%

in:
every candidate structural-damage regime
measured so far.

5.
PURE RELABEL:
direct unnecessary certificate invalidation
remains:
well below 5%.

NEGATIVE SIGNALS

1.
ACCUMULATED-MICROPATCH final ARI:

0.9121,

below:
the preregistered
0.97 gate.

2.
TRANSIENT-LOCAL-NOISE structural handoff:

9.5%,

above:
the preregistered
5% false-handoff gate.

3.
PURE RELABEL structural handoff:

11.75%,

above:
the preregistered
1% handoff gate.

4.
LOCAL global-redevelopment frequency:

LOCAL-5:
12%.

LOCAL-10:
21.5%.

Both exceed:
their preregistered
5% / 10% ceilings.

5.
MOVING-WOUND structural detection improves,
but:
final topology quality remains low

at:
0.8062.

COMPLETED ACCEPTED COMPARATORS

A —
H148-SCOPED-WITNESS

complete on:

LOCAL-5,
LOCAL-10.

F —
IMMEDIATE GLOBAL

complete on:

LOCAL-5,
LOCAL-10,
STACKED.

B —
DUAL-HISTORY-WITNESS

complete on:
STACKED.

C —
DUAL-HISTORY-COHORT

complete on:
STACKED.

SELECTED COMPARATOR GATE READOUT

LOCAL-5 scratch units:

E:
0.665.

A:
0.795.

LOCAL-10 scratch units:

E:
1.490.

A:
1.185.

Thus:
E improves scratch cost on LOCAL-5
but:
not LOCAL-10.

LOCAL-5 deliberate observations:

E:
468.915.

F:
449.985.

LOCAL-10 deliberate observations:

E:
590.355.

F:
450.165.

Thus:
the preregistered local deliberate-observation cost advantage
does not currently hold.

STACKED final ARI:

E:
0.9964.

B:
0.9993.

C:
0.9993.

Difference from better B/C:

approximately:
0.0029.

STACKED scratch units:

E:
5.900.

F:
6.000.

Thus:
the STACKED quality / scratch gate
currently appears:
supported.

FULL PRIMARY STATUS

The full:

28,000 policy-regime-world

comparator matrix
is:

NOT YET COMPLETE.

Do not:
close H149
until:
the remaining accepted comparator cells
are completed
or:
an explicit protocol-compliant stopping rule
is documented.

No stopping rule has been invoked.

H150 remains:
UNASSIGNED
and:
UNSPENT.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.



FINAL ACCEPTED PRIMARY CLOSURE — FULL COMPARATOR MATRIX

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE.

FROZEN HARNESS SHA-256

36408075f911e0a0ea4b44184f95f298198fd56a1228e39dd61368fd74a32b22.

ACCEPTED PRIMARY FAMILY

R0:
20260919500000..20260919500399.

Each subsequent regime:
+1000 seed base.

MATRIX

400 worlds / regime.

10 regimes.

7 policies.

28,000 policy-regime-worlds.

Validation before analysis:

- every policy-regime cell contains exactly 400 unique seeds;
- no accepted-seed gaps;
- no accepted-seed duplicates;
- all accepted seeds belong to the final 20260919500000 family;
- contaminated 20260919300000 and 20260919400000 families remain NON-EVIDENCE.

PRIMARY CANDIDATE E — FINAL READOUT

R0 LOCAL-5

final ARI:
0.9910.

global redevelopment:
12.0% of worlds.

regional re-validation:
1.0075 / world.

regional redevelopment:
0.3050 / world.

scratch:
0.665 / world.

deliberate observations:
468.915 / world.

false inherited-certificate rate:
0.0056%.

R1 LOCAL-10

final ARI:
1.0000.

global redevelopment:
21.5% of worlds.

regional re-validation:
1.1000 / world.

regional redevelopment:
0.8450 / world.

scratch:
1.490 / world.

deliberate observations:
590.355 / world.

false inherited-certificate rate:
0%.

R2 DIFFUSE-10

final ARI:
1.0000.

global redevelopment:
100%.

false inherited-certificate rate:
0.1062%.

R3 ACCUMULATED-MICROPATCH

final ARI:
0.9121.

structural handoff:
95.75%.

max accepted path P:
0.0446.

regional re-validation:
2.5025 / world.

regional redevelopment:
2.1850 / world.

global redevelopment:
0.5650 / world.

R4 MOVING-WOUND

final ARI:
0.8062.

structural handoff:
100%.

max accepted path P:
0.0108.

max challenge exposure Q:
0.4984.

max distinct challenge exposure V:
0.2840.

max challenge diffusion C_Q:
0.5968.

false inherited-certificate rate:
0.0836%.

false actionable inherited-certificate rate:
1.3789%.

R5 BOUNDARY-PING-PONG

final ARI:
0.9861.

structural handoff:
93.25%.

global redevelopment:
9.0%.

R6 TRANSIENT-LOCAL-NOISE

final ARI:
1.0000.

false structural handoff:
9.5%.

R7 PURE RELABEL

final ARI:
1.0000.

structural handoff:
11.75%.

pure-relabel unnecessary invalidation:
0.1736%.

false inherited-certificate rate:
0%.

R8 STACKED

final ARI:
0.9964.

B / C comparator final ARI:
0.9993.

difference from better B/C:
approximately 0.0029.

E scratch:
5.900 / world.

IMMEDIATE GLOBAL scratch:
6.000 / world.

false inherited-certificate rate:
0.2964%.

R9 ROAMING-SUBPATCH

final ARI:
0.8776.

structural handoff:
100%.

max accepted path P:
0.0127.

max challenge exposure Q:
0.2163.

max distinct challenge exposure V:
0.2010.

max challenge diffusion C_Q:
0.5941.

false inherited-certificate rate:
0.1776%.

false actionable inherited-certificate rate:
0.9876%.

PREREGISTERED GATE REVIEW

SUPPORTED

1.
LOCAL structural quality.

LOCAL-5:
ARI 0.9910.

LOCAL-10:
ARI 1.0000.

Both exceed:
0.99.

2.
LOCAL-10 regional re-validation
is used more often than:
regional redevelopment.

1.1000
versus:
0.8450 / world.

3.
MOVING-WOUND structural handoff:
100%.

Required:
>=90%.

4.
ROAMING-SUBPATCH structural handoff:
100%.

Required:
>=90%.

5.
Challenge-exposure history becomes material
while:
accepted repair path remains low.

MOVING-WOUND:
Q approximately 0.498
while P approximately 0.011.

ROAMING-SUBPATCH:
Q approximately 0.216
while P approximately 0.013.

This confirms:
accepted repair history alone
is insufficient
for fast moving structural injury.

6.
False inherited-certificate rate
remains:
<1%
in every primary structural-damage regime.

7.
STACKED quality remains:
within 0.01
of the better B/C comparator

and:
uses fewer scratch units
than IMMEDIATE GLOBAL.

MIXED / FAILED

1.
LOCAL GLOBAL-REDEVELOPMENT CEILING.

LOCAL-5:
12.0%.

Required:
<=5%.

LOCAL-10:
21.5%.

Required:
<=10%.

FAIL.

2.
LOCAL SCRATCH ADVANTAGE OVER H148.

LOCAL-5:
E 0.665
versus A 0.795.

PASS.

LOCAL-10:
E 1.490
versus A 1.185.

FAIL.

3.
LOCAL DELIBERATE-EVIDENCE ADVANTAGE
OVER IMMEDIATE GLOBAL.

LOCAL-5:
E 468.915
versus F 449.985.

LOCAL-10:
E 590.355
versus F 450.165.

FAIL.

Regional re-validation
is not yet:
an evidence-cost saving operation
under this realization.

4.
ACCUMULATED-MICROPATCH QUALITY.

E final ARI:
0.9121.

Required:
>=0.97.

FAIL.

Handoff occurs before:
P reaches 0.25,

but:
the handoff / re-validation sequence
does not preserve enough final topology quality.

5.
TRANSIENT-LOCAL-NOISE FALSE HANDOFF.

Observed:
9.5%.

Required:
<=5%.

FAIL.

6.
PURE-RELABEL STRUCTURAL HANDOFF.

Observed:
11.75%.

Required:
<=1%.

FAIL.

The cohort proof itself:
remains relabel-safe
with:
zero false inherited-certificate rate

and:
very low direct unnecessary invalidation,

but:
the structural controller
still launches unnecessary handoff.

7.
MOVING-WOUND ACTION SAFETY.

Although:
cached false inheritance
remains below 1%,

false actionable inherited-certificate rate
is:
approximately 1.379%.

This new amendment metric
exposes:
residual stale action authority
during fast wound motion.

FINAL INTERPRETATION

H149 is:

MIXED-NEGATIVE.

The experiment establishes a useful architectural result:

DUAL STRUCTURAL HISTORY
IS REAL.

Accepted-change history P
and:
challenge-exposure history Q

measure:
different failure modes.

Q materially detects:
moving / roaming structural injury

that:
P almost completely misses.

However:

THE CURRENT HANDOFF CONTROLLER
IS TOO EAGER

and:

REGIONAL RE-VALIDATION
IS TOO EXPENSIVE /
TOO DISRUPTIVE

to serve as:
the default intermediate repair mode.

The failure is not:
that challenge history lacks signal.

The failure is:
signal-to-action conversion.

A future repair-controller experiment
should separate:

1.
FAST ACTION SUSPENSION,

from:

2.
DURABLE STRUCTURAL HISTORY,

from:

3.
AUTHORITY TO RE-DEVELOP.

These should not:
share one effective threshold path.

A fast residual
may justify:
temporary action suspension

without:
consuming redevelopment authority.

Likewise:

regional baseline refresh
should only be attempted
when:
current topology is already strongly coherent
and:
the evidence cost is demonstrably below
scratch reconstruction.

COHORT PROOF RESULT

Cohort / relation proof objects remain:
promising.

They avoid:
the worst fixed-witness brittleness,

remain:
numeric-relabel invariant,

and:
keep cached false inheritance
below:
1%
through all primary structural-damage regimes.

But:

certificate provenance alone
cannot compensate for:
incorrect structural handoff timing.

H149 DOES NOT AUTHORIZE

- production thresholds;
- biological claims;
- STAB-18-R1 execution;
- runtime activation;
- canonical scientific claims.

STAB-18-R1:
UNTOUCHED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
