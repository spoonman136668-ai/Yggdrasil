TITLE: YGG-C16 Near-Onset Pressure Sweep Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: 1c19f852ff1472abf167246ac70eef2c11aa5106
PARENT_EXPERIMENT: YGG-C15
PRESSURE_PARENT: YGG-C5

QUESTION
Does the minimal observed positive learned-control blend alpha=0.1357421875 preserve useful behavior across the full accepted L8-L16 fine resource-pressure sweep, compared with the established alpha=0.25 regime?

NORTH-STAR TARGET
Move from local interaction onset to robustness under scaling/resource pressure.

FROZEN
- exact C5 L8-L16 nested one-cell pressure construction;
- exact ten manifests, task, scheduler, recovery semantics, matching, retention definition, learned weights, seeds, and deterministic execution;
- no retraining or online adaptation.

ALPHAS
near_onset = 0.1357421875
reference = 0.25

LEVELS
L8 through L16 inclusive.

For each alpha:
- use that same alpha for the L8 anchor and every pressure level;
- run exact C5 nested lesions;
- compute the exact C3/C5 summary and retained classification versus the same-alpha L8 anchor.

VALIDITY
- alpha levels exact;
- strict one-cell lesion nesting L8-L16;
- L8 exact inherited lesion;
- non-lesion fields frozen;
- learned-weight identity exact;
- matching integrity exact at every alpha/level;
- duplicate complete sweep byte-identical;
- runtime alpha and all harness globals restored.

REPORT
For each alpha:
- retained_by_level map L8-L16;
- first failure level;
- first recovery level after any failure;
- max retained level;
- correct-completion-area ratios;
- stream-noncollapse by level.

COMPARISON CLASSIFICATION
NEAR_ONSET_MATCHES_REFERENCE:
retained maps are identical.

NEAR_ONSET_WEAKER:
every near-onset retained level is also retained at .25 and at least one .25 level is not retained near onset.

NEAR_ONSET_STRONGER:
every .25 retained level is also retained near onset and at least one near-onset level is not retained at .25.

CROSSING_PATTERNS:
neither map contains the other.

No classification is required to be favorable.

SUCCESS
YGG_C16_NEAR_ONSET_PRESSURE_SWEEP=true iff all validity gates pass and exactly one preregistered comparison class is produced.

FAILURE
Do not alter alphas, lesion construction, retention thresholds, weights, task, seeds, scheduler, or classification after observing results.

BOUNDARY
C15 fine-bisection series remains closed.
No accepted source mutation.
No weight update.
No online adaptation.
No recursive self-modification.
