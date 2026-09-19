TITLE: DG-1A-AR-C2 — Multi-Sensor Distributed Context Consensus Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE / FAIL-SAFE CONSENSUS AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arc1-repeated-context-ordering-audit.ice

PURPOSE
AR-C1 established repeated context ordering with a bounded serial epoch,
but assumed a source packet was semantically correct.

Prior sensor-reliability work showed that independent sensors can suppress wrong-mode error.

AR-C2 combines those problems:

Can several noisy/damaged local sensors produce a robust ordered context without assigning one permanent sensor as the sole semantic authority?

BOUNDARY
Synthetic communication audit.

It does not:
- replace AR-01 broadcast context;
- authorize explicit sensor IDs in final Yggdrasil;
- prove real environmental sensors are independent;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX
ANALYTIC where stated.

BODY
613-cell radius-14 disk.

communication:
8-neighbor local.

stochastic update probability:
0.5

message dropout:
50%

seasonal switch period:
128 steps

switches:
12 per seed

sensors:
4 boundary sensors

serial epoch modulus:
16

ORDER
AR-C1 modular newer-than rule:

0 <
(e_msg - e_local) mod 16
<
8

SENSOR OBSERVATION
At each true context transition,
each surviving sensor independently:

detects the new epoch with probability:
p_detect

if detected,
reports:

correct mode
with probability:
1 - p_wrong

otherwise:
one of the five incorrect modes.

A missed sensor remains on its older epoch/context evidence until a later observation.

PROTOCOL A — LATEST PACKET WINS
Cells accept the first reachable packet from a newer epoch.

Equal-epoch semantic conflicts are not accumulated.

This preserves order
but does not require corroboration.

PROTOCOL B — PROVENANCE-DE-DUPLICATED QUORUM
Each sensor contributes one unique evidence identity.

For the current newest epoch,
cells locally merge mode evidence using set-union / idempotent provenance.

A mode is committed only if:

at least 2 distinct sensor identities support it

and

it has a unique largest vote count.

The context evidence itself can propagate before commitment.

Cells retain the prior committed context until the new epoch reaches quorum.

WHY UNIQUE PROVENANCE MATTERS
If relayed copies of one sensor vote are counted as independent evidence:

one sensor
->
many relay copies
->
false quorum.

Therefore redundant evidence must be IDEMPOTENT under relay.

This is an analytic distributed-systems requirement.

The explicit synthetic bitmask is only one implementation.

PRIMARY TEST
Fresh seeds:
8

p_detect:
0.90

message dropout:
0.50

p_wrong varied.

P_WRONG = 0.05

LATEST-WINS

switches reaching 90% correct current context:
77.08%

median successful latency:
18 steps

p95:
24

mean end-of-phase correct fraction:
93.35%

mean wrong committed current-context fraction:
6.65%

QUORUM

switch success:
98.96%

median:
30

p95:
37

end correct:
98.96%

wrong committed:
0.00%

P_WRONG = 0.10

LATEST-WINS

switch success:
67.71%

median:
18

p95:
24

end correct:
90.04%

wrong committed:
9.96%

QUORUM

switch success:
95.83%

median:
30

p95:
37

end correct:
97.52%

wrong committed:
1.01%

P_WRONG = 0.25

LATEST-WINS

switch success:
29.17%

median:
18

p95:
23

end correct:
71.39%

wrong committed:
28.61%

QUORUM

switch success:
82.29%

median:
32

p95:
39

end correct:
84.20%

wrong committed:
5.58%

PRIMARY RESULT
Semantic quorum trades latency for much higher context reliability.

At 10% sensor error:

latest-wins:
18-step median
67.7% switch success
~10% wrong committed current context.

two-sensor quorum:
30-step median
95.8% switch success
~1% wrong committed current context.

This is a favorable trade in a system where confident wrong mode is known to be dangerous.

DETECTION-MISS STRESS
Keep:

p_wrong = 0.10.

Quorum protocol.

p_detect = 0.95:
switch success 95.83%
median latency 26.5
end correct 96.30%
wrong committed 0.35%

p_detect = 0.90:
switch success 95.83%
median 30
end correct 97.52%
wrong 1.01%

p_detect = 0.75:
switch success 84.38%
median 32
end correct 85.26%
wrong 0.86%

p_detect = 0.50:
switch success 59.38%
median 36
end correct 59.38%
wrong 0.00%

INTERPRETATION
When too few sensors observe the current epoch,
quorum becomes a LIVENESS limitation.

Importantly,
it tends to block rather than confidently invent a mode.

SENSOR-DAMAGE STRESS
p_wrong:
0.10

p_detect:
0.90

quorum:
2

fresh seeds:
8

0 of 4 sensors damaged:
switch success:
95.83%
median:
30
end correct:
97.52%
wrong:
1.01%

1 damaged
3 surviving:
success:
87.50%
median:
33
end correct:
87.50%
wrong:
1.04%

2 damaged
2 surviving:
success:
65.62%
median:
38
end correct:
65.62%
wrong:
0.00%

3 damaged
1 surviving:
success:
0%
correct committed current epoch:
0%
wrong committed current epoch:
0%

FAIL-SAFE RESULT
With only one surviving sensor,
a two-sensor quorum refuses to declare a new distributed context.

It loses liveness,
but does not fabricate independent evidence.

This is preferable to duplicating one surviving sensor's relayed packet until it appears to be consensus.

CRITICAL STATE DISTINCTION
A cell needs to distinguish:

I HAVE NOT YET COMMITTED THE NEW EPOCH

from

THE OLD MODE IS STILL VERIFIED.

Therefore a future decentralized context state should separate:

observed/newest epoch evidence

from

committed semantic mode.

Simply overwriting the mode register as soon as a newer epoch appears is unsafe.

PROVENANCE / DUPLICATION PROBLEM
The synthetic protocol uses sensor identity bits to make evidence merging idempotent.

Final Yggdrasil does not necessarily need literal sensor IDs.

But it needs some mechanism preventing:

same causal observation
from being copied through many relay paths
and counted many times as independent evidence.

Possible future mechanisms:
- compact source/provenance tags;
- spatially separated evidence classes;
- learned decorrelated sensor modules;
- causal-domain tags;
- bounded set-like sketches.

Do not use raw relay-copy count as confidence.

RELATION TO PRIOR REDUNDANCY RESEARCH
This reinforces the same principle found in:

injury cues:
independent error modes matter.

seasonal sensors:
common-mode failures erase redundancy benefit.

local credit cues:
correlated copies fail to suppress noise.

AR-C2 adds:
NETWORK COPIES OF THE SAME EVIDENCE ARE NOT NEW EVIDENCE.

That distinction becomes essential in a recurrent cellular substrate.

ARCHITECTURAL CONSEQUENCE
A robust decentralized context stack now looks like:

multiple partially independent sensors

->
ordered epoch evidence

->
provenance-safe local merge

->
semantic quorum / confidence

->
committed context

->
AR-01 shared-rule modulation.

This is substantially more decentralized than global broadcast,
while preserving a way to reject stale and semantically uncorroborated control.

COST
Quorum increases switch latency.

At the primary 10% error condition:

latest:
18 steps

quorum:
30 steps.

That cost must be compared against:
the much larger danger of confident wrong-mode context already measured in AR-01 robustness work.

NEXT
AR-C3 — PROVENANCE COMPRESSION

Question:
Can the organism preserve "independent evidence count" without explicit permanent sensor identities?

Test:
- small source sketches;
- spatial evidence sectors;
- randomized source signatures;
- learned decorrelation/confidence;
- relay loops.

Goal:
idempotent redundancy with minimal state.

PARALLEL
AR-U13:
shared novelty/confidence state.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX_AND_ANALYTIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
body_cells = 613
