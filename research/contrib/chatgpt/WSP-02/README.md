# WSP-02 — Directly programmed causal-interaction weights (DEV only)

**Status:** implementation awaiting independently executed engineering checks. **Not a scientific first-use result**, training-free general intelligence, or deployment claim. Stacked on unmerged [WSP-01 PR #853](https://github.com/spoonman136668-ai/Yggdrasil/pull/853); the two projects are not modified outside isolated research files plus the existing generated G29 atlas.

## Research question

Can we directly compile a known 64-member causal family into immutable network connection weights, update only recurrent hypothesis state from real public observations, and infer action preferences at unseen **combinations** of familiar context variables?

The hypothesis index is `h=(mask<<3)|(interaction<<2)|(flip<<1)|bias`, with a three-bit mask and three one-bit variables (64 possibilities). Context is three bits; action and outcome are one bit. The public generative rule is:

`reward=parity(context&mask) XOR bias XOR (action&flip) XOR (action&context_bit2&interaction)`

The last term makes action preference depend on the third contextual bit. All 64 rule candidates and their fixed connection weights are compiled **before** seeing outcomes. This is a preprogrammed hypothesis family, not intelligence emerging without prior structure.

## Frozen observations and transfer

Observe only these six public (context, action) interventions, in order: `(0,0), (1,0), (2,0), (4,0), (0,1), (4,1)`. Only the observed public rewards enter the recurrent state. Transfer queries are contexts 3, 5, 6, and 7, after the six interventions. No transfer labels are used by the weight-written system or conventional training control.

- Weight-written: 64 x 32 binary compatibility weights, plus 8 x 2 x 64 binary decision-vote weights = **3,072 fixed binary weights**; zero trainable coefficients, 64 retained state bits, 44-byte integrity checkpoint. Compilation rules and code incur real information and compute costs.
- Strong symbolic control: exact version-space enumeration over the same 64 hypotheses and six observations.
- Tabular control: empirical reward counts from identical observations; no unseen-context structural prior.
- State-erased weight-written control: exact same precompiled weights, zero observations.
- Conventional trained control: 6-8-1 tanh/sigmoid, **65 trainable FP scalars**, deterministic initialization seed 17, **512 full-batch gradient steps** at 0.05 learning rate, six public observations only. Its fixed input features are context bits, action, and two interactions. Convergence and loss must be reported, not assumed. No claimed compute parity or strongest fully trained benchmark.

## Out-of-family falsification

The frozen outside-family world adds `XOR(context_bit0 AND context_bit1)` to the reward. This perturbation is **action-independent**: it can invalidate predicted rewards without changing the best action. WSP-02 must separately report bad reward predictions before any OOD witness, bad decisive action choices, and the post-witness survival/abstention state.

The OOD witness is a single additional **observed** `context=3, action=0` reward, after pre-witness evaluation. The known family cannot explain that observation after all six initial interventions; a correctly programmed bounded candidate set must become empty and abstain. This does not establish general OOD detection or recovery. If the true reward changes only by an action-neutral offset, action preference can remain correct for the wrong reason.

## Exact reproducibility

From repository root, standard-library Python 3.12:

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-02 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-02/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

The runner emits public DEV JSON; any reported speed is one toolchain measurement only. The frozen prereg was committed first and the incorrect placeholder specification SHA-256 was explicitly corrected **before** any primary scoring. The original prereg SHA remains in Git history. All subsequent engineering qualification artifacts and optional companion workflow must be separately identified as additions outside the preregistered changed-path pattern, not concealed.

## Scientific limitations

The symbolic exact-family solver is the real comparison. Tying it does **not** demonstrate intelligence beyond programmed logic. The six observations uniquely identify all 64 hypotheses in this family. The conventional control may not converge within 512 steps, may have worse uncertainty handling, and is not a separately qualified strongest baseline. No independent environment, prospective unseen causal mechanism, compute-matched information budget, cold retention under interference, or novel generalization claim is tested here.

This contribution creates no autonomous research-loop authority, promotion, official acceptance, runner ownership, scheduler, training or production integration. It remains a research candidate requiring separate scientific first-use controls.
