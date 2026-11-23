# CCE-02 — Bounded interventional signature discovery

**Research-only; separate from CCE-01 and from native Yggdrasil acceptance.**

- Parent before preregistration: 4092b3ce41438f948056b12c6f4ccdadcd9b3d1d.
- Frozen CCE-02 preregistration commit: d32644ef28d120e80351f24d0ace59f666996cde.
- Fixed implementation + test + evaluator commit (before result): acd54f2c21cba294088d4db6cbdf630cc03b7553.
- Primary outcome recorded in result.json; source file SHA256 and runtime context in provenance.json.

## What was attempted

A tiny, bounded, action-grounded set of *conditional reward-predicting contracts* learns from public probe, observation, terminal action and reward. It receives neither the hidden binary regime nor the identity of the informative probe. Its local counters estimate reward likelihoods under action/observation signatures, and a **central, disclosed, non-neural** evidence gate selects a single probe after 512 randomized training episodes.

The environment is purposely simple: in the positive world, probe 0 yields a 90%-accurate noisy measurement of an unobserved binary regime, while probe 1 is uninformative; in the negative world both probes are uninformative. A terminal action is rewarded for matching the regime. **The terminal reward is itself highly informative about the hidden regime once the action is known, so this is not an unsupervised emergence of object identity.** The learner discovers which *intervention* is useful for decision making under this constrained interaction model. It has neither autonomous structural growth nor compositional reasoning.

No oracle regime labels or generator rules are supplied to the learner. Both the proposal and full-table controls train on the same 512 open-loop intervention/action/outcome records per seed, and are frozen during the 256-episode evaluation. One preregistered seed list for each of two worlds; no extra data or post-score tuning.

## Measured result (first recorded synthetic primary evaluation)

| Metric | Frozen result |
|---|---:|
| CCE-02 success, positive world | 0.87578125 |
| Uniform-probe full-table control | 0.69375000 |
| Full-table best-trained-probe control | **0.87578125** |
| Pooled memoryless control | 0.48593750 |
| Positive correct probe 0 | 5/5 seeds |
| Null-world spurious selection | 0/5 seeds |
| Exact serialized/cold state | 5/5 seeds |
| Checkpoint resident payload per positive seed | 374–375 bytes |
| Frozen development classification | **DEVELOPMENT_SIGNAL** |
| Scientific gain relative to strongest trained control | **0** |

CCE-02 beats random probe choice on this synthetic task by 18.20 percentage points, but **ties the strongest fully informed trained table baseline**. It is a functional proof of the intended evidence-gating behavior, **not a superior learner**, general intelligence, self-generated concepts or native scientific improvement. It must not be promoted as SCIENTIFIC_PASS.

The experiment is also not a matched proof of computational efficiency: although checkpoint bytes are recorded, no full-table checkpoint-byte comparator or runtime/energy win has been independently qualified.

## Engineering-only tests

From the project root:

    python -B -m unittest discover -s research/contrib/chatgpt/y2-cce02 -p test_cce02.py -v

Development benchmark (already consumed once and recorded; do **not** rerun as a new first-use trial):

    python -B research/contrib/chatgpt/y2-cce02/run_cce02.py --output research/contrib/chatgpt/y2-cce02/result.json

The eight deterministic unit fixtures test positive intervention admission, null restraint, malicious checkpoint tampering and forgery rejection, public-data validation, frozen budget, and serialized prediction continuity. Local focused tests passed on Linux CPython 3.13.5. This is **not** the mandatory full candidate regression.

## Limits and next falsification

The central mechanism is still a hand-bounded fixed set of public-feature signature cells. The environmental task indirectly reveals latent regime through rewarded actions. Thus it has not solved representation emergence, persistent identity under partial observability, reusable causal abstractions, or transfer.

The next study should **separate the identity discovery mechanism from a direct terminal-action label surrogate**. It should enforce multiple environments, delayed effects, unfamiliar compositions, competing predictive hypotheses, no privileged label channel and strong trained HMM/POMDP/explicit-memory controls. Freeze a new experiment ID before accessing any original evaluation outcomes. Do not tune the completed CCE-02 results.

## Isolation and CI

Draft PR #1367 and branch research/y2-cce01-causal-contract-ecology-20261123 only. Source and experiment evidence cannot authorize changing existing accepted Yggdrasil components. The repository G29 atlas check remains **FAIL** because the existing committed atlas indexes a source file set from before these new research files. Use only the existing source-pinned generator to produce the exact three G29 artifacts on a validated source SHA; do not bypass it, edit generated .ice by hand, dispatch a runner, or fabricate a passing CI receipt.

Full Windows/Linux regression, source tree identity, native first-use and independent reproduction are unverified. No protected merge or deployment.
