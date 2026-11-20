# ENERGY-FLUX-01 — source-free flux diagnostic and negative control (2026-11-20)

**ENGINEERING: reproducible independent arithmetic diagnostic; full exact-source/native qualification UNVERIFIED. SCIENCE: NO-GO for superiority, representation boundary established analytically. DEPLOYMENT: NONE.**

## Source custody
- Accepted `main` starting SHA: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; no accepted ref or native checkpoint mutation.
- Preregistration committed **before executable source and before scoring**: `01e780582687dedc22adc0021f74dffde7bd65b6`.
- Frozen stdlib source committed **before scoring**: `99226f41a4c4a0e7a7632d0b179f401c70dbd0f3`, `experiment.py`. Source was uploaded and remotely stored, but **the frozen file itself was not executed here** because this chat's local runtime could not fetch GitHub's raw file. No false exact-source execution claim.
- One local **independently reimplemented protocol** ran the six preregistered seeds, 18 synthetic worlds, 288 witnessed transitions, 36,864 never-trained scored transitions. The independent code was preserved after scoring in `independent_audit.py`; it is **post-score code, not a pre-frozen original-source qualification**. No further scoring on these six seeds is authorized by this receipt.
- Independent local full result semantic digest excluding timings: `3b4c8a6c300bc7daff7732da14e71d156e392550b484758d2b009d6c5cf203c1`; original local raw JSON SHA-256: `55fc3613a0ce32aac0cc3ba702d8e8c2788ea074431d8c9e7dc191e3fff01e3a`. These local files are not yet GitHub-readback-verified as byte-exact results; `independent_audit.py` reconstructs them. No CI/Windows/full-native regression receipt.
- Analytical cycle criterion: detailed balance implies `product(P_cw/P_ccw)=1` around a closed loop. With `P_cw=.8`, `P_ccw=.2` over four edges, the ratio is `4^4=256`, with log affinity `4 ln 4=5.545177...`. A single-valued scalar equilibrium potential cannot reproduce that nonzero circulation. An antisymmetric edge flux can represent it. **This is a mathematical representation boundary, not proof of learning or energy efficiency.**

## Independently reproduced held-transition observations

All Brier scores are lower-is-better. Every arm receives the same witnessed transitions. There are six worlds per scenario, 12,288 held predictions per scenario.

| Scenario | Reversible .5 | Proposed pooled flux | Fitted row-wise Markov | Exact structured Bayes | Action-blind fitted | False action-effect declarations (of 6) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DRIFT (.8/.2) | .25000000 | **.17855794** | .22471047 | **.17855794** | .25517015 | 5 true declarations |
| REVERSIBLE (.5/.5) | **.25000000** | .26827148 | .27858769 | .26827148 | .26785743 | 0 |
| ACTION_NULL (.8/.8) | .25000000 | .19274414 | .22020503 | .19274414 | **.18218818** | **1 false declaration** |

The pooled flux predicted the preferred clockwise intervention in 6/6 DRIFT worlds, and beat the conservative baseline there by **0.07144206 Brier**. Against the strongest equally informed exact structured Bayesian baseline, advantage was **0.00000000** by construction: both calculate the identical Beta(1,1) pooled posterior. DRIFT pooled flux accuracy was 0.75130 vs 0.61491 for the conventional row-wise Markov model. Under REVERSIBLE, flux *worsened* Brier by 0.01827148 vs no-learning .5. One ACTION_NULL world exceeded the preregistered 0.30 spurious action-difference threshold.

The finite source-free experiment's **representation-feasibility gate** (against the conservative model) is supported by the independent diagnostic. The frozen negative-control requirement fails (1/6 spurious declarations), and **scientific superiority is NO-GO** due to exact Bayes tie. The cold-restore gate in the frozen executable remains **UNVERIFIED by direct executable run**; the independently reimplemented scoring routine did not test it. Whole-process 2x efficiency is also **UNVERIFIED**; a ~0.1-second standalone diagnostic is not a cross-arm or total-process resource study.

## Decision and integration seam
Do not promote this candidate as a new native intelligence mechanism. Preserve the mathematical insight: **nonconservative, directed causal circulation is a distinct representation problem from minimizing scalar energy**. A future contributor could preregister a genuinely unfamiliar directed causal topology with structure learned from public interventions, using full fitted reversible/nonreversible Markov, matched latent-state, and exact graph Bayes controls. Compete on novel-topology transfer and retention plus whole-process compute—not on the already solved Beta pooled posterior.

Research-only proposed seam (NOT integrated): action-conditioned `NativeEpisodeExperience` / `NativeCausalAmalgam.observe_experience` in [Amalgam #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278). Only the central coordinator may evaluate custody and integrate a separately science-qualified mechanism. No original-world actions, no reruns of consumed sources, no merges, model training restarts, research-loop dispatch, scheduled tasks or deployment.
