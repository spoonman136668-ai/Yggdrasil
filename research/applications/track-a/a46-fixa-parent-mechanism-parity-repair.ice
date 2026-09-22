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
