TITLE: YGGDRASIL A34 / T8R — Contradiction-Suppressed Independent Recruitment
DATE: 2026-09-21
STATUS: PREREGISTERED DISTRIBUTED-DEADBAND EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8R / APPLICATION-A
PARENT: A33 Independent Competing-Hazard Recruitment
BRANCH: dg1a-ar

PURPOSE

A33 proved that independent recruitment clocks
successfully spread recruitment over time,
but population oscillation increased.

The failure was localized:

when candidate and stale evidence are both strong,
both recruitment hazards remain positive.

Cells continuously join both sides,
local cross-inhibition ejects some,
refractory memory delays re-entry,
and after release both hazards may still be active.

A34 changes one mechanism only:

OPPOSING EVIDENCE SUPPRESSES EACH CELL'S RECRUITMENT HAZARD.

No global all-cell gate returns.
No centralized confidence scalar is introduced.

FROZEN PARENT

A33 closure:

798255d25dc1a1aff840eb5c56bf5df92d856bbd.

A34 FREEZE

Let the exact A34 implementation freeze commit be:

F34.

No real A34 world,
suppressed hazard,
recruitment event,
or scientific result
may be derived before F34 exists.

WORLD SHAPE

Fresh post-F34 worlds.

384 trials:

48 contexts
x
8 replicas.

48 cells.

48 epochs.

Initial population:

12 C;
12 S;
24 U.

World families remain structurally identical to A33:

0 stable C advantage;
1 stable S advantage;
2 spatial contradiction;
3 reversal C -> S;
4 reversal S -> C;
5 transient / oscillatory uncertainty.

PULSE ECOLOGY — UNCHANGED

Base pulses,
committed feedback pulses,
3/4 pool decay,
local sensing,
A30 cross-inhibition,
and A31 D2/D3 refractory memory
remain unchanged.

INDEPENDENT CLOCKS — UNCHANGED

Every eligible U cell owns
independent deterministic stochastic recruitment draws.

One cell firing cannot recruit another cell.

Recruitment radius:

3.

ETA:

1/2.

Pool normalization:

160.

Weight pairs remain exactly:

P75L25 = 3/4 pool + 1/4 local.

P50L50 = 1/2 pool + 1/2 local.

P25L75 = 1/4 pool + 3/4 local.

Both D2 and D3 remain.

SUPPORT FIELDS

For each eligible U cell i:

SUP_C(i,t)
=
w_pool * P_C(t)
+
w_local * L_C(i,t).

SUP_S symmetrically.

These are the exact A33 support terms
before ETA multiplication.

OPPOSITION FIELDS

OPP_C(i,t)
=
w_pool * P_S(t)
+
w_local * L_S(i,t).

OPP_S symmetrically.

Thus a candidate recruitment clock
is suppressed by stale-side evidence
from the same global/local channels.

CONTRADICTION SUPPRESSION

Fixed suppression law:

G(x)
=
1
/
(1 + (x / K_SUPP)^N_SUPP).

Frozen constants:

K_SUPP = 1/2.

N_SUPP = 3.

These reuse the moderate nonlinear shape
that behaved usefully in A30.

PRIMARY SUPPRESSED HAZARDS

lambda_C
=
ETA
*
SUP_C
*
G(OPP_C).

lambda_S
=
ETA
*
SUP_S
*
G(OPP_S).

If both sides are strong:

both hazards are suppressed.

If one side is strong
and opposition is weak:

that side retains a substantial recruitment rate.

The mechanism creates no explicit:

"UNCERTAIN"

number.

Uncertainty appears as low recruitment activity
when both opposing fields are elevated.

PRIMARY ARMS

D2_S_P75L25.
D2_S_P50L50.
D2_S_P25L75.

D3_S_P75L25.
D3_S_P50L50.
D3_S_P25L75.

UNSUPPRESSED PAIRED REFERENCES

For every primary arm,
run the exact A33 hazard without G(OPP):

D2_U_P75L25.
D2_U_P50L50.
D2_U_P25L75.

D3_U_P75L25.
D3_U_P50L50.
D3_U_P25L75.

This produces direct matched comparisons
on the same fresh worlds.

NEGATIVE CONTROL

D3_LINEAR_P50L50:

same as D3_S_P50L50
except:

N_SUPP = 1.

This tests whether shallow proportional suppression
fails to create a useful deadband.

No arm is selected post-result.

PRIMARY METRICS

For every arm report:

aggregate service;

beneficial / neutral / harmful;

harmful rate;

false C dominance;

false S dominance;

contradiction no-majority fraction;

population oscillation;

cell chatter;

recruitment width;

directional coordination;

reversal acquisition;

worst cumulative drawdown.

CONTRADICTION-SPECIFIC METRICS

For epochs where:

C_pool >= 48
AND
S_pool >= 48,

report:

mean lambda_C among eligible U;

mean lambda_S among eligible U;

total U -> C joins;

total U -> S joins;

fraction of contradictory epochs
with zero recruitment events;

fraction with no population majority.

Also report same quantities
outside contradiction.

DEADBAND EFFECT

For each suppressed arm versus paired unsuppressed reference report:

reduction in joins during contradiction;

change in joins outside contradiction;

change in oscillatory trial count;

change in false dominance;

change in aggregate service.

The intended mechanism is selective:

recruitment should be reduced
more strongly during contradiction
than during one-sided evidence.

FAMILY-5 RETEST

Report exact oscillatory identity overlap
between every suppressed arm
and its paired unsuppressed reference.

Report:

broken oscillators;

new oscillators;

remaining oscillators.

A34 directly asks whether
the persistent FAMILY-5 oscillatory set
is broken by contradiction-sensitive silence.

PRIMARY QUALIFICATION

A suppressed primary arm is CONTRADICTION-SUPPRESSION-QUALIFIED iff:

1. oscillatory fraction <= 0.05;

2. oscillatory fraction
   < paired unsuppressed reference;

3. at least 50% of paired-reference
   FAMILY-5 oscillatory trials are broken;

4. median finite recruitment width >= 3 epochs;

5. median directional coordination >= 0.80;

6. false C dominance <= 0.05
   among S-favoring worlds;

7. false S dominance <= 0.05
   among C-favoring worlds;

8. reversal acquisition >= 0.80;

9. contradiction no-majority fraction >= 0.90;

10. aggregate service >= 95%
    of paired unsuppressed reference;

11. all integrity probes pass.

A34_CONTRADICTION_SUPPRESSION_INFORMATION_GAIN

TRUE iff at least one primary suppressed arm:

reduces oscillation;

breaks at least 25% of paired-reference
FAMILY-5 oscillatory trials;

reduces contradictory-epoch recruitment
by at least 50%;

retains at least 80% directional coordination;

and retains at least 90% paired-reference service.

This is descriptive only.

INTEGRITY PROBES

P1:
384 trials.

P2:
48 contexts x 8 replicas.

P3:
48 cells.

P4:
48 epochs.

P5:
initial C/S/U = 12/12/24.

P6:
pool decay = 3/4.

P7:
local inhibition R/n/K = 12/3/1/2.

P8:
recruitment radius = 3.

P9:
ETA = 1/2.

P10:
pool normalization = 160.

P11:
D2 = 2 refractory epochs.

P12:
D3 = 3 refractory epochs.

P13:
primary weights exactly 75/25, 50/50, 25/75.

P14:
K_SUPP = 1/2.

P15:
primary N_SUPP = 3.

P16:
linear control N_SUPP = 1.

P17:
suppression multiplies hazard;
it cannot change pulse generation.

P18:
FC / FS have zero recruitment hazard.

P19:
one recruitment event cannot recruit another cell.

P20:
no global all-cell recruitment exists.

P21:
no future environment enters current hazard.

P22:
paired unsuppressed references use exact A33 hazard.

P23:
no centralized confidence scalar exists.

P24:
two complete primary sweeps byte-identical.

INTERPRETATION

If suppression reduces oscillation
without destroying coordination or reversal,
A33's failure was continuous recruitment during contradiction.

If suppression reduces all recruitment equally,
the mechanism is not selective enough.

If contradiction becomes quiet
but false dominance remains high,
the remaining problem is attractor persistence,
not actuation churn.

If even suppressed independent hazards oscillate,
the oscillatory environment may require explicit bet-hedging
rather than repeated commitment attempts.

PLAIN-SPEAK QUESTION

A33 gave every cell its own clock.

That stopped the stampede.

But both clocks kept ticking
when both sides were shouting.

A34 teaches each cell one more local rule:

"strong opposition slows my clock."

Candidate evidence still speeds the candidate clock.

Stale evidence still speeds the stale clock.

But if both are strong,
both clocks become quiet.

No central judge says:

"we are uncertain."

The uncertainty shows up as:

fewer cells deciding to join either side.

A34 asks:

CAN YGGDRASIL BECOME QUIET
WHEN THE EVIDENCE ITSELF IS CONTRADICTORY?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A34 CONTRADICTION-SUPPRESSED INDEPENDENT RECRUITMENT

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F34-DERIVED WORLD,
SUPPRESSED HAZARD,
RECRUITMENT EVENT,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

d1723f67b18041c8a5704f7cdd558428eacbf0ff.

SOURCE BUNDLE

Loader:

research/applications/track-a/a34_t8r_contradiction_suppressed_independent_recruitment_v1.py

Loader Git blob:

0accbb2809bb2e14820465d534096ec46ff07238.

Payload:

research/applications/track-a/a34_t8r_contradiction_suppressed_independent_recruitment_v1.py.gz

Payload Git blob:

87d0e8e653898d6d9b4190fe77e052621dfdedf3.

Decompressed source SHA-256:

b8095a5839b5bef2567e28fe6c8d2d9aeaf85b697d46f9bf2507078088c53d88.

Decompressed source bytes:

25824.

Deterministic gzip SHA-256:

0ba3f748703a890c7f7de6fe867d39f7a672d914f438f05ad9cd4b298228f19c.

Compressed payload bytes:

6707.

EXECUTION NOTE

The 13-arm matrix is executed arm-isolated
and combined deterministically.

This is an execution optimization only.

All arms consume identical frozen worlds.

No scientific rule differs from the preregistration.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F34-NONPRIMARY.

Two complete arm-isolated sweeps were byte-identical.

Serialized combined output SHA-256:

a3ed946755744eefbfff7403bb88b9ee2bf9e7f04a8526e893da8d2da57b69a9.

All P1-P24 integrity probes:

PASS.

No primary suppressed arm qualified.

No primary suppressed arm met
A34_CONTRADICTION_SUPPRESSION_INFORMATION_GAIN.

Mechanical contradictory-join reduction
relative to paired unsuppressed references:

D2_S_P75L25:
26.41%.

D2_S_P50L50:
19.26%.

D2_S_P25L75:
10.03%.

D3_S_P75L25:
23.30%.

D3_S_P50L50:
16.50%.

D3_S_P25L75:
9.53%.

Thus the preregistered moderate suppressor
did reduce recruitment during contradiction,
but well below the frozen 50% information-gain target.

Mechanical contradiction zero-recruitment fractions
remained only approximately:

6% to 10%.

Mechanical suppressed-arm oscillation remained:

14.32% to 19.27%.

The linear D3_P50L50 control produced:

15.63% oscillation.

This mechanical evidence does NOT support
post-hoc tuning of:

K_SUPP;
N_SUPP;
ETA;
pool/local weights;
refractory duration.

The full preregistered design remains unchanged.

REAL A34 STATUS

No real F34-derived world exists.

No real suppressed hazard has been observed.

No real A34 primary outcome has been observed.

Let the resulting commit SHA be:

F34.

After F34 exists:

1. derive exactly 384 fresh worlds from F34;
2. bind the complete world-manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical combined output;
5. report all six suppressed arms,
   all six paired unsuppressed references,
   and the linear control.

NO POST-RESULT SUPPRESSION TUNING.
NO POST-RESULT WEIGHT TUNING.
NO POST-RESULT ETA TUNING.
NO POST-RESULT REFRACTORY CHANGE.
NO POST-RESULT LOCAL-INHIBITION CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A34 CONTRADICTION-SUPPRESSED INDEPENDENT RECRUITMENT

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A34 ARM EXECUTION
OR SCIENTIFIC OUTCOME.

F34:

41efa57ccd12c3b6e7a375feecf9741a863a79bd.

FROZEN SOURCE SHA-256:

b8095a5839b5bef2567e28fe6c8d2d9aeaf85b697d46f9bf2507078088c53d88.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen environmental contexts
x
8 F34-derived replicas.

CELLS:

48.

EPOCHS:

48.

COMPLETE WORLD-MANIFEST SHA-256:

016bfb2365bc6c44d65d37b88706bf7fe83f2a376246333e1f8b5fe5e289f43d.

Serialized manifest-wrapper SHA-256:

74d5fc5afe060a5c1c0a30c80a03dc9c9932cfa2ec53d4975403b1f6d66e53ff.

Serialized manifest-wrapper bytes:

39954.

PRIMARY STATUS AT MANIFEST BIND

Real suppressed-hazard outcomes observed:

0.

Real paired-reference outcomes observed:

0.

Real contradiction-deadband outcomes observed:

0.

Real A34 qualification outcomes observed:

0.

The next permitted operation is:

two complete deterministic A34 primary sweeps
using F34 as seed.

NO WORLD REDRAW.
NO SUPPRESSION CHANGE.
NO ETA CHANGE.
NO WEIGHT CHANGE.
NO REFRACTORY CHANGE.
NO LOCAL-INHIBITION CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
