# WSP-06 — All-weight construction of a bounded causal task solver

**Public synthetic development experiment.** Stacked on unmerged [WSP-05 PR #870](https://github.com/spoonman136668-ai/Yggdrasil/pull/870). The predecessor's fully converged trained and symbolic baselines are retained, not replaced. No new FORGE/Yggdrasil/Wingless research-loop work, controller, schedule or training was triggered.

## What is programmed, and what still runs in software?

WSP-01 through WSP-05 manually computed causal signatures and learning operations in Python, even when they generated some connection weights. WSP-06 moves the **entire bounded WSP-05 task-specific solver** into explicit numerical matrices interpreted by a generic sequence of arithmetic neural operations.

The program has **two fixed neural layers**: a four-neuron signature classifier with twelve explicit numeric coefficients, and an action-routing matrix with four explicit numeric coefficients. All **177 persistent writable slots** are zero at initialization, divided into: successor transition weights (12 × 12), action-0 reward weights (1 × 12), action-0 coverage weights (1 × 12), signature-to-action-1 reward weights (1 × 4), signature observation coverage weights (1 × 4), and a fail-closed safety weight (1 × 1). **193 total scalar weight slots**.

A raw event contains only state ID, action, reward, successor ID. The host performs an identity-only conversion to one-hot coordinates; it does not supply the hidden class, correct consequence fingerprint or generated reward rule.

The **fixed recurrent inference tape**, executed by one generic matrix interpreter, computes:

`raw state onehot → learned successor synapses → successor action-0 reward → two-bit causal consequence → fixed 4-neuron threshold classifier → learned action-1 reward readout`.

The **fixed local plasticity tape** uses numeric action-routing gates and one generic binary Hebbian outer-product/OR synapse rule to update those matrices. Causal knowledge is stored in the weights themselves: no Python per-state transition dictionaries, class map, hand-computed signature, symbolic reward table or gradient fitting is used for the direct circuit. Repeated data are idempotent; a genuine incompatible observation sets the **plastic numeric fail-closed latch**.

This is a small recurrent circuit **simulated by Python**, not a physical implementation of all cognition. The host still implements generic matrix multiplication, thresholding, synaptic update primitives, raw input encoding, output decoding and integrity checks. The prior that two action-0 consequences determine transferable state equivalence is **programmed in advance**. The experiment does **not** establish arbitrary new representations, general intelligence, or every possible neural operation residing in self-contained weights.

## Frozen before outcomes

[Public protocol](protocol.json) and [preregistration](prereg.json) were committed first. No primary outcome was observed before that freeze.

Use the **unchanged WSP-05 authored synthetic evaluator** from its exact parent SHA `6c45a20af790d7eca8d1b69387559000b2bc4d03`. Each of 32 worlds supplies 12 action-0 observations plus 8 action-1 observations from opaque state IDs, then 4 unseen action-1 rewards for **128 heldout binary prediction queries**. Abstentions count as incorrect.

Independent strongest controls are the WSP-05 symbolic two-step state-signature matcher and its 33-trainable-parameter tanh/sigmoid baseline trained to the frozen BCE threshold ≤0.02 (full-batch Adam; 2048-step cap, seed17). Also disable transition weights, disable fixed signature weights and erase learning memory to verify the result depends on the numeric circuit.

After all baseline observations, an alternative synthetic world flips **only** the held-out action-1 rewards. The public experiences are identical; before a hidden-label witness, all confidently wrong predictions count as negatives. After one genuine contradicting observation, the weight-coded safety latch must cause abstention. No hidden facts are inferred from that single witness. Test cold checkpoint integrity, replay of four old events, input validation and cross-world model isolation.

## Reproduce using Python 3.12 and no installed ML dependencies

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-02 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-03 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-04 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-05 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-06 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-06/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

Require **full exact-candidate SHA qualification** on GitHub-hosted Linux and Windows, source atlas guard, clean working tree, correct restored weights, all prior tests and negatives. Only `research/contrib/chatgpt/WSP-06/**` is new research source. A single read-only PR-triggered CI workflow and three generated G29 code-atlas files are necessary **engineering companions outside the frozen research path**, not a change to the experiment.

**Scientific status:** Development mechanism and cost *may* be supported by measurements, but superior data efficiency, training efficiency, native intelligence, novel unseen-world generalization, or independence from a generic synapse interpreter is **not established**. Do not merge or promote from this result. No autonomous loop or live first-use performed.
