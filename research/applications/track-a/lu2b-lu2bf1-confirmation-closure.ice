TITLE: LU-2B LU2BF1 INDEPENDENT CONFIRMATION CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / INDEPENDENT CONFIRMATION FALSE
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
2a8430c0b88be19adb4bf5c18c49d56abe1b0ab6

LU2BF1:
ce52acc9826eb9c385a022dba9abdcbe19797472

PARENT LU2AF1-R1:
ba771ec410b5a35498e0b146e71781ac4df4285c

FIVE-MANIFEST BINDING:
59a0e809e7913aaec25dc1d64573732f34e39545

LU-2A QUALIFIED PRIMARY:
dc235c5a6712c199803cc51d066b16378f10d438

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

DUPLICATE CONFIRMATION GATE

complete five-world paired confirmation sweeps:
2

raw canonical sweep bytes each:
243950

SHA256 both:
6eba1bcb2a03796ca78238ac2971fb015b828e42878859c62fb501eb178ba123

byte-identical:
TRUE

Confirmation qualification was opened only after duplicate identity passed.

CAUSAL CONFIRMATION

H evaluations:
8

H nonzero learned-vs-teacher probability deltas:
8

U evaluations:
7364

U nonzero learned-vs-teacher TV deltas:
7364

realized learned-controlled H/U transition differences:
186

LU2B_LEARNED_PARTICIPATION_CAUSAL:
TRUE

FUNCTIONAL CONFIRMATION

Replicate 1:
all functional-preservation checks PASS.

completion-area ratio:
1.0121457490

Replicate 2:
all functional-preservation checks PASS.

completion-area ratio:
1.0000000000

Replicate 3:
all checks PASS except paired Phase-4 final-window gap.

completion-area ratio:
0.9799196787

teacher Phase-4 final-window correct-completion rate:
1.25

hybrid Phase-4 final-window correct-completion rate:
1.09375

paired difference:
-0.15625

required:
no worse than -0.10

FAIL.

absolute hybrid Phase-4 requirement:
>=0.85

observed:
1.09375

PASS.

teacher anchor-rotation recovery latency:
1 epoch

hybrid anchor-rotation recovery latency:
0 epochs

teacher correct DONE:
286

hybrid correct DONE:
282

teacher final-16 total backlog area:
575

hybrid final-16 total backlog area:
608

teacher operations per correct completion:
10.1118881119

hybrid operations per correct completion:
10.1631205674

All of those remain within their preregistered bars.

Replicate 4:
all functional-preservation checks PASS.

completion-area ratio:
0.9959514170

Replicate 5:
all functional-preservation checks PASS.

completion-area ratio:
0.9959839357

MEDIAN COMPLETION-AREA RATIO

0.9959839357

required:
>=0.95

PASS.

SCIENTIFIC STATUS

LU2B_LEARNED_PARTICIPATION_CAUSAL:
TRUE

LU2B_FUNCTIONAL_CONFIRMATION:
FALSE

LU2B_INDEPENDENT_CONFIRMATION:
FALSE

CAUSAL DETAIL — REPLICATE 3

H evaluations:
4

H realized transition differences:
0

U evaluations:
1262

U realized transition differences:
33

first causal divergence epoch:
5

epochs with different state vector:
155

trajectories later reconverge:
FALSE

Thus the replicate-3 confirmation miss
occurred on a trajectory whose causal divergence
was driven by learned U-recruitment outcomes,
not by an H-release outcome.

INTERPRETATION

The original LU-2A result remains a valid qualified result.

LU-2B does not reproduce it under the exact same universal gates.

The failure is narrow:

four of five fresh confirmation worlds pass every bar;

the fifth remains functionally strong in absolute terms
but misses the paired Phase-4 final-window tolerance
by 5.625 percentage points beyond the allowed 10-point gap.

Do not promote LU-2A into the substrate.

Do not expand learned authority.

Do not relax the Phase-4 paired bar.

Do not retune on confirmation replicate 3.

NEXT AUTHORIZED STEP

Perform one observation-only diagnosis
of LU-2B replicate 3.

Determine whether the Phase-4 paired miss is associated with:

persistent state-allocation divergence from early U decisions;

stream-specific completion loss;

localized role imbalance after anchor relocation;

or backlog-drain timing.

No retraining.

No new model.

No changed threshold.

No replacement confirmation world.

After that diagnosis,
decide whether the next scientific question should be:

A.
distribution-shift correction for U recruitment training;

B.
a narrower learned-U authority boundary;

C.
a second-task transfer test before any substrate promotion;

or

D.
close learned closed-loop promotion for this model family.

PLAIN-SPEAK INTERPRETATION

The first five-world batch worked.

The second fresh five-world batch almost repeated it,
but not quite.

Four worlds passed everything.

In the fifth world,
the neural version still performed well,
but it cleared old backlog more slowly after relocation
than the hand-written organism.

The neural version reached 109.375% of normal arrival throughput
during the final window,
which is strong.

The hand-written version reached 125%
because it drained more old work at the same time.

That 15.625-point gap is larger
than the frozen 10-point tolerance,
so confirmation fails.

We do not move the goalposts.

The next step is to inspect that one divergence
and find out whether the problem is
where U cells were recruited,
when they were recruited,
or how the resulting spatial allocation affected backlog drain.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
