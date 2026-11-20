# ENERGY-29: preserved first independent-auditor failure

The frozen primary scorer completed 480 worlds successfully. The independently authored auditor then completed its source and prediction reconstruction checks but failed at the final `audit_result.json` serialization step: `TypeError: Object of type int64 is not JSON serializable`.

Cause: NumPy `int64` aggregates in the result dictionary are not directly accepted by standard `json.dumps`. This was strictly an audit output-format error, **not** a scoring failure or learner disagreement. No scored input, frozen source, seeds, thresholds or first result changed. The auditor alone was adjusted to serialize NumPy scalar integers, and its explanatory note corrected a count from 96 to 48 stratified exact-posterior cases (48 × 24 = 1,152 comparisons). The full final auditor was re-executed after this correction; the initial failure is retained for provenance.

The first attempted repair corrected the persisted JSON writer but the console-summary writer independently hit the same NumPy scalar serialization issue. Both code paths were corrected in the second auditor-only revision; the frozen experiment remained intact.
