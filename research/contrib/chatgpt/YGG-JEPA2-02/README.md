# YGG-JEPA2-02 — source-frozen native causal multilearner

**STAGE: preregistered source preflight; no new original-world scientific first use.**

This independent development branch extends the already qualified [CKAD37 native causal stream](https://github.com/spoonman136668-ai/Yggdrasil/pull/1260) with a separately learned transition specialist and terminal specialist, each trained from the same authenticated public observed interventions as original `NativeEpisodeExperience`. Neither specialist uses hidden world identities, phase labels, future outcomes, tokens, or privileged source states.

The formal preregistration was committed before implementation at `f00d39793bff2091b7c74c05192a873725e675c2` and explicitly preserves Yggdrasil's negative development [JEPA2-01](https://github.com/spoonman136668-ai/Yggdrasil/pull/1259) as precedent. No training parameters or acceptance rules may be changed based on the scored source results.

The source snapshot is [CKAD37 qualified parent](https://github.com/spoonman136668-ai/Yggdrasil/commit/60634ab8c46b13039e021f28f8fa70bb6b69db96); the two original pilot receipts were already consumed and have independently verified Git blobs. This is actual native recorded experience, **not a toy generator**, but also not new held-out scientific first use.

The first workflow stage checks current native APIs, source pins, model checkpoint integrity, deliberate tampering and replay before undertaking complete source-bound training. Scientific acceptance and deployment remain disabled.

## Pre-training qualification note

The first preflight run #44414711518 demonstrated 5/5 NEW multi-learner integrity tests PASS on Linux (also no learner source error), but the job was marked FAILURE because an inherited focused test glob named a nonexistent file and Python exited code 5 on zero discovered tests. This was corrected in the CI selector only at commit 4ae58e04e82b161eb6a98569d7761cac4573cb48; training code, frozen thresholds, prereg and original source inputs remain unchanged. Full source-bound native training is guarded by renewed successful Linux and Windows preflight.

Engineering-only preflight correction: run #44414890149 passed all five new native multi-learner unit tests, then failed two existing sparse-repair tests because that CI stage had not installed the original pinned numpy/scipy dependencies. The dependencies were added in commit 9e2265834c93396df613d2a8abdde2a4842a2a49. No model algorithm, preregistration, source identity, budget or score changed. The next trigger requires two-platform preflight success before the source-bound training job executes.

## Immutable original-evidence sealing correction

All 4/4 Linux and Windows preflight/train jobs in [run 44415015937](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44415015937) passed, and each platform independently audited the original 919 observed episodes and cold-restorable trainable model. Both frozen seed results are DEVELOPMENT_NO_GO. The source evidence sealer failed ONLY because different OS float serialization changed an advisory checkpoint byte count, while original native checkpoint bytes are checked separately. The sealer was corrected to compare semantic learned weights within a frozen 1e-9 tolerance and native source bytes exactly. Recover using the two immutable already-uploaded original ZIPs; DO NOT repeat original training/scoring to seal.
