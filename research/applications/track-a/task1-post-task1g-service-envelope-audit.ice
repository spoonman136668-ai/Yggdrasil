TITLE: TASK-1 POST-TASK1G SERVICE-ENVELOPE AUDIT
DATE: 2026-09-23
STATUS: OBSERVATION-ONLY / FROZEN-MANIFEST DIAGNOSIS
TRACK: DG-1 / TASK-1
PARENT CLOSURE: b11eb856b1348d8d08cc99497ac59f7a15e7ceaa

PURPOSE

Determine whether the remaining Task-1F / Task-1G
repair qualification misses
are caused by substrate dynamics
or by the frozen Task-1 service envelope.

No dynamics were changed.

SOURCE / WORLD BOUNDARY

Exact T1GF1 source:
dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197

Exact five Task-1G manifests:
bound at
b7519d905f07d6b91551c1b44636d284ebd8f376.

Observed arm:
LOCAL_HEDGE_PARENT.

This is the exact frozen Task-1F LOCAL_HEDGE behavior
on the five fresh Task-1G worlds.

RAW OBSERVATION EVIDENCE

raw audit bytes:
415361

raw audit SHA256:
fbfc6423120e729d3181bd4952df2965828f9550824cc2eb221a850895069327

compact summary bytes:
16728

compact summary SHA256:
3b718ebfb334b4f3e3828be600084b963c3658aafe9ef583cea119e47890383c

PIPELINE MINIMUM

A clean request requires:

SENSE;
PROCESS;
six ROUTE hops;
VERIFY.

Total operations:
9.

With one-operation-per-request-per-epoch,
a zero-wait clean request completes
8 epochs after its first SENSE.

A corrupted request additionally requires:

failed VERIFY;
REPAIR;
mandatory re-VERIFY.

Total operations:
11.

A zero-wait corrupted request therefore completes
10 epochs after first SENSE.

EXPIRY CONTRACT

Frozen expiry:
32 epochs.

A failed first verification
must occur with at least
3 epochs of remaining lifetime
to permit:

next epoch REPAIR;

following epoch mandatory re-VERIFY;

before the request expires.

Thus any corruption first detected
with remaining_lifetime < 3
is mathematically unrecoverable
under the frozen Task-1 contract,
regardless of repair scheduler quality.

CROSS-MANIFEST PIPELINE WAIT

Across all five manifests:

requests reaching SENSE:
1537.

PRE-SENSE wait:

mean:
7.678 epochs.

median:
6.

p90:
19.

maximum:
24.

SENSE -> PROCESS extra wait
beyond the mandatory next epoch:

mean:
0.443.

median:
0.

p90:
1.

maximum:
14.

PROCESS -> first ROUTE extra wait:

mean:
0.036.

median:
0.

p90:
0.

maximum:
2.

BETWEEN ROUTE HOPS extra wait:

mean:
0.0095.

median:
0.

p90:
0.

maximum:
3.

LAST ROUTE -> first VERIFY extra wait:

mean:
0.00139.

median:
0.

p90:
0.

maximum:
1.

Therefore the dominant queueing delay
is before SENSE.

After a request enters the functional pipeline,
the typical path is nearly continuous.

FIRST VERIFY AGE

Requests reaching first VERIFY:
1442.

Mean age at first VERIFY:
16.804 epochs.

Median:
16.

p90:
27.9.

Maximum:
31.

Median remaining lifetime at first VERIFY:
16 epochs.

CORRUPTED REQUESTS

Detected corruptions across five manifests:
77.

Mean remaining lifetime at first VERIFY:
14.117 epochs.

Median:
15.

Three detected corruptions
were already mathematically unrecoverable
at the moment corruption became observable:

R1 request 239.

R3 request 120.

R3 request 121.

These three first reached failed VERIFY
with fewer than three epochs
of lifetime remaining.

No post-detection scheduler
can complete both mandatory later operations
before expiry for these requests.

FINITE-HORIZON CENSOR

One additional request:

R5 request 281

was detected at epoch 158
and correctly repaired at epoch 159.

The fixed experiment ends after epoch 159.

Its mandatory re-verification
would be the next operation,
but the observation horizon closes first.

This is horizon censoring,
not failed repair computation.

REPAIR ACCOUNTING

Detected corruptions:
77.

Observed correct DONE after repair:
73.

Raw observed repair success:
73 / 77
=
94.805%.

Deadline-impossible after first detection:
3.

Finite-horizon-censored after correct repair:
1.

Detected repair paths that are both:

mathematically recoverable under expiry;

and observable through mandatory re-verification
within the frozen horizon:

73.

Correctly completed among those:
73.

Feasible-and-observable repair completion:
100%.

This does NOT retroactively change
Task-1F or Task-1G qualification.

It explains the source
of the formal misses.

CAUSAL INTERPRETATION

The Task-1 repair mechanism
is not the remaining weak link.

The Task-1G EDF negative
is also explained.

By the time the failing jobs
enter the detected repair critical path,
three have insufficient remaining lifetime
and one reaches repair at the horizon boundary.

For ordinary requests,
post-SENSE stage transitions
are almost always immediately serviceable.

The heavy tail is concentrated
in PRE-SENSE admission delay.

Task-1C already showed that
unconditional ingress priority
merely moves this pressure downstream.

Task-1D showed admission backpressure
does not remove total congestion.

Task-1E removed request-handoff migration.

Task-1F fixed the dominant local-H semantic trap.

Task-1G shows
post-detection repair priority
does not solve lifetime already consumed upstream.

Together these results identify
a workload / service-envelope boundary,
not another justified cellular knob.

ARCHITECTURAL CONSEQUENCE

Do not tune V0
to chase the remaining Task-1 repair misses.

Do not extend Task-1 expiry post hoc.

Do not weaken mandatory re-verification.

Do not reinterpret Task-1F or Task-1G
as formally qualified.

The robust LOCAL_HEDGE causal result remains valid
and should now receive
a clean independent confirmation experiment
before any V0.1 promotion.

NEXT

Preregister a frozen confirmation:

GLOBAL_HEDGE
versus
LOCAL_HEDGE

on fresh manifests,

with no new mechanism.

Primary question:

does the Task-1F local-ambiguity information gain
replicate on a new preregistered world set?

Repair metrics remain reported,
but benchmark deadline/horizon censoring
must be separated descriptively
from substrate-mechanism failure.

No Task-1 service rule changes
inside that confirmation.

PLAIN-SPEAK SUMMARY

The repair system is doing its job.

Of 77 broken jobs that were actually detected,
three were discovered too late
for the rules to physically allow
fix + final check before expiry.

One more was fixed on the last experiment step,
so the experiment stopped
before the final check.

Every other repair path
that had enough time
and enough experiment horizon
finished correctly:

73 out of 73.

Most waiting happens
before a job even gets sensed.

Once work enters the pipeline,
it usually moves almost every epoch.

That tells us to stop inventing
repair tricks for this benchmark.

The important organism result
is still Task-1F:

local ambiguity handling
made the system much better
at spatial reorganization.

That mechanism now deserves
a fresh confirmation,
not another tweak.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
