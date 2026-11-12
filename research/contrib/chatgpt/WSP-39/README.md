# WSP-39 — maximum-first programmed action model (PUBLIC DEV)

A single frozen, broad training-free capability test. The evaluation constructs a model from actual queries of unknown state transitions, rather than loading all source relation facts, and then scores unfamiliar-state prediction, 2–4-step rollouts, depth-three goal planning, checkpoint retention, a local causal intervention and negative controls.

**The strong known-family bound:** four actions each transform a binary state by an unknown affine GF(2) map. The fixed general-purpose numeric interpreter is authored software. A zero probe and every basis-state probe uniquely identify the affine transition parameters. Without full basis evidence, the same model cannot infer omitted columns. An adversarial nonlinear pair interaction is invisible to zero and singleton probes and must cause held-out failures. No labels or hidden matrices are passed to the learner.

One PRIMARY includes five descending state widths (1024, 512, 256, 128, 64), two world families (affine, nonlinear OOD), two information budgets (full and half basis), four frozen PRIMARY seeds (1049, 1051, 1061, 1063), 80 episodes, 32 one-step queries, eight unseen multi-step sequences and three hidden-oracle-goal planning tasks per episode. Action depth is fixed at three, only 64 routes. All experiments run on CPU with standard-library Python.

The main control is an independently fitted GF(2) sparse-operator model reconstructed from *the same captured probe replies*; it also performs the same goal-planning search. Literal observed-state lookup and empty identity/zero controls are included. A secondary world is stored and verified unchanged following a single-weight repair of the first model. Cold restoration, corruption rejection and non-interference are tested.

**Scientific limitation:** exact construction of a known representable operator family is not general neural intelligence, language cognition, or independent acquisition of unknown rules. Neither exact fit nor fewer gradients proves better all-in performance than fully trained neural baselines. We explicitly preserve negative results for nonlinear rules and incomplete evidence; this research may receive ENGINEERING PASS and SCIENTIFIC_NEGATIVE.

Preregistration-only commit: `98131c1419dd2a697c85338087e4ce7ce06776c4` preceding implementation and frozen PRIMARY.

From repository root:
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-39 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-39/battery.py --cohort DEV
python research/contrib/chatgpt/WSP-39/qualify.py
python research/contrib/chatgpt/WSP-39/battery.py --cohort PRIMARY
```

This is a draft external contribution only; no main, official accepted refs, protected science, Yggdrasil/Wingless/FORGE/Hybrid integrations, schedulers, private runners, paid APIs, deployment, live actions, or autonomous controller modifications.
