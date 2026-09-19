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
