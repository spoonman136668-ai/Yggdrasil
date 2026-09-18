TITLE: DG-1A-P0-STAB-18-R1 — Temporal Wound-Cue Geometry Generalization Audit
DATE: 2026-09-18
STATUS: EXPLORATORY SYNTHETIC OOD-GEOMETRY AUDIT — NOT A CANDIDATE RESULT
TRACK: DG-1A
PARENT: WOUND-MEMORY ACTUAL-PERCEPTION POC

PURPOSE
Test whether the temporal local wound cue discovered on disk organisms is merely exploiting disk geometry, or whether it generalizes to qualitatively different boundaries:
- convex;
- rectangular;
- branched;
- multi-lobed;
- concave;
- pre-existing internal holes.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- establish real Yggdrasil repair;
- select a future classifier or hidden-channel semantics;
- claim universal shape invariance;
- hide failure on hard concave/large-lesion cases.

TRAINING DISTRIBUTION
The local classifier was trained ONLY on filled disks.

Training radii:
6, 8, 10, 12, 14, 16.

Training lesion fractions:
0.20, 0.25, 0.45, 0.50.

Features:
exact Yggdrasil-style identity/Sobel-x/Sobel-y perception for:
1. current binary LIFE4;
2. one retained local SupportMemory field.

Network:
6 -> 32 -> ReLU -> 1.

Training samples:
2964 dead-frontier candidates.

Training fit:
100% on the synthetic disk training set.

The purpose of this audit is out-of-distribution geometry, not training fit.

HELD-OUT MORPHOLOGY FAMILY
Seven shapes were generated inside the same 40x40 bounded grid:

shape      | active cells | geometric feature
ellipse    | 467          | smooth anisotropic convex
rectangle  | 609          | flat edges / sharp corners
cross      | 441          | branched concave boundary
dumbbell   | 399          | two lobes + narrow bridge
crescent   | 360          | strong concavity
annulus    | 596          | stable internal hole
C-shape    | 533          | internal + external concavity / opening

None of these shapes appeared in classifier training.

LESION FAMILY
For every shape:
- lesion fractions 0.20, 0.30, 0.40, 0.50;
- five lesion locations:
  central,
  left-offset,
  right-offset,
  upper-offset,
  lower-offset.

When a requested center fell outside the body, the nearest live body cell was used.

Total:
140 out-of-distribution shape/lesion cases.

CLASSIFICATION QUESTION
For each currently dead cell adjacent to current life:

POSITIVE:
the site belonged to the pre-lesion organism and was removed by the lesion.

NEGATIVE:
the site did not belong to the original organism and is ordinary exterior space or a stable pre-existing hole/cavity.

This is the local recruitment distinction needed for selective repair.

TEMPORAL SUPPORT-MEMORY RESULT
Mean over 140 OOD cases:

accuracy:
96.9815%

precision:
91.6580%

recall:
84.3035%

specificity:
99.2485%

The classifier therefore preserved a very low outward / stable-hole false-positive rate on morphologies it never saw during fitting.

BY SHAPE
ellipse:
- accuracy 97.90%
- precision 100%
- recall 90.10%
- specificity 100%

rectangle:
- accuracy 98.64%
- precision 100%
- recall 94.44%
- specificity 100%

dumbbell:
- accuracy 97.37%
- precision 96.86%
- recall 88.31%
- specificity 99.53%

annulus:
- accuracy 96.46%
- precision 87.80%
- recall 87.81%
- specificity 98.41%

C-shape:
- accuracy 96.62%
- precision 89.64%
- recall 83.14%
- specificity 98.93%

cross:
- accuracy 95.71%
- precision 97.13%
- recall 80.03%
- specificity 99.51%

crescent:
- accuracy 96.17%
- precision 70.18%
- recall 66.30%
- specificity 98.36%

IMPORTANT HARD CASE
The strongest weakness is not uncontrolled exterior growth.
It is missed wound sites on difficult concave / large-lesion geometry.

Worst representative case:
crescent,
50%-class large/off-center lesion family:
wound recall can fall substantially below the disk regime.

Another representative hard case:
crescent,
40% lesion,
off-center:
- accuracy approximately 89.94%;
- precision 80%;
- recall 46.15%;
- specificity 97.90%.

This failure is retained explicitly.

INTERPRETATION
The temporal cue is substantially more geometry-general than a disk-specific coordinate trick.

It can distinguish:
- acute missing internal tissue;
from
- ordinary stable external space

even on:
- sharp corners;
- multiple lobes;
- persistent internal cavities.

However, one simple support-memory representation does not provide complete recruitment coverage for strongly concave / large wounds.

This supports using temporal information as one injury cue,
NOT promoting one support-memory scalar as the entire repair representation.

CURRENT-LIFE-ONLY CONTROL
The same 32-ReLU classifier was trained on the same disk data using only:
- current LIFE4 identity;
- current LIFE4 Sobel-x;
- current LIFE4 Sobel-y.

Across the 140 OOD cases:

accuracy:
67.3465%

precision:
35.4231%

recall:
78.8092%

specificity:
63.8565%

The static classifier often detected wound-like boundaries but mislabeled large amounts of ordinary exterior/cavity frontier as repair sites.

Examples:
rectangle:
- mean accuracy approximately 26.15%;
- mean specificity approximately 11.54%.

cross:
- mean accuracy approximately 35.60%;
- mean specificity approximately 27.52%.

This is strong synthetic confirmation of the information ambiguity already identified analytically:
current local LIFE4 geometry alone is not sufficient for reliable general wound-vs-boundary discrimination.

STABLE-HOLE RESULT
The annulus is particularly informative because it contains a permanent internal dead region.

A purely geometric rule risks treating that hole as a wound forever.

The temporal classifier generalized to the annulus with:
- approximately 98.4% specificity;
- approximately 87.8% precision;
- approximately 87.8% recall.

Therefore temporal state history can substantially distinguish:
stable internal absence
from
new internal absence.

It is not perfect, so persistent holes remain an important future control.

MECHANISTIC CONSEQUENCE
Temporal information appears to encode something closer to:
"this local structure changed unexpectedly"

rather than:
"there is empty space next to me."

That property is precisely what a developmental repair mechanism needs if it must preserve legitimate:
- outer boundaries;
- concavities;
- cavities;
- non-convex morphology.

RELATION TO PREDICTIVE-ERROR HYPOTHESIS
The geometry audit strengthens the move from raw SupportMemory toward learned local prediction error.

SupportMemory already generalizes strongly,
but hard cases show that one scalar local expectation is insufficient.

A richer predictive state can condition expected transitions on:
- local cell type;
- visible phenotype;
- latent module state;
- developmental region;
- recent trajectory.

This could retain the geometry-general advantage while increasing coverage on concave and large wounds.

NO TARGET-GEOMETRY REQUIREMENT
The local classifier receives:
- current local state;
- retained local temporal state.

It does not receive:
- target mask;
- absolute x/y coordinates;
- shape identity;
- lesion location.

That boundary is important for Yggdrasil's developmental architecture.

LIMITATION
These shapes are hand-constructed binary geometries, not trained NCA phenotypes.

The classifier was evaluated on frontier classification only, not full recurrent continuous repair for all 140 cases.

The audit therefore establishes information generalization,
not end-to-end regeneration.

NEXT RESEARCH USE
Do not tune this classifier into a future candidate.

Use the result to define future controls for any learned injury-state experiment:
- convex shape;
- branched shape;
- strong concavity;
- stable internal cavity;
- off-center lesion;
- large lesion;
- no-spurious-growth exterior control.

A repair mechanism that works only on the canonical centered disk is not sufficient evidence for the broader Yggdrasil thesis.

RELATION TO STAB-18-R1
R1 remains unchanged and prior.

This audit is contingency research only.

PROVENANCE
evidence_class = EXPLORATORY_SYNTHETIC_OOD_GEOMETRY_AUDIT
canonical_scientific_execution = false
new_yggdrasil_training_run = false
ood_case_count = 140
classifier_hidden_width = 32
