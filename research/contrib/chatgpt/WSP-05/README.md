# WSP-05 — causal-state signature learning from opaque action consequences

**Status:** isolated public **development** experiment, not an independent scientific first-use or deployment. Stacked on [WSP-04 draft PR #868](https://github.com/spoonman136668-ai/Yggdrasil/pull/868); predecessor WSP-01/02/03/04 source, negative results, owners and research loops are unchanged.

## Research shift from WSP-04

WSP-04 constructed increasingly higher-degree Boolean monomials. This experiment instead studies **causal state representation**: whether a learner can construct a useful binary representation from **action-conditioned observations and transitions**, transfer a learned action consequence to an unfamiliar opaque state identity, then reject invalid inference when a hidden behavior change becomes observable.

The learner never receives the environment's latent state class, seed, reward mask, or rule generator. All objects are identified only by shuffled opaque integers. It observes two-step action-0 consequences and creates a **new four-input one-hot binary threshold detector** on the first public action-1 outcome associated with each causal fingerprint. It learns the detector-to-reward link through experience, not by optimization of pretrained connection weights. Its initial hypothesis that equal consequence fingerprints imply equal action-1 rewards is nevertheless programmed in advance. This is **not** invention of an unanticipated mathematical primitive.

## Frozen public protocol and data budget

The [protocol.json](protocol.json) was committed first, followed by [prereg.json](prereg.json), both before implementation and scoring.

- **32 deterministic synthetic worlds**, each with 12 shuffled opaque state identities organized secretly by the evaluator into four behavior classes with three replicas. Each action has a binary reward and public successor state.
- **12 action-0 interventions per world** observe the first reward and next-state identifier for every state. The publicly observed action-0 outcome at each successor supplies the second part of a *learned* two-step signature; the hidden class is not provided.
- **8 action-1 interventions per world** expose a reward and successor from two replicas per hidden class. The third replica's action-1 reward stays unobserved until scoring.
- **128 binary held-out action-1 reward predictions** (4 per world). Abstention counts as **wrong** on this reward task, unlike earlier decision-tie experiments; separate incorrect confidence and abstention.
- Exactly 4 possible learned signature detectors per world, each with **four binary input weights and threshold 2**. The output reward bit comes directly from public experience, with zero direct gradient updates. State includes a canonical 32-byte SHA-256 integrity digest, replayable experience log and newly written detector weights. Cold-restart and already-observed intervention replay must preserve the predictions and checkpoint.

## Adversarial evidence limit

An alternative world flips only the **four held-out action-1 rewards** while leaving *all twenty public training interventions unchanged*. Until at least one of those hidden consequences is observed, the original and shifted worlds are observationally indistinguishable. Every confidently wrong prediction must be counted against the learner. After **one actual shifted held-out action-1 observation**, the original causal-equivalence assumption becomes contradictory; the circuit must abstain rather than infer the three remaining unseen labels without evidence. This is fail-closed detection, not recovery.

## Controls with matched observations

- **Independent exact symbolic causal-signature matcher:** two-step action-0 consequences plus public action-1 reward table. It receives identical evidence; a tie is expected and is the main limiting baseline.
- **One-step ablation:** only the first action-0 reward, refusing ambiguous public associations.
- **Opaque-state-ID memorizer:** stores only actually observed action-1 rewards and cannot transfer.
- **Erased direct circuit:** no observations.
- **Fully trained-to-threshold conventional baseline:** 2-input, 8-tanh hidden, sigmoid output (**33 floating trainable parameters**) using the same two-step signature inputs and 8 public action-1 labels. Deterministic full-batch Adam, seed 17, learning rate .03, stop only at binary cross-entropy ≤0.02 or **2048 gradient steps**. Measure convergence, steps, loss, and held-out correctness. Any nonconverged world is **unqualified** as a fully trained comparison, not opportunistically scored as a scientific win.

In-family matching information does not make compute and complexity equal; all exact timing and whole-process claims remain unqualified.

## Reproduce with standard-library Python 3.12

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-02 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-03 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-04 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-05 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-05/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

**Qualification:** full exact-source Python regression and isolated control tests on GitHub-hosted Windows 2022 and Ubuntu, plus source-anchored G29 atlas and clean-tree guard. The prereg's isolated changed-path scope `research/contrib/chatgpt/WSP-05/**` is extended only by read-only PR CI and mandatory **generated** source-atlas companions as transparently disclosed engineering deviations. No scheduled tasks, self-hosted runners, model APIs, independent first-use, accepted refs, new controllers, promotion, training loop or production integration.

**Scientific limits:** Even perfect performance would establish transfer over opaque identities *within a supplied two-step causal-fingerprint inductive bias*. An exact symbolic tie is not general intelligence, new math or superiority over a fully trained conventional model. Independent unfamiliar worlds and matched compute/action budget remain future scientific acceptance work.
