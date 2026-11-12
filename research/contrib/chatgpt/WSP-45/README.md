# WSP-45 — numerical acquisition inside a fixed learning machine

The learner's observation decoder, probe winner, memory writes, incremental Boolean coefficient updates, coverage certificates and readout are fixed threshold/dot-product/synaptic state transitions. Reuses the principles of WSP15/WSP24. The actual learning path does not call a task-specific external compiler or search candidate programs. Generic Python simulates the fixed arithmetic; integrity validation and the independent external control use separate symbolic transforms.

Preregistration-only commit `31dd280493c685d4dc2e471604fc29ea12016146` preceded implementation and PRIMARY. Parent WSP44 #935. This does **not** port all WSP44 adaptive randomized interventions into neurons; it isolates internal acquisition arithmetic, coverage and a numerical first-missing query policy. The feature family and learning rule are still programmed.

PRIMARY:48 worlds (8/6/4 bits, linear/quadratic/cubic/arbitrary output rules,4 disjoint seeds),3 evidence phases each,144 evaluations. Linear phase supplies zero and all singletons; quadratic phase adds all pairs; full phase supplies every state. Partial phases grade32 genuinely unseen source states/action. Full phase is **exhaustive trained-state replay**, never unseen generalization.24 action compositions and4 plans per phase are scored separately. A single real replacement reply after full learning must repair a point edit, preserve the other action/second world, and update all affected numeric coefficients.

Numeric certified coefficient writes are compared against an independent external exact compiler on identical facts and priors. A fully fitted one-hot least-squares control sees the same actual replies and must fit every supplied label; it is a weak prior for low-degree generalization and not a strongest-neural comparison. Erasure/disabled learning and cubic/hash early-phase negatives are retained. The learner has preallocated all2^width Boolean features; it does not discover a new primitive or grow an unbounded representation.

Local6 tests and12-world DEV completed after protocol freeze. Linear and quadratic unseen transfer worked at sufficient low-degree evidence; cubic/hash early failures persisted. Full truth learned arbitrary rules but only from complete source observations. Point repairs/cold/isolation checks passed. PRIMARY was not evaluated locally. A pre-PRIMARY evaluator clarification checks negative preservation separately in all four family/early-phase groups; it changes no data, budget or thresholds.

Memory includes truth/partial/seen task bits, bounded subset counters, fixed address/order wiring, derived certified coefficients and checkpoints; analytical task-bit counts do not represent total Python heap. Instrumentation and validation/IO/simulation costs are included in whole-process timing. Output masks and action IDs are provided, unrestricted source membership probes remain available. This is not general intelligence, internal invention of a learning algorithm, prior-free knowledge or data/compute superiority.

Reproduce:
```
python -m unittest discover -s research/contrib/chatgpt/WSP-45 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-45/qualify.py
python research/contrib/chatgpt/WSP-45/battery.py --cohort PRIMARY
```

Isolated contributor draft; no merge/main/accepted refs, official loop, protected first-use, private runner, controller, scheduler, paid API, integration, deployment or live actions.
