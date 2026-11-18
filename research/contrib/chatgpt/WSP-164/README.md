# WSP-164 — FIT-calibrated reliability for continuous public-history direct weights

**External source-free research. Not real CartPoleWind training, CKAD, accepted native learner, original first use, or scientific improvement.**

## Prior negative and strict lineage

WSP-163 draft PR1218 at qualified exact head 245dae308bc3b7ca04b2a5af574ffc45cd6621a4 (tree 98d420dc6cdfa527c963974e9be89e990407890f): full Linux+Windows root/NKR05 run 44266783693 PASS, independent G29 run 44266791915 PASS. The same earlier WSP163 learned public-history weights improved authored persistent regimes but failed all three iid-switch stress gates, increasing RMSE by 0.0338–0.0675. Source-free model checkpoint SHA/byte lengths differed across OS. Preserve that DEVELOPMENT_NO_GO and original raw CI evidence unchanged.

WSP164 solely preregistration FIRST: 028af69c6317b9f8c8ec5d1b83c0affb63473273. This contribution adds only a new isolated external-research directory, a scoped branch-only qualification workflow and exactly three generated atlas files. WSP159–163 native/public research modules, CKAD native learner and Yggdrasil accepted main are unchanged.

Original upstream CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf is STATIC READ-ONLY background only. Original source actions, resets, do/ctf_do = 0. An independently verified owner-signed virgin source cohort and actor lease remain missing; historical CVH10 action cap does not authorize this experiment.

## Mechanism, intended interpretation and learning

Train the unchanged WSP160 4D static predictor on 512 ordinary public FIT action-consequence transitions, then unchanged WSP163 four-output/4-lag direct-write RLS residual program on the 480 within-episode predecessor/target pairs. Calibrate exactly ONE new gating scalar from all 480 consecutive public FIT residual cosines:

    threshold = max(0.75, min(0.86, mean(FIT residual cosine similarities)-0.10))

At prediction, use only the preceding five observed public transitions from the current episode (no terminal prior). Enable the learned WSP163 history correction only if every adjacent cosine similarity among those five previous public residuals exceeds this FIXED FIT threshold. Otherwise predict using the original static model. First step and steps with fewer than five available prior outcomes remain static. This is a **bounded self-supervised consistency heuristic** and an existing conventional rank-one trained readout, NOT a new algorithm for general causal discovery or intelligence. No family-specific expert bank, transformed hidden-world labels or future target read before prediction.

YGR1 integrity-checked canonical snapshot includes the frozen WSP163 program and scalar. Same-host cold restore must reproduce bytes and predictions exactly. Cross-platform byte-identity failures remain a separate open qualification rather than being hidden.

## Precommitted experiment

New independent source-free seed streams 1931,2053,2179 (NOT the earlier 1631/1741/1867). Each 32 TRAIN persistent episodes x16 observed steps, 16 independent held VALID persistent episodes x16, and 16 independent IID-switch STRESS episodes x16. Only fabricated public 4D states, selected actions, next-state outcomes and terminal flags. Same authored process family/support as WSP163; new draws are NOT real unfamiliar external transfer.

Score **prequentially**, using only preceding already witnessed public feedback within the current episode. For each seed report later-step and all-step static/ungated/gated errors, Bayesian control, carry, randomized FIT-history negative, gate-on fractions, first-step parity, same-host checkpoint parity, cross-OS SHA/size, CPU and source-action count.

Independent conventional Bayesian strong control sees exactly same public FIT data and preceding feedback: fit two residual-mode prototype means by *public residual first-coordinate sign*, learn a Beta-smoothed within-episode same-mode probability from FIT public sequences, compare persistent-vs-IID process likelihoods online with an equal prior. It receives NO hidden actual regime, oracle labels, current target or future observations. This comparator can beat the gate and such a result must be reported. Full-trained standard WSP160 static, inherited WSP163 un-gated RLS and previous residual carry also remain controls. A matching conventional forecast does not show a new native architecture advantage.

Frozen development gate: in every seed gated held persistent later-step RMSE improves >=0.04 versus static, gated IID RMSE regret <=0.01 versus static, old un-gated IID regret >=0.01, shuffled public history worse, gate never sees future/hidden source, strict cold/negative tests PASS, mandatory exact Linux/Windows full inherited root+NKR05 regression and independently qualified G29 PASS. Any failure preserves DEVELOPMENT_NO_GO without adjusting seeded scores or thresholds. SCIENTIFIC_PASS is always FALSE.

Reproduce focused development:

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-164 -p 'test_*.py' -v

**ENGINEERING:** pending exact dual-platform final qualification.
**SCIENTIFIC:** original source first-use NOT AUTHORIZED, zero original actions; synthetic performance only; Bayesian control may win.
**DEPLOYMENT:** NONE, keep draft/unmerged, no controller/scheduler/runner action.
