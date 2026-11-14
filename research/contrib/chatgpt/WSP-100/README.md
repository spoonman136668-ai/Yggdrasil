# WSP-100 — development fixture construction only

**Status: engineering task-validity checks; scientific first-use UNAUTHORIZED.**

We are testing whether a six-channel, four-valued system with two hidden latches and four possible actions can exhibit delayed consequences, and whether an independent checker can detect when observations do or do not uniquely determine the answer.

**Plain English:** An action may secretly change the machine now, but that change becomes visible only on a later step. The checker examines every one of 256 possible *development-fixture* programs and asks whether all programs still compatible with the experience would predict the same unseen result. If they disagree, that prediction is not established by the evidence.

- First WSP-100 design prereg: `ac55988cbef6daafa5afd79c50bbf4ce6d5b243f`.
- Detailed fixture and audit protocol was frozen **before implementation**: `3c0db5b16255d8e9ddf6a0c23a278e9a2c84a691`.
- Only DEV worlds numbered 0–7 may be instantiated; FIT 100011–100034, TRANSFER 100101–100132, NOVEL 100201–100216, and RESERVED 100301–100332 are blocked.
- The sampled program is an evaluator-only internal, never an input to the source-side action policy or to a learner.
- Auditing 256 development variants is **not** equivalent to auditing the broader original WSP-100 causal grammar. No generalization, scientific superiority, or AGI claim.
- No gradient training, direct-weight learning, accepted-model promotion, controller/scheduler/queue, or paid API is performed.

Development command: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s research/contrib/chatgpt/WSP-100 -p 'test_*.py' -v`

The next research gate must first establish original-task identifiability against the full broad allowed grammar, freeze strong comparison models and budgets, and independently admit any original first-use. Never use fixture scores to claim intelligence.
