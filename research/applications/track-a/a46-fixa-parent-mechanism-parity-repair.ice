TITLE: YGGDRASIL A46-FIXA / T9D-FIXA — Parent-Mechanism Parity Repair
DATE: 2026-09-22
STATUS: PREREGISTERED IMPLEMENTATION-CONFORMANCE REPAIR / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T9D-FIXA / APPLICATION-A
ORIGINAL EXPERIMENT: A46 / T9D
ORIGINAL F46: 80c1673f5fccfe55e98e85a2dad8453b6ad3291e
DEFECT RECORD: 9a9dbc4bb5711c3156ca22efa0dd878554226319
REPAIRED COMMON-RANDOM DIAGNOSTIC: 3a8a47cf077bf84cc1a050bddb2e06e1800bff47
BRANCH: dg1a-ar

PURPOSE

Repair one implementation-conformance defect
in the frozen A46 treatment
without changing the A46 scientific design.

The original A46 preregistration
remains the scientific specification.

All original:

G5 equations;

world families;

metrics;

information-gain rules;

qualification rules;

safety boundaries;

and RNG identities

remain unchanged.

DEFECT

F46 G5_REENTRY
did not enter all A45 ECHO_PHASE
parent-mechanism branches.

Therefore G5 treatment lost:

challenge cooperative echo defense;

support-gated active recruitment.

FIXA REPAIR

Restore G5_REENTRY
to the ECHO_PHASE parent behavior
everywhere outside
the explicit G5 refractory action.

Exactly four source-pattern classes
may change.

1. CHALLENGE Q_EFF DISPATCH

FROM:

elif kind=='ECHO_PHASE'
and mode=='CHALLENGE'

TO:

elif kind in
('ECHO_PHASE','G5_REENTRY')
and mode=='CHALLENGE'.

2. ECHO-SPECIFIC REPORTING

Include G5_REENTRY
in the existing
ECHO_MARGIN / ECHO_PHASE
diagnostic kind set.

3. SUPPORT-FIELD GATING

Both support-margin-field
gated expressions
must include G5_REENTRY.

4. ACTIVE SUPPORT RECRUITMENT

The existing
PHASE_SWITCH / ECHO_PHASE
active-recruitment branch
must include G5_REENTRY.

FORBIDDEN CHANGES

No change to:

arm list;

D2/D3 durations;

rho;

G5 gate;

G5 action;

G5 timing;

Q_raw timing;

M_post timing;

support/challenge classification;

recruitment equations;

cooperative radius;

echo duration;

qualification thresholds;

information-gain thresholds;

world construction;

sensor RNG;

heterogeneity RNG;

or treatment RNG identity.

RNG

Formal FIXA treatment preserves
the original A46 RNG discipline.

ECHO_PHASE controls:

YGG-A45-ARM-SEED.

G5_REENTRY treatments:

YGG-A46-ARM-SEED.

The common-random diagnostic
is not the formal FIXA primary.

PARENT PARITY GATE

Before freeze,
construct a diagnostic-only parity probe:

disable the explicit G5 action;

assign G5_REENTRY
the paired A45 ECHO_PHASE
action-random identity.

Then G5_REENTRY
must reproduce ECHO_PHASE
behavior exactly.

Observed pre-registration repair probe:

60 representative
world/arm pairs;

behavioral mismatches:

0.

This probe must remain green
on the final FIXA candidate.

REPAIR CANDIDATE IDENTITY

Current repair candidate source SHA256:

53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885.

This hash may freeze
only if duplicate mechanical sweeps
pass byte-identically.

F46A FREEZE

Let the exact repaired implementation
freeze commit be:

F46A.

No real FIXA world
may be derived before F46A exists.

SOURCE FORM

F46A may reuse
the existing verified F46 source bundle.

The F46A loader must:

verify the original F46
bundle/archive/source identities;

verify exact replacement counts;

apply only the four
authorized dispatch repairs;

verify the repaired source SHA256;

then execute.

Any mismatch fails closed.

MECHANICAL GATE

Run two complete
non-primary mechanical sweeps
from the final repair source.

They must be byte-identical
before F46A.

PRIMARY

After F46A:

derive a fresh
384-world FIXA manifest.

Bind it before
any FIXA arm execution.

Run two complete primary sweeps.

They must be byte-identical
before scientific analysis.

SCIENTIFIC INTERPRETATION

Use the original A46
information-gain and qualification rules
without modification.

The repaired primary
answers the originally intended question:

Does G5 evidence-confirmed
early refractory re-entry to U

improve A45 ECHO_PHASE recovery

when every other A45 mechanism
is actually preserved?

PLAIN-SPEAK QUESTION

This is not a new experiment idea.

We wired A46 incorrectly.

FIXA puts back
the two A45 behaviors
that the treatment
was always supposed to keep.

Then we rerun
the experiment we meant to run
in the first place.

Nothing about the gate changes.

Nothing about the worlds changes.

Nothing about what counts
as success changes.

Only the broken inheritance
gets repaired.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F46A MECHANICAL GATE / EXACT REPAIR IDENTITY

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F46A
AND BEFORE ANY A46-FIXA SCIENTIFIC OUTCOME.

REPAIRED SOURCE

Bytes:
75238.

SHA256:
53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885

The repaired source differs from F46
only in the four authorized dispatch classes:

CHALLENGE Q_eff dispatch;

echo-specific reporting dispatch;

two support-field gated expressions;

active support-recruitment dispatch.

PARENT PARITY

With explicit G5 action disabled
and G5_REENTRY assigned
the paired A45 ECHO_PHASE action-random identity:

representative comparisons:
60.

Behavioral mismatches:
0.

MECHANICAL VALIDATION

Mechanical seed:
MECHANICAL-A46-FIXA-CANDIDATE.

Complete sweeps:
2.

Worlds per sweep:
384.

Arms:
4.

Output bytes per sweep:
44154.

Output SHA256:
aeb98a67922ee305ce23dd27e8135a537440f6df65c920dee543b7cb198fa0f9

BYTE IDENTICAL:
true.

stderr:
empty for both sweeps.

All executable pre-primary integrity probes:
PASS.

No mechanical-world population outcome
is used as scientific evidence.

F46A SOURCE FORM

F46A will reuse
the existing verified F46 source bundle:

base64 SHA256:
b6edfab88e74753d5d32c113ccee30941ce3421f9a15dc38664d25e214479a5b

gzip SHA256:
4e0d2b5ded1f71f55cf3e94652d52224c3bae10bfe9e308a6e101de44f4037f3

F46 source SHA256:
efee5637a1ba709b5299199489f02988517abc49392788b72ea25b295119fcec

The F46A loader must:

verify those three original identities;

verify exact authorized replacement counts;

apply only the four preregistered dispatch repairs;

verify repaired source SHA256:

53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885;

then execute.

Any mismatch fails closed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-F46A PRIMARY MANIFEST BINDING

DATE:
2026-09-22.

F46A:
6a52b0ed4372371727649e4f14f5967d28345551

REPAIRED SOURCE SHA256:
53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885

PRIMARY SEED:
A46-FIXA-F46A-6a52b0ed4372371727649e4f14f5967d28345551-PRIMARY

WORLD COUNT:
384.

WORLD SHAPE:
48 contexts x 8 replicas.

PRIMARY WORLD MANIFEST SHA256:
faba5e274d757b6712467b725f4353003966773e6a4eef5a0412837ee570ca90

STATUS:
BOUND AFTER F46A
AND BEFORE ANY A46-FIXA PRIMARY ARM EXECUTION.

The formal repaired primary retains
the original A46 RNG discipline:

ECHO_PHASE controls:
YGG-A45-ARM-SEED.

G5_REENTRY treatments:
YGG-A46-ARM-SEED.

No repaired-arm scientific outcome,
qualification result,
or population comparison
was observed before this binding.

Two complete repaired primary sweeps
must be byte-identical
before scientific analysis.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


A46-FIXA PRIMARY CLOSURE

DATE:
2026-09-22.

F46A:
6a52b0ed4372371727649e4f14f5967d28345551

MANIFEST-BINDING COMMIT:
3992f3efd382de09a913ff38160647903e7b6103

REPAIRED SOURCE SHA256:
53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885

PRIMARY SEED:
A46-FIXA-F46A-6a52b0ed4372371727649e4f14f5967d28345551-PRIMARY

PRIMARY WORLD MANIFEST SHA256:
faba5e274d757b6712467b725f4353003966773e6a4eef5a0412837ee570ca90

PRIMARY OUTPUT SHA256:
d66b8475be964cab80da82af3c868fec98c9015d66d9fd374d609e02e670de12

PRIMARY RUNS:
2.

PRIMARY OUTPUT BYTES:
44338.

BYTE IDENTICAL:
true.

stderr:
empty for both runs.

All executable integrity probes:
PASS.

SCIENTIFIC STATUS

D2_G5_REENTRY:
A46_RECOVERY_INFORMATION_GAIN = FALSE.
NOT QUALIFIED.

D3_G5_REENTRY:
A46_RECOVERY_INFORMATION_GAIN = TRUE.
NOT QUALIFIED.

Therefore the repaired intended A46 question
has positive information gain in D3
but does not reach full qualification.

D2 TECHNICAL EVIDENCE

D2 ECHO_PHASE parent:

aggregate service 236606;
harm rate 15.36%;
overall oscillation 7.29%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 0.00%;
reversal acquisition 88.28%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 31.23%;
mean unresolved episode duration 4.148 epochs;
mean favored-majority recovery latency 5.148 epochs;
median recovery latency 4 epochs;
mean refractory fraction
across recovery steps 1-3 32.58%;
favored-to-unresolved transitions 66;
recovery-never count 8;
same-side short-cycle chatter 644.

D2 repaired G5_REENTRY:

aggregate service 237710;
harm rate 15.62%;
overall oscillation 7.55%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 0.00%;
reversal acquisition 88.28%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 35.32%;
mean unresolved episode duration 3.402 epochs;
mean favored-majority recovery latency 4.250 epochs;
median recovery latency 3 epochs;
mean refractory fraction
across recovery steps 1-3 24.31%;
favored-to-unresolved transitions 68;
recovery-never count 8;
same-side short-cycle chatter 779.

D2 causal deltas:

mean unresolved episode:
-17.98%;

mean recovery latency:
-0.898 epoch;

mean refractory fraction steps 1-3:
-25.41%;

aggregate service:
+1104
(+0.47%);

5:3 epoch-3 core persistence:
+4.10 percentage points;

6:2 oscillator delta:
0.

D2 misses
the original A46 information-gain thresholds
of:

at least 25%
unresolved-duration reduction;

and at least 1 epoch
mean recovery-latency reduction.

D3 TECHNICAL EVIDENCE

D3 ECHO_PHASE parent:

aggregate service 232105;
harm rate 15.62%;
overall oscillation 6.77%;
biased-periodic oscillation 46.88%;
5:3 oscillation 93.75%;
6:2 oscillation 0.00%;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 29.24%;
mean unresolved episode duration 5.408 epochs;
mean favored-majority recovery latency 6.506 epochs;
median recovery latency 5 epochs;
mean refractory fraction
across recovery steps 1-3 45.71%;
favored-to-unresolved transitions 61;
recovery-never count 9;
same-side short-cycle chatter 0.

D3 repaired G5_REENTRY:

aggregate service 234550;
harm rate 16.15%;
overall oscillation 7.29%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
median old-majority loss 3 epochs;
5:3 epoch-3 core persistence 32.45%;
mean unresolved episode duration 3.975 epochs;
mean favored-majority recovery latency 5.034 epochs;
median recovery latency 4 epochs;
mean refractory fraction
across recovery steps 1-3 28.62%;
favored-to-unresolved transitions 64;
recovery-never count 8;
same-side short-cycle chatter 298.

D3 causal deltas:

mean unresolved episode:
-26.50%;

mean recovery latency:
-1.472 epochs;

mean refractory fraction steps 1-3:
-37.39%;

aggregate service:
+2445
(+1.05%);

5:3 epoch-3 core persistence:
+3.21 percentage points;

recovery-never:
9 -> 8;

6:2 oscillator delta:
0.

D3 therefore satisfies
the original A46 recovery-information-gain rule.

G5 ACTIVITY / SAFETY

Repaired G5 remains active.

D2 G5:

5:3 recovery gate rate
approximately 30.24%;

balanced gate exposure
approximately 3.39%.

D3 G5:

5:3 recovery gate rate
approximately 34.51%;

balanced gate exposure
approximately 6.65%.

For both D2 and D3:

direct favored-to-adverse
majority flips in 5:3:

0.

Adverse-majority entries:

0.

Adverse-majority epochs:

0.

Old-side G5 fires
during the first four epochs
after true reversal:

0.

Thus repaired G5
does not gain recovery
by creating wrong-side capture
or by reactivating
the obsolete side after genuine reversal.

WHY NO ARM QUALIFIES

The repair confirms
that refractory debt
is a real recovery bottleneck.

But G5 does not solve
the inherited hard macro phenotype.

D2 5:3 oscillation remains:

100.00%.

D3 5:3 oscillation moves
from 93.75%
to 100.00%
in the independent treatment stream.

Neither arm approaches
the frozen A46 qualification ceiling
of 25% 5:3 oscillation.

Favored-to-unresolved transition counts
are not reduced by 50%.

Unresolved duration
is not reduced by 50%.

Median favored-majority recovery
remains above 2 epochs.

Therefore:

D2_G5_REENTRY NOT QUALIFIED.

D3_G5_REENTRY NOT QUALIFIED.

CHATTER COST

Recovery acceleration is not free.

D2 same-side short-cycle chatter:

644 -> 779
(+20.96%).

D3:

0 -> 298.

This reinforces the repaired
common-random diagnosis:

the G5 evidence signal is useful,

but immediate re-entry to U
is a stronger plasticity action
than necessary.

CAUSAL INTERPRETATION

The A46 parent-mechanism defect
materially invalidated
the original frozen G5 treatment comparison.

A46-FIXA repairs that defect
and answers the intended question.

The repaired result is:

refractory availability
really is part
of the post-disturbance recovery bottleneck.

In D3,
the preregistered information-gain threshold
is crossed.

The organism releases refractory debt faster,
recovers favored majority sooner,
preserves the already-solved 6:2 regime,
does not enter the wrong side,
and remains reversible.

However immediate re-entry
does not solve the full 5:3 phenotype
and increases local short-cycle behavior.

Therefore the next justified experiment
is not a stronger release gate.

It is a smaller action:

one-tick refractory acceleration
on the first locked epoch,

with the cell remaining refractory
for that current epoch.

The previously proposed comparison remains justified:

SUPPORT-only acceleration
as the causal control;

SUPPORT + M_post > 0
as the evidence-aligned treatment.

A47 must use common stateless
action-random draws
to isolate this smaller timer action.

PLAIN-SPEAK INTERPRETATION

The wiring repair changed the conclusion.

When A46 is actually given
the full A45 organism
it was supposed to inherit,
early re-entry really does help recovery.

With D3,
it clears the frozen
information-gain bar.

The system gets out
of its unresolved state
about one and a half epochs sooner,
and much less of the population
is stuck serving refractory time.

It still does not
jump onto the wrong side.

It still accepts
a real environmental reversal.

And the easier 6:2 problem
stays solved.

But opening the bench gate completely
also makes more cells
cycle through short commitments.

And the hardest 5:3 worlds
still lose majority into uncertainty
often enough to fail qualification.

So the direction is now much firmer:

the waiting rule
really is slowing recovery.

But we do not need
to abolish the waiting rule.

The next test should make it
one beat more flexible.

A cell still sits out
the current turn.

Good local evidence
can only remove one future turn
from its remaining wait.

That is A47.

NORTH-STAR IMPLICATION

A46-FIXA provides
the first repaired evidence
that developmental plasticity timing
can be locally evidence-sensitive
without requiring:

a central controller;

a global phase signal;

or wrong-side recommitment.

The remaining task
is to find the smallest local adjustment
that captures the recovery benefit
without paying unnecessary chatter cost.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
