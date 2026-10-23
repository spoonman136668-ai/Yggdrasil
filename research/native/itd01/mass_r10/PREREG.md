# Mass Research R10-F — finite 32-probe identifiability challenger (frozen first)

**Status:** SOURCE-ONLY SYMBOLIC RESEARCH GATE / NO LEARNER OR ORIGINAL COHORTS / NO CKB ADMISSION.
**Frozen source parent:** Yggdrasil independent Mass R8 PR #420, commit `587ee450ca2a74140d2357e814a1c2eab56314d0`. This file is the first change on an isolated independent audit branch, separate from native Yggdrasil R10 prereg draft #422 `c0e442f6295d2b520ea5e27f3222f229ad6ce25a` and R9 #421.
**Scientific role:** Challenge—not author, choose, or instantiate—the future R10 unfamiliar-family environments.

## Exact predeclared falsification question

Does population identifiability of distinct action-conditioned causal worlds imply a family-blind learner can distinguish the worlds using only the **32** publicly allowed R10 adaptation/intervention episodes? **No in general.** Prove the gap *without sampling episodes*, source-generator calls, model training, test-DEV data, or privileged H1/H2 use.

Compute exact equal-prior Bayes-optimal hypothesis-identification error from `n=32` independent diagnostic binary responses under known symbolic likelihoods `P(y=1|world0)=p` and `P(y=1|world1)=q`. The privileged knowledge of p and q **favors** this oracle; its lower bound applies to any learner with equal or less information on this fixed interface. Compute rational
`R(n,p,q) = 1/2 sum_{k=0..n} min(Binomial(n,p)[k], Binomial(n,q)[k])`.

Frozen source-free contrast families:
- `STRONG`: p=1/4, q=3/4
- `MODERATE`: p=2/5, q=3/5
- `WEAK`: p=9/20, q=11/20
- `UNIDENTIFIABLE`: p=q=1/2

Second constructive lower-bound witness: `RARE_LATENT` binary outcome under a fixed most-informative probe: W0 always reports 0; W1 reports 1 only if an independent hidden trigger occurs with probability 1/64 per legal probe. No legal alternative probe conveys more information. The exact minimum error under equal priors and 32 actions is `(1/2)*(63/64)^32`. This demonstrates why a *rare, independently changing* hidden causal condition may remain unidentifiable with 32 adaptation episodes even though the population distributions differ. Also compute the minimum number of probes needed to make error <=1/20 using only rational arithmetic (no floating point).

**Advisory reference target:** Bayes identification error <=1/20 (5%) for the 32-probe oracle. This target is a **predeclared diagnostic display threshold only**. It is NOT added retroactively as a scientific pass criterion to the frozen R10 preregistration and cannot authorize/deny scientific first use. Do not claim R10's actual unknown source laws are tested by these toy worlds.

## Implementation and controls

Add a deterministic Python 3 stdlib `finite_probe.py` using `fractions.Fraction` and `math.comb`, with `--audit` JSON output. Add `test_finite_probe.py` that asserts hand-checkable identities R(0)=1/2, exchange symmetry, equal-probability R=1/2, exact strong/moderate/weak ordering, rare-world closed form, 32-budget used, and threshold minimum-step inequality. Fail on invalid probabilities/negative n. Exact output uses numerator/denominator pairs plus human-readable decimals and explicit privilege/authority disclaimers. No random generator, filesystem source access, network, supervised labels or DEV/HELDOUT inputs. Intentionally do NOT call it an independent source-birth witness.

## Result interpretation (frozen)

- If some worlds are very easy, conclude **feasibility for those contrived oracle-known distributions only**.
- If others are hard, conclude **32 public actions do not guarantee identification** even for distinguishable distributions, and flag **R10_SOURCE_CERTIFICATE_NOT_ESTABLISHED** until a truly independent source-born finite-budget identifiability certificate arrives with concrete source paths and legal interventions.
- Do not infer native Wingless/Yggdrasil superiority, causal emergence, full CPU/RSS/resource matching, first use or heldout transfer.
- Preserve Q19A's exact population proof and Q19B's finite-trained negative [FORGE #729](https://github.com/spoonman136668-ai/FORGE/pull/729), [#730](https://github.com/spoonman136668-ai/FORGE/pull/730), and Mass R8's native omitted-action proof [Yggdrasil #420](https://github.com/spoonman136668-ai/Yggdrasil/pull/420).

**Execution authority:** Existing CKB-plane only. Local symbolic analysis or draft GitHub CI is not a controller command, admission, first-use reservation, source-generation act, model qualification, or protected ref promotion.
