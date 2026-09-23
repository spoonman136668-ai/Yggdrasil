TITLE: LU-0E — V0.2 BOUNDED-LOCAL STAGED IDENTIFIABILITY AUDIT
DATE: 2026-09-23
STATUS: PREREGISTERED / NO PRIMARY AUDIT EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Determine whether the current hand-designed
Developmental Substrate V0.2
can be represented exactly by a practical
bounded-local staged student observation
before training the first learned per-cell updater.

This audit occurs after the replicated removal
of the organism-wide recruitment-pool contribution.

PARENT

Developmental Substrate V0.2:

e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2.

V0.2 parent evidence:

LU-0C closure:
2356cdb49171a1144c3f56a28ba9d29a47f42796.

LU-0D closure:
f77fa375e484859628081f67c54c734cf7eb41d5.

QUESTION

Given only bounded local cell/neighborhood state
and bounded local task-perception channels,
is the exact V0.2 focal-cell transition distribution identifiable?

A second question is:

what local information is actually necessary?

Do not train a student in LU-0E.

This is an information-boundary audit only.

WHY STAGED

The V0.2 teacher performs several ordered
within-epoch operations:

1. local evidence / B update;

2. refractory lifecycle update;

3. H release;

4. C/S defection;

5. Q/ECHO trace update;

6. U recruitment.

Later stages observe the realized local state
produced by earlier stages in the same epoch.

Therefore LU-0E does not require
a one-shot pre-epoch student
to marginalize every possible neighboring stochastic event.

Instead it tests a staged local interface
that preserves the teacher's existing causal order.

This staging is not phase identity
and carries no task/future oracle.

It is simply the teacher's already-existing
local lifecycle order.

PROPOSED STUDENT OBSERVATION V1

For focal cell i,
the learned stochastic update heads may receive:

FOCAL LIFECYCLE

state_i;

timer_i;

B_i / B_pre_i as appropriate to the stage;

Q_prev_i;

Q_prev_side_i.

RADIUS-3 LOCAL VECTOR

For offsets d = -3..+3,
after the preceding frozen microstage has completed:

state_(i+d);

B_pre_(i+d);

LC12_(i+d);

LS12_(i+d).

FOCAL LOCAL TASK PERCEPTION

LC3_i;

LS3_i.

The center radius-3 vector already contains:

LC12_i;

LS12_i.

No organism-wide scalar is included.

No task id.

No request id.

No phase id.

No global queue length.

No global majority.

No global C/S/H count.

No future request.

No future lesion.

No future anchor location.

No global score.

FIXED LOCAL PREPROCESSING

LC12 / LS12 and LC3 / LS3
are bounded local perception fields,
not learned global summaries.

They are derived from local d_C / d_S task fields
using the inherited fixed-radius operators.

If these fields are instead reconstructed
from raw request occupancy,
the maximum request-space causal radius
for OBS-V1 is:

R_TASK
+
LOCAL_R
+
RECRUIT_R

=
2 + 12 + 3

=
17.

Thus the equivalent raw task-perception envelope
is bounded radius 17.

LEARNED / HARD BOUNDARY FOR FIRST STUDENT

LU-0E audits the stochastic decision heads:

H RELEASE;

C/S STAY-DEFECT;

U RECRUITMENT INTO C/S/H.

Sampling remains external and stateless
under the existing deterministic RNG discipline.

For the first learned imitation experiment,
the following may remain hard lifecycle/perception machinery:

fixed local perception operators;

B recurrence;

refractory timer decrement/release;

Q/ECHO trace bookkeeping;

released-this-epoch exclusion;

hard state validity;

hard resource/safety constraints.

This is consistent with the existing
Cell Model / Developmental Genome architecture,
which permits fixed perception operators
and explicit hard-coded lifecycle constraints.

A later experiment may learn more of these operations.

EXACT LOCAL DERIVABILITY CLAIM

Under V0.2:

H release depends only on:

state_i = H;

LC3_i;

LS3_i;

radius-3 H density.

C/S stay-defect depends only on:

state_i;

B_pre_i;

LC12_i;

LS12_i;

radius-3 neighbor state/B_pre;

Q_prev_i;

Q_prev_side_i.

U C/S/H recruitment depends only on:

state_i = U;

LC3_i;

LS3_i;

radius-3 neighbor state/B_pre/LC12/LS12.

No pc/ps recruitment-pool term remains.

No learned stochastic head should require
an organism-wide read.

COUNTERFACTUAL PRIMARY AUDIT

Freeze implementation as:

LU0EF1.

Only after LU0EF1 exists,
derive the deterministic audit suite.

Use a fixed probe cell
and a matrix of local templates covering:

H release;

C commitment under SUPPORT / CHALLENGE / NEUTRAL;

S commitment under SUPPORT / CHALLENGE / NEUTRAL;

U recruitment with:

C-dominant local support;

S-dominant local support;

mixed local support;

low-demand local support.

For every local template,
construct paired global worlds that are:

byte-identical under OBS-V1 for the focal cell;

but differ outside the bounded local causal envelope.

Distant perturbation families must include:

distant C/S/U/H state redistribution;

distant B-value redistribution;

distant request-load redistribution
strictly outside the radius-17 raw task envelope;

and combined distant perturbations.

The distant worlds must materially change
at least one global diagnostic
such as global C/S/H counts,
global signed B sum,
or distant request stream counts,
so the pair is not a duplicate world.

PRIMARY PAIR COUNT

At least:

64 counterfactual pairs.

The exact deterministic count
must be frozen in LU0EF1
before the primary audit runs.

IDENTIFIABILITY GATE

LU0E_V02_STAGED_LOCAL_IDENTIFIABLE = TRUE iff all are true:

1. at least 64 counterfactual pairs execute;

2. every paired focal OBS-V1 signature
   is byte-identical;

3. every pair materially differs
   in at least one distant/global diagnostic;

4. for H release pairs,
   exact teacher release probability difference
   <= 1e-12;

5. for C/S stay-defect pairs,
   exact teacher stay probability difference
   <= 1e-12;

6. for U recruitment pairs,
   total-variation distance between
   exact teacher [C,S,H,U] distributions
   <= 1e-12;

7. all audited formulas use V0.2 NO_POOL semantics;

8. no pc/ps organism-wide recruitment signal
   enters any audited decision;

9. no global count/queue/majority/phase/future channel
   enters OBS-V1;

10. duplicate complete primary audits
    are byte-identical.

If any exact transition difference survives
under byte-identical OBS-V1:

identifiability is FALSE.

Do not train yet.

MINIMALITY / NECESSITY CONTROLS

A positive identifiability result
must not be obtained by stuffing
unnecessary teacher-specific answers
into the observation.

Therefore LU-0E also runs three
predeclared reduced-input controls.

CONTROL A — REMOVE Q TRACE

Remove:

Q_prev_i;

Q_prev_side_i.

Construct at least one paired
C/S CHALLENGE case
with identical reduced observation
but different valid ECHO trace.

Required negative-control result:

stay probability difference > 1e-6.

If not observed,
the audit has failed to prove
that the Q trace is necessary.

CONTROL B — REMOVE NEIGHBOR LC12/LS12

Keep focal LC12/LS12,
but remove neighbor LC12/LS12
for offsets d != 0.

Construct at least one U recruitment pair
with identical reduced observation
but different neighbor support-mode evidence.

Required negative-control result:

teacher U transition TV > 1e-6.

If not observed,
the audit has failed to prove
that neighbor local-evidence channels
are necessary.

CONTROL C — RAW TASK RADIUS 16 VS 17

Construct a request perturbation
at the outer causal boundary
that is invisible to a raw radius-16
request observation
but changes at least one
neighbor LC12/LS12 value needed
by the focal U recruitment law.

Required result:

radius 16 insufficient = TRUE;

radius 17 sufficient for the audited
raw task-perception dependency = TRUE.

This control is about fixed perception geometry,
not about recommending a 35-cell flattened MLP input.

STAGED-ORDER CONTROL

Construct at least one U recruitment case
in which a radius-3 neighbor
changes state during an earlier teacher microstage.

Show that:

a pre-epoch-only local snapshot
and the post-microstage OBS-V1 snapshot differ.

This establishes that the staged interface
is causally meaningful
rather than documentary relabeling.

LU0E_STAGING_REQUIRED = TRUE
iff such a case is constructed
without global information or future access.

This does not mean
one-shot learning is mathematically impossible.

It means the exact current teacher
contains same-epoch local causal ordering
that the initial student interface should preserve.

INTERPRETATION

CASE A

If:

LU0E_V02_STAGED_LOCAL_IDENTIFIABLE = TRUE

and:

all three minimality controls pass

and:

LU0E_STAGING_REQUIRED = TRUE

then:

the information boundary is sufficiently clean
to preregister the first learned per-cell
teacher-imitation experiment.

Use OBS-V1 or an exactly information-equivalent encoding.

The first student should be:

shared across cells;

small feed-forward MLP;

no per-cell learned parameter block;

no global context channel;

no task-id shortcut;

no future information.

CASE B

If identifiability is TRUE
but a minimality control fails:

do not train yet.

Reduce or revise the observation representation
so the student is not being handed
unjustified teacher-specific derived information.

CASE C

If identifiability is FALSE:

locate the surviving nonlocal dependency.

Do not add a global student channel
merely to make imitation easy.

Either remove the dependency
from the teacher substrate
or explicitly downgrade the strict-local claim.

MECHANICAL GATE

Before LU0EF1 prove:

1. V0.2 parent identity exact;

2. NO_POOL semantics exact;

3. pc = ps = 0
   in audited U recruitment;

4. LOCAL_HEDGE exact V0.1/V0.2 semantics;

5. ECHO_PHASE exact V0.2 semantics;

6. OBS-V1 contains only declared bounded-local channels;

7. radius-3 vector length = 7 cells;

8. raw task causal-radius calculation = 17;

9. no phase/future/global-count channel
   in observation serialization;

10. all probability vectors sum to 1;

11. deterministic pair-suite construction;

12. duplicate mechanical structure byte-identical.

PRIMARY DISCIPLINE

After LU0EF1:

derive the exact deterministic pair suite;

run complete audit twice;

require byte identity;

then open identifiability and minimality outcomes.

NO POST-RESULT TUNING

Do not change:

OBS-V1 fields;

radii;

pair count;

distant perturbation families;

1e-12 identifiability tolerance;

1e-6 negative-control threshold;

teacher equations;

V0.2;

LOCAL_HEDGE;

ECHO_PHASE;

or staging interpretation
after primary execution begins.

PLAIN-SPEAK QUESTION

We removed the obvious global wire.

Now we need to check
whether another hidden wire is still there.

A future learned cell
should be able to decide what to do
from itself and its neighborhood.

So we will build pairs of worlds
that look exactly the same
to one cell locally,
while everything far away is changed.

If the correct action probabilities
for that cell stay exactly the same,
the far-away world is no longer secretly controlling it.

We will also deliberately hide
some local memory and local evidence
to prove which inputs the cell really needs.

And we will test one more subtle point:

the current organism updates itself
in several local steps inside each epoch.

A newly uncertain or defecting neighbor
can matter later in that same epoch.

So the first learned cell
should probably learn those local stages
instead of pretending the whole epoch
happens in one indivisible jump.

If this audit passes,
the information boundary is finally clean enough
to train the first genuinely local learned updater.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
