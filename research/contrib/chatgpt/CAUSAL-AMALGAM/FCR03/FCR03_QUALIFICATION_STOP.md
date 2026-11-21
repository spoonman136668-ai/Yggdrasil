# FCR03 qualification stop: uninformative action choice and saturated transition score

**Disposition:** `SAME_FAMILY_ACTION_AND_STRICT_TRANSITION_GAIN_STOP`. Retrospective evidence audit, not a fresh FCR04 study or authorization to train. Keep the failed candidate archived; do not retune, merge or promote it. Preserve the original consumed eight-seed/2,944-event trial as `DEV_NO_GO`.

## Source and evidence identity

- Research owner: single Yggdrasil Amalgam coordinator [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), pinned `86264b41a08d49f558418c0fba367f3a2636befa`.
- Accepted Yggdrasil `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, unchanged.
- FCR03 one-time source-free development outcome: `DEV_NO_GO`, original commit `e9ba639b038b4f18f2ada68b8b5576687ae0740c`, Git tree `a71c6fbcb9e460c21c1bda977a076062b2cca301`.
- Prior source-code and analytic action-identifiability audit commit: `7dd3322e1d3a6d7c26c7d4805a54b9e1e442b014`; [full audit](FCR03_ACTION_IDENTIFIABILITY_AUDIT.md).
- The stop audit in `qualification_ceiling.py` verifies original Git blobs of the source, the XZ raw-result archive Git blob `f9ca478fe6ff6d3fd7b694d70ec279c22bebfe34` and its decompressed SHA256 `a81297f6a0f0bf7c982f7c8656af85be92c432e321b5e49dfbea9b5beee92cee`. It uses the already frozen original numeric results; **no new trial was executed**.

## Mathematical ceiling: not another promising trial

FCR03's deterministic affine models always predict probabilities in `[1/16, 15/16]`. A perfectly identified deterministic outcome cannot yield an in-class Brier score below `(1/16)^2=1/256=0.00390625`. In original recombination phase C, both the candidate and the strongest equal-information affine-Bayes control attained exactly **0.00390625** on transitions. Their predictions already met that protocol-specific bound. A strictly positive candidate transition Brier gain is therefore **impossible within the same probability-clipping rule and deterministic transition family**. A *tie* does not mean the complete preregistered research comparison could succeed: the candidate's reward and old-memory return gates in fact failed.

The original return-phase transition Brier was `0.0572265625`, versus strongest matched `0.02239503154664356`; excess `+0.03483153095335644` exceeds allowed `+0.020`. Original recombined C reward Brier `0.077734375` vs hazard-Bayes `0.030970337824882153`; excess `+0.04676403717511785`. These are real negatives. The mathematical transition floor **only** restricts interpreting improvements on the saturated C task; it does not erase the failed other gates.

## Action identifiability: choosing another intervention cannot fix this fixture

FCR03 compared deterministic A vs B transition `s2=x1 XOR c` vs `s2=x1` and reward `y=s2 XOR x2` vs `y=s2 XOR x2 XOR c`. Public context `c` was drawn exogenously, not influenced by action. Complete enumeration proves at `c=0`, **both** action choices have **zero** model separation, and at `c=1`, **every** action separates them. The reward result remains true at all public `s2` and `x2`. Context `c=1` was already observed in **310/640** C-phase episodes (at least 30 for each prior seed).

The audit also includes a separate analytic **positive sanity contrast** where two hypothetical laws are distinguishable by a different action depending on context: A predicts zero; B predicts `(action XOR context)`. At c=0 action 1 is informative; at c=1 action 0 is informative. Context-aware choice distinguishes in both contexts, while one fixed action distinguishes in only one. This confirms the decision gate is not constructed to reject every action-information design. **It is algebra, not a source, trained model, fresh trial, proof of native policy learning, or a positive scientific gain.**

## Decision for the cumulative learner

**STOP FCR03 same-family experiment variants.** Do not create another controller, independent learner, or action-policy trial on this frozen A/B source. Failure localization now points to actual *detector/recall state, prequential adaptation and cold retention*, not selection of `x1/x2` actions. CKAD36 PR #1253 previously found fixed and active actions tied under its own restricted source; CKAD25-AB PR #1270 has a narrow positive native historical-intervention development signal but its fully trained conventional Beta learner ties the same actions and outputs. Neither is proof of a uniquely capable learner or justifies repeating protected first-use.

Before a **distinct future experiment** is considered, its frozen contract must provide and independently verify: (1) action-conditional causal outcome distributions whose separation **changes with available actions and contexts** (unlike FCR03), (2) genuine future action cost and delayed effect where relevant, (3) learned model state carried by **the one existing native cumulative learner** and an independently cold-restored true prior checkpoint, (4) matched actions/observations/compute against fully trained exact Bayes/HMM/change-point, fixed, random, target-only and symbolic controls, (5) unfamiliar causal operators or hidden-state shifts outside the supplied law library, (6) old task retention with preset **+0.020 Brier drift bound**, and (7) resource `<=2x` baseline on one exact SHA/platform. Full Linux and Windows regression, independent reproductions and separately authorized source-owner original-world first-use are mandatory for scientific acceptance. **Current owner issue #426 does not authorize protected new-world first-use.** Do not choose new seeds or start a trial merely to complete this documentation gate.

**ENGINEERING:** prior 17/17 plus 4 new read-only focused tests = **21/21 local Python stdlib tests PASS**; original Git blob identity and frozen result checks PASS. Full exact candidate cross-platform final regression **UNVERIFIED**. **SCIENTIFIC:** `SCIENTIFIC_PASS=false`; no new original-world episodes, transfer, scientific gain or model promotion. **DEPLOYMENT:** none. No merge, runner/workflow dispatch, paid API, controller change, accepted SHA change or user workstation requirement.

### Reproduce retrospective certificate

From this **same exact FCR03 research branch**, not an earlier unpinned copy:

```bash
cd research/contrib/chatgpt/CAUSAL-AMALGAM/FCR03
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_mechanism_recall.py test_dev_trial.py test_identifiability_audit.py test_qualification_ceiling.py
PYTHONDONTWRITEBYTECODE=1 python qualification_ceiling.py
```

`qualification-ceiling.json` is a deterministic, source-pinned read-only summary. Its stored bytes are not generated by an action simulator or scientific evaluation. Original research issue/coordinator owner and unchanged P0 custody must independently qualify any new science.
