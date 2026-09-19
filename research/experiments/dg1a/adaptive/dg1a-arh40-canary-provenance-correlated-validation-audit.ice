TITLE: DG-1A-AR-H40 — Canary Provenance / Correlated Validation Failure Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE PROVENANCE-DIVERSE VALIDATION RESULT + HARD GLOBAL-COMMON-MODE NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh39-in-manifold-template-poisoning-versioned-promotion-audit.ice

PURPOSE
H39 showed that versioned shadow promotion can protect shared generative memory against in-manifold poisoning,
provided the promotion canary is trustworthy and independent from the update stream.

H40 attacks that assumption.

QUESTION
What happens when:
- the template-update stream;
- and one or more promotion canaries;

share the same corruption provenance?

BOUNDARY
This is synthetic.

It does not:
- establish cryptographic trust;
- freeze a quorum rule;
- prove real Yggdrasil canaries have these source families;
- solve all-source common-mode corruption;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BASE POISON TASK
Same focused in-manifold family-prior task as H39.

Coefficient dimensions:
3.

True clean family mean:
[0,0,0].

Poisoned update stream:

+0.8 shift
along coefficient dimension 0.

Update blocks:
120.

Updates per block:
100.

Shadow update EMA:
0.08.

Validation every:
5 blocks.

Canary samples per source per validation:
160.

The poison remains inside the current family basis.

CANARY SOURCE CONDITIONS

CLEAN INDEPENDENT
Three independent clean canary sources.

ONE CORRUPTED FAMILY
One poisoned canary source
+
two independent clean canaries.

RAW RELAY MAJORITY
One poisoned canary source is copied:

6 times.

Plus:
2 independent clean canaries.

A raw vote treats all 8 messages as independent.

PROVENANCE-COLLAPSED
The six poisoned relays are recognized as one source family.

Authority is evaluated at:
family level

not:
message-count level.

GLOBAL COMMON-MODE
All canary families receive the same poisoned context/value bias.

COMPARATOR 1 — RAW MESSAGE MAJORITY
Each received canary message votes whether:
shadow
outperforms
live.

A simple majority authorizes promotion.

This intentionally treats relay copies as independent evidence.

PRIMARY RAW-RELAY RESULT
200 matched poison streams.

RAW RELAY MAJORITY

final true live-template excess error:
0.20610.

mean successful promotions:
7.95.

PRIMARY HARD RELAY NEGATIVE
Six copied poisoned canaries overwhelm two clean independent canaries.

The candidate appears strongly validated
only because one bad source has been counted six times.

Thus:

RAW VALIDATION MESSAGE COUNT
IS NOT
INDEPENDENT VALIDATION EVIDENCE.

This reproduces the source-copy problem already found in:
S8
H10
H18.

COMPARATOR 2 — FAMILY-LEVEL PROVENANCE
Collapse relay copies into one canary family.

The validation layer now sees:

1 poisoned family

+
2 clean independent families.

This prevents duplicated provenance from multiplying authority.

A simple family-level majority substantially reduces corruption relative to raw relay counting,
but one corrupted family can still occasionally influence promotion under noisy finite samples.

COMPARATOR 3 — STRONG INDEPENDENT-FAMILY AGREEMENT
For high-impact shared-template promotion,
require:

all three independent canary families

to show that shadow improves on live.

This is deliberately conservative.

It is a discriminating research rule,
not a frozen production quorum.

POISON RESULT
200 matched streams.

THREE CLEAN INDEPENDENT CANARIES

final excess error:
0.

median:
0.

mean promotions:
0.

ONE CORRUPTED FAMILY
+
TWO CLEAN FAMILIES
with unanimous family agreement required:

mean final excess error:
0.000464.

median:
0.

95th percentile:
0.

mean promotions:
0.02.

PRIMARY PROVENANCE-DIVERSE POSITIVE
A single corrupted validation family no longer has enough authority to promote a poisoned shared template.

The live family memory remains essentially clean in the tested condition.

This is the desired failure direction:

VALIDATION DISAGREEMENT
->
HOLD LIVE TEMPLATE.

Not:

average the disagreement until the poison wins.

GLOBAL COMMON-MODE HARD NEGATIVE
All three independent canary families are now corrupted in the same direction.

200 matched streams.

UNANIMOUS FAMILY VALIDATION

mean final excess template error:
0.18500.

mean promotions:
5.86.

PRIMARY HARD NEGATIVE
When every validation family shares the same corruption:

PROVENANCE DIVERSITY
DOES NOT CREATE
VALIDATION INDEPENDENCE.

All canaries agree
and
all canaries are wrong.

This is the shared-template analogue of:

H10:
global structural common-mode artifact.

H18:
global context common-mode corruption.

Thus:

CONSENSUS
CANNOT MANUFACTURE
INDEPENDENCE.

LEGITIMATE-DRIFT COST
Strong cross-family agreement also slows real adaptation.

The H39 legitimate family drift is repeated:

true coefficient mean moves from:
0
to
0.8

over 60 blocks,
then remains stable.

All three canary families are clean and track the true family state.

200 matched streams.

UNANIMOUS FAMILY VALIDATION

late stable excess error:
0.00261.

peak drift error:
0.02438.

mean successful promotions:
10.62.

first post-drift promotion:

mean:
15.75 blocks.

median:
15 blocks.

FAMILY MAJORITY
for comparison:

late stable error:
0.00114.

peak:
0.01787.

first promotion:
mean 12.33 blocks.
median 10.

PRIMARY SAFETY / PLASTICITY TRADEOFF
Requiring stronger independent-family agreement sharply reduces poisoned promotion,
but increases legitimate adaptation latency.

This is appropriate for:
HIGH-LEVERAGE SHARED MEMORY.

The write threshold should depend on:
how many capabilities the shared state can affect.

CANARY PROVENANCE OBJECT
A validation source should carry at least:

SOURCE / FAMILY PROVENANCE

+

CURRENT TRUST

+

ACTION / UPDATE EXPOSURE

+

FRESHNESS

+

CORRELATION / COPY RISK

+

VALIDATION RESULT.

Several raw canary messages with the same provenance should not multiply promotion authority.

CURRENT SHARED-TEMPLATE PROMOTION PIPELINE
UPDATE STREAM

->
SHADOW TEMPLATE.

Then:

MULTIPLE PROVENANCE-DIVERSE CANARY FAMILIES

->

FAMILY-LEVEL VALIDATION RESULTS

->

INDEPENDENCE / COPY CHECK

->

PROMOTION CONFIDENCE

->

PROMOTE
or
HOLD / ROLLBACK.

RELATION TO H39
H39 established:
independent validation protects against in-manifold poisoning.

H40 qualifies that:

INDEPENDENT
must mean:
independent failure provenance,

not:
different message IDs.

RELATION TO H10 / H18
The same architecture law now appears in:

structural-memory evidence;

context fingerprints;

causal controls;

shared generative-template promotion.

The recurring rule is:

COUNT FAILURE-MODE DIVERSITY,
NOT OBSERVATION COUNT.

GLOBAL COMMON-MODE LIMIT
If:
update stream
and
all canary families

share the same corruption,
passive validation is under-identified.

Another source of truth is required.

Possible future source:

FUNCTIONAL REGENERATION CHALLENGE
against a real local consequence signal.

This is analogous to H12/H20:
observational agreement may nominate,
but causal functional consequence must ultimately authorize.

DECISION
AR-H40 is POSITIVE for provenance-diverse promotion validation,
with a HARD NEGATIVE for global common-mode canary corruption.

Supported synthetically:

- copied corrupted canaries can overwhelm clean sources if raw messages are counted independently;
- provenance-family collapsing removes relay-count authority inflation;
- strong agreement across independent canary families sharply suppresses single-family poison;
- stronger validation safety slows legitimate family adaptation;
- globally shared corruption defeats provenance diversity.

Not demonstrated:

- real Yggdrasil canary provenance;
- optimal quorum rule;
- real common-mode corruption detector;
- functional regeneration challenge for template promotion;
- distributed canary trust under cell birth/death.

CLEAN SCIENTIFIC PAUSE
H36-H40 now form a coherent generative-lineage-memory sequence:

H36:
related retired lineages can share a compact generative basis.

H37:
template families can merge/split according to memory price and persistent fit cost.

H38:
off-manifold corrupt lineage updates should be quarantined,
but legitimate coherent shifts must remain learnable.

H39:
in-manifold slow poisoning requires shadow versioning and independent promotion canaries.

H40:
promotion canaries themselves need provenance diversity;
copies are not independent,
and global common-mode corruption remains unresolved.

NEXT HIGH-VALUE MOVE
AR-H41 — FUNCTIONAL REGENERATION CANARY FOR GLOBAL COMMON-MODE TEMPLATE FAILURE

Question:

When:
update evidence
and
all observational canaries

agree on the same bad template change,

can a tiny bounded regeneration/function challenge reject that candidate because:

the candidate does not actually improve regenerated local function?

Compare:

A.
observational canary consensus only;

B.
functional regeneration micro-challenge;

C.
value-gated functional challenge;

D.
legitimate family drift;

E.
global common-mode poisoned candidate.

Desired:

global observational corruption
->
fail functional promotion.

legitimate family evolution
->
pass functional promotion.

This remains synthetic until a real target-free functional consequence signal exists.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
coefficient_dimensions = 3
poison_blocks = 120
updates_per_block = 100
canary_sources = 3
relay_copy_stress = 6 poisoned copies + 2 clean sources
primary_poison_streams = 200
legitimate_drift_streams = 200
