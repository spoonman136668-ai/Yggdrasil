# WSP-67 — Source-blind learning writes executable neural weights

## Why this experiment exists
The previous WSP63–WSP66 research constructed and stored causal numerical rules, but that is **not by itself direct neural weight programming**. Earlier WSP53 direct sparse-acoustic writing had negative results and weak relative controls. This successor tests our actual weight-edit research objective: **infer knowledge from charged consequences, write a three-layer neural model's W1/b1/W2/b2/W3/b3 parameters from scratch, then use its neural forward pass without consulting the symbolic compiler**.

## Prospective frozen protocol
- `prereg.json` committed first, exact prereg SHA **`3efb9568a1f5d7246ccf72992a246030344e665e`**, before any WSP67 source, model or test code/outcomes.
- Parent WSP66 [draft PR #957](https://github.com/spoonman136668-ai/Yggdrasil/pull/957) exact SHA `827e0682e7f57842eeb1cfc855a274e574fbec1a`, structured pair design LOST to same-action-budget random (169/1024 vs 489/1024), full inherited regression not then closed. No original source or negative evidence modified.
- SELFTEST-only seeds `4101..4108` using a new WSP67 physics generator. Four shuffled visible binary sensor roles, four shuffled physical action channels, causal flip effects conditional on positive/negated one- or two-sensor conjunctions. Some actions affect two output sensor bits. All source physics, shuffled action roles and evaluator labels remain **only in `source.py`**.
- **96 charged consecutive no-reset physical source actions/world** with one seeded random action policy common to ALL learning arms. Stage A after 64 actions, Stage B after 32 additional actions from the same uninterrupted physical session. No arbitrary-state training queries, source imports, paid API, evaluator task feedback or protected DEV/PRIMARY data.

## Actual neural weight construction
- During **learning only**, the programmer enumerates the source-blind constant and at-most-two-literal conjunctive *flip* hypotheses for each action/output bit. It writes an executable numeric **8→H→13→5 ReLU neural network**: action+condition detector weights, four current-state residuals, ReLU XOR cross-terms, and an in-network confidence head.
- The confidence head is a learned bank of state/action indicator neurons for inputs where all remaining hypothesis functions agree. **These neurons contain no outcome labels.** Output content is computed by the factorized causal detector neurons; every direct heldout prediction uses **only the forward neural matrix operations**.
- After 64 actions, serialize and cold restore real matrices. After 96, directly rewrite weights using the enlarged source-blind evidence. Track changed/nonzero neural parameters, stage A→B confidence/correctness, and cold restore **from matrices alone without rebuilding the learner or replaying evidence**.
- No gradient updates for the writer. Important: the *compiler* is an externally engineered symbolic rule search, and the gate topology/hypothesis grammar match this source family. Success proves **bounded evidence-to-weight compilation**, not autonomous general neural architecture formation or open-world AGI.

## Independent, same-evidence controls
- Exact state/action memory with identical charged rows and the same two-step composition tasks.
- **Separate symbolic implementation** that retains all <=2-literal predicate candidates and predicts only by unanimous consistency. This is a **strong source-aligned control** that may tie the neural compiler on accuracy. Ties do not establish neural superiority.
- **Independently trainable gradient MLP** (8 inputs, 24 ReLU, 4 sigmoid outputs), random initialized and optimized on the same 96 charged physical observations, 8000 SGD steps cap with train-only >=98% exact-training accuracy stopping condition after minimum 2000 steps. Report any unconverged case as *INCOMPLETE BASELINE*, never a direct-weight advantage.
- Neural all-zero-parameters and erased confidence head controls to ensure success actually requires constructed weights.

## Frozen heldout criterion
- Exhaustive `8 ×16 ×4 = 512` physical source consequences scored only AFTER learning; previously observed versus **never observed** source input/action pairs reported separately.
- 32 new independently sampled **two-action compositions/world** (256 total) with public starting state, action IDs and hidden intermediate/outcome used only for evaluator scoring. A two-step neural result must be confident at both steps.
- Preregistered exploratory `SELFTEST_SIGNAL` requires ≥48 **unseen** correct confident physical predictions, **zero** wrong-confident physical predictions across all 512, ≥120/256 two-action exact neural outcomes, ≥20 more correct all-domain than equal-evidence exact memory, no forgetting of Stage A confident-correct predictions, nonzero weight changes in ≥4/8 worlds, and 8/8 cold matrix-only restoration + tamper rejection.
- If any fail, preserve `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`. Even a passing synthetic SELFTEST does **not** establish neural superiority over independently trained models, unbounded direct neural learning, linguistic knowledge, cross-family transfer, or general intelligence.

## Reproduction, authority and limitations
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-67 -p 'test_*.py' -v
```

Focused Ubuntu/Windows CI, source-pinned generated-only G29, and inherited full Linux/Windows regression qualify **separately** on the final exact candidate. No merge, promotion, protected first-use, deployment, new controller, paid API, scheduled task or official Yggdrasil/FORGE research-loop integration without separate existing authority.
