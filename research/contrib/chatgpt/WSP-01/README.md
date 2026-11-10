# WSP-01 — Directly weight-written causal network (DEV only)

**Status:** `DEV_MECHANISM_VERIFIED_SCIENCE_UNVERIFIED`. No real-world intelligence, independent first-use, or acceptance claim. Implemented solely as an isolated Yggdrasil research contribution; no existing model, controller, training or runtime interfaces are modified.

## Question

Can we directly program a fixed-weight recurrent network that carries an explicit causal inference procedure, instead of initializing random weights and using gradient descent? Yes for this tiny, fully specified family. This is a **compiler for a known rule family**, not evidence that cognition can be constructed for unfamiliar worlds from first principles.

## Frozen synthetic mechanism

The public rule is `reward = parity(context & context_mask) XOR (action & action_flip) XOR bias`, where context is 2 bits, action and reward are 1 bit, and the latent 4-bit rule describes exactly 16 hypotheses. Hypotheses are enumerated in ascending `h=(mask << 2)|(flip << 1)|bias` order. The four observed `(context, action)` interventions are `(0,0),(1,0),(2,0),(0,1)`; only genuine public outcomes update the state. The transfer query is context `3`, an unseen combination. The model never receives the true hypothesis index.

An input is encoded as 16-dimensional one-hot `(context, action, observed_outcome)`. The 16×16 binary compatibility matrix is compiled from the rule and is immutable. A recurrent threshold gate preserves a candidate only when its previous state and the new compatibility weight both equal one. An immutable 4×2×16 binary readout chooses an action only when **every** remaining hypothesis agrees on a strict advantage. Inconsistency or ambiguity produces abstention. Model state is 16 bits; its integrity-checkpoint is 38 bytes. The 384 static weights and compiler source are part of the persistent information cost and are **not free**.

There is no gradient, optimizer, tokenizer, transformer, downloaded model or model API. This fixed-weight system **does still learn about a world** through four real action-outcome observations and state updates. It does not eliminate the need for information or generalize beyond the specified model class.

## Independent controls and limits

- **Strong control**: symbolic exact hypothesis elimination with the *same pre-programmed rule family*. Must tie the network.
- **Tabular**: identical four experiences but no built-in cross-context composition, abstains on unobserved context 3.
- **State erased**: same programmed weights, no observed outcomes.
- **Negative controls**: insufficient evidence abstains; contradictory evidence yields no candidates and abstains; malformed observation and corrupted checkpoint are rejected; cold restoration reproduces state and decision.

In the 16 public DEV fixtures the weight-written and exact symbolic arms each scored 16/16, with eight correct action decisions and **eight correct abstentions**. Tabular and erased-memory arms each scored 8/16 by abstaining on the eight true ties. The symbolic tie means there is no new cognitive capability over the strongest control. All fixture data and scoring rules are visible to the author and cannot qualify as independent or prospective generalization evidence.

## Reproduction

From the repository root, in Python 3.10+ (3.13.5 was used for the local test):

```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p 'test_*.py' -v
```

No libraries beyond the Python standard library are required. The files `prereg.json`, `dev_result.json` and `provenance.json` bind the freeze and the measured local development result. The single-run development wall time is not a comparable cost measurement. New scientific first-use would require independently sourced environments, a fully trained conventional baseline, data/compute/action parity, and separate qualification/authority before any promotion.
