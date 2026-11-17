# WSP-152 — source-free Bayesian confidence ceiling, frozen negative development result

- Frozen sole-file prereg before code: `d7698974f5c2930a0bbf54ed137d41f5c6dad340`.
- Parent qualified WSP-151: `86595cd728c2978502f877e2cd6b61a9802e00d9`, source tree `8a39159776c23aed558f164b9729b73b03896ccb`.
- Standalone deterministic development program: `confidence_policy.py`; five exhaustive/negative/fabricated unit tests, `test_confidence_policy.py`.
- Source-free preflight both Linux and Windows: [run #44166833368](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44166833368) PASS, byte-equivalent output receipt.
- No WSP-151 model/prereg modification. No protected source, no first-use experiment, no native weights, no merge/accepted-ref mutation.

## Mathematical limitation

For WSP-151's explicit UNKNOWN posterior mass `q=unknown/denominator`, the posterior predictive probability of every binary output is in `[q/2, 1-q/2]`. At its previously frozen threshold 99%, if `q > 0.02`, every context must abstain, even if the supplied OR/AND grammar otherwise gives a strongly preferred law. This is an exact consequence of the existing learner; changing the threshold is NOT this experiment's remediation.

A new, separate intervention policy uses **current posterior only** to maximize the expected number of confidently predicted as-yet-uncharged contexts after one additional paid binary action. It computes two hypothetical outcomes without revealing either real effect. Numerical counterfactual weights equal an independent full posterior refit (probability-by-probability verification). Its fixed 8-action budget and the original 99% confidence cutoff match the EIG and deterministic fixed controls.

## Completed fabricated-only development (NOT original science)

- 16 independently invented source-free worlds: 12 OR/AND, 4 off-family XOR; exactly 8 do-style observations per policy per world.
- Each policy sealed predictions before comparison on the common uncharged 786 contexts. Same 16 world units, frozen 16-world FIT prior, cold digest `5545e250a39e9e140dfb9c821fc164d5606696914f0bb6c25e4325c2d6469145`.
- **Existing EIG:** 29 confidently correct, 0 confident wrong, 757 abstained, 10/16 globally blocked by UNKNOWN.
- **Fixed actions:** 114 confidently correct, 8 confident wrong, 664 abstained, 9/16 blocked.
- **New expected-confidence coverage:** 132 confidently correct, **9 confident wrong**, 645 abstained, 7/16 blocked.
- Improvement vs stronger confident-correct incumbent fixed = **+2.290076 pp** over 786 test contexts, below preregistered **+5 pp**, with **9 extra confident errors vs safest control**, violating zero-extra-error gate. Scientific_pass remains false.
- **Outcome: `SOURCEFREE_CONFIDENCE_POLICY_NO_GO`.** Do not choose the apparently more productive policy based on correctness alone.
- Both operating systems emitted the identical non-resource digest `373f478e74282944dd3578314d2b63c7dabe1f94ae51bcb5cc118c0d1e1d66c0`, world receipt `348f1e0dfdbea0b8eb3e9ffe42f6e59ad3098fcb99474da024820216721b5cea`. Measured development whole-process CPU/wall: Linux ~5.2522/5.2526 s; Windows ~9.3750/9.3637 s. No energy or native model measurements.

## Decision

Preserve the failed confidence/coverage hypothesis without post-result tuning, resampling or replay. The baseline WSP-151 stays the experimental candidate, not accepted science. Follow-on hypothesis must independently preregister unfamiliar compositional operator learning and a mechanism that distinguishes OFF-family contradictions before confident admission, tested against strong fully fitted conventional and independently derived symbolic controls. Never treat these synthetic exercises as causal discovery or general intelligence.
