TITLE: YGGDRASIL A46 POST-CLOSURE DEFECT — G5 PARENT-MECHANISM PARITY FAILURE
DATE: 2026-09-22
STATUS: MATERIAL IMPLEMENTATION DEFECT / A46 TREATMENT SCIENCE INVALIDATED
TRACK: YGGDRASIL TRAINING T9D / APPLICATION-A
F46: 80c1673f5fccfe55e98e85a2dad8453b6ad3291e
A46 PRIMARY CLOSURE: 2f8ebeeeef2ad0987b7f18f371533b65c9c48a5c
BRANCH: dg1a-ar

PURPOSE

Record a post-closure implementation defect
found before successor-mechanism freeze.

This note does not rewrite F46.

It preserves the frozen execution
as provenance
while invalidating causal interpretation
of the G5 treatment arm
against the preregistered A46 question.

PREREGISTERED REQUIREMENT

A46 states:

use A45 ECHO_PHASE unchanged
except for the explicit
G5 refractory re-entry rule.

Therefore G5_REENTRY must retain:

A45 one-epoch cooperative echo
during local CHALLENGE;

and

A44/A45 support-gated
active margin recruitment
during local SUPPORT.

DEFECT IN F46

F46 encodes arm kinds:

ECHO_PHASE;

G5_REENTRY.

But several parent behaviors
are dispatched only when:

kind == ECHO_PHASE.

The frozen G5_REENTRY treatment
therefore fails to enter
those parent code paths.

Specifically:

1. CHALLENGE COOPERATIVE DEFENSE

The cooperative q_eff term
is applied only for ECHO_PHASE.

G5_REENTRY therefore receives
no A45 echo-phase cooperative defense.

2. ECHO-SPECIFIC REPORTING

G5_REENTRY is excluded
from the echo-specific
cooperative reporting branch.

3. SUPPORT-GATED RECRUITMENT FIELD

The support-margin field
is gated only for
PHASE_SWITCH / ECHO_PHASE.

G5_REENTRY therefore does not receive
the A44/A45 support-gated
active recruitment field.

4. ACTIVE SUPPORT RECRUITMENT

The active recruitment increment
is applied only for
PHASE_SWITCH / ECHO_PHASE.

G5_REENTRY therefore loses
the A44/A45 support-growth behavior.

MATERIALITY

These are not diagnostic-only differences.

They alter the organism dynamics.

Therefore the frozen G5_REENTRY arm
does NOT test:

A45 ECHO_PHASE
plus G5 refractory re-entry.

It tests a different,
weaker organism
plus G5 refractory re-entry.

Consequently:

A46_RECOVERY_INFORMATION_GAIN = FALSE

remains the literal frozen output
of F46,

but the treatment result
cannot answer
the preregistered A46 causal question.

A46 G5_REENTRY qualification
is scientifically INVALID,
not merely negative.

The A45 ECHO_PHASE control
remains valid.

The world manifest,
determinism proof,
and execution hashes
remain valid as artifact evidence.

They do not repair
the treatment-conformance failure.

COMMON-RANDOM NOTE

The post-closure common-random note:

bf17b3c4f80f5ba61c5c9891d39d879ddde5952a

was generated from the A46 lineage
before this parent-dispatch defect
was recognized.

Its causal conclusion
must not be used
to select the successor
until repeated
with the repaired parent mechanics.

REPAIR SCOPE

A46-FIXA is authorized
as an objective conformance repair.

No scientific parameter changes.

No G5 equation changes.

No threshold changes.

No timer changes.

No world-family changes.

No qualification changes.

Only restore G5_REENTRY
to the parent ECHO_PHASE behavior
everywhere outside
the explicit refractory action.

Required repaired dispatch:

G5_REENTRY must participate
in the same CHALLENGE q_eff branch
as ECHO_PHASE.

G5_REENTRY must participate
in the same support-gated
margin field
as ECHO_PHASE.

G5_REENTRY must participate
in the same support active-recruitment
increment
as ECHO_PHASE.

Echo-specific diagnostics
must also include G5_REENTRY.

RNG

The formal repaired primary
must retain the originally preregistered
A46 treatment RNG identity:

YGG-A46-ARM-SEED.

A separate common-random
diagnostic may pair
G5_REENTRY to ECHO_PHASE
for causal attribution,
but that diagnostic
does not replace
the repaired frozen primary.

PRE-FREEZE PARITY PROBE

A repair candidate was constructed
with only the parent-dispatch corrections.

Candidate source SHA256:

53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885

For parity testing only:

G5 action was disabled;

G5_REENTRY was assigned
the exact paired A45 ECHO_PHASE
random identity.

Across 60 representative
world/arm pairs spanning:

constant;
spatial;
reversal;
balanced periodic;
6:2;
5:3;

behavioral mismatches:

0.

This confirms that,
when the explicit G5 action
is removed,
the repaired treatment path
is parent-equivalent.

NEXT STEP

Repeat the common-random
G5 causal diagnostic
with repaired parent mechanics.

Then freeze A46-FIXA
from the repair candidate
under the original
independent A46 treatment RNG.

Derive a fresh post-freeze
384-world manifest.

Run two byte-identical
repaired primaries.

Only then may the intended
A46 scientific question
be closed.

PLAIN-SPEAK INTERPRETATION

We found a wiring mistake.

The A46 treatment
was supposed to take
the full A45 organism

and change only one thing:

let a confirmed refractory cell
return to U early.

Instead,
the treatment accidentally
lost two abilities
that A45 already had:

its cooperative defense
during challenge;

and its active growth
during support.

So when A46 looked worse,
we were not comparing:

A45
versus
A45 plus early re-entry.

We were comparing:

A45
versus
a partially stripped organism
plus early re-entry.

That is not the experiment
we registered.

The correct response
is not to reinterpret the numbers.

It is to repair
the wiring,
prove the repaired treatment
matches A45 everywhere
except the intended G5 seam,
and rerun the experiment.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
