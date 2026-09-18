TITLE: DG-1A-P0-STAB-18-R1 — Wound-Memory Actual-Perception Proof-of-Concept
DATE: 2026-09-18
STATUS: SYNTHETIC REPRESENTATIONAL-CAPACITY AUDIT — NOT A CANDIDATE RESULT
TRACK: DG-1A
PARENT_CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Test whether the temporal wound-signal hypothesis survives the ACTUAL Yggdrasil NCA perception bottleneck:
- per-channel identity;
- Sobel-x;
- Sobel-y;
- followed by a shared 1x1 ReLU MLP.

This audit asks a narrow feasibility question:
can a current local state plus one recurrent hidden support-memory channel distinguish dead wound frontier from ordinary external growth frontier without enlarging the receptive field or state width?

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- prove that the trained Yggdrasil NCA will learn this representation;
- reserve a hidden channel;
- add parameters;
- preregister a repair candidate;
- establish performance on real learned phenotypes.

CURRENT NCA ARCHITECTURE
From src/yggdrasil/nca.py:
- state_channels = 16;
- visible channels = 4;
- LIFE4 occupies hidden channel 4;
- hidden channels 5..15 remain available to emergent state;
- perception per channel = identity + Sobel-x + Sobel-y;
- perception width = 16 * 3 = 48;
- learned update network = Linear-equivalent 1x1 Conv 48 -> 128 -> ReLU -> 16.

No architecture change is necessary to make one existing hidden state dimension carry temporal support memory.

SYNTHETIC DATASET
40x40 lattice.
Filled disk bodies with radii:
6, 8, 10, 12, 14, 15, 16.

Active-cell range:
113 .. 797.

Centered lesion fractions of the live bounding box:
0.20, 0.25, 0.35, 0.45, 0.50.

Total geometry conditions:
35.

For each condition:
CurrentLife =
binary live mask after lesion.

SupportMemory before lesion =
normalized prior 3x3 live-neighborhood count / 9
stored on live cells.

Lesion semantics:
all channels inside the lesion are zeroed.
Therefore SupportMemory is also zero inside destroyed cells.
Only surviving cells retain their prior local-support memory.

Candidate recruitment sites:
currently dead cells with at least one currently live Moore neighbor.

Positive class:
candidate site belonged to the pre-lesion body and was removed by lesion.

Negative class:
candidate site lies outside the original body and is an ordinary external growth frontier.

This directly models the desired discrimination:
REBUILD WOUND
versus
DO NOT EXPAND OUTWARD.

ACTUAL PERCEPTION FEATURES
For CurrentLife:
- identity at candidate center;
- Sobel-x;
- Sobel-y.

For SupportMemory:
- identity at candidate center;
- Sobel-x;
- Sobel-y.

Total:
6 features.

These are exactly the feature TYPES supplied by Yggdrasil's existing NCA perception operator for two state channels.

EXACT FEATURE-CLASS OVERLAP TEST
Across all 35 geometry conditions:
- positive and negative wound-memory perception feature classes had ZERO exact overlap.

For the canonical 709-cell / 35%-lesion example:
- dead wound-frontier candidates = 40;
- ordinary exterior-frontier candidates = 128.

Current binary LIFE4 local geometry alone remained highly ambiguous.

With SupportMemory added, no exact perception-feature vector observed on the wound frontier was observed on the stable external frontier.

This result holds for every tested body radius and lesion fraction in the 35-condition synthetic family.

SMALL-MLP PROOF OF CONCEPT
To test whether the disjoint feature classes require an implausibly complex decoder, a standalone classifier was trained with:

input:
actual-perception feature vectors described above.

network:
6 -> 32 -> ReLU -> 1.

This is substantially smaller than the existing Yggdrasil local update hidden width of 128.

Loss:
weighted binary cross entropy.

This classifier is NOT the NCA and does not model recurrent rollout.
It is a local representational-capacity control.

DATASET SIZE
Across the 35 cases:
4552 dead-frontier candidate examples.

HELD-OUT BODY-SIZE GENERALIZATION
Train on all radii except one.
Test on all five lesion fractions at the unseen radius.

WITH SUPPORT MEMORY:

held-out radius | accuracy | precision | recall | specificity
6               | 99.43%   | 100%      | 97.22% | 100%
8               | 100%     | 100%      | 100%   | 100%
10              | 100%     | 100%      | 100%   | 100%
12              | 100%     | 100%      | 100%   | 100%
14              | 100%     | 100%      | 100%   | 100%
15              | 100%     | 100%      | 100%   | 100%
16              | 100%     | 100%      | 100%   | 100%

CURRENT-LIFE-ONLY BASELINE
The same 32-ReLU classifier using only:
- current LIFE4 identity;
- current LIFE4 Sobel-x;
- current LIFE4 Sobel-y

showed substantial unavoidable confusion.

held-out-radius results were approximately:
- accuracy: 82.1% .. 86.8%
- precision: 55.6% .. 65.5%
- recall: 72.2% .. 92.5%
- specificity: 78.9% .. 88.9%

The baseline often identified wounds but also mislabeled many stable exterior-frontier sites as recruitment sites.

This is consistent with the earlier exact-pattern ambiguity result.

HELD-OUT LESION-SIZE GENERALIZATION
Train on four lesion fractions.
Test on the fifth lesion fraction across all body radii.

WITH SUPPORT MEMORY:
- 20% held out: 100% accuracy / precision / recall / specificity
- 25% held out: 100%
- 35% held out: 100%
- 45% held out: 100%
- 50% held out: 100%

CURRENT-LIFE-ONLY:
- accuracy approximately 81.8% .. 85.3%;
- precision approximately 40.0% .. 69.4%;
- recall approximately 74.1% .. 90.7%;
- specificity approximately 82.95%.

Thus the temporal support-memory representation generalized across both unseen body scale and unseen lesion scale in this synthetic family.

WHY SUPPORT MEMORY WORKS
A stable outer boundary is missing neighbors NOW, but it was also missing those neighbors BEFORE.

A wound boundary is missing neighbors NOW that were present BEFORE.

A hidden state approximating prior local support therefore converts:
static geometry
into
local temporal prediction error.

The lesion destroys memory inside the removed region, but surviving wound-edge cells retain their prior support state.
The existing Sobel perception of that survivor memory is enough to mark adjacent dead wound-frontier sites.

This is important:
the dead site itself does not need to remember that it used to exist.
Its surviving neighbors carry the temporal evidence.

MAINTENANCE-TURNOVER STRESS CONTROL
In the earlier temporal-signal audit, 1% independent random live-cell loss generated only a small number of strong survivor support-loss triggers.

A more recruitment-specific control measured FALSE OUTWARD activation:
ordinary exterior-frontier cells whose neighboring survivor memory showed >=2 lost local supports under 1% random turnover.

5000 trials per body radius:

radius | active | mean false outward sites | p95
6      | 113    | 0.0986                   | 0
8      | 197    | 0.1310                   | 1
10     | 317    | 0.1728                   | 1
12     | 441    | 0.2102                   | 2
14     | 613    | 0.2188                   | 2
15     | 709    | 0.2496                   | 2
16     | 797    | 0.2652                   | 2

Therefore the temporal representation remains highly localized in this simplified turnover model.

Randomly removed interior cells are not counted as false positives here:
repairing isolated acute cell loss is compatible with the desired repair semantics.

HIDDEN-L2 COST CHECK
Current hidden-state regularization:
hidden =
mean(result[:, visible_channels:] ** 2)

loss contribution =
1e-5 * hidden.

There are 12 hidden channels over a 40x40 lattice.

Upper-bound diagnostic:
if ONE hidden memory channel had magnitude exactly 1.0 on all 800 allowed live cells and every other hidden value were zero,

hidden mean =
800 / (12 * 1600)
= 0.0416667

weighted hidden-L2 contribution =
approximately 4.17e-7.

This is negligible relative to observed morphology/auxiliary losses on the order of 1e-2 to 1.

Real support-memory values normalized to 0..1 would generally cost less than this upper-bound toy.

Therefore the existing hidden-L2 coefficient is not an obvious capacity barrier to one bounded temporal memory signal.

PARAMETER / RESOURCE COST
A memory hypothesis can be tested without:
- increasing state_channels;
- increasing hidden_channels;
- changing grid size;
- adding a global controller;
- increasing the NCA perception radius.

It asks the existing 16-state-channel recurrent substrate to specialize one portion of its hidden state.

This aligns with Yggdrasil's developmental-intelligence objective:
specialization should emerge inside a compact shared local rule rather than through externally routed repair logic.

LITERATURE CONSISTENCY
NCA literature already treats hidden channels as cell memory / latent computational state.
Recent 2026 GNCA analyses further report:
- hidden channel modularization;
- stable spatially coherent mature cell types;
- structured temporal fluctuations that contribute to repair.

The present result is a Yggdrasil-specific feasibility study:
a particular kind of local temporal state is sufficient to solve an information ambiguity created by LIFE4 decoupling in the synthetic geometry.

RELATION TO FUTURE EXPERIMENT DESIGN
Do not alter R1.

If R1 demonstrates useful maintenance-stage causal pruning but retains the LIFE4 recruitment failure, a future preregistered packet can test whether a lesion-trained temporal support trace allows:

stable maintenance boundary:
NO recruitment

acute internal wound boundary:
local LIFE4 recruitment

repaired boundary:
signal decays

post-repair:
causal/occupancy pressure contracts redundant substrate.

A future candidate should prefer training the shared NCA to encode/respond to this temporal information rather than inserting an explicit runtime damage mask.

No exact channel, target value, memory decay, coefficient, or duration is selected here.

BOUNDARY
This is a synthetic classifier / information-capacity result.
It is not an NCA rollout result.
The standalone MLP does not include:
- stochastic fire masks;
- recurrent repair dynamics;
- continuous learned LIFE4;
- irregular real Yggdrasil morphologies;
- interaction with causal pruning;
- multi-seed robustness.

Its value is narrower:
the EXISTING Yggdrasil local perception and MLP capacity are sufficient to decode a plausible recurrent wound-memory representation in the tested geometry.

PROVENANCE
evidence_class = SYNTHETIC_ACTUAL_PERCEPTION_POC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
classifier_seed_family = 20260918
