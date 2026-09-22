TITLE: YGGDRASIL A45 POST-CLOSURE DIAGNOSTIC — REFRACTORY EVIDENCE-GATE AUDIT
DATE: 2026-09-22
STATUS: POST-CLOSURE OBSERVATIONAL AUDIT / NO DYNAMICS CHANGE
PARENT CLOSURE: d99afa1aefcba407aaf6522f0ba6660f6783381d
POST-CLOSURE PHENOTYPE DIAGNOSIS: 8f67b4aa0a04eb5f140714dc2e482b4b24a925b9
F45: c9207c0fd0034160ea546db5e367cda84f5bc1c0
PRIMARY SEED: A45-F45-c9207c0fd0034160ea546db5e367cda84f5bc1c0-PRIMARY
BRANCH: dg1a-ar

PURPOSE

Determine whether currently refractory
former-favored cells expose a local signal
that can distinguish:

temporary 5:3 recovery,

from:

true reversal,
balanced cycling,
and nonperiodic noise.

No refractory behavior is changed here.

AUDITED CANDIDATE GATES

For a refractory cell,
relative to its former committed side:

SUPPORT_ONLY:
local mode is SUPPORT.

SUPPORT_MPOST_POSITIVE:
local mode is SUPPORT
and post-update aligned former-side margin M_post > 0.

SUPPORT_MPRE_POSITIVE:
local mode is SUPPORT
and pre-update aligned former-side margin M_pre > 0.

SUPPORT_MPOST_Q_POSITIVE:
SUPPORT,
M_post > 0,
and current same-side raw cooperative field Q_raw > 0.

FIRST REFRACTORY EPOCH — 5:3 RECOVERY

D2 ECHO_PHASE:

SUPPORT_ONLY fires 100.00%.

SUPPORT_MPOST_POSITIVE fires 73.87%.

SUPPORT_MPRE_POSITIVE fires 0.00%.

SUPPORT_MPOST_Q_POSITIVE fires 0.00%.

D3 ECHO_PHASE:

SUPPORT_ONLY fires 100.00%.

SUPPORT_MPOST_POSITIVE fires 72.48%.

SUPPORT_MPRE_POSITIVE fires 0.00%.

SUPPORT_MPOST_Q_POSITIVE fires 0.00%.

Thus pre-update margin
and cooperative-field positivity
cannot accelerate the first recovery epoch.

The immediately current evidence
has not yet propagated into those quantities.

BALANCED-PERIODIC FIRST REFRACTORY EPOCH

D2:

SUPPORT_ONLY 47.12%.

SUPPORT_MPOST_POSITIVE 35.08%.

D3:

SUPPORT_ONLY 47.03%.

SUPPORT_MPOST_POSITIVE 36.40%.

Therefore SUPPORT alone
is too permissive.

Adding post-update former-side margin
reduces balanced firing,
but does not make it rare.

Balanced false-majority,
majority residence,
and chatter therefore remain
mandatory safety measurements
for any successor.

TRUE REVERSAL — OLD SIDE AFTER REVERSAL

D2:

SUPPORT_ONLY 0.00%.

SUPPORT_MPOST_POSITIVE 0.00%.

D3:

SUPPORT_ONLY 0.00%.

SUPPORT_MPOST_POSITIVE 0.00%.

The old commitment side
is locally CHALLENGE
through the observed post-reversal refractory window.

Therefore the candidate gate
does not observationally request
early old-side re-entry
during genuine reversal.

CONSTANTLY OPPOSED FORMER SIDE

Both D2 and D3:

SUPPORT_ONLY 0.00%.

SUPPORT_MPOST_POSITIVE 0.00%.

CONSTANTLY SUPPORTED FORMER SIDE

Both D2 and D3:

SUPPORT_ONLY 100.00%.

SUPPORT_MPOST_POSITIVE 100.00%.

NONPERIODIC FIRST REFRACTORY EPOCH

D2:

SUPPORT_ONLY 28.0%.

SUPPORT_MPOST_POSITIVE 24.7%.

D3:

SUPPORT_ONLY 27.9%.

SUPPORT_MPOST_POSITIVE 24.9%.

Thus the post-update-margin gate
is not a complete noise discriminator.

It is best interpreted
as a conservative evidence-alignment condition,
not a proof of environmental persistence.

5:3 RECOVERY TIMING

At recovery step 1:

M_pre is essentially zero
for first-locked former-favored cells.

M_post becomes positive
for roughly 72-74%.

By later recovery steps,
M_pre and Q_raw recover strongly,
but waiting for those signals
would miss the earliest useful acceleration point.

CAUSAL INTERPRETATION

The strongest no-new-threshold gate
available at the first recovery epoch is:

local SUPPORT
AND
post-update former-side M > 0.

It has three useful properties:

1. it fires for a large majority
   of first-epoch 5:3 recovery cells;

2. it does not fire
   for the old side
   in the audited true-reversal window;

3. it is more selective
   than SUPPORT alone
   in balanced-periodic worlds.

But it is not selective enough
to justify deleting refractory protection.

NEXT JUSTIFIED MECHANISM

Test a ONE-TICK refractory acceleration only.

Do not release immediately.

Do not eliminate refractory state.

Do not add a threshold.

On the first locked refractory epoch only:

if local mode relative to former side
is SUPPORT

and post-update former-side M > 0,

advance the refractory timer
by one additional tick.

The cell remains refractory
for the current epoch.

Therefore each qualifying episode
can become recruitable
at most one epoch earlier
than the parent.

Use SUPPORT-only acceleration
as the causal control.

This directly tests whether:

evidence-aligned plasticity recovery

is better than:

generic shortening
whenever local support appears.

PLAIN-SPEAK INTERPRETATION

We found a signal
that is good enough to test,
but not good enough
to throw away the safety lock.

When a three-hit disturbance ends,
about three quarters
of the benched former-favored cells
immediately see two things:

their old side is locally supported again,

and the new evidence
has already started rebuilding
their old-side confidence.

When the world truly reverses,
the old side sees none of that.

That is encouraging.

But balanced worlds
also produce this signal
often enough
that releasing cells immediately
would be too aggressive.

So the next experiment
should be modest:

do not unlock them now.

Just shorten the waiting period
by one tick
when that local evidence agrees.

In plain terms:

the cell still has to sit out,

but good evidence can take
one turn off its sentence.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
