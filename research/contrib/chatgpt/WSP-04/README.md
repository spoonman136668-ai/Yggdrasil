# WSP-04 — bounded causal grammar expansion by direct weight writing

**Status:** public synthetic DEV experiment, not independent scientific first-use or deployment. Stacked on [WSP-03 #863](https://github.com/spoonman136668-ai/Yggdrasil/pull/863). Its predecessors are unmerged drafts; no research loop is modified.

## What this actually tests

WSP-03 could compile only degree-three context conjunctions; it rejected an unfamiliar fourth-order causal relation. WSP-04 gives the same general kind of recurrent compiler a five-bit input and a generic binary AND-threshold gate emitter. When a real action/outcome observation has a nonzero unexplained residual, the compiler writes the input weights of a **new degree-four neuron**: each of five binary connections is set from the witnessed context mask, and its threshold is the number of active bits. The node connects to a fixed XOR readout for the observed action. This is **learning from experience without gradient descent**.

The gate compiler, binary data representation, XOR logic, sparse-coefficient extrapolation assumption, and finite capacity were all programmed in advance. The specific weights of each newly formed fourth-order cell are *not* supplied as a candidate list in the model. This is a bounded extension of the prior grammar, **not** discovery of an entirely unknown computational primitive.

## Frozen challenge and information limits

[Protocol](protocol.json) and [preregistration](prereg.json) were committed before initial results. Context has five bits, action and reward one bit. For each of 120 public synthetic worlds (8 deterministic seeds × 5 fixed degree-four-mask pairs × modes with 0, 1 or 2 novel terms), the learner sees all 26 lower-degree basis contexts for both actions: 52 public outcomes. It then sees two additional *actual* action-1 rewards at the selected fourth-order masks, one at a time. Its unobserved transfer query is context 31.

Report results **before** either new observation, **after only the first**, and **after both**. The second case is important: acquiring one valid rule can temporarily make a prior extrapolation worse when another unseen rule cancels its effect. Test cold restoration and replay of four previously seen outcomes. No transfer labels are used for learning or training.

The frozen fifth-order negative flips the binary reward of action 1 at context 31 after all positive tests. Only two of five degree-four coefficients have been identified. A discrepancy at context 31 therefore cannot be uniquely attributed to a fifth-order rule. Before the contradiction is revealed, report any wrong confident decisions. After one real contradictory observation, the safe result is **abstention**, not invented rule recovery.

## Independent controls

The strongest comparator for this pilot is independent exact symbolic algebraic-normal-form coefficient inversion with the **same sparse extrapolation prior and information**. Matching this comparator does not constitute a scientific advantage. The degree-three no-growth ablation shares the same data but refuses novel degree-four residuals; the erased-memory circuit receives no observations. A conventional 6–12–1 tanh/sigmoid MLP with 97 trainable scalar weights is trained from seed 17 for 256 full-batch steps at learning rate 0.05 on the exact same 54 public observations. This budget is fixed, but does **not** qualify the strongest fully converged or compute-matched baseline. Do not call the MLP result a definitive comparison of training versus direct weight programming.

## Reproduction and authority

Using Python 3.12 and only the standard library:

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-02 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-03 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-04 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-04/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

**Mandatory:** full final regression at exact candidate SHA on Windows and Linux, pinned G29 source atlas, clean tree and isolated negative controls. The original contribution change-path freeze covers only `research/contrib/chatgpt/WSP-04/**`. Any generated source-atlas artifacts and one read-only PR-triggered CI workflow are engineering qualification companions outside this scope, must be documented as deviations, and cannot confer scientific acceptance.

No merge, production model change, scheduler, new autonomous owner, model calls, paid APIs, GPU training, first-use experiment, or live research-loop dispatch is authorized or performed. Preserve unsuccessful outcomes and report source SHA, receipts and cold-retention evidence.
