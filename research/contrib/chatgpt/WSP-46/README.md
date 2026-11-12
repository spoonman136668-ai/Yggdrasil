# WSP-46 — actual action trajectories versus unrestricted source probes

This tests a major assumption behind the previous successes: can the learner still work when it cannot inject arbitrary input states? The agent starts at0, chooses one of two actual actions, receives the true next state and continues there. Only a scheduled reset to0 every64 steps is available. Evaluation reachability is never supplied to the agent.

Preregistration-only `f06002e72e1e01a33768b31fcc7bbc2e3ef159ba` precedes implementation/PRIMARY. Parent WSP45 #936. `frozen_numeric.py` is byte-identical to the WSP45 numerical learner; this study changes the evidence regime and source policy, not its learning algorithm. A pre-PRIMARY development action-gate defect initially incremented both visit banks. It was corrected to update only the selected action; a dedicated alternation/visit-count test now verifies it. The superseded DEV output is discarded; only the corrected replay is evidence.

PRIMARY:48 disjoint worlds (8/6/4 bits; linear/quadratic/cubic/hash source rules;4 seeds),512/1,024 actual source-transition budgets,96 evaluations. Controls are a numerical least-visited action policy, random actions with identical raw step/reset budgets, unrestricted numeric membership acquisition, and fully fitted one-hot regression on the active trajectory's actual facts. The membership control can choose arbitrary states and therefore may obtain very different information despite the same reply count.

The numeric source policy decodes the current state with signed-weight threshold matches, reads two visit counters and selects the smaller via threshold comparator/tie0. Generic Python simulates arithmetic and routes source replies into the two frozen numerical memory banks. Exploration policy and state representation are still provided. It is not learned action selection.

Metrics separate unseen reachable pairs, unseen all-state pairs, observed recall, reachable replay and whole-source replay. If no unseen reachable cases remain, mark them unavailable and report replay separately. Random-policy exposure to the active arm's common unseen test pairs is counted. Plans start from genuinely reachable states; primitive compositions can revisit observed states. A counterworld differing at one unobserved edge preserves the entire source transcript and exposes non-identifiability; it is not a universal impossibility proof against other priors or learners.

Unrestricted membership should recover every source map by512 raw replies at these widths. Trajectory learning can fail because the fixed all-subset coefficient learner never receives the required basis/subcube evidence; even observed-state recall can remain incomplete because its readout uses certified coefficients rather than an observed-fact fallback. Preserve that mechanism limit instead of quietly changing the frozen learner. The fitted one-hot head may recall more observed facts but has a different generalization prior, not a strongest neural baseline.

Reproduce:
```
python -m unittest discover -s research/contrib/chatgpt/WSP-46 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-46/qualify.py
python research/contrib/chatgpt/WSP-46/battery.py --cohort PRIMARY
```

Full final Windows/Linux regression and source atlas are mandatory; PRIMARY never evaluated locally. Draft external synthetic evidence only: no main/merge/accepted refs, official loop, private runner, protected first-use, controller, scheduler, paid API, integration, deployment or live action. No general-intelligence or conventional-training superiority claim.
