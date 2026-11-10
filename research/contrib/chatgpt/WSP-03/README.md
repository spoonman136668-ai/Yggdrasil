# WSP-03 — Direct weight construction from public causal interventions (DEV only)

**Status:** proposed bounded development experiment. It is not an independent scientific first-use, production integration or demonstration of general intelligence. Source is stacked on [WSP-02 PR #862](https://github.com/spoonman136668-ai/Yggdrasil/pull/862), which retains its negative finding and is still draft and unmerged.

## What is actually constructed?

The system starts with a *programmed learning operator* rather than a pretrained predictor. It compiles binary four-input **AND threshold neurons** only when an observed public action/reward causes a nonzero prediction residual. Each new neuron is constructed by writing four input connection weights (1 where the observed context mask has a bit, otherwise 0), a threshold equal to their sum, and an XOR output edge for the relevant action.

The observed outcomes change the circuit's topology and persistent binary connection weights, **without gradient optimization**. This is nevertheless a form of **learning from experience**. The grammar (conjunctions of at most three of four context bits), outcome domain, direct weight-writing operator, and safety budget are predefined. This is neither arbitrary new mechanism discovery nor open-ended self-improvement.

The circuit stores each observed outcome and checkpoint integrity signature. At most 15 dynamic conjunction gates per action are admitted. Unsupported fourth-order residuals or conflicting repeat observations cause fail-closed abstention, not unbounded growth.

## Frozen protocol

Exact [protocol specification](protocol.txt) and [preregistration](prereg.json) are committed before the first experimental run. Full recipe:

- Four binary context dimensions, binary action, binary reward. The public base world is an algebraic-normal-form XOR polynomial of degree at most two, with coefficients fixed deterministically by SHA-256 seeds 0–15.
- Four possible new **third-degree interactions**, encoded as context masks 7, 11, 13 and 14. The novelty flag is 0 or 1, giving 16 × 4 × 2 = **128 authored synthetic DEV worlds**.
- Exactly **22** public action-outcome observations, covering each degree-0/1/2 basis context for both actions. Before any witness, score the circuit's action and reward prediction on held-out context 15.
- Reveal one actual public reward for the chosen previously unseen triple context, action 1. The circuit may add a new three-way neuron if the residual is nonzero. Assess transfer on unobserved context 15, then cold-restart and replay four already known observations without changing state.
- In **64 further negative tests**, add a previously absent degree-four interaction affecting context 15/action 1. Without the fourth-order witness, the mechanism's confidently wrong decisions count as negatives. Once this actual reward is observed, the degree-three circuit must abstain rather than invent nonexistent fourth-order capacity.

## Matched evidence; comparisons that matter

The **strongest relevant no-gradient baseline** is an exact symbolic algebraic-normal-form (ANF) solver. It receives identical observations and degree-three prior knowledge, so a tie is expected. Also compare a quadratic no-growth ablation, a state-erased circuit, and a conventional 5-10-1 tanh/sigmoid network with 71 trainable coefficients and 512 deterministic full-batch training steps on the same 23 public observations. Report train loss and runtime. **Training budget is fixed but compute and strongest-baseline convergence are not qualified.**

A correct abstention counts as an exact-policy hit only if the true actions tie. Report decisive correctness separately. Do not posthoc alter the source family, thresholds, first-use status, train steps or evaluation order.

## Reproduce in Python 3.12

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-02 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-03 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-03/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

The final GitHub CI must attest exact tree/SHA, both operating systems, source-atlas integrity and clean worktree. All experimental measurements remain **public development evidence**, not independently sourced science. No controller, training loop, live model, scheduled task, research first-use or production pathway is changed.
