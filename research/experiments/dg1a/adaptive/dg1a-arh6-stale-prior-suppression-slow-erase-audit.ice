TITLE: DG-1A-AR-H6 — Stale-Prior Suppression vs Slow Erase / Rewrite
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE WRITE-ERASE-SEPARATION AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh5-heritable-write-credit-audit.ice

PURPOSE
H5 established that slow heritable write should require persistent, coherent, locally useful action credit.

H5 also exposed a separate unresolved problem:

once a slow prior becomes useful enough to store,
how should the organism react when that inherited prior later becomes stale?

H6 asks whether Yggdrasil should separate:

1.
FAST SUPPRESSION OF INHERITED EXPRESSION

from

2.
SLOW ERASURE / REWRITE OF HERITABLE STATE.

BOUNDARY
This is synthetic.

It does not:
- implement a real Yggdrasil micro-genome;
- prove a real target-free local stale-prior signal exists;
- freeze any threshold or time constant;
- modify global shared network weights;
- execute or modify STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CORE HYPOTHESIS
A contradictory environment should not force an immediate choice between:

OBEY OLD HEREDITY

and

DESTROY OLD HEREDITY.

A safer ordering may be:

contradiction
->
suppress inherited influence quickly
->
adapt fast phenotype
->
rewrite slow prior only if contradiction persists.

TOY
Independent local lineages:
1000 per seed.

Confirmation:
24 matched seeds.

Fast role state:
4 bounded dimensions.

Slow inherited prior:
4 bounded dimensions.

Familiar regime A:
[0.25, 0.45, 0.25, 0.35]

Changed regime B:
[0.20, 0.25, 0.80, 0.15]

Fast observation noise:
sigma = 0.16

Fast role update:
eta = 0.14

Role-state turnover:
every 10 episodes.

The inherited prior is used as a developmental reinitialization bias at turnover.

It is NOT continuously pulled into the fast state every step.

This preserves the H3 result that heredity should bias development rather than continuously override current local utility.

LOCAL CONSEQUENCE
Fast actions receive a noisy local consequence signal:

benefit =
loss_before_action
-
loss_after_action
+
measurement noise.

Fast-action consequence noise:
sigma = 0.003.

The mechanism receives no regime label.

LOCAL PRIOR CHALLENGE
To ask whether the inherited prior is currently useful,
the synthetic organism evaluates a small candidate move toward the slow prior:

prior_action =
0.10 * (slow_prior - fast_role).

It receives only the measured local consequence of that candidate prior-directed move.

Prior-challenge consequence noise:
sigma = 0.0015.

If movement toward the inherited prior is repeatedly locally harmful,
that is stale-prior evidence.

The mechanism is NOT told:
- A;
- B;
- repair;
- maintenance;
- event duration;
- whether the current regime is temporary or persistent.

The synthetic benchmark computes the consequence from the hidden target only to generate the local consequence observation.

The controller itself receives only the consequence observation.

STALE EVIDENCE
Convert prior-challenge consequence into a bounded soft stale sample.

FAST stale evidence:
EMA update weight = 0.30.

SLOW stale evidence:
EMA update weight = 0.015.

Thus:
fast expression can react quickly,
while slow heredity requires much longer persistence.

FAST SUPPRESSION
Fast stale evidence above an exploratory threshold reduces inherited influence at future turnover events.

Suppression state relaxes toward the current fast stale gate with update rate:
0.45.

SLOW REWRITE
Only the split mechanism uses the slow stale gate.

When long-horizon stale evidence matures,
the slow prior moves toward the current fast role at exploratory rate:

0.012 * slow_stale_gate.

These values are synthetic discriminating parameters only.

Do not freeze them for Yggdrasil.

COMPARATORS

A. SYMMETRIC SLOW WRITE / ERASE
Use the H5-style persistence/coherence slow-write gate in either direction.

No fast inherited-prior suppression.

Slow state changes symmetrically toward the current fast role.

B. FAST SUPPRESSION ONLY
Inherited expression can be suppressed quickly when prior challenge is repeatedly harmful.

Slow prior itself is preserved.

This tests whether functional reversibility can be obtained without erasure.

C. SPLIT SUPPRESSION + SLOW REWRITE
Use the same fast suppression as B.

In addition:
persistent stale-prior evidence opens a separate slow rewrite gate.

This tests whether phenotype and heredity can operate on different reversal timescales.

LIFECYCLE
Warm familiar A:
120 episodes.

First B exposure:
20
50
100
or
160 episodes.

Brief return to A:
20 episodes.

Second B exposure:
80 episodes.

Final A:
60 episodes.

Primary scientific contrasts:
- B=20 tests short contradiction;
- B=160 tests persistent contradiction;
- brief A return tests whether retained old memory can become useful again;
- B2 tests whether persistent B memory reduces re-entry cost.

PRIMARY RESULTS

SHORT CONTRADICTION — B1 = 20

SYMMETRIC
B1 mean loss:
0.028157

B1 last-10 loss:
0.028183

slow-prior distance from A at B1 end:
0.022478

SLOW STATE is still near A,
but repeated developmental resets keep re-imposing the stale A prior,
so fast adaptation is poor.

FAST SUPPRESSION ONLY
B1 mean loss:
0.015786

B1 last-10:
0.003451

mean suppression during B1:
0.845747

slow-prior distance from A:
0.022581

SPLIT
B1 mean loss:
0.015786

B1 last-10:
0.003451

mean suppression:
0.845663

slow-prior distance from A:
0.022558

Interpretation:

the split mechanism reacts behaviorally almost immediately,
but the 20-episode contradiction produces essentially no slow rewrite.

This is the desired:
FAST PHENOTYPE
+
PRESERVED HEREDITY
behavior.

PERSISTENT CONTRADICTION — B1 = 160

SYMMETRIC
B1 mean loss:
0.017265

B1 last-10:
0.007013

slow-prior distance from A:
0.349963

slow-prior distance from B:
0.271609

FAST SUPPRESSION ONLY
B1 mean loss:
0.006391

B1 last-10:
0.005120

slow-prior distance from A:
0.022581

slow-prior distance from B:
0.620814

The phenotype adapts,
but heredity never consolidates the persistent B regime.

SPLIT
B1 mean loss:
0.006235

B1 last-10:
0.004655

slow-prior distance from A:
0.343065

slow-prior distance from B:
0.278442

Interpretation:

persistent contradiction eventually opens slow rewrite.

The slow prior moves strongly away from A and toward B,
while the fast phenotype remains protected by suppression during the transition.

PRIMARY POSITIVE
The same local history can support two different questions:

FAST QUESTION
Should I express this inherited prior right now?

SLOW QUESTION
Has this contradiction persisted long enough to rewrite heredity?

Those questions should not share one time constant.

BRIEF RETURN TO FAMILIAR A AFTER PERSISTENT B
After B1=160,
return to A for 20 episodes.

SYMMETRIC
A-return mean loss:
0.009739

last-10:
0.009701

FAST SUPPRESSION ONLY
A-return mean:
0.009288

last-10:
0.001398

SPLIT
A-return mean:
0.009254

last-10:
0.004787

Interpretation:

the suppression-only mechanism kept the old A prior intact.

Once the stale suppression signal clears,
that preserved prior becomes useful again.

The split mechanism had already consolidated much of B into slow state,
so the old A memory is only partially retained.

This is the central retention/rewrite tradeoff.

SECOND B EXPOSURE AFTER THE BRIEF A RETURN

SYMMETRIC
B2 first-10 loss:
0.006661

B2 mean:
0.006652

FAST SUPPRESSION ONLY
B2 first-10:
0.028130

B2 mean:
0.007657

SPLIT
B2 first-10:
0.013847

B2 mean:
0.005709

Interpretation:

preserving A forever gives excellent A recall,
but forces B to be rediscovered after every return.

The split mechanism retains enough B in slow state to reduce B re-entry cost materially.

LIFECYCLE AGGREGATE
For the persistent-B lifecycle:

B1=160
+
A return=20
+
B2=80

mean loss across those phases:

SYMMETRIC:
0.013421

FAST SUPPRESSION ONLY:
0.007004

SPLIT:
0.006305

The split architecture is best at this synthetic lifecycle working point.

This is NOT a universal optimum claim.

It only shows that separating suppression and rewrite can dominate a single symmetric timescale when regimes recur.

DURATION SWEEP
The split slow prior moves progressively only as contradiction persists.

B1 duration 20:
distance from A:
0.022558

distance from B:
0.619366

B1 duration 50:
distance from A:
0.042328

distance from B:
0.584253

B1 duration 100:
distance from A:
0.207552

distance from B:
0.414134

B1 duration 160:
distance from A:
0.343065

distance from B:
0.278442

Thus:
brief contradiction
mostly suppresses expression.

Persistent contradiction
progressively rewrites heredity.

LONG RETURN CHECK
After B1=160,
extend return to A from 20 to 160 episodes.

SPLIT slow-prior distance from A:

after A return 20:
0.315325

after A return 160:
0.223079

The slow prior begins moving back toward A only when the reverse contradiction itself persists.

This supports reversible slow reconsolidation rather than one-way erasure.

IMPORTANT NEGATIVE 1
FAST SUPPRESSION ALONE is not enough.

It preserves useful old memories,
but it never consolidates a genuinely persistent new regime.

Repeated B re-entry therefore remains expensive.

IMPORTANT NEGATIVE 2
SLOW REWRITE is not free.

Once B is consolidated,
a brief return to A no longer receives the full benefit of the original A prior.

The system has a real:

MEMORY RETENTION
vs
RECONSOLIDATION

tradeoff.

IMPORTANT NEGATIVE 3
The synthetic prior challenge consumes local consequence evidence.

A production mechanism cannot assume unlimited inherited-prior probing.

This directly connects H6 to:

AR-U13 budgeted active evidence

and

AR-U14 value-of-information / urgency.

A cell should spend stale-prior evidence only when the expected value of resolving inherited-state validity justifies the adaptive resource cost.

IMPORTANT IDENTIFIABILITY LIMIT
H6 assumes local consequence can tell whether a small prior-directed move was helpful or harmful.

That remains synthetic.

Real Yggdrasil still lacks a demonstrated:
target-free local semantic / causal consequence signal.

Therefore H6 supports an architecture conditional on local consequence credit.

It does NOT close the real-signal bridge.

DESIGN PRINCIPLE
Maintain conceptually separate state for:

FAST ROLE
current reversible function.

INHERITED PRIOR
slow developmental bias.

EXPRESSION TRUST
whether inherited prior should influence phenotype now.

WRITE CONFIDENCE
whether repeated useful adaptation should enter slow state.

STALE-PRIOR CONFIDENCE
whether inherited information has remained harmful long enough to be rewritten.

These may share inputs,
but they should not be collapsed into one scalar.

EMERGING MEMORY RULE
Short contradiction:

suppress expression
+
preserve heredity.

Persistent contradiction:

suppress expression first
+
rewrite heredity later.

Return before rewrite:

old prior becomes useful again.

Return after rewrite:

fast suppression protects behavior while slow state reconsolidates.

RELATION TO H5
H5 solved:

WHEN MAY USEFUL FAST ADAPTATION WRITE SLOW STATE?

H6 adds:

WHEN SHOULD OLD SLOW STATE STOP CONTROLLING FAST BEHAVIOR?

and

WHEN SHOULD OLD SLOW STATE ITSELF BE REPLACED?

The answer supported by this synthetic benchmark is:

not at the same time.

DECISION
AR-H6 is POSITIVE as a synthetic architectural result.

Supported:
- fast inherited-prior suppression can preserve functional reversibility;
- slow rewrite can be gated by a longer stale-evidence timescale;
- brief contradiction can leave slow memory intact;
- persistent contradiction can progressively reconsolidate heredity;
- preserving old memory and consolidating new memory have a measurable tradeoff.

Not demonstrated:
- real Yggdrasil stale-prior consequence;
- optimal thresholds;
- optimal number of memory timescales;
- bounded implementation cost;
- interaction with spatial lineage;
- multi-regime memory capacity;
- catastrophic interference limits.

CLEAN SCIENTIFIC PAUSING POINT
H5 + H6 now give a coherent first-order slow-memory architecture:

FAST LOCAL ADAPTATION
->
PERSISTENCE-GATED WRITE
->
FAST STALE-PRIOR SUPPRESSION
->
SLOW PERSISTENCE-GATED REWRITE.

The next inheritance experiment should not merely extend duration sweeps.

A useful next frontier is:

AR-H7 — BOUNDED MULTI-REGIME RECONSOLIDATION / INTERFERENCE

Question:
with a very small slow-state budget,
can the organism retain more than one recurring developmental prior without:
- assigning explicit semantic regime IDs;
- growing one memory slot per environment;
- or catastrophically overwriting older useful structure?

Parallel:
AR-U15 — learned local value-of-information.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
lineages_per_seed = 1000
confirmation_seeds = 24
warm_A_episodes = 120
B1_durations = 20,50,100,160
brief_A_return_episodes = 20
B2_episodes = 80
final_A_episodes = 60
