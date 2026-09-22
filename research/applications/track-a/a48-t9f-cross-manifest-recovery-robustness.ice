TITLE: YGGDRASIL A48 / T9F — Cross-Manifest Recovery Robustness Replication
DATE: 2026-09-22
STATUS: PREREGISTERED REPLICATION / NO NEW DYNAMICS
TRACK: YGGDRASIL TRAINING T9F / APPLICATION-A
PARENT: A47 Recovery Dose-Response and Stagger
IMPLEMENTATION PARENT: F47
BRANCH: dg1a-ar

A47 CLOSURE

943f6aea84220c839af7e962dfea575df8ceb3be.

F47

284515acf6ef5d414cd91bdb352214d309f23f13.

F47 SOURCE SHA256

645b1d8b8417702fce62a6268b9ba97dd41aba21e8cb9f48ccf683f32fc6d468.

WHY A48 EXISTS

The recovery direction is consistent
but effect magnitude varies
across fresh world realizations.

Repaired A46-FIXA D3 G5_FULL:

unresolved-duration reduction:
26.50%;

mean recovery-latency improvement:
1.472 epochs.

Repaired A46 common-random diagnostic:

unresolved-duration reduction:
22.61%;

mean recovery-latency improvement:
approximately 1.125 epochs.

A47 fresh common-random primary:

unresolved-duration reduction:
18.35%;

mean recovery-latency improvement:
0.857 epoch.

All point in the same direction.

But the magnitude crosses
the preregistered 25% / 1-epoch boundary
in some world sets
and misses it in others.

Therefore another mechanism change
would be premature.

A48 estimates robustness
with the recovery mechanism frozen.

NO NEW DYNAMICS

A48 introduces:

no new state;

no new gate;

no new dose;

no new probability;

no new timer law;

no new radius;

no new recruitment rule;

no new cooperative rule.

It reuses exact F47 dynamics.

PRIMARY MECHANISM UNDER REPLICATION

G5_FULL.

Eligibility is the repaired A46/A47 G5 signal:

local SUPPORT;

M_post > 0;

Q_raw > 0.

Action:

immediate re-entry to U
exactly as F47 G5_FULL.

No direct recommitment.

No former-side recruitment bonus.

ARMS

Exactly four arms:

D2_BASE_ECHO_PHASE;
D2_G5_FULL;
D3_BASE_ECHO_PHASE;
D3_G5_FULL.

A48 does not re-estimate
the entire A47 dose curve.

A47 already established
that smaller actions trade away
recovery benefit.

A48 asks only
whether the strongest evidence-confirmed
recovery action has
a reproducible effect.

COMMON-RANDOM DESIGN

Within each D family,
BASE and G5_FULL use
the exact same inherited
A45 ECHO_PHASE stateless
action-random identity.

G5 is deterministic.

World generation,
sensor noise,
heterogeneity,
and inherited event salts
are paired.

Thus each replicate
is a common-random causal comparison.

REPLICATION COUNT

Five independent primary manifests.

Each replicate contains:

384 worlds;

48 contexts x 8 replicas;

48 cells;

48 epochs.

Total:

1920 worlds per arm
across five manifests.

REPLICATE IDENTITIES

After F48 exists,
derive exactly five fresh seeds:

A48-F48-<F48>-R1;
A48-F48-<F48>-R2;
A48-F48-<F48>-R3;
A48-F48-<F48>-R4;
A48-F48-<F48>-R5.

All five world-manifest SHA256 values
must be bound
before any A48 arm execution.

No sixth replicate
may be added after results.

F48

F48 freezes
the A48 replication driver
and the exact F47 source identity
used by that driver.

No A48 primary world
may be derived before F48.

MECHANICAL GATE

Before F48:

verify F47 source identity;

verify exactly four A48 arms;

verify common-random pairing;

run two complete
non-primary A48 mechanical sweeps
byte-identically.

The mechanical sweep may use
one fake replication seed.

No mechanical population result
is scientific evidence.

PER-REPLICATE PRIMARY METRICS

For D2 and D3 separately report:

BASE mean unresolved-episode duration;

G5 mean unresolved-episode duration;

percent reduction;

BASE mean favored-majority recovery latency;

G5 mean recovery latency;

absolute improvement;

BASE refractory fraction
across recovery steps 1-3;

G5 refractory fraction;

percent reduction;

aggregate service delta;

5:3 direct favored-to-adverse flips;

5:3 adverse-majority entries;

6:2 oscillator delta;

balanced false-majority delta;

reversal acquisition;

old-side G5 fires
during first four true-reversal epochs;

short same-side chatter rate
for BASE and G5;

absolute chatter-rate increase.

Retain inherited oscillator metrics
for reporting only.

ROBUST DIRECTIONAL RECOVERY

For a D family:

TRUE iff at least 4 of 5 replicates
show BOTH:

positive unresolved-duration reduction;

and

positive mean recovery-latency improvement.

No minimum magnitude
is required for this directional test.

STRONG REPLICATE

A replicate is STRONG iff:

unresolved-duration reduction >=25%;

and

mean recovery-latency improvement >=1.0 epoch;

and

refractory fraction steps 1-3 is lower;

and

all safety/non-regression requirements pass.

ROBUST STRONG RECOVERY

For a D family:

TRUE iff at least 3 of 5 replicates
are STRONG.

POOLED RECOVERY

Pool all five manifests
within each D family
using the same summary equations
as A47.

POOLED STRONG RECOVERY is TRUE iff:

pooled unresolved-duration reduction >=25%;

pooled recovery-latency improvement >=1.0 epoch;

pooled refractory fraction steps 1-3 is lower;

and all pooled safety/non-regression requirements pass.

SAFETY / NON-REGRESSION

Every replicate must satisfy:

5:3 direct favored-to-adverse flips = 0;

5:3 adverse-majority entries = 0;

6:2 oscillator
does not exceed paired BASE;

balanced false-majority
does not exceed paired BASE
and remains <=10%;

reversal acquisition >=80%;

aggregate service >=95%
of paired BASE;

old-side G5 fires
during first four true-reversal epochs = 0.

CHATTER CEILING

Recovery is not considered
a lockable layer
if it requires excessive local cycling.

For D3,
pooled G5 short same-side chatter rate
must remain <=1.50%.

For D2,
pooled G5 short same-side chatter rate
must remain <=3.00%.

These ceilings are fixed
before A48 execution.

They are above
the A47 observed G5_FULL rates:

D2 approximately 2.71%;

D3 approximately 0.92%;

but still bound
cross-manifest variability.

A48_RECOVERY_ROBUST

For a D family:

TRUE iff:

ROBUST_DIRECTIONAL_RECOVERY = TRUE;

and

all five replicates pass
safety/non-regression;

and

the pooled chatter ceiling passes.

A48_RECOVERY_STRONG

For a D family:

TRUE iff:

A48_RECOVERY_ROBUST = TRUE;

and either:

ROBUST_STRONG_RECOVERY = TRUE;

or

POOLED_STRONG_RECOVERY = TRUE.

RECOVERY-LAYER DECISION

D3 is the primary recovery-layer decision arm
because the longer D3 refractory duration
showed the clearest repaired A46 effect.

If D3 A48_RECOVERY_STRONG = TRUE:

lock repaired G5_FULL
as the recovery-layer candidate.

Stop refractory-mechanism tuning.

Return to the macro
population-organization / oscillation track.

If D3 A48_RECOVERY_ROBUST = TRUE
but A48_RECOVERY_STRONG = FALSE:

record G5_FULL
as a reproducible moderate recovery aid,

but do not add more refractory complexity.

Park the recovery layer
and return to the macro
population-organization track.

If D3 A48_RECOVERY_ROBUST = FALSE:

do not carry G5_FULL forward
as a default recovery mechanism.

Return to the macro track
with A45 ECHO_PHASE
as the recovery baseline.

D2 is secondary evidence.

A48 does not require
the same magnitude
in D2 and D3
because their fixed refractory durations differ.

OUT-OF-SCOPE

A48 does not attempt
to lower the inherited 5:3 oscillator score.

The 5:3 oscillator metric
is reported for lineage continuity only.

A48 does not retune
the recovery layer
based on replicate outcomes.

A48 does not compose
A41/A42 macro mechanisms.

That work begins only
after A48 closes.

INTEGRITY PROBES

P1:
F47 source SHA256 exact.

P2:
exactly four arms.

P3:
five and only five primary replicate seeds.

P4:
384 worlds per replicate.

P5:
48 contexts x 8 replicas.

P6:
48 cells.

P7:
48 epochs.

P8:
BASE dynamics equal F47 BASE.

P9:
G5_FULL dynamics equal F47 G5_FULL.

P10:
paired common-random inherited action identity.

P11:
G5 deterministic.

P12:
no new dynamics.

P13:
no new thresholds inside cell dynamics.

P14:
no new probability inside cell dynamics.

P15:
no new radius.

P16:
no future evidence.

P17:
no global phase.

P18:
no majority label enters dynamics.

P19:
two mechanical sweeps byte-identical before F48.

P20:
F48 exists before replicate worlds are derived.

P21:
all five manifest hashes bound
before primary execution.

P22:
two complete five-replicate primary sweeps
byte-identical.

PLAIN-SPEAK QUESTION

We already know
the recovery rule can help.

The problem is that
one fresh set of worlds says:

it helps a lot.

Another says:

it helps moderately.

So A48 does not
change the organism again.

It asks whether
the same recovery rule
keeps helping
when we roll five completely fresh
sets of worlds.

If it helps reliably
and strongly enough,

we lock the recovery layer
and stop touching it.

If it helps reliably
but only moderately,

we record that honestly,
stop tuning it,
and move on.

If it does not
help reliably,

we drop it
as a default mechanism.

Either way,
A48 ends the current
refractory-recovery tuning loop.

Then the research returns
to the bigger question:

how a recovered core
controls the surrounding population
without a central judge.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F48 MECHANICAL GATE / REPLICATION-DRIVER IDENTITY

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F48
AND BEFORE ANY A48 PRIMARY WORLD EXISTS.

A48 DRIVER SOURCE

Bytes:
7554.

SHA256:
fba47337867b8b90a69324a45c3d70edeb6e790d62fb25bb4c29224449023444

The driver introduces
replication bookkeeping only.

It imports
the exact F47 loader
and reuses these four frozen arms:

D2_BASE_ECHO_PHASE;
D2_G5_FULL;
D3_BASE_ECHO_PHASE;
D3_G5_FULL.

No cell-state dynamics
are implemented in the A48 driver.

F47 SOURCE IDENTITY

Required parent source SHA256:

645b1d8b8417702fce62a6268b9ba97dd41aba21e8cb9f48ccf683f32fc6d468

The F47 loader remains fail-closed
on its own source-bundle identities.

MECHANICAL VALIDATION

Mechanical seed:

MECHANICAL-A48-F48-CANDIDATE

Complete sweeps:

2.

Worlds per sweep:

384.

Arms per sweep:

4.

Output bytes per sweep:

2662.

Output SHA256:

f753407c39d99bca40ef1edd8fbc9ab340121a3e7f3caa7ac30aac2a107fc4ec

BYTE IDENTICAL:

true.

stderr:

empty for both sweeps.

All executable pre-primary
driver integrity probes:

PASS.

No mechanical-world population outcome
is used as scientific evidence.

F48 FREEZE FORM

F48 will freeze
the exact A48 driver source above.

No new F47 source copy
is created.

The driver must import
the existing F47 loader
from the same repository directory.

Any F47 identity failure
therefore fails A48 closed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-F48 FIVE-MANIFEST PRIMARY BINDING

DATE:
2026-09-22.

F48:
430f4ec780d822829cfb058e8c1fa32608134d73

F47 PARENT SOURCE SHA256:
645b1d8b8417702fce62a6268b9ba97dd41aba21e8cb9f48ccf683f32fc6d468

A48 DRIVER SHA256:
fba47337867b8b90a69324a45c3d70edeb6e790d62fb25bb4c29224449023444

REPLICATE COUNT:
5.

WORLD COUNT PER REPLICATE:
384.

TOTAL WORLD COUNT PER ARM:
1920.

REPLICATE 1

SEED:
A48-F48-430f4ec780d822829cfb058e8c1fa32608134d73-R1

MANIFEST SHA256:
82eed03d3a4473f95d51c703c5f0bc7f7c54af27bfca470aaffb11b0ea63d845

REPLICATE 2

SEED:
A48-F48-430f4ec780d822829cfb058e8c1fa32608134d73-R2

MANIFEST SHA256:
e74cff17b55fe6aab9297fad02f1f71503fc6583f70acd301e77921dc9e8c480

REPLICATE 3

SEED:
A48-F48-430f4ec780d822829cfb058e8c1fa32608134d73-R3

MANIFEST SHA256:
31c44cb6c8478f6a2226cdf2f0cfc52d817fcfb90a0db3a6fbf97aeafb1ccd54

REPLICATE 4

SEED:
A48-F48-430f4ec780d822829cfb058e8c1fa32608134d73-R4

MANIFEST SHA256:
5b7b1984034a3647369f70f045d0d4e9d73fe1e28c7f0d9fef7a24c0669c8980

REPLICATE 5

SEED:
A48-F48-430f4ec780d822829cfb058e8c1fa32608134d73-R5

MANIFEST SHA256:
7e9bbadcc3313c29033c2cc291fcd34b58fe736d77eb5b128f230bceeafd8577

STATUS:
BOUND AFTER F48
AND BEFORE ANY A48 PRIMARY ARM EXECUTION.

No A48 replicate population outcome,
effect-size estimate,
robustness result,
pooled result,
or recovery-layer decision
was observed before this binding.

Two complete
five-replicate primary sweeps
must be byte-identical
before scientific analysis.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
