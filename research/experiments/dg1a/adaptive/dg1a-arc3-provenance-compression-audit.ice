TITLE: DG-1A-AR-C3 — Provenance Compression / Idempotent Evidence Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX DISTRIBUTED-EVIDENCE AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-adaptive-research-frontier-r4-20260918.ice

PURPOSE
AR-C2 showed that relayed copies of one sensor report must not count as independent evidence.

This audit asks:

Can Yggdrasil preserve provenance-safe quorum
without permanent globally assigned sensor IDs?

BOUNDARY
This is synthetic.

It does not:
- reserve packet fields in Yggdrasil;
- require literal networking packets;
- modify or execute STAB-18-R1;
- establish that sensors are explicit cell types.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

QUORUM TARGET
Semantic context commitment requires evidence from:

at least TWO independent source sensors.

Relayed duplicates from the same source must be idempotent.

PRIMARY SENSOR MODEL
4 potential sensors

per-sensor detection probability:
0.90

trials:
500,000 per primary condition.

METHOD A — EXPLICIT PERMANENT SENSOR ID
Exact provenance control.

Correct but undesirable as the architectural default because it hard-codes persistent identity.

METHOD B — ORIGIN SPATIAL SECTOR
Source evidence carries only the spatial sector in which it originated.

Duplicate relays preserve origin sector.

Two reports from the same sector count as one provenance class.

Tested sector counts:
4
8
16.

UNIFORM SENSOR PLACEMENT
Conditional missed-quorum rate when at least two real sensors detected:

4 sectors:
4.09%

8 sectors:
1.18%

16 sectors:
0.43%

False independent quorum from one true source:
0%

CLUSTERED SENSOR PLACEMENT
Synthetic clustered placement:
each sensor has 60% probability of occupying the same origin sector as a cluster center.

Conditional missed-quorum rate:

4 sectors:
28.48%

8 sectors:
21.99%

16 sectors:
19.16%

PRIMARY NEGATIVE
Spatial-sector provenance is idempotent,
but it confuses:

two genuinely independent sensors in the same region

with

one duplicated source.

This becomes severe when useful sensors cluster around the same environmental interface.

Therefore:
SPATIAL SEPARATION
is not equivalent to
CAUSAL INDEPENDENCE.

METHOD C — STABLE PER-EPOCH RANDOM SOURCE SIGNATURE
When a sensor first originates evidence for a declared context epoch,
it generates one compact random signature.

That signature:
- remains stable for that source and epoch;
- is copied unchanged by every relay;
- changes only for a later source epoch.

No permanent cross-lifetime sensor ID is required.

Quorum:
at least two distinct signatures.

SIGNATURE-COLLISION RESULTS
Conditional missed-quorum rate from accidental signature collision:

4 bits:
0.4336%

6 bits:
0.0893%

8 bits:
0.0191%

10 bits:
0.00482%

12 bits:
0.00100%

16 bits:
0.000201%

False quorum from duplicate copies of one stable signature:
0%

PRIMARY POSITIVE
A small epoch-local random provenance token can make evidence aggregation idempotent without permanent identity.

At 16 bits in this four-sensor toy:
collision-caused lost quorum is approximately:
2 per million true-quorum trials.

Do not freeze 16 bits from this synthetic result.

The required width depends on:
- number of simultaneous sources;
- tolerated collision risk;
- number of retained epochs;
- fault model.

METHOD D — REGENERATED SIGNATURE PER MESSAGE
NEGATIVE CONTROL.

One real sensor sends several copies,
but generates a fresh random signature for every copy.

False two-source quorum probability:

8-bit signatures:
2 copies:
~99.60%

12-bit:
2 copies:
~99.98%

16-bit:
2 copies:
~99.9985%

With 4 or more copies:
approximately 100% in tested conditions.

CRITICAL RESULT
The source signature must identify:

ORIGINATING EVIDENCE INSTANCE

not

MESSAGE INSTANCE.

Randomness alone does not create provenance.

STABILITY CONTRACT
A useful ephemeral signature must be stable over:

SOURCE
x
CONTEXT EPOCH

and relayed unchanged.

Conceptual key:

Signature =
ephemeral_source_nonce_for_epoch

not:

Signature =
new_random_value_per_transmission.

EPOCH ORDERING
AR-C1 already supplies bounded serial context epochs.

Therefore a provenance record can conceptually bind:

context_epoch
+
semantic_mode
+
ephemeral_source_signature.

Relays preserve all three.

A signature from an older epoch cannot satisfy quorum for a newer epoch.

LOOP SAFETY
Because merges operate on distinct provenance signatures:

receiving the same evidence around a relay loop does not increase source count.

Aggregation is idempotent:

merge(E,E)
=
E.

This is the required property from AR-C2.

COMPACT QUORUM-ONLY STATE
If the only required semantic decision is:

have at least two independent sources agreed?

the organism does not need to retain an unbounded set.

A bounded local state can retain:

signature_A
signature_B

for the current epoch/mode,

where:
- A is the first source seen;
- B is the first distinct source seen.

After B exists:
quorum=true.

Additional source identities need not be retained for a two-source gate unless confidence analysis requires them.

This bounds provenance state.

CAUTION — COLLISION
If two real sources collide:
they are conservatively undercounted.

This produces:
false lack of quorum

rather than:
false independent quorum.

That is the safer failure direction for context switching.

CAUTION — BYZANTINE / ADVERSARIAL SOURCES
This audit assumes random accidental faults,
not a malicious source intentionally forging many signatures.

Do not call the mechanism Byzantine-safe.

Adversarial ecology is a separate future lane.

CAUTION — SOURCE REGENERATION
A physical sensor that loses its epoch-local state and creates a new signature in the SAME epoch could be double-counted as two sources.

Therefore source-local signature freshness must be more stable than relay-message state.

Potential implementation strategies:
- small persistent latent nonce;
- deterministic hash of stable local latent state + epoch;
- spatial/lineage-derived seed + epoch;
- another locally stable identifier.

Each has different collision/canalization risks.

Do not choose yet.

RELATION TO YGGDRASIL
Final Yggdrasil need not implement literal:
network packets
or
integer sensor IDs.

The information requirement is:

duplicate evidence must retain enough source-instance identity
that repeated relay cannot manufacture independence.

This could be represented through:
- latent signatures;
- spatial phase codes;
- bounded source sketches;
- learned provenance features.

The synthetic ephemeral signature is a discriminating control.

CROSS-DOMAIN RULE
Again:

COPIES ARE NOT REDUNDANCY.

This rule now applies to:
- injury information;
- seasonal sensors;
- causal-credit cues;
- relayed context evidence.

PRIMARY DECISION
Reject:
mode-only packet counting.

Reject:
relay-count quorum.

Reject:
fresh random provenance per message.

Do not prefer:
coarse spatial sectors as the only provenance mechanism.

Carry forward:
stable per-source-per-epoch provenance identity,
with bounded local storage.

NEXT
AR-C4 — PROVENANCE UNDER SENSOR BIRTH / DEATH / ROLE SWITCHING

Question:
if sensor identity itself is dynamic,
how should an epoch-local source signature behave when:
- a sensor cell dies;
- another cell adopts sensing function;
- a lineage divides;
- two components reconnect?

The key seam is:
functional source independence
vs
physical cell identity.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_trials_per_condition = 500000
