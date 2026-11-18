# CKAD37 — Native cumulative learning across unannounced causal-rule shifts

**Scope:** isolated experimental branch; not accepted-model training, not Forge orchestration, not deployment.

The predecessor [CKAD36 draft #1253](https://github.com/spoonman136668-ai/Yggdrasil/pull/1253) had engineering PASS (Linux and Windows 382/382), but its externally specified active Bayesian intervention policy **did not** beat an equal-budget fixed-input baseline. CKAD37 stops extending that conventional inference wrapper and tests the existing native `NativeEpisodeExperience` stream's ability to learn, react to change, and retain source evidence.

## True source and model identity

The model gets an uninterrupted sequence of genuinely sampled **synthetic** two-stage public intervention episodes. Each episode supplies paired numeric views, selected first action, observed next-state, selected second action, and observed delayed binary reward. Its stable causal feature must be learned in the presence of nuisance-view variation. Across each world the environment changes **A → unfamiliar B → A return** at hidden times. The transition probability in B reverses the old causal action effect; the terminal reward mechanism changes from conjunction-XOR to conjunction-OR. Those changes are not announced to the model.

The candidate trains the actual existing `NativeEpisodeExperience(repair=True)` with `observe()` after every revealed episode, starts the native unannounced `begin_stream()` once after 48 warm-up events **before any rule change**, reads `context_forecast()` prequentially, and cold restores checkpointed native state at multiple milestones. No new neural architecture, model controller, private runtime or surrogate learn-from-oracle route is created.

## Matched conventional controls

- Same existing cumulative native episode mechanism *without* stream/context adaptation.
- Fully trained standard Beta(1,1) causal-cell posterior on **all** available source observations.
- Fully updated sliding-window 24 and window 48 Beta(1,1) causal-cell models.
- Fully updated exponential-discount 0.95 Beta(1,1) causal-cell model.
- Constant 0.5 negative control.

All arms receive identical actual observed action-consequence rows in the same chronological order. Each episode has two independently scored prequential forecasts: transition probability before next-state is known and terminal reward probability after actual next-state but **before** reward is revealed. A model never trains on the evaluator's hidden regime/shift labels or on unchosen counterfactuals.

Two independent worlds per original seed, each roughly 220–240 real synthetic episodes, with A warm, hidden B, and A return. Original pilot seeds **14071/14072**; DEV-only fixtures **88411/88412**; reserved primary **24071/24072/24073**. The model cannot receive boundary timestamps even though the evaluator partitions scores by source phases.

## Frozen decisions

Compare pooled *late B + late return A* transition/reward Brier with the strongest individually trained conventional dynamic baseline and unmodified native global memory. Both original pilot seeds must meet: native stream Brier ≤0.16 and ≥0.025 absolute advantage over **both** native nonstream and the strongest conventional alternative, and native early-B and late-return Brier cannot exceed the unmodified native learner. Exact cold byte parity, old native archival-block/source-prefix preservation, ledger identity, duplicate idempotency, contradiction atomicity, and native consolidation must PASS.

Any miss becomes `SCREEN_NO_GO`, source integrity loss becomes `INVALID`. **No retuning on consumed pilot seeds**, no primary test, no merge/promotion. Even an engineering GO does **not** prove SCIENTIFIC_PASS, real-world grounding, general intelligence, or a mature continually trained Yggdrasil model.

## Evidence handling

Frozen prereg commit `d675309bec3134a91f2fab470d736d490a4e280c` predates source. `campaign.py` will be Git blob-locked after complete pre-first-use DEV qualification and before pilot. The original two one-use pilot JSON receipts (including full public event trace, timestamp-free learner forecasts and Brier, native source hashes and checkpoints) are stored in the repository. The separate `seal_pilot.py` never imports the candidate learner or generator; it independently reconstructs the source truth, every fully trained conventional forecast and every prequential loss. Mandatory **full final Linux and Windows regression** qualifies the exact post-evidence candidate tree. The branch stays DRAFT/unmerged. No scheduled tasks or paid APIs.
