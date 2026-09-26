TITLE: YGG-C19 Maturity Failure Localization Preregistration
DATE: 2026-09-26
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_RESULT: YGG-C18 MATURITY_GATED
PARENT_RUN: 36228903415

QUESTION
Which frozen replicate loses maturity immediately below the interaction onset, and is that same replicate responsible across pressure levels 8..16?

FROZEN
- exact YGG-C18 above/below alpha values, levels 8..16, manifests, learned weights, task, scheduler, retention predicates and maturity predicate;
- no threshold redefinition, retraining, online adaptation, topology change, or accepted-baseline mutation;
- deterministic execution.

DESIGN
Re-evaluate the exact YGG-C18 above and below arms and expose per-replicate maturity predicate outcomes at every level 8..16. No scientific parameter changes are permitted.

REPORT
For each alpha arm and level report actual replicate IDs failing maturity, maturity pass count, retained state and the other existing retention predicates.

CLASSIFICATION
SINGLE_STABLE_REPLICATE: exactly one actual replicate fails maturity below onset at every level and no replicate fails maturity above onset.
LEVEL_DEPENDENT_REPLICATE: below-onset failing replicate set changes with level.
MULTIPLE_REPLICATES: any below-onset level has more than one maturity-failing replicate.
ABOVE_ONSET_MATURITY_FAILURE: any above-onset level has a maturity-failing replicate.
OTHER_VALID_PATTERN: valid evidence matches none above.

SUCCESS
YGG_C19_MATURITY_FAILURE_LOCALIZATION=true iff evidence is valid, actual replicate IDs are preserved, duplicate analysis is byte-identical, YGG-C18 aggregate outcomes are reproduced exactly, and exactly one classification is emitted.

FAILURE
Do not change alpha, levels, maturity threshold, retention predicates, manifests, weights, task, scheduler, or classifications after results.

BOUNDARY
Diagnostic only. Synthetic computational research only. No production integration. No online adaptation. No recursive self-modification.
END
