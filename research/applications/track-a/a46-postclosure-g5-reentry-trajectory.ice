TITLE: YGGDRASIL A46 POST-CLOSURE DIAGNOSTIC — G5 RE-ENTRY TRAJECTORY
DATE: 2026-09-22
STATUS: POST-CLOSURE OBSERVATIONAL TRACE / NO DYNAMICS CHANGE
PARENT CLOSURE: 4d63d2a4e3dc2f21ce7efe1a5aa157a77ff70f59
F46: 80c1673f5fccfe55e98e85a2dad8453b6ad3291e
PRIMARY SEED: A46-F46-80c1673f5fccfe55e98e85a2dad8453b6ad3291e-PRIMARY
PRIMARY OUTPUT SHA256: 53ff44daf08eae604d2801f23527b441e56280012dc8984e580864a19deddf5b
BRANCH: dg1a-ar

PURPOSE

Explain why G5 early re-entry
reduces instantaneous refractory occupancy
yet lengthens unresolved recovery
and destabilizes previously controlled 6:2 worlds.

This diagnostic replays only
the frozen biased-periodic A46 worlds:

contexts 44;
45;
46;
47;

with observational event tracing.

No dynamics,
RNG,
gate,
threshold,
arm,
or A46 conclusion changes.

TRACE

For every G5 early re-entry record:

release epoch;

former side;

remaining refractory timer;

current favored/adverse pulse relation;

same-epoch destination;

next committed side and latency;

next defection latency;

whether refractory debt restarts.

PRIMARY TIMING RESULT

6:2 worlds:

D2 G5 early re-entries:
1457.

Favored-support phase:
1457 / 1457 = 100%.

Adverse phase:
0.

D3:

1556 early re-entries.

Favored-support phase:
1556 / 1556 = 100%.

Adverse phase:
0.

5:3 worlds:

D2:
364 total early re-entries;
361 occur during favored support;
3 during adverse evidence.

D3:
941 total;
930 during favored support;
11 during adverse evidence.

Therefore A46 does not mainly fail
because G5 fires
during the wrong environmental phase.

The gate is overwhelmingly
a recovery-phase signal.

REMAINING-TIMER RESULT

6:2 D2:

timer 2:
917 releases.

timer 1:
540.

6:2 D3:

timer 3:
896;

timer 2:
531;

timer 1:
129.

5:3 D2:

timer 1:
359 of 364.

5:3 D3:

timer 1:
635;

timer 2:
306.

Thus the 5:3 gate
usually removes only the last
one or two refractory ticks.

Even this modest compression
is enough to worsen long-term recovery
when the released cell enters
the fully plastic U pool.

SAME-EPOCH DESTINATION

6:2 D2:

42.0% of early releases
receive a same-epoch destination.

32.4% of all releases
immediately recommit
to the former side.

1.6%
immediately commit
to the opposite side.

8.0%
enter H.

6:2 D3:

42.7% receive
a same-epoch destination.

31.1% immediately
recommit former side.

1.4% commit opposite.

10.2% enter H.

5:3 D2:

39.6% receive
a same-epoch destination.

24.7% immediately
recommit former side.

2.2% commit opposite.

12.7% enter H.

5:3 D3:

35.8% receive
a same-epoch destination.

23.9% immediately
recommit former side.

2.7% commit opposite.

9.2% enter H.

STABILITY BY DESTINATION

The most important result
is that immediate former-side recommitment
is NOT the unstable cohort.

6:2 D2:

same-epoch former-side recruits:

472 events.

Fast defection
within 4 epochs
of that commitment:

0.00%.

6:2 D3:

484 events.

Fast defection:

0.00%.

5:3 D2:

89 same-epoch former-side recruits.

Fast defection:

12.4%.

5:3 D3:

222 events.

Fast defection:

18.5%.

By contrast,
cells not assigned
a same-epoch destination
are substantially more fragile
after their later commitment.

6:2 D2:

845 no-same-epoch releases.

96.0% eventually commit.

Of those later commitments:

21.1% defect again
within 4 epochs.

6:2 D3:

891 no-same-epoch releases.

94.5% eventually commit.

Fast defection:

22.7%.

5:3 D2:

218 no-same-epoch releases.

88.1% eventually commit.

Fast defection
among those commitments:

70.8%.

5:3 D3:

597 no-same-epoch releases.

91.5% eventually commit.

Fast defection:

70.0%.

OPPOSITE-SIDE SAME-EPOCH DESTINATION

This cohort is small
but highly unstable.

6:2 D2:

23 opposite-side
same-epoch commitments.

Fast defection:

100%.

6:2 D3:

22.

Fast defection:

100%.

5:3 D2:

8.

Fast defection:

100%.

5:3 D3:

25.

Fast defection:

96%.

H DESTINATION

Cells entering H
after early re-entry
also show substantial later instability.

6:2:

later-commit fast-defection
approximately 30-40%.

5:3:

approximately 60-65%.

RECOMMITMENT-LATENCY EFFECT

The diagnostic does not support
a one-epoch forced U delay.

In 6:2 worlds,
commitments occurring immediately
or one epoch after release
have relatively low fast-defection rates.

Fragility rises strongly
for many commitments
formed roughly 2-6 epochs
after release.

In 5:3 worlds,
delayed commitments
are especially fragile:

latency 1-4 commitments
commonly show
approximately 60-88%
fast defection.

Therefore:

SAME-EPOCH RECRUITMENT
IS NOT THE PRIMARY FAILURE.

Forcing every released cell
to remain U
for an additional epoch
is not justified by this evidence
and could remove
the most stable immediate-recovery path.

REFRACTORY RESTART

A large fraction
of early-released cells
eventually re-enter refractory state.

6:2:

approximately 66%
of G5 release events
eventually restart refractory debt.

5:3:

approximately 79-81%
restart refractory debt.

This explains the A46 paradox:

refractory occupancy is reduced
immediately after G5 release,

but a large plastic cohort
later recommits,
defects,
and creates new refractory debt.

The system is moving debt forward
rather than eliminating it.

CAUSAL DIAGNOSIS

The critical distinction
is not:

locked
versus
unlocked.

It is:

EVIDENCE-CONFIRMED REACTIVATION

versus

RETURN TO UNBOUNDED PLASTICITY.

G5 itself is a three-part
former-side confirmation signal:

local SUPPORT;

positive post-update
former-side margin;

positive current
former-side cooperative field.

When G5 release is followed
immediately by former-side commitment,
that cohort is unusually stable.

When the same cell is instead
released into U
without immediate anchoring,
its former-side evidence state
is discarded as an action constraint.

It can drift through U/H,
commit later under a different
local phase configuration,
and frequently defect again.

Therefore the likely A46 failure
is not that G5 re-entry happens too soon.

It is that G5 re-entry
uses the wrong destination phenotype.

The cell has enough evidence
to leave refractory lock,

but A46 treats it
as completely undecided.

NEXT JUSTIFIED MECHANISM CLASS

Test G5-CONFIRMED REACTIVATION
to the former commitment side.

The successor should compare:

A46 G5_REENTRY:
G5 -> U -> ordinary recruitment;

against:

G5_REACTIVATE:
G5 -> former committed side directly.

For G5_REACTIVATE:

the commitment must restart
as a NEW commitment episode;

commit age = 0;

A45 cooperative echo trace = 0;

no old cooperative trace
crosses refractory;

no extra persistence bonus;

no preserved old commitment age;

no special recruitment gain.

Thus the only causal difference is:

destination after
the already-audited G5 confirmation.

Safety must remain strict
because direct reactivation
is stronger than U re-entry.

Report especially:

balanced false-majority;

true-reversal old-side reactivation;

same-side short-cycle chatter;

6:2 stability;

5:3 unresolved duration;

wrong-side majority capture.

PLAIN-SPEAK INTERPRETATION

We found out
what went wrong with A46.

It was not simply
that we let cells off the bench too early.

The cells that got off the bench
and immediately returned
to their old, now-supported job
were actually the most stable group.

The trouble came from
the cells we released
and then treated
as completely undecided.

They wandered through uncertainty.

Many committed later,
when the local situation
had already shifted again.

Those later commitments
were much more likely
to break quickly

and put the cells
right back onto the bench.

So A46 was often doing this:

BENCH
-> FREE
-> DRIFT
-> COMMIT
-> BREAK
-> BENCH AGAIN.

That makes the waiting line
look shorter at first,

but it creates
a new waiting line later.

The three-part G5 signal
already says something stronger
than:

"this cell may be undecided again."

It says:

"the side this cell previously served
is supported again;

the cell's own evidence
has turned back toward it;

and a real same-side core
exists nearby."

The next clean question is whether
that signal should mean:

REACTIVATE THE OLD ROLE

instead of:

FORGET THE OLD ROLE
AND START FROM ZERO.

That fits the developmental idea
we have been approaching:

temporary displacement
does not necessarily require
complete loss of identity.

But reactivation must still
restart without old age,
old echo,
or extra privilege,
so genuine change
can remove it again.

NORTH-STAR IMPLICATION

A46 separates two forms
of plasticity:

identity erasure;

and reversible dormancy.

The current evidence suggests
that distributed recovery
may benefit from preserving
a locally re-confirmable identity
through a short refractory period

rather than forcing every displaced cell
through fully blank uncertainty.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
