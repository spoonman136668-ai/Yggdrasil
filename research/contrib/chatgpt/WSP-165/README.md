# WSP-165 — Public-consequence causal-context transfer and limits

**Source-free R&D only. No protected original-source first-use or native deployment. Keep draft and unmerged.**

## Purpose and provenance

Earlier WSP-163 and WSP-164 source-free experiments established that static direct-weight programs cannot predict opposite hidden consequences for identical current public observations; a learned public-history AR(1) program reduces error on persistent synthetic regimes but degrades on IID regime changes; a simple FIT-derived consistency gate removes most IID regret but is beaten by a fully fitted Bayesian two-mode conventional control. Those prior results, including a bounded WSP-164 postscore negative-test-harness correction and cross-OS checkpoint byte mismatches, remain untouched.

Qualified WSP-164 parent: exact final Git SHA f34b0b3825e2cb847cf344f177940fb271012e4e, tree 9132bef54545e96b579892f8ae355b6a99e0dc4c, mandatory full dual-OS #44270813124 PASS, independent G29 #44270816286 PASS. WSP-165 sole-file preregistration was committed FIRST: e23950f4081a51182d6149597ba0af73c9e9372b. CKAD independent Yggdrasil research remains unchanged. All source and tests are isolated under this directory.

The original CausalAILab/Causal-Gymnasium source is only a read-only reference; the source-owner signed virgin cohort, one-shot actor lease and custody are unverified. Original upstream CartPoleWind reset/step/do count = **zero**. The historic conditional CVH10 action cap does not authorize WSP-165 original scientific first-use.

## Mechanism

Fit the already qualified WSP160 4D action-conditional direct-written ridge base on 512 synthetic, strictly public FIT transitions (32×16 within-episode records). Derive each FIT public residual: witnessed next state minus the static public forecast. Partition residuals by the **publicly witnessed residual's first coordinate sign**, directly program two bounded four-dimensional prototype mean weight vectors, and record a Beta(1,1)-smoothed within-episode same-mode rate based only on inferred public residual signs, not source regime identities. This model adds only 8 direct-written residual coefficients and one fitted scalar; there is **one shared learner**, no per-source model or hidden mode labels.

For each future public forecast, require five previously witnessed public transitions from the SAME episode; otherwise return the exact static output. Map each previous public residual to the closest fitted 4D prototype, compute a Bayesian persistent-vs-iid process likelihood ratio from four observed inferred-mode transition pairs with equal prior, and forecast current next state as:

    static + prototype_center
            + posterior_persistent × (2 × trained_stay_probability - 1)
            × (most_recent_public_prototype - prototype_center)

The learned weights are frozen throughout held evaluation. The caller can provide only WSP159 whitelisted PublicTransition values, the current public state, and chosen action; no protected source state, hidden regime sign, future target or post-outcome feedback before prediction is accepted. Checkpoint YCP1 seals the frozen static base, directly programmed prototypes, public FIT counts and stay scalar with SHA256 integrity. Native equality within one process must be checked; cross-platform exact-byte portability is independently audited rather than assumed.

This is conventional Bayesian evidence conditioning of direct-written moments. A separately independently **fully FIT** batch prototype/Bayesian posterior estimator sees identical public FIT and identical prior public history and must be scored side by side; an exact tie proves correct implementation, NOT a new architecture advantage.

## Frozen evaluation

Independent deterministic source-free seeds 2281,2393,2503. Each uses 32×16 FIT persistent episodes, followed by four domains of 16×16 **held** episodes each:

1. **Persistent:** unseen noisy episodes from the original authored two-offset process with regime fixed within each episode.
2. **IID switching:** held episodes with independent latent sign redraw at every step.
3. **Moderately switching, not present during FIT:** new source-free generator with latent sign switch probability 0.2 per step, same 4D offset vector.
4. **Structurally changed, not present during FIT:** new held generator with sign switch probability 0.2 plus action-dependent offset reversal and a rotated 4D magnitude vector (0.05,0.18,-0.20,0.12).

All evaluation public states/actions lie on the inherited 16-point support; only latent generator dynamics change. The hidden generator sign is NEVER passed into a learner or comparator. Because these are authored synthetic processes, they do **not** satisfy original externally unfamiliar-world scientific first-use or prove general causal discovery.

Controls: frozen WSP160 FIT static, fully FIT WSP163 history RLS, WSP164 fitted reliability gate, independent full-trained conventional Bayesian persistence-vs-IID from WSP164, independently implemented exact-capacity FIT prototype Bayes control, cheap last-public residual carry and shuffled FIT history negative. All predictions are strictly **prequential**: current next state is revealed to scorer only after a forecast. Report later-step RMSE for every domain, first-step no-leakage parity, cold byte/hash integrity, CPU FIT/evaluation cost and cross-OS state identity.

Precommitted primary development criteria: each seed persistent later-step RMSE <=0.08, IID regret <=0.01 vs FIT static. Separate **moderate-switch transfer signal** requires >=0.015 later-step RMSE gain over static in all three seeds; **rotated-action structural transfer** requires >=0.015 gain over static in all three seeds. Missing a criterion yields a frozen NO-GO for that dimension, **not a reason to tune after scoring**. The experiment's engineering qualification is a separate question from its numerical scientific outcome; unit tests may PASS while transfer results FAIL.

All original WSP164 failures and negative metrics are immutable historical evidence; WSP165 model capacity, seeds, data splits, controls and thresholds are frozen before scoring. Original source actions = 0. No paid API, GPU, controller, scheduler, CKAD or native model file edits.

## Source-free reproduction

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-165 -p 'test_*.py' -v

The branch-only GitHub workflow should run inherited WSP159–165 tests, mandatory original root 195/195 and NKR05 6/6 regression, generate exactly the three source atlas derived files, and run independent G29 on the final exact SHA across Linux and Windows. No claim of SCIENTIFIC_PASS is allowed based on CI alone.

**ENGINEERING:** pending exact final dual-OS qualification.
**SCIENTIFIC:** source-free transfer and conventional comparison pending; original first-use UNVERIFIED; SCIENTIFIC_PASS=false.
**DEPLOYMENT:** none; branch/PR draft only.
