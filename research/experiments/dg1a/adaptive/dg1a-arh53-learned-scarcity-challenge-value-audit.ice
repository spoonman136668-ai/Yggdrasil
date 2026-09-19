TITLE: DG-1A-AR-H53 — Learned Scarcity-Challenge Value Under Distributed Price Fields
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE LEARNED-SCARCITY-VoI RESULT + TOPOLOGY-SHIFT/CONFOUNDING LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh52-value-gated-scarcity-override-audit.ice

PURPOSE
H52 established that scarcity override challenge should be purchased selectively by expected value.

Its analytic comparator knew:
- calibrated false-scarcity risk;
- challenge resolvability.

H53 removes those privileged variables from the adaptive policy.

QUESTION
Can a bounded local learner estimate:
WHEN SCARCITY OVERRIDE IS WORTH CHALLENGING

using only noisy local distributed price/transfer features,
resource runway,
candidate value,
and realized consequence?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil exposes these exact local features;
- freeze the state bins;
- freeze EMA learning;
- solve target-free consequence;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

LATENT EVENT MIX
Persistent scarcity proposals.

Approximately:
22%

are false/coordinated scarcity.

The rest are genuine scarcity.

The learner never receives the true scarcity label.

CANDIDATE BRANCH VALUES

0.15
0.35
0.80
1.50.

RUNWAY COST MULTIPLIER

1
2
5.

CHALLENGE EFFECT STRENGTH

0.20
0.32
0.50.

OBSERVABLE LOCAL FEATURES

1.
PRICE-vs-LOCAL-ANCHOR DISAGREEMENT

coarse bins.

2.
TRANSFER FULFILLMENT

coarse bins.

3.
LOCAL RUNWAY / RESERVE STRESS

coarse bins.

4.
CANDIDATE BRANCH VALUE

coarse bins.

No:
false-scarcity probability
or
challenge-resolvability label
is supplied.

A total of:
240
bounded discrete local states
are available in the primary synthetic representation.

ACTIONS

A0:
TRUST SCARCITY
and
do not challenge.

A1:
BUY FUNCTIONAL SCARCITY CHALLENGE.

Training exploration:
10%.

Primary value update:
EMA.

PRIMARY MATURATION
8 matched seeds.

Training:
180,000 events.

Greedy evaluation:
70,000 events.

PRIMARY LEARNED POLICY
Best tested EMA working point:

alpha:
0.03.

mean true loss:
0.06498.

between-seed SD:
0.00058.

mean challenge pairs per proposal:
1.410.

fraction challenged:
13.03%.

NEVER CHALLENGE BASELINE

mean loss:
0.10543.

PRIMARY POSITIVE
The bounded local learner substantially improves on always trusting scarcity:

0.1054
->
0.0650.

It does so without:
- true false-scarcity risk;
- true challenge-resolvability labels.

Most candidates:
approximately 87%

receive no challenge.

Thus:
useful scarcity-challenge value can be learned from local history.

INFORMATION CEILING
A per-event oracle that knows the realized best action reaches:

approximately:
0.03714.

The learned policy remains materially above that level.

The gap reflects:
- coarse local state;
- noisy context;
- hidden challenge resolvability;
- exploration / value estimation error.

Do not interpret the remaining gap as merely:
more training needed.

TOPOLOGY / COMMON-MODE SHIFT
The local mapping between:

PRICE-LOCAL DISAGREEMENT

and

TRUE FALSE-SCARCITY RISK

is changed.

Before shift:
false scarcity usually creates larger disagreement with direct local resource evidence.

After shift:
a common-mode/topology change partially corrupts the local anchor,
so:
false scarcity disagreement shrinks
and
genuine scarcity disagreement increases.

No semantic topology-change label is supplied.

STATIC PRE-SHIFT POLICY EVALUATED POST-SHIFT

loss:
approximately 0.127 to 0.129.

NEVER-CHALLENGE post-shift baseline:

approximately:
0.1054.

PRIMARY SHIFT NEGATIVE
A previously useful challenge-value policy can become:

WORSE THAN DOING NOTHING

after the observation topology changes.

Thus:

LEARNED SCARCITY ECONOMICS
ARE THEMSELVES CONTEXT-DEPENDENT STATE.

ONLINE RELEARNING
Fresh shift streams.

Checkpoint losses after topology change.

CUMULATIVE HISTORY

5,000 events:
0.1273.

20,000:
0.1226.

50,000:
0.1180.

90,000:
0.1128.

The policy remains worse than:
never challenge

for most of the tested horizon.

MEDIUM RECENCY EMA
alpha:
0.01.

5,000:
0.1267.

20,000:
0.1174.

50,000:
0.1101.

90,000:
0.1064.

FAST RECENCY EMA
alpha:
0.03.

5,000:
0.1245.

20,000:
0.1107.

50,000:
0.1070.

90,000:
0.1015.

PRIMARY RECENCY RESULT
Recency-weighted challenge-value trust adapts substantially faster than cumulative history.

At the late checkpoint,
the fast-recency learner again outperforms the:
never-challenge
baseline.

The same recurring stability/plasticity tradeoff remains:

too much history
->
stale resource policy.

too much forgetting
->
noisy challenge allocation.

PASSIVE CONSEQUENCE CONFOUND
The challenge action consumes time.

A synthetic passive improvement is now added to the observed challenge outcome during TRAINING.

The true evaluation loss is unchanged.

Primary:
8 matched seeds.

NO CONFOUND

true eval loss:
0.06512.

challenge pairs:
1.442.

fraction challenged:
13.32%.

CONFOUND BONUS = 0.02

loss:
0.06504.

pairs:
1.485.

challenged:
13.73%.

CONFOUND = 0.05

loss:
0.06616.

pairs:
1.871.

challenged:
17.29%.

CONFOUND = 0.08

loss:
0.06804.

pairs:
2.262.

challenged:
20.90%.

CONFOUND = 0.12

loss:
0.07287.

pairs:
2.850.

challenged:
26.35%.

PRIMARY CONFOUNDING NEGATIVE
Passive improvement during challenge causes the local learner to overestimate:

VALUE OF SCARCITY OVERRIDE EVIDENCE.

Challenge spending nearly doubles across the tested confound sweep,
while true functional performance worsens.

Therefore:

OUTCOME IMPROVED WHILE I CHALLENGED SCARCITY

DOES NOT IMPLY:

THE CHALLENGE CAUSED THE IMPROVEMENT.

CAUSAL-CONTROL CONSEQUENCE
H53 therefore inherits the S7-S9 / H51 requirement.

Challenge-value learning should update from:

TARGET CONSEQUENCE CHANGE

minus

ACTION-DECOUPLED WAITING / DISTURBANCE CHANGE.

The learned resource policy needs causal hygiene
just like the lower-level adaptive behavior it regulates.

CURRENT LEARNED SCARCITY-VALUE STATE
A practical bounded local learner now plausibly needs:

PRICE TRUST / DISAGREEMENT

+

TRANSFER FULFILLMENT HISTORY

+

DIRECT LOCAL RESOURCE ANCHOR

+

RUNWAY / RESERVE STATE

+

CANDIDATE VALUE

+

RECENT CHALLENGE OUTCOMES

+

CHALLENGE COST

+

VALUE-POLICY TRUST / RECENCY

+

CAUSAL WAITING CONTROL

->

BUY CHALLENGE
or
TRUST SCARCITY
or
HOLD.

RELATION TO H22
H22:
learned context-challenge value can mature,
become stale,
and become confounded.

H53 shows:
the exact same meta-failure appears for scarcity challenge
inside a distributed price/transfer system.

This strongly supports:
one reusable local resource-value learning motif

rather than:
bespoke evidence schedulers.

DECISION
AR-H53 is POSITIVE WITH TOPOLOGY-SHIFT AND CONFOUNDING LIMITS.

Supported synthetically:

- local history can learn useful scarcity-challenge allocation without true hidden labels;
- sparse challenge allocation can strongly outperform never challenging;
- challenge-value policies can become stale after distributed observation topology changes;
- recency improves adaptation;
- passive consequence confounding causes systematic over-challenging;
- causal-control hygiene is required at the resource-policy layer.

Not demonstrated:

- real Yggdrasil scarcity-value learning;
- real false-scarcity risk representation;
- real matched waiting control;
- distributed learning across many cells;
- stability when multiple price regions learn challenge value simultaneously.

CLEAN SCIENTIFIC PAUSE
H49-H53 now form a coherent distributed scarcity-trust sequence:

H49:
coordinated in-range price drift defeats single-message bounds,
but direct local anchors and temporal change budgets help.

H50:
shared provenance should coexist with separate price/transfer authority state.

H51:
mutually consistent false scarcity requires functional causal validation.

H52:
functional scarcity validation must itself be value-gated.

H53:
that challenge value can be learned locally,
but maturation, topology shift, and confounding remain.

NEXT HIGH-VALUE MOVE
AR-H54 — MULTI-REGION SCARCITY-CHALLENGE COUPLING / HERDING

Question:

What happens when many neighboring regions learn scarcity-challenge value at the same time?

A local policy may be individually rational
but collectively create:

- synchronized challenge storms;
- correlated override of real scarcity;
- oscillatory memory-price fields;
- repeated local branch bursts.

Compare:

A.
independent local challenge learners;

B.
local challenge-price / inhibition field;

C.
randomized/staggered challenge leases;

D.
real system-wide scarcity shock;

E.
false coordinated scarcity.

Desired:

uncertain region
->
bounded localized validation.

many uncertain neighbors
->
avoid simultaneous probe storm.

real organism-wide scarcity
->
do not let challenge herding overwhelm the resource envelope.

This should connect:
H33 wake-storm coordination

with
H47-H53 distributed memory-price validation.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_training_events = 180000
primary_eval_events = 70000
primary_matched_seeds = 8
best_tested_alpha = 0.03
