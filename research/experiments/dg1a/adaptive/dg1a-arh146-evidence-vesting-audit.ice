TITLE: DG-1A-AR-H146 — Evidence Vesting / Dormant Maturity-Certificate + Contradiction-Triggered Reactivation Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh145-post-blastema-maturation-audit.ice

PURPOSE

H145 established:

DIRECTED EVIDENCE ROUTING
CAN
MATURE
USEFUL ACTIVE VALUE
QUICKLY.

It also established a decisive failure:

if:
all maturity evidence decays
with wall-clock time,

then:

DORMANCY
BECOMES
INDISTINGUISHABLE
FROM
EVIDENCE AGAINST
A MEMBER.

That produced:

premature consolidation,
then:
mass re-quarantine.

At 40 episodes:

EXPECTED-RELEASE

consolidated:
100%

but ended with:
approximately 99%
of members quarantined.

H146 asks:

CAN
MATURITY
VEST
INTO
A DORMANT
EPISTEMIC CERTIFICATE

SO THAT:

INACTIVITY
DOES NOT
ERASE
PREVIOUSLY EARNED
TRUST,

WHILE:

REAL CHANGE
STILL
REACTIVATES
EVIDENCE GATHERING?

BOUNDARY

Synthetic research only.

It does not:
- implement biological tissue;
- claim biological memory equivalence;
- establish production certificate lifetimes;
- execute or modify STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX
LONGITUDINAL
POST-MATURATION

CORE DISTINCTION

LABILE EVIDENCE

Fast-changing.

Used while:
a member is still maturing
or:
being revalidated.

Primary labile evidence decay:

0.95 / episode.

VESTED CERTIFICATE

A typed record that:

does NOT
decay merely because:
the member is inactive.

It can be invalidated by:
explicit structural / evidentiary events.

CERTIFICATE OBJECT

C = {
    member_id,
    topology_epoch,
    provisional_region,
    support_class,
    boundary_class,
    calibration_class,
    evidence_provenance,
    vesting_episode,
    contradiction_budget,
    hazard_class,
    last_revalidation_episode
}

PRIMARY VESTING CONTRACT

A member may vest only when:

effective labile observations >= 10

AND

own assignment support >= 0.90

AND

support margin >= 0.35

AND

no unresolved direct contradiction
in:
the last 3 member-targeted observations.

Region requirement:

the member's region must have:

cross-boundary contradiction rate <=5%

with:
at least 10 effective cross-boundary observations.

Vesting is:
member-specific.

One mature representative:

does NOT
vest:
other members.

VESTED ACTION STATUS

A valid vested certificate counts as:

ACTION-MATURE

even when:

raw labile evidence
has decayed below:
the H145 maturity threshold.

This is the central H146 intervention.

PRIMARY ECOLOGY

Family size:
60..100.

True regions:
4..6.

Promoted topology residual error:
2%.

Member values:
H145 primary lognormal.

Active fraction:
20%..50% / episode.

Horizon:
60 episodes.

Primary sensor error:
5%.

Evidence budget during:
active maturation / revalidation:

0.5N target-region observations / episode.

Dormant certificate maintenance cost:

0.

Primary directed router:

H145 EXPECTED-RELEASE.

PHASE SCHEDULE

Episodes 1..20:

MATURATION PHASE.

Use:
EXPECTED-RELEASE

to:
mature
and:
vest
eligible members.

Episodes 21..40:

DORMANCY / ROTATING ACTIVITY PHASE.

No global structural event.

Activity rotates so that:
many vested members spend:
10+ consecutive episodes inactive.

Episodes 41..60:

EVENT / REACTIVATION PHASE.

Each world receives:
one preregistered event class.

PRIMARY EVENT CLASSES

E0 — STABLE RETURN

No structural change.

Previously dormant members reactivate.

Correct behavior:

use valid vested certificates
with:
near-zero re-audit cost.

E1 — TOPOLOGY EPOCH CHANGE

A true region:
splits
or:
merges.

The accepted topology epoch increments.

Certificates from:
the old epoch

are:
STALE.

Correct behavior:

do not trust stale certificates
for broad action.

E2 — LOCAL NEIGHBORHOOD CHANGE

10% of members change:
functional region

without:
a global epoch increment.

This tests:

whether contradiction-driven
local revalidation

can detect:
a change that
global epoch tagging
does not announce.

E3 — CONTRADICTION BURST

No true topology change.

For:
5 episodes,

a subset of members receives:
elevated contradictory observations.

Then:
the environment returns to normal.

Correct behavior:

do not:
permanently destroy
good certificates

from:
short noisy contradiction.

E4 — CALIBRATION SHIFT

Sensor error changes:

5%
->
20%

at episode 41.

Calibration class changes.

Correct behavior:

do not treat:
old evidence quality

as:
still calibrated.

E5 — HIGH-VALUE DORMANT RETURN

A member with:
a long-dormant valid certificate

becomes:
high-value active.

No structural change.

Correct behavior:

avoid:
full re-audit

while allowing:
a bounded lightweight check
for stricter policies.

PRIMARY POLICIES

A — DECAYING-RAW

H145 comparator.

No certificate.

All trust derives from:
labile evidence.

B — FOREVER-CERT

Once vested:

certificate never expires
and:
ignores contradiction,
epoch,
and:
calibration changes.

Negative comparator.

C — WALL-CLOCK-EXPIRY

Vested certificate expires after:

10 episodes

regardless of:
activity
or:
environmental stability.

Tests:
whether simple time expiry
recreates unnecessary maintenance.

D — ACTIVITY-COUNT-EXPIRY

Certificate does not age:
while inactive.

It expires after:

8 active episodes
since:
last revalidation.

E — EPOCH-CERT

Certificate remains valid:

until:
topology epoch changes.

Contradiction alone
does not invalidate.

F — CONTRADICTION-BUDGET

Certificate stores:
contradiction debt.

Primary budget:

3 net contradictory observations

within:
a rolling 6-observation local window

triggers:
REVALIDATION.

No wall-clock expiry.

G — HYBRID-VESTED

Certificate remains valid unless:

- topology epoch changes;
- calibration class changes;
- contradiction budget is exceeded;
- member's provisional region identity changes.

Additional high-value return rule:

if:
member has been inactive >=15 episodes

AND

current active value
>3x family mean,

require:
2 fresh local observations

before:
broad action.

No full re-audit.

REVALIDATION

When a certificate is invalid / challenged:

member returns to:
LABILE REVALIDATION.

Revalidation contract:

effective fresh observations >=6

AND

own support >=0.85

AND

margin >=0.25.

If passed:

certificate is:
RE-VESTED

under:
the current epoch / calibration class.

If failed:

member remains:
QUARANTINED.

CERTIFICATE CONTRADICTION ACCOUNTING

A fresh observation contributes:
+1 contradiction

when:
it conflicts with:
the vested member's region relation.

A confirming observation reduces:
contradiction debt by 1

to:
a minimum of 0.

This produces:

HYSTERESIS

against:
single noisy observations.

PRIMARY METRICS

1. stable-return immediate safe coverage;
2. dormant certificate retention;
3. audits / active-value unit after episode 20;
4. false trusted-action rate;
5. stale-certificate action rate;
6. revalidation rate;
7. revalidation latency;
8. unnecessary revalidation rate;
9. change-detection rate;
10. contradiction-burst false invalidation rate;
11. calibration-shift unsafe-action rate;
12. high-value dormant-return audit cost;
13. final quarantined fraction;
14. total post-maturation evidence cost;
15. action coverage under each event class.

PRIMARY ACCEPTANCE SHAPE

Evidence vesting is supported if:

- HYBRID-VESTED retains materially more stable-return action coverage than DECAYING-RAW;
- HYBRID-VESTED uses materially fewer post-maturation audits than DECAYING-RAW;
- stable dormant members do not lose validity merely from inactivity;
- EPOCH-CERT and HYBRID invalidate old-epoch certificates after E1;
- HYBRID detects most E2 local-neighborhood changes through contradiction-triggered revalidation;
- FOREVER-CERT demonstrates a measurable unsafe stale-action failure under E1/E2/E4;
- WALL-CLOCK-EXPIRY performs materially more unnecessary revalidation than HYBRID in E0/E5;
- contradiction hysteresis avoids catastrophic false invalidation under E3;
- calibration shift causes HYBRID to fail closed rather than trust the old sensor class;
- high-value dormant return does not require full-family re-audit;
- valid certificate storage incurs zero per-episode active compute while dormant.

FAILURE CONDITIONS

Treat H146 as mixed/negative if:

- vested certificates preserve coverage only by trusting stale members;
- E2 local changes evade contradiction-triggered detection;
- contradiction noise causes widespread false certificate destruction;
- safe policies re-audit nearly as much as DECAYING-RAW;
- stable inactivity still requires periodic refresh;
- calibration shift cannot be distinguished from ordinary contradiction;
- high-value return forces full evidence reacquisition;
- certificate state grows without bounded fields / expiry semantics.

PRIMARY CONFIRMATION SIZE

1,000 held-out worlds / event class.

6 event classes.

7 certificate policies.

42,000 policy-event-worlds.

Common-world discipline:

within each event world:

policies receive:
- identical true topology;
- identical active schedule;
- identical member values;
- identical event realization;
- identical potential observation outcomes
  for matching member-region audit slots.

ROBUSTNESS

Sensor error before event:
1%, 5%, 10%.

Sensor error after calibration shift:
10%, 20%, 30%.

Residual promoted-topology error:
0%, 2%, 5%.

Contradiction budget:
1, 3, 5.

Contradiction window:
4, 6, 10 observations.

Wall-clock expiry:
5, 10, 20 episodes.

Activity-count expiry:
4, 8, 16 active episodes.

Dormancy:
5, 15, 30 episodes.

High-value return:
2x, 3x, 8x family mean.

OUT-OF-BOX EXTENSION

If H146 succeeds:

Yggdrasil gains:
TWO-TIMESCALE EPISTEMIC MEMORY.

Fast state:

LABILE EVIDENCE.

Slow state:

VESTED MATURITY CERTIFICATE.

This means:

DORMANCY

can become:
cheap

without becoming:
epistemically amnesic.

A later experiment should test:

whether vested certificates
can be inherited
through:
bounded topology split / merge

with:
explicit loss of strength.

The separately recorded:

STRUCTURAL TRUST REGION
/
BOUNDED INCREMENTAL PATCHING

hypothesis remains future work.

H146 does not modify:
topology repair policy.

FROZEN BEFORE EXECUTION

Certificate fields,
vesting contract,
phase schedule,
event classes,
policies,
contradiction accounting,
revalidation contract,
metrics,
acceptance shape,
failure conditions,
confirmation size,
and robustness dimensions above

are fixed before synthetic execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX_LONGITUDINAL_POST_MATURATION
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = 156e02cfb0e8d0875cfbd7639b18a3390c375f15


IMPLEMENTATION FREEZE — BEFORE PRIMARY EXECUTION

The following mechanics resolve details not fixed in the initial preregistration.

No policy,
certificate invalidation rule,
event class,
acceptance gate,
world count,
or evidence budget
is changed.

PHASE-1 MATURATION REALIZATION

Episodes 1..20 use:

H145 EXPECTED-RELEASE
member targeting

under:
the H145 region-stratified sufficient-statistic evidence realization.

Primary sensor error:
5%.

Episode deliberate-audit budget:
ceil(0.5N).

For H146 vesting:

member-targeted evidence is summarized as:
assignment-confirming
versus:
assignment-contradicting.

A correct provisional assignment produces:
a confirming observation
with probability:
0.95.

A residual wrong assignment produces:
a confirming observation
with probability:
0.05.

The potential outcome stream is keyed by:

world,
episode,
member,
audit-slot.

Vesting uses:
the preregistered 10-observation,
0.90 support,
0.35 margin-equivalent,
last-three-no-contradiction contract.

The H144-promoted topology is treated as carrying:
a valid region-boundary class

for members whose provisional assignment is correct.

Residual wrong assignments:
cannot inherit that member-level validity.

PHASE-2 ACTIVITY ROTATION

Episodes 21..30:

activity is sampled only from:
a fixed world-specific half of the population

plus:
the minimum random supplement needed to satisfy
20%..50% active fraction.

Episodes 31..40:

the complementary half becomes:
the preferred active pool.

This guarantees:
substantial 10+ episode dormancy

without:
changing the preregistered active-fraction range.

OPPORTUNISTIC ACTIVE FEEDBACK

Every active member produces:

one local relational feedback observation / episode

as a byproduct of:
ordinary active use.

This feedback:

costs:
0 deliberate audits.

It may:
confirm
or:
contradict
a vested certificate.

It does NOT:
by itself
satisfy:
the six-audit revalidation contract.

Its only authority is:

- contradiction-debt update;
- challenge / invalidation triggering;
- calibration / epoch mismatch observation.

This prevents:

ZERO-MAINTENANCE DORMANCY

from implying:

ZERO DETECTABILITY
ON REACTIVATION.

DELIBERATE REVALIDATION BUDGET

When one or more active members require:
revalidation,

the policy may spend up to:

ceil(0.5N)

deliberate member-targeted observations / episode.

Allocation:

EXPECTED-RELEASE style:

current active member value
/
estimated remaining revalidation observations.

No deliberate audit is spent on:
valid dormant certificates.

REVALIDATION OUTCOME

For current correct assignment:

confirm probability =
1 - current sensor error.

For current wrong / changed assignment:

confirm probability =
current sensor error.

After:
6 fresh deliberate observations:

support >=0.85

is equivalent in this binary realization to:

at least:
6 confirming observations

when six observations are present.

Therefore:

primary revalidation pass requires:
6 / 6 confirming observations.

If failed:

the member remains:
QUARANTINED

and:
a new six-observation revalidation block
may begin on a later active episode.

This is intentionally strict.

EVENT TIMING

All E1..E5 event changes occur:

at the start of episode 41

before:
that episode's active feedback.

E0 has:
no change.

E1 — TOPOLOGY EPOCH CHANGE

Increment:
topology_epoch.

Additionally:

select one current true region
and:
one second region.

Move:
approximately half
of the first region's members

into:
the second region's functional identity.

This creates:
a real epoch-level topology change

while:
keeping K fixed.

No policy receives:
the changed member identities.

E2 — LOCAL NEIGHBORHOOD CHANGE

At episode 41:

select:
ceil(0.10N) members.

Each changes:
functional true region

to:
a different existing region.

topology_epoch:

does NOT change.

E3 — CONTRADICTION BURST

True topology:
unchanged.

Select:
20% of members.

Episodes 41..45:

their opportunistic feedback
has:
45% contradiction probability.

Episode 46 onward:

return to:
5% primary sensor error.

Deliberate revalidation audits
retain:
5% sensor error.

E4 — CALIBRATION SHIFT

At episode 41:

known calibration class changes.

Opportunistic
and:
deliberate observation error:

5%
->
20%.

No true topology change.

HYBRID-VESTED:

invalidates certificates carrying:
the old calibration class.

E5 — HIGH-VALUE DORMANT RETURN

Before phase 2:

choose:
one vested candidate member

from:
the half scheduled for long dormancy
when available.

Force it:
inactive
for episodes 21..40.

At episode 41:

force active.

Temporary active value:

8x
its baseline value.

True topology:
unchanged.

HYBRID-VESTED:

requires:
2 deliberate fresh observations

before:
certificate-backed broad action

when:
the preregistered dormancy / value conditions are met.

POLICY ACTION RULE

An active member contributes:
certificate-backed action coverage

only when:

its certificate is:
currently valid

or:

for DECAYING-RAW:
its current labile maturity contract passes.

A challenged,
expired,
stale,
or:
revalidating member

is:
QUARANTINED
from broad action.

FALSE TRUSTED ACTION

Count an action as false trusted when:

the member is allowed:
certificate-backed / mature broad action

while:

its current true functional region
differs from:
the certificate / provisional region.

CALIBRATION-STALE ACTION

For E4:

also record:

action performed under:
a certificate whose calibration class
does not match:
the current known calibration class.

This is an epistemic invalidity

even when:
the member's true region is unchanged.

DECAYING-RAW COMPARATOR

After episode 20:

continue:
H145-style 0.95 evidence decay.

Spend:
ceil(0.05N)
uniform maintenance observations / episode.

No vested certificate exists.

This reproduces:
the H145 retention failure mode.

WALL-CLOCK EXPIRY

Age is measured from:
last vest / re-vest episode.

At age:
>10 episodes

certificate becomes invalid.

ACTIVITY-COUNT EXPIRY

Increment:
certificate active-age

for every episode
the member is active
while certificate is valid.

At:
>8 active episodes

certificate becomes invalid.

EPOCH-CERT

Episode E1 epoch mismatch:

invalidates:
all old-epoch certificates

before:
episode-41 action.

CONTRADICTION-BUDGET

Maintain:

integer contradiction debt.

Opportunistic contradiction:

debt += 1.

Opportunistic confirmation:

debt -= 1
to minimum:
0.

If:

debt >=3

before the episode's broad action decision:

invalidate
and:
enter revalidation.

The implementation also retains:
the most recent six opportunistic outcomes

to verify:
the challenge occurred within
the preregistered local window.

HYBRID-VESTED

Applies:

- topology epoch mismatch;
- calibration class mismatch;
- region-identity mismatch when known;
- contradiction-budget rule;
- high-value dormant-return two-audit check.

No wall-clock expiry.

No inactivity expiry.

PRIMARY RANDOMNESS

1,000 held-out worlds / event.

No H145 primary or robustness seed is reused.

Event seed blocks:

E0:
20260919146000..20260919146999.

E1:
20260919147000..20260919147999.

E2:
20260919148000..20260919148999.

E3:
20260919149000..20260919149999.

E4:
20260919150000..20260919150999.

E5:
20260919151000..20260919151999.

No execution-semantic change is permitted after:
primary H146 execution begins.
