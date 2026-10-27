# ITD-02 source-blind native action-score fusion: prospective gate (2026-10-27)

Authority: isolated source-free engineering only. No original world/source access, no FSA first-use, no accepted-branch or controller authority, no model promotion. Exact unchanged original reference is draft PR #582 `a39171a76d0d7817e3563682bb139a9d7ecf37c4`.

## Prior grounding

The current original `NativeTaskRingBridgeDev.choose()` fuses two already-learned, public-only scores as `memory[i] + .15 * native[i]`. The original eight-cell native predictor produced distinct action reward scores for two public observations that aliased completely at the memory head (source-bound independent native-local diagnostic run #40575348091). A third neighbor-only memory relay resolved the raw feature aliases but gave essentially no task reward improvement relative to its 50%-larger messaging budget (run #40576214826). This suggests the fixed fusion may undervalue genuinely informative native prediction relative to a locally ambiguous memory signal.

## Exactly one locked hypothesis

For the **candidate only**, change the fixed native score weighting in `NativeTaskRingBridgeDev.choose()` from **0.15** to **0.60**, leaving local memory policy, native predictor, reward training, native eight-cell topology, training parameter count and checkpoint format untouched. Fixed source-blind weights; no context-specific reward oracle, extra state or learned meta-controller. No adjustment after examining this holdout. Original `native_reward_scores` and native learning remain unaltered.

The candidate must prove that the original public-native prediction is used more effectively in *actual action choice*, not merely that its precomputed score is different. Structural negative controls: tampering public data still forbidden; frozen training veto still holds; native predictor changes on actual rewarded public events; cold interpreter restore retains both model identities and behavior; no increased trainable parameters or message count; source SHA verified byte-exact.

## Prospective discriminating evaluation

Do not reuse earlier search/selection family or seed IDs. Use **synthetic family IDs 22..29 and seeds 20..27**, independently evaluator-hashed reward maps, original public observation domain and three original public actions. Four independently acting comparators: the original native baseline, modified native candidate, and *for each exact source checkout* the same three simple fully acting public-only conventional actors (full-history reward means, EMA 0.5, last-six reward window) under the identical source-blind action exploration and 90 initial + 90 unfamiliar/changed episodes. Four jobs: Linux & Windows × reference & candidate, each 8 families × 8 seeds × 4 actors × 180 = 46,080 public actor-events. Forced actions and reward feedback only to chosen action. A fresh independent Python interpreter verifies a checkpoint at the phase boundary for every native trial.

**Decision rule fixed before experiment:** The hypothesis survives as development only if both initial and unfamiliar mean native actual on-policy reward improve relative to the frozen reference on the matched family/seed pairs and all native tests pass. Report reward deltas on all 64 paired trials (wins/ties/losses), per-family breakdown, explicit gap to the best on-policy conventional baseline and resource/retention overhead. Do not claim an underlying generic real-world causal model or unfamiliar environment first-use. If one phase worsens, reject and do not promote. Even if both improve, remain draft until separate G29 exact-source Atlas, consumer retail benchmark, durable process-restart source custody, independent world/family validation and FSA gates.

The hypothesized relative weight 0.60 was chosen before any work on the locked new families/seeds. No repeated optimization over this same held-out split. Original research structures and running work remain untouched.
