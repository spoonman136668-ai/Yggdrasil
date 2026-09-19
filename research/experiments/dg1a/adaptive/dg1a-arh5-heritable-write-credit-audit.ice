TITLE: DG-1A-AR-H5 — Heritable Write Credit / Persistence Without Semantic Oracle
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-INCOMPLETE SLOW-WRITE AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh4-temporary-repair-inheritance-audit.ice

PURPOSE
Remove H4's semantic/persistence oracle.

Question:
Can the slow heritable layer decide WHEN to begin writing a developmental bias using only:
- local action identity;
- repeated local causal consequence;
- temporal consistency / eligibility;

without being told:
- "this is repair";
- "this is a permanent niche";
- or the duration of the event in advance?

BOUNDARY
This is synthetic.

It does not:
- implement a Yggdrasil micro-genome;
- modify global shared network weights;
- add semantic repair labels to the slow layer;
- alter or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TOY
Independent local lineages:
1000

Fast role state:
4 bounded dimensions.

Slow inherited prior:
4 bounded dimensions.

Baseline regime A:
[0.25, 0.45, 0.25, 0.35]

Changed regime B:
[0.20, 0.25, 0.80, 0.15]

Fast evidence noise:
sigma = 0.16

Fast role update:
eta = 0.14

Role-state turnover:
every 10 episodes,
fast role is reconstructed from slow prior plus small noise.

This makes slow state useful only if it captures persistent information.

LOCAL CONSEQUENCE
Each fast role update receives only a noisy local scalar consequence comparison:

benefit =
loss_before_action
-
loss_after_action

Measurement noise:
sigma = 0.003

The write mechanism does NOT receive the regime label.

CONTROL A — NO SLOW WRITE
Slow prior remains fixed.

CONTROL B — IMMEDIATE BENEFIT WRITE
Every fast action whose measured local consequence improves is allowed to write slow state immediately.

This is a permissive control.

CONTROL C — CAUSAL ELIGIBILITY / DIRECTION-CONSISTENCY GATE
Maintain a bounded vector eligibility trace:

E_t =
decay * E_(t-1)
+
(1-decay)
*
sign(measured_benefit)
*
fast_action_delta

Also maintain a decaying mean action magnitude.

Compute:

PersistenceMagnitude =
RMS(E)

DirectionalCoherence =
RMS(E)
/
decaying_action_magnitude

Slow write gate is high only when BOTH:
- the credited action direction has persisted strongly enough;
- recent credited actions are directionally coherent.

Then:

slow_prior
moves slowly toward
current fast role state.

No event timer is supplied.

PRIMARY SYNTHETIC WORKING POINT
Exploratory values:

eligibility decay:
0.98

persistence magnitude threshold:
0.010

magnitude transition scale:
0.001

directional coherence threshold:
0.40

coherence transition scale:
0.05

slow write rate:
0.015

These are synthetic discriminating values only.

Do not freeze them for Yggdrasil.

EVENT DURATIONS
Changed regime B persists for:

20
50
100
150

episodes,

then returns to A.

CONFIRMATION
8 matched seeds per duration.

1000 lineages per seed.

RESULTS

CONTROL A — NO SLOW WRITE

D=20
changed-regime mean loss:
0.037077

late-20 loss:
0.037077

first-50 post-return loss:
0.001202

slow-prior distance from A at event end:
0.004705

D=50
changed loss:
0.037047

late-20:
0.036998

post50:
0.001203

D=100
changed:
0.037050

late-20:
0.037046

post50:
0.001197

D=150
changed:
0.037048

late-20:
0.037038

post50:
0.001206

Interpretation:
perfect preservation,
no persistent adaptation.

CONTROL B — IMMEDIATE BENEFIT WRITE

MAINTENANCE WRITE ACTIVITY
mean write eligibility before event:
0.48445

This is the key failure:
nearly half of noisy ordinary fast actions are judged locally beneficial and immediately alter slow state.

D=20

changed loss:
0.034795

late-20:
0.034795

post50:
0.001456

slow-prior distance from A:
0.027217

distance from B:
0.284081

D=50

changed:
0.030873

late-20:
0.027054

post50:
0.002431

g distance A:
0.061231

g distance B:
0.249530

D=100

changed:
0.025750

late-20:
0.018257

post50:
0.004914

g distance A:
0.107968

g distance B:
0.202654

D=150

changed:
0.021891

late-20:
0.012672

post50:
0.007716

g distance A:
0.144215

g distance B:
0.166394

PRIMARY NEGATIVE
Immediate local usefulness is NOT sufficient evidence for heritable write.

Noisy maintenance contains many individually useful fast corrections.

If every useful fast correction enters slow state:
transient/noisy behavior becomes geneticized.

CONTROL C — CAUSAL ELIGIBILITY / DIRECTION CONSISTENCY

MAINTENANCE
mean slow-write gate before event:
approximately 0.000005

This is effectively closed.

D=20

changed loss:
0.037068

late-20:
0.037068

post50:
0.001202

slow-prior distance from A:
0.004722

distance from B:
0.309951

mean write gate during event:
0.004748

Interpretation:
the 20-episode transient is almost completely filtered from heredity.

D=50

changed:
0.035753

late-20:
0.033927

post50:
0.001606

g distance A:
0.032824

g distance B:
0.277867

mean write gate:
0.275523

Interpretation:
persistent same-direction usefulness begins opening slow write.

D=100

changed:
0.029378

late-20:
0.018765

post50:
0.005512

g distance A:
0.111748

g distance B:
0.198849

mean write gate:
0.584169

Interpretation:
slow prior now captures substantial persistent information.

D=150

changed:
0.023864

late-20:
0.011043

post50:
0.010216

g distance A:
0.156987

g distance B:
0.153640

mean write gate:
0.625145

Interpretation:
long-lived regime strongly enters slow state.

PRIMARY POSITIVE
A semantic-free temporal causal-credit trace can distinguish:

many short/noisy useful fast corrections

from

a persistent coherent direction of useful adaptation.

This is the desired bridge from:
AR-U causal credit
to
AR-H slow inheritance.

The mechanism does not need to know:
repair,
season,
niche,
or event duration.

It asks only:

HAVE USEFUL LOCAL ACTIONS KEPT POINTING IN THE SAME DIRECTION FOR LONG ENOUGH?

H4 ORACLE REPLACEMENT
H4 used an explicit 50-episode persistence holdoff as a discriminating control.

H5 shows that an action-tagged consequence trace can create similar qualitative selectivity without receiving a regime-change timer.

Short event:
write remains closed.

Persistent event:
write opens progressively.

This is a meaningful architectural improvement.

IMPORTANT INCOMPLETE RESULT
H5 does NOT solve slow-state erasure.

Once the slow prior has substantially moved toward regime B,
returning to A produces a post-event hangover.

For example:

D=150

no-write post50:
0.001206

immediate-write post50:
0.007716

eligibility-write post50:
0.010216

The eligibility candidate wrote more selectively,
but once its persistence criterion was satisfied,
it stored a relatively strong B prior.

Thus:

CONSERVATIVE WRITE
does not automatically imply
FAST SAFE ERASE.

WRITE / ERASE ASYMMETRY
The next slow-state problem is now explicit.

WRITE QUESTION:
has useful evidence persisted long enough to justify storing it?

ERASE QUESTION:
has the inherited bias become stale enough to suppress or forget?

These need not use the same time constant.

Using one symmetric slow rule for both directions creates avoidable hysteresis.

EXPLORATORY FORGETTING NEGATIVE
A small exploratory sweep tried faster relaxation toward a shared neutral prior under local contradiction.

It reduced some long-event hangover,
but also changed transient adaptation and depended on where the chosen shared prior lay relative to the regimes.

Therefore:
"forget toward a fixed neutral vector"
is not yet a general solution.

Do not promote it.

DESIGN PRINCIPLE
The slow layer should likely maintain at least conceptually separate evidence for:

WRITE CONFIDENCE

and

STALE-PRIOR CONFIDENCE.

Potential architecture:

FAST ROLE
responds immediately to local utility.

WRITE ELIGIBILITY
accumulates repeated useful same-direction action credit.

SLOW PRIOR
changes only after write eligibility matures.

STALE-PRIOR EVIDENCE
can suppress inherited influence before full slow-state rewrite completes.

This would allow:
behavioral override first,
genetic/slow erasure later.

RELATION TO H3
H3 already showed:
current local utility should override inherited bias in fast role expression.

Therefore post-event functional recovery does not require immediate destruction of the old slow state.

This suggests a safer ordering:

1.
contradictory local evidence suppresses inherited influence quickly;

2.
if contradiction persists,
slow state is eventually erased/re-written.

This separates:
FUNCTIONAL REVERSIBILITY
from
HERITABLE MEMORY DECAY.

RELATION TO U13
Shared novelty/confidence can potentially help answer:

"should I trust the inherited prior right now?"

while H5 eligibility answers:

"should this repeated useful direction be stored slowly?"

Do not collapse those into one scalar.

NEXT
AR-H6 — STALE-PRIOR SUPPRESSION VS SLOW ERASE

Test three mechanisms:

A.
symmetric slow write/erase

B.
fast suppression of inherited influence
+
slow state unchanged

C.
fast suppression
+
separate persistence-gated slow erase/rewrite.

Desired result:

short contradiction:
fast behavior adapts,
old prior survives.

persistent contradiction:
old prior is eventually replaced.

return to familiar regime before slow erase:
old prior becomes useful again.

This would give Yggdrasil:
reversible phenotype
+
conservative hereditary memory.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
lineages_per_seed = 1000
confirmation_seeds = 8
event_durations = 20,50,100,150
