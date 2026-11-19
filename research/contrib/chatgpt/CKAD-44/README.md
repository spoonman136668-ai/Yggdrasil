# CKAD44 — Source-contrastive causal evidence vs Bayesian changepoint baseline

Research development only. This new independent native Yggdrasil-contributed mechanism follows **CKAD43's frozen DEV_NO_GO** and reuses its source architecture without editing accepted model code or rerunning old science. Parent exact SHA `d11cb31d7fad45d917068703982c9ab4df85e2bc`, original source-independent preregistration `0c613f55a2e5d68d5bbc9ce21a5b8fbc8a84e0a7`.

## Falsifiable hypothesis

Earlier CKAD43 made a second retained causal expert from raw surprise and sometimes created B *50 episodes before a real change*, then oscillated. This successor instead trains a **persistent learned causal A reference from the first 64 authentic observed episodes** and **continually trains a second learned causal model on all genuine source observations**, without hidden phase, oracle labels, or future rewards.

At the 64-episode freeze, the source generator is known from the task contract to be in A; using that warm-stable period is a **declared task-specific structural advantage**. It does *not* prove unsupervised change detection in genuinely unknown time structures, and no first-use or transfer claim is permitted.

For each subsequent already observed intervention and paired transition/terminal consequence, both learned causal source models issue prequential probabilities; only then is their log-likelihood ratio added to a fixed 12-observation history. At the next prediction, the old A belief comes from an equal-prior soft Bayesian ratio, clipped to [-8,+8]. If the evidence window fails to include both distinct first and second intervention values, the candidate falls back to the continually trained model; it does not pretend a single action can identify a causal relation.

The prediction is a source-trained weighted mixture; after observing the next state, the separate terminal forecast correctly updates the mixture weight by that **already observed transition**, but never by the future reward. The first 64 source observations remain a byte-exact cold-restorable frozen reference throughout the run. The original native `NativeEpisodeExperience` keeps learning sequentially from precisely the same witnessed public events.

## Fully fitted conventional causal-change comparator

A distinct **Bayesian online change-point Beta filter** is trained on the exact same actions and outcomes. Its run-length states have a fixed per-event hazard 1/72 and a cap of 48; it keeps independent Beta(1,1) posterior counts per public transition and terminal intervention cell. Each real observed event updates the likelihood of every retained run length, creates one new reset state weighted by the hazard, discards excess old runs and renormalizes. Its terminal mixture conditions on the observed transition before the terminal outcome.

Other separately fitted strong baselines: unchanged original native stream, CKAD42 full/discount.93/dual causal relation learners, Beta full/window12/24/48/discount85/95, prequential Beta Hedge, uniform frozen/current learned mixture, frozen learned reference alone, action-masked learned causal ablation and sham. All arms receive **identical authentic synthetic action/consequence events**, no private world identity.

Fixture-only action-symbol bijection checks the generic fitted Beta change-point baseline for binary action relabel consistency. This does not test genuinely unseen action identities or new causal families. DEV reuses CKAD39 stochastic A→B→A families, and thus cannot establish novel-world transfer, language learning, or broad intelligence.

## Frozen scientific stop

The two **new DEV seeds 44111/44112** each run two stochastic original worlds (one DEV execution cross-replicated on Ubuntu and Windows). Held pilots 44211/44212 and primary 44311/44312/44313 are forbidden by CLI and remain untouched.

Each seed must reach a late-B + late-return pooled Brier **≤ 0.145** and improve **≥ 0.010 absolute over the best separately fitted source-trained control**, including the online Beta change-point baseline. Late return A must improve by **≥0.020** over original native; early return A and late B must not worsen by more than **0.005** relative to original native. Candidate must also beat its action-masked ablation by **≥0.015**, and original source / frozen64 / exact cold checkpoint / read purity / conflict and identity controls must pass. **Any failure is DEV_NO_GO.** Never retune on the consumed DEV seeds. DEV success would *not* be a scientific pass without disjoint unfamiliar-family held tests, compute/cost matching, independent owner and full final regression.

Source and checkpoint SHA identity across Linux/Windows is required for the native and candidate; float Brier arithmetic in separately trained conventional baselines may show sub-ULP differences and is recorded honestly. Extra candidate-memory and BOCPD update/forecast cost is measured as whole-process CPU and wall, **not matched compute**.

## Reproduction — development scope only

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-44 -p test_ckad44.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-44/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-44/screen_dev.py
```

The isolated GitHub Action is only triggered by a frozen, exact-source commit message, with Python 3.12 on Linux and Windows. It runs no scheduler, paid API, owner runner, Forge controller or accepted-model training integration. Source qualification and original negative results belong in an in-repo `dev_screen_report.json`; a draft stacked PR is research evidence, **not** merge/promotion authority.
