# WSP-100 — development fixture construction only

**Status: engineering task-validity checks; scientific first-use UNAUTHORIZED.**

We are testing whether a six-channel, four-valued system with two hidden latches and four possible actions can exhibit delayed consequences, and whether an independent checker can detect when observations do or do not uniquely determine the answer.

**Plain English:** An action may secretly change the machine now, but that change becomes visible only on a later step. The checker examines every one of 256 possible *development-fixture* programs and asks whether all programs still compatible with the experience would predict the same unseen result. If they disagree, that prediction is not established by the evidence.

- First WSP-100 design prereg: `ac55988cbef6daafa5afd79c50bbf4ce6d5b243f`.
- Detailed fixture and audit protocol was frozen **before implementation**: `3c0db5b16255d8e9ddf6a0c23a278e9a2c84a691`.
- Only DEV worlds numbered 0–7 may be instantiated; FIT 100011–100034, TRANSFER 100101–100132, NOVEL 100201–100216, and RESERVED 100301–100332 are blocked.
- The sampled program is an evaluator-only internal, never an input to the source-side action policy or to a learner.
- Auditing 256 development variants is **not** equivalent to auditing the broader original WSP-100 causal grammar. No generalization, scientific superiority, or AGI claim.
- No gradient training, direct-weight learning, accepted-model promotion, controller/scheduler/queue, or paid API is performed.

Development command: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s research/contrib/chatgpt/WSP-100 -p 'test_*.py' -v`

The next research gate must first establish original-task identifiability against the full broad allowed grammar, freeze strong comparison models and budgets, and independently admit any original first-use. Never use fixture scores to claim intelligence.

## Next gate: broader independent fixture identifiability audit

Frozen **before implementation**: `4d80e9fc3872eb72e088a04befeb6455905adf0e` (`broad_audit_prereg.json`).

The earlier 256-program DEV checker used exactly the generating family's hypothesis space. The separately implemented `broad_auditor.py` now uses **2,048** programs by considering four alternative second-stage compositions and two hidden-memory mixing laws. The true DEV programs remain embedded, but the checker must not assume the exact generating class. This is a stricter test of whether source observations genuinely determine an unseen outcome: a bigger hypothesis class can only maintain or reduce confidence.

The independent audit validates original-free source and heldout-plan SHA256 receipts, source/action counts and trajectory continuity, and the precommitted 12 paired future plans, without reading target outcomes, hidden-state or oracle rules. Negatives require empty-history ambiguity, failure on tampering, and rejection by the narrower class of a fixture-only world with altered operator composition. `broad_dev_report.py` publishes DEV diagnostic counts, never scientific acceptance. Run `python research/contrib/chatgpt/WSP-100/broad_dev_report.py` on fixtures only.

This remains a toy hypothesis catalogue, **not** the future full WSP-100 broad causal grammar; it cannot establish general intelligence, direct-weight learning benefits, or an eligible original first-use. Preserve any ceiling or underidentification observations without post-result tuning.

## Original wider DEV diagnostic: all eight worlds uniquely identifiable

- Frozen source: `fd152b20014fb6466d8c003fc583ae369b39cc2d`.
- [One-shot full 2,048-program DEV audit](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43614683066): engineering SUCCESS.
- Source/plan receipt: `3866022ac910b996ed0cd7c9e2f171fdda9898fdc42efd8c3864f025cb340111`.
- On **all eight** fixture IDs 0..7, the full observed 24 passive + 8 active episodes reduced the broadened program set to exactly **one surviving explanation**. All 432 heldout visible components per world were invariant among that set (3,456/3,456 across eight).
- Full per-world signed-by-source SHA256 receipts preserved after result in `BROAD_DEV_EVIDENCE.json`; narrow 256-program and broad 2,048-program certifiers both measured 100% DEV identifiability.

**Meaning:** This synthetic *fixture class* remains easy to identify even after broadening the search space. It is a ceiling-risk diagnostic, not a direct-weight learning breakthrough, not a full original-grammar validity result, and not permission to inspect FIT, TRANSFER, NOVEL or RESERVED world outcomes. Preserve the result; do not retune these fixture rules, evidence thresholds or split based on it. A new independent original-world task design must demonstrate real unknown-composition transfer, matched strong-control headroom, and original-source identifiability before first use.
