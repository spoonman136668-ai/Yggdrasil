# MR32-M implementation clarification

Date: 2026-10-31

This additive clarification was committed before the first execution of the
task_utility_trial.py implementation on any cohort. It does not change the
frozen MR32-M protocol thresholds, cohort IDs, task generator or model
definitions. The original protocol remains preserved unchanged.

## Feedback-stream semantics

All controllers receive the same frozen FIT episode seeds, public query
orders, task outcome process and reward function. Their selected-memory
sets can differ; therefore the set of selected-use feedback events is
necessarily policy-specific. Each controller receives only the paired
task-return delta for the memories that it actually selected and used.
No controller receives another controller's feedback, nor any feedback for
an unselected memory.

The task fixture defines a no-memory action as abstention with return zero.
A retrieved memory contributes the task return of the action encoded in that
memory (+1 for correct, -1 for incorrect). The learner is updated after the
task event using 0.5 + 0.5 * (return_with_memory - return_no_memory).
This is a deterministic paired counterfactual on the same task event, not a
second source-environment replay. The controlled fixture is intentionally
small; it is not a substitute for a future external task-reward evaluation.

## Action/target correspondence

Each memory has one frozen proposed action encoded in its public
representation. The task outcome generator now conditions correctness on
that exact stored action for the queried item and varies the Bernoulli
outcome by seed, regime, episode and task step. Thus the item metadata's
task-generating relationship governs the expected utility of the action
that the memory actually proposes. The selected action is the only action
credited by the feedback interface.

## Audit receipts

FIT receipts retain every task event's seed, regime, episode, step, queried
item, selected status per learned controller, realized task return per
controller, and the post-use feedback value for each selected memory.
An episode summary stores selected item IDs and summed task return by
controller.

TRANSFER receipts retain the same event-level and episode-level selection
and task-return detail for all five methods. The transferred models receive
zero TRANSFER feedback. Held-out outcome receipts are not fed back into any
model weights or policy state.

## Disposition

These clarifications preserve the original source-family and cohort
boundaries. The run remains a controlled task-fixture DEVELOPMENT test:
no original Farama, Pycolab, Crafter, Gridworlds or protected scientific
first-use is involved. Passing it cannot qualify FSA, establish independent
source-family transfer, or authorize integration/promotion.
