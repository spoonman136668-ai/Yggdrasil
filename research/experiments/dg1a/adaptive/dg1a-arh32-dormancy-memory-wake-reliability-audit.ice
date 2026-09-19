TITLE: DG-1A-AR-H32 — Dormancy Memory Retention / Wake Reliability Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE COMPACT-DORMANCY-STATE RESULT + CONTEXT-FIT REQUIREMENT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh31-recursive-lineage-growth-resource-envelope-audit.ice

PURPOSE
H31 showed that reversible dormancy can reduce permanently active structure while preserving rapid regenerative capability.

H32 asks:

WHAT STATE SHOULD A DORMANT CELL RETAIN?

Too much retained state:
- costs memory;
- can preserve stale fast phenotype.

Too little:
- forces relearning after every wake.

BOUNDARY
This is synthetic.

It does not:
- freeze a production dormant-state layout;
- prove current Yggdrasil regimes lie on the tested rank-2 manifold;
- establish real memory bytes;
- freeze wake thresholds;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

DEVELOPMENTAL REGIMES
Four-dimensional synthetic developmental state.

Three recurring regime means:

A
[0.25, 0.45, 0.25, 0.35]

B
[0.20, 0.25, 0.80, 0.15]

C
[0.65, 0.55, 0.30, 0.65].

The three means occupy an affine rank-2 structure,
matching the H7-style bounded inherited manifold.

FAST LOCAL PHENOTYPE
Before sleep,
the active cell contains:

regime mean
+
small local fast offset.

Local offset SD:
0.06.

Fast-state residual error before sleep:
approximately 0.015 per component.

SLEEP CONTEXT DYNAMICS
During dormancy,
the latent regime can change with hazard:

0.005 per sleep step.

Local fast offset also decorrelates with sleep duration.

Offset retention:

rho
=
exp(-sleep_duration / 120).

Thus:
short sleep preserves more local fast context.

Long sleep makes old fast phenotype stale even if the broad regime recurs.

WAKE EVIDENCE
At wake,
the cell receives:

2 noisy local observations.

Observation noise SD:
0.16.

Then normal active adaptation resumes with:

learning rate:
0.18

for:
20 steps.

STRATEGIES

FULL FROZEN FAST STATE
Retain old fast 4D phenotype
and directly re-express it on wake.

SLOW PRIOR ONLY
Retain only the old regime-level slow prior.

Re-express it directly.

COMPRESSED PRIOR + FIT GATE
Retain:
- two coordinates in the shared rank-2 slow manifold;
- compact fit/freshness information.

At wake:
reconstruct the slow prior.

Compare it to current local wake evidence.

Prior expression weight:

w
=
exp(
 - ||cue - prior||^2
 / (2 * 0.28^2)
).

Then:

wake_state
=
w * slow_prior
+
(1-w) * current_cue.

This is an exploratory discriminating gate.

Do not freeze:
0.28.

FULL FAST + FIT GATE
Higher-state comparator.

Apply the same wake-time fit logic
to the retained full fast state.

STATELESS
Retain no useful phenotype/prior.

Wake from the noisy current cue only.

SLEEP-DURATION SWEEP
5,000 fresh synthetic wakes per duration.

Reported:

instant wake MSE;

mean MSE over first 5 adaptation steps;

mean MSE over full 20-step reacquisition window.

DURATION = 10

probability broad regime remains unchanged:
95.42%.

FULL FAST

instant:
0.00457

first-5:
0.00345

full:
0.00282.

SLOW PRIOR

0.00730
0.00472
0.00320.

COMPRESSED + FIT

0.00453
0.00344
0.00282.

FULL + FIT

0.00306
0.00279
0.00263.

STATELESS

0.01270
0.00718
0.00400.

SHORT-SLEEP RESULT
Full fast retention is useful when dormancy is brief and context remains nearly unchanged.

Compressed prior + fit performs almost identically at the tested short duration.

DURATION = 50

regime unchanged:
79.32%.

FULL FAST first-5:
0.01034.

SLOW:
0.01067.

COMPRESSED:
0.00428.

FULL + FIT:
0.00409.

STATELESS:
0.00740.

PRIMARY CROSSOVER
By moderate sleep duration,
directly replaying frozen state becomes worse than:
using current evidence.

The fit-gated representations avoid that crossover.

DURATION = 100

regime unchanged:
65.08%.

FULL FAST

instant:
0.03257

first-5:
0.01647

full:
0.00694.

SLOW PRIOR

0.03189
0.01615
0.00684.

COMPRESSED + FIT

0.00751
0.00483
0.00326.

FULL + FIT

0.00774
0.00494
0.00330.

STATELESS

0.01285
0.00728
0.00403.

PRIMARY POSITIVE
The compact fit-gated slow prior beats:
- full frozen state;
- direct slow-prior replay;
- stateless wake.

It retains useful historical structure
without forcing that structure onto a changed context.

DURATION = 250

regime unchanged:
45.04%.

FULL FAST first-5:
0.02485.

SLOW:
0.02340.

COMPRESSED:
0.00565.

FULL + FIT:
0.00592.

STATELESS:
0.00727.

DURATION = 500

regime unchanged:
34.80%.

FULL FAST first-5:
0.02938.

SLOW:
0.02747.

COMPRESSED:
0.00607.

FULL + FIT:
0.00637.

STATELESS:
0.00726.

LONG-SLEEP RESULT
Long dormancy makes direct state replay strongly stale.

Compressed prior + fit continues to outperform stateless wake
while remaining far safer than frozen-state replay.

CONDITIONAL CONTEXT ANALYSIS
DURATION = 100.

REGIME UNCHANGED

FULL FAST instant:
0.00431.

SLOW:
0.00356.

COMPRESSED:
0.00406.

STATELESS:
0.01287.

REGIME CHANGED

FULL FAST:
0.08594.

SLOW:
0.08484.

COMPRESSED:
0.01388.

STATELESS:
0.01298.

PRIMARY FIT-CONFIDENCE RESULT
When context is unchanged,
retained prior information is highly valuable.

When context changed,
the old prior becomes approximately:

6.5x

worse than current cue if replayed directly.

The fit gate suppresses most of that stale-prior penalty.

This is the dormancy version of:
H6
and
H7.

REPEATED SLEEP / WAKE STRESS
20 sleep/wake cycles.

Each sleep:
100 steps.

Normal active adaptation:
15 steps between sleeps.

300 matched seeds.

Mean first-5 wake loss across all cycles.

FULL FAST

0.02487.

SLOW PRIOR

0.02227.

COMPRESSED + FIT

0.00644.

FULL FAST + FIT

0.00531.

STATELESS

0.00800.

Average broad-regime changes across 20 sleeps:

7.05.

PRIMARY REPEATED-CYCLE POSITIVE
A compact fit-gated prior retains most of the useful wake acceleration across repeated dormancy cycles
without carrying the high stale-state burden of direct frozen fast replay.

The full fast + fit comparator is somewhat better:

0.00531
vs
0.00644,

but retains more dormant state.

This creates a real:

DORMANT MEMORY COST
vs
WAKE PERFORMANCE

tradeoff.

ILLUSTRATIVE STATE-COST PROXY
Because the three slow regime means lie in a shared rank-2 manifold,
a dormant cell need not retain the full 4D regime vector.

A conceptual compact dormant representation can retain approximately:

2 slow-manifold coordinates

+

1 fit/freshness scalar.

This is:
3 scalar-equivalent local states
in the toy.

A full frozen representation requires at least:

4 fast phenotype coordinates

+

slow prior coordinates

+

fit metadata.

This is a STATE-COUNT PROXY ONLY.

It is not:
measured bytes
or
final implementation cost.

DORMANCY PRINCIPLE
A dormant cell should retain:

SLOW REUSABLE INFORMATION

more readily than:

FAST PHENOTYPE.

Fast phenotype should normally be:
reconstructed
or
revalidated
on wake.

CURRENT DORMANT STATE CANDIDATE
A compact dormant lineage record now plausibly contains:

SLOW PRIOR COORDINATES

+

LINEAGE / PROVENANCE

+

FIT / STALE CONFIDENCE

+

RESOURCE / ESCROW CLAIM STATE

+

OPTIONAL WAKE ELIGIBILITY.

It does NOT need to retain:

fully active fast role dynamics
at full precision indefinitely.

WAKE RULE
On wake:

CURRENT LOCAL CUE

vs

RETAINED SLOW PRIOR

->

FIT CONFIDENCE.

HIGH FIT

->

use inherited prior to accelerate reacquisition.

LOW FIT

->

suppress old prior
and
trust current evidence.

This reuses the same:
STATE
vs
AUTHORITY
separation established across H6-H29.

RELATION TO H31
H31 showed dormancy is valuable because it:
reduces active maintenance
while preserving rapid regenerative reserve.

H32 shows the reserve can remain useful without preserving:
the entire active phenotype.

That strengthens the original objective:

CAPABILITY RETENTION
WITHOUT
PERMANENT FULL ACTIVATION.

IMPORTANT LIMITATION
H32 assumes:
- a useful rank-2 shared slow manifold;
- a local wake cue;
- synthetic Euclidean fit;
- no memory bit corruption;
- no lineage mutation during sleep.

Real dormant-state retention may require different geometry.

DECISION
AR-H32 is POSITIVE.

Supported synthetically:

- full frozen fast-state replay becomes stale with sleep duration;
- stateless dormancy avoids staleness but relearns more slowly;
- compact slow prior + wake-time fit gating gives a strong middle ground;
- repeated sleep/wake cycles preserve the advantage;
- current evidence should control whether inherited dormant memory is expressed;
- dormant state can plausibly be smaller than active state.

Not demonstrated:

- final dormant-state encoding;
- real rank of Yggdrasil slow lineage state;
- hardware memory savings;
- wake signaling;
- bit-level long-term memory integrity;
- spatial coordination of many simultaneous wakes.

NEXT CLEAN QUESTION
AR-H33 — WAKE-STORM / DORMANT-POPULATION COORDINATION

Question:

What happens when a large dormant reserve receives the same wake signal?

Can local resource pricing and value-of-information prevent:
ALL DORMANT CELLS
from waking simultaneously
and recreating the H31 growth/resource spike?

Compare:

A.
broadcast wake-all;

B.
local resource-floor wake;

C.
local marginal-value wake bidding;

D.
staggered wake lease / refractory period;

E.
damage region that moves over time.

Desired:

damage
->
rapid local wake concentration.

stable unaffected tissue
->
remain dormant.

resource pressure
->
bound simultaneous wake count.

No global role histogram or central wake scheduler.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
sleep_duration_conditions = 10,50,100,250,500
wakes_per_duration = 5000
repeated_cycle_seeds = 300
repeated_cycles = 20
wake_observations = 2
wake_observation_noise_sd = 0.16
