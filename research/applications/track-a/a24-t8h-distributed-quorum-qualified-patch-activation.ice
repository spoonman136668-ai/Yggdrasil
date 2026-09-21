TITLE: YGGDRASIL A24 / T8H — Distributed Quorum-Qualified Patch Activation
DATE: 2026-09-21
STATUS: PREREGISTERED QUORUM-SENSING EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8H / APPLICATION-A
PARENT: A23 Persistent Patch Confidence Ledger
BRANCH: dg1a-ar

PURPOSE

A23 showed that remembering global WIN / TIE / LOSS evidence
does not solve activation uncertainty.

Repeated positive global outcomes
can still fail prospectively.

A24 tests a different information source:

DISTRIBUTED LOCAL QUORUM.

Instead of asking only:

"did the whole canary trajectory beat the stale twin?"

A24 asks:

"how many individual software cells independently experienced
candidate control as locally more useful,
and how broadly is that evidence distributed
across fixed provenance families and fixed developmental niches?"

A24 isolates quorum sensing.

It does NOT add:

temporal low-pass filtering;
new persistence thresholds;
negative feedback;
positive-feedback commitment;
bet-hedging;
adaptive threshold tuning.

Those remain later experiments.

RESEARCH MOTIVATION

Biological quorum sensing coordinates collective responses
through population-distributed signaling.

Modern single-cell work also shows
that quorum responses can remain heterogeneous
rather than behaving as one perfectly synchronized vote.

For Yggdrasil,
that suggests quorum should preserve:

support;
opposition;
abstention;
provenance diversity;
niche diversity.

Quorum is not treated as simple majority truth.

FROZEN PARENT FRONTIER

A23 closure:

874d94fc68d7b0680cd43e8635a0a44c3295f506.

A17 remains the frozen developmental patch substrate.

DG-1R-05 remains unspent.

A24 FREEZE

Let the exact A24 implementation freeze commit be:

F24.

No real A24 trajectory
or quorum outcome
may be derived before F24 exists.

FRESH TRAJECTORIES

After F24,
derive exactly:

384

fresh trajectories:

48 fixed A17 patch contexts
x
8 F24-derived replicas.

Each trajectory contains:

16 fresh demand epochs.

W1:
epochs 0-7.

W2:
epochs 8-15.

Replacement episodes:

0;
8.

Every 16-demand sequence has exact mean
equal to the candidate target prior.

All A24 demand / replacement namespaces are:

YGG-A24-*.

They are distinct from A17-A23.

FIXED CANARY EXPOSURE

A24 uses only:

C3 = 3 of 4 candidate-controlled newborns.

Reason:

A21 showed C3 supplied the most decision coverage
under the one-window canary design
but still failed safety.

Using one fixed exposure isolates
the information value of quorum
from the effect of changing exposure size.

At epoch 0:

first three canonical replacement births:
candidate target prior.

fourth:
stale-previous prior.

Matched stale twin:

all four births stale-controlled.

LOCAL CELL EVIDENCE

There are exactly:

12 persistent cell identities.

For every epoch in W1
and every cell identity cid,
compute that cell's marginal service contribution:

MARGINAL(cid)
=
service(population)
-
service(population with cid removed).

Because service is count-matched,
MARGINAL is always:

0 or 1.

For the same persistent cell identity,
compare:

candidate-canary marginal
minus
stale-twin marginal.

Per-epoch local evidence is therefore:

-1;
0;
+1.

For each cell,
sum its eight W1 local evidence values:

CELL_DELTA[cid].

Cell signal:

CELL_DELTA > 0:
SUPPORT.

CELL_DELTA == 0:
ABSTAIN.

CELL_DELTA < 0:
OPPOSE.

No global service delta
is copied into cell signals.

FIXED PROVENANCE FAMILIES

Cell provenance is immutable:

family 0:
IDs 0-3.

family 1:
IDs 4-7.

family 2:
IDs 8-11.

Thus each provenance family contains
one cell from each original developmental niche.

A cell can change runtime role,
but its provenance family never changes.

FIXED DEVELOPMENTAL NICHE IDENTITY

Each cell has immutable origin niche:

NICHE(cid) = cid mod 4.

Thus there are four fixed niche identities:

0;
1;
2;
3.

Runtime migration does not rewrite niche provenance.

QUORUM SUMMARY

For every trial report:

support count;
abstain count;
oppose count;

supporting provenance families;
opposing provenance families;

supporting fixed niches;
opposing fixed niches;

per-cell signed deltas;

per-family summed evidence;
per-niche summed evidence.

Quorum failure means:

UNCERTAIN / DORMANT.

It does NOT mean:

PATCH INVALID;
PATCH DELETE;
PATCH FORGET.

PREREGISTERED GATES

G0 — GLOBAL ONE-HIT REFERENCE

Expand iff:

global W1 canary service
>
global W1 stale-twin service.

This reproduces the basic A21-style
one-window global consequence rule
on fresh A24 worlds.

G0 is diagnostic only.

Q1 — POPULATION QUORUM

Expand iff:

SUPPORT count >= 7.

This is a simple 7-of-12 local-cell quorum.

Q2 — PROVENANCE-QUALIFIED QUORUM

Expand iff:

SUPPORT count >= 7

AND

supporters include all three
immutable provenance families.

Q3 — PROVENANCE + NICHE QUORUM

Expand iff:

SUPPORT count >= 7

AND

supporters include all three
immutable provenance families

AND

supporters include at least three
of the four immutable developmental niches.

No gate uses:

future W2 information;
A19 shadow statistics;
A23 ledger scores;
global positive margin magnitude.

W2 AUTHORITY

At epoch 8:

if a gate EXPANDS:

continue that gate's canary trajectory;
all four epoch-8 newborns use candidate target prior.

if a gate DOES NOT EXPAND:

restore the exact stale-twin state;
all four epoch-8 newborns use stale prior.

Then execute untouched W2.

No W2 demand identity
may be visible to the gate.

REFERENCE LABEL

For each fresh trajectory,
also execute:

R0:
always stale.

R1:
always candidate.

The R1-minus-R0 W2 sign is reported
as a frozen reference label
for whether full candidate control
was beneficial,
neutral,
or harmful
in the untouched second half.

PRIMARY METRICS

For G0 / Q1 / Q2 / Q3 report:

expansion count;

actual W2:
beneficial;
neutral;
harmful;

actual harm rate;

R1 label among expanded trials:
beneficial;
neutral;
harmful;

R1-label harm rate;

W1 provisional aggregate service delta;

W2 aggregate service delta versus stale;

complete 16-epoch service delta versus R0;

complete service delta versus R1.

QUORUM-SPECIFIC METRICS

For Q1 / Q2 / Q3 report:

expansions rejected relative to G0;

harmful G0 expansions rejected;

beneficial G0 expansions rejected;

trials where global W1 delta > 0
but local-cell support < 7;

trials where support >= 7
but provenance diversity fails;

trials where provenance passes
but niche diversity fails;

support / abstain / oppose distributions.

PRIMARY QUALIFICATION

A quorum gate is QUORUM-QUALIFIED iff:

expansion count >= 48

AND

actual W2 harmful expansion rate <= 0.05

AND

R1 W2 harmful-label rate
among expansions <= 0.05

AND

actual harmful expansion rate
is no greater than half
the unconditional R1 W2 harm rate
when that unconditional rate is nonzero

AND

all integrity probes pass.

Coverage floor:

48 / 384.

Harm ceiling:

5%.

These are inherited from A21-A23.

A24 does NOT select a winning quorum gate.

If one or more gates qualify,
that supports a later independent replication.

If none qualify,
quorum alone is insufficient.

COMPARISON CLAIM

A24_QUORUM_INFORMATION_GAIN is TRUE iff
at least one of Q1 / Q2 / Q3:

has lower actual harm rate than G0

AND

rejects at least one harmful G0 expansion

AND

retains at least 50% of G0's beneficial expansions.

This is descriptive.

It does not grant authority.

INTEGRITY PROBES

P1:
exact A17 replay unchanged.

P2:
384 unique F24-derived trajectories.

P3:
16 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly 0 / 8;
four unique IDs each.

P5:
W2 future leakage impossible.

P6:
every per-cell per-epoch marginal is exactly 0 or 1.

P7:
every local evidence difference is exactly -1 / 0 / +1.

P8:
same persistent cell ID is compared
between canary and stale twin.

P9:
provenance family is fixed by cid // 4.

P10:
developmental niche is fixed by cid mod 4.

P11:
runtime role migration cannot rewrite family or niche identity.

P12:
same-family vote fanout cannot satisfy Q2.

P13:
same-niche concentration cannot satisfy Q3
unless at least three fixed niches support.

P14:
non-expansion restores exact stale twin.

P15:
learned patch remains preserved.

P16:
restart equivalence at W1 boundary.

P17:
two complete primary sweeps byte-identical.

P18:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

NEGATIVE / LIMIT CONTROLS

N1 — COPY GLOBAL DELTA TO ALL 12 CELLS

Invalid fake quorum.

N2 — COUNT DUPLICATED SAME-LINEAGE SIGNALS
AS INDEPENDENT SUPPORT

Invalid provenance inflation.

N3 — USE MUTABLE RUNTIME ROLE AS PROVENANCE

Invalid identity rewrite.

N4 — DROP ABSTENTION

Invalid forced certainty.

N5 — SIMPLE GLOBAL ONE-HIT

G0 reference.

N6 — TEMPORAL FILTERING

Not tested in A24.

N7 — FEEDBACK / COMMITMENT / BET-HEDGING

Not tested in A24.

INTERPRETATION

If Q1 improves safety,
distributed local evidence itself carries information.

If Q2 improves over Q1,
provenance diversity matters.

If Q3 improves over Q2,
cross-niche agreement matters.

If all quorum gates fail similarly to G0,
local collective agreement alone
does not resolve temporal uncertainty.

A24 should then close negative
and the next mechanism can be tested separately.

PLAIN-SPEAK QUESTION

Until now,
we mostly asked the whole organism one question:

"did the patch win?"

A24 asks the cells individually.

Each cell compares:

"was my own place in the candidate organism
actually more useful
than my matched self in the old-policy twin?"

A cell can say:

yes;
no;
or
I don't know.

Then we ask whether enough cells agree.

But we also ask:

did that agreement come from different family lines?

did it span different kinds of developmental cells?

That prevents seven copies of the same narrow experience
from pretending to be broad consensus.

If broad independent local agreement
predicts the untouched future better
than one global score,
quorum sensing has earned a real place
in Yggdrasil's uncertainty architecture.

If it does not,
we keep the negative result
and move to the next biological mechanism.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
