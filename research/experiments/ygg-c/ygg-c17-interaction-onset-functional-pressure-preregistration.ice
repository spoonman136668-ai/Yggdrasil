TITLE: YGG-C17 Interaction-Onset Functional Pressure Test Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: df34abeeda7b4fe185f57676bf6c146a118c423b
PARENT_EXPERIMENT: YGG-C16
ONSET_PARENT: YGG-C15

QUESTION
Is the C15 interaction onset functionally necessary for the L8-L16 resource-pressure retention map?

NORTH-STAR TARGET
Determine whether the sharply localized C6 interaction is causal for pressure robustness or merely co-occurs with it.

FROZEN
- exact C16/C5 L8-L16 nested pressure construction;
- exact task, ten manifests, scheduler, recovery semantics, retention definition, learned weights, seeds, thresholds, and deterministic execution;
- no retraining or online adaptation.

ALPHAS
below_onset = 0.134765625
above_onset = 0.1357421875

C15 ANCHORS
below_onset must remain non-interaction at the C6 factorial.
above_onset must remain interaction-driven with context slots A,C.

PRESSURE SWEEP
For each alpha:
- same-alpha L8 anchor;
- exact nested L8..L16 lesions;
- exact C3/C5 retained classification.

VALIDITY
- alpha levels exact;
- strict one-cell nesting L8-L16;
- L8 inherited lesion exact;
- non-lesion fields frozen;
- learned-weight identity exact;
- matching integrity exact at every alpha/level;
- duplicate complete sweeps byte-identical;
- runtime alpha, dose allowlist, and all harness globals restored.

COMPARISON
BELOW_MATCHES_ABOVE:
retained maps identical.

BELOW_WEAKER:
every below-onset retained level is retained above onset, and at least one additional level is retained above onset.

BELOW_STRONGER:
every above-onset retained level is retained below onset, and at least one additional level is retained below onset.

CROSSING_PATTERNS:
neither retained set contains the other.

SUCCESS
YGG_C17_INTERACTION_ONSET_FUNCTIONAL_PRESSURE_TEST=true iff all validity/anchor gates pass and exactly one preregistered comparison is produced.

INTERPRETATION
If BELOW_MATCHES_ABOVE, the localized C6 interaction is not necessary for this pressure-retention phenotype.
If BELOW_WEAKER, the onset has direct functional relevance to pressure robustness.

FAILURE
Do not alter alphas, lesions, thresholds, weights, task, seeds, scheduler, or classification after results.

BOUNDARY
No further decimal bisection.
No accepted source mutation.
No online adaptation.
No recursive self-modification.
