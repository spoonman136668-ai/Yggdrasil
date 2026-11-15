# FKP-02 — Previously unseen causal-operator headroom

Source-only follow-on to [Issue #1088](https://github.com/spoonman136668-ai/Yggdrasil/issues/1088) and FKP-01 [PR #1089](https://github.com/spoonman136668-ai/Yggdrasil/pull/1089).

## Purpose

FKP-01 failed its development headroom requirement: exact symbolic learner identified each DEV law after three action observations. FKP-02 changes the *scientific task*, not that consumed evidence.

We want to test whether accumulating a **large connected foundation** helps a tokenless native learner *construct* previously unseen three-parent causal rules from observed action consequences, beyond flat storage of the same 16,384 training experiences and against independently trained/symbolic references.

A **novel operator relative to foundation training** is not a proof of an unbounded self-invented law; MUX3 and majority3 belong to the evaluator's general Boolean hypothesis space and a strong prior-aware Bayesian/symbolic control must remain eligible to win.

## Frozen identities and execution fences

- Yggdrasil parent `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; tree `180008502f6bdfe5a06c3d0d6f47f941dd01f20b`.
- Prereg-only first commit `30ce15f994e8aeaf4715511f6e214376ef510bf9`. All original source, controls, outcomes are subsequent.
- `prereg.json`: 256 foundation worlds ×64 real action-consequence observations = **16,384 foundation examples**, each with 16-bit input and 4-bit outcome. Source DEV 16 worlds only; protected scientific primary 64 worlds, negative 16, interference 16.
- `source.py`: public actions, genuine feedback (16 scored paid actions/world), cold held 128 distinct unobserved vectors; source-owner/HMAC private laws. Private evaluator key absent from repository and must remain outside any worker/model process, including workflow logs.
- `audit_headroom.py`: deliberately strong **family-aware** exact enumeration of 3-parent MUX/majority operators, with 16- versus 64-action source identifiability *only on DEV 200..215*. Any 64-action results used to train a learner or scored as originally held science invalidate the comparison.
- `test_source.py`: public source, deterministic fingerprints, strict action order, unique action budget, cold-held disjointness and protected-key rejection.

## Source-only qualification

Reproduce using Python 3.12 standard library, at an exact Git checkout:

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-02 -p test_source.py -v
python -B research/contrib/chatgpt/FKP-02/source.py
python -B research/contrib/chatgpt/FKP-02/audit_headroom.py
python -B -m unittest discover -s research/contrib/chatgpt/FKP-02 -p test_foundation.py -v
python -B research/contrib/chatgpt/FKP-02/foundation.py
```

The final command reports source feasibility, **not an implemented neural/native learner**. Its precommitted gate requires >=0.02 accuracy improvement from 16 to 64 source probes, >=0.98 reference accuracy at 64, and >=4/16 DEV worlds with ambiguous hypotheses at 16. On failure, preserve NO-GO, do not retune protected cohorts.

## Science, native integration and authority

A separate **public-experience-only foundation acquisition** now fits two-input truth tables by searching the 256×64 prior intervention histories. Its generic compositor then forms three-input functions from the *learned* two-input table bank with no explicit hardcoded MUX/majority instructions. Constructibility is a representation feasibility check, **not** evidence that Yggdrasil autonomously discovers these new rules after 16 fresh actions.

Stage0 source audit alone is not engineering+scientific acceptance. Stage1 still requires actual directly programmed native model, at least one fully trained strong neural/decision-tree/logical conventional comparator plus exact Bayesian/symbolic control, identical 16,384 foundation facts and 16 new-world interventions, locked capacity and whole-process budget, cold retention tests, external disjoint scientific source qualification and exact-SHA full Windows/Linux regression.

The actual `yggdrasil/public_causal_cells.py` on main is unchanged, and PR #1089's isolated source does not magically fit a broad foundation into its 128-byte learned state. Only an independently beneficial result may justify a separately scoped **real native** extension, accepted through Yggdrasil owner controls. No authority for production, main, Wingless, Hybrid, FORGE, runners/schedulers/controllers or additional scientific first-use.
