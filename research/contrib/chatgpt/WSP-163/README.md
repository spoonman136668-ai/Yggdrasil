# WSP-163 — One-step public-history direct-weight programming

**Source-free research contribution, not original CartPoleWind training, not a new Yggdrasil production/CKAD readout.**

## Why this gate follows WSP-162

WSP-162 [PR #1216](https://github.com/spoonman136668-ai/Yggdrasil/pull/1216) proved a restricted fact: when the identical public state/action is followed by incompatible transitions and no extra information is supplied, a single static deterministic predictor has unavoidable error. WSP-163 tests whether *previously observed public consequences* supply useful distinguishing information without exposing a simulator's hidden regime, source internals, or future outcome.

The focus is continuous 4-dimensional numerical relationships and cost, distinct from CKAD-21's integrated discrete feedback-based context selection.

## Exact source and frozen controls

- Qualified WSP-162 parent: 890507bf393dd87d4aed36c01680d11742b2bd31, tree c26d19bd235724837b3098e461e6627cea38ff25.
- Preregistration committed FIRST, before source, tests or primary run: 6049e4c542d9e98b4383376dade7508721d6daad.
- WSP163 implementation and frozen tests are isolated in this directory. WSP159/160/161/162, CKAD, Yggdrasil native source and accepted main remain unmodified.
- Original external source CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf is static background only: 0 original resets, steps, do/ctf_do. No virgin owner/actor source lease is inferred from historical conditional CVH10 budget.

## Mechanism — one numerical learner, not separate family experts

First train the already-qualified WSP160 4-output/10-feature static action-conditioned continuous ridge program from 512 synthetic public FIT transitions (32 episodes x16). Freeze this predictor and its checkpoint.

Then fit a single 4-output/4-lag-feedback direct coefficient program to pairs of **consecutive public transitions within the same episode**. Input to the new program is only the four-dimensional difference between the previously *observed* next-state and the static model's corresponding prediction. Its target is the current observed difference. A classical recursive least-squares rank-one update programs a 4x4 coefficient matrix, with a 4x4 inverse regularized covariance. There is no gradient descent, transformer, oracle regime input or family-specific expert bank.

On a future public observation/action, forecast the static next-state plus the learned memory correction from *last already witnessed* public feedback. The first step in an episode has no prior witness and therefore must predict identically to the static model. Public terminated/truncated flags require a reset across episodes. All public records flow through the unchanged WSP159 strict boundary. Full base, learned lag weights, covariance and count cold-serialize as SHA256 integrity-bound canonical bytes.

This is ordinary **linear multivariate AR(1) over observed public residuals**. A separately fitted full-batch 4x4 lag-residual ridge using the same 512 source-free FIT rows, static base, 480 prior-feedback pairs, and Gaussian elimination is a strong conventional comparator and should match to floating tolerance. No mathematical invention or native intelligence superiority is claimed.

## Frozen source-free experiment

Three independent deterministic seed streams 1631/1741/1867, each with 32 TRAIN episodes, 16 held persistent-regime VALID episodes, and 16 independent iid-reversal STRESS episodes, 16 steps each. Public state/actions come from the same 16 overlapping WSP162 contexts with two possible hidden state transition offsets ±(0.20,-0.15,0.10,-0.05) plus 4 independent Gaussian noises at σ=0.02. The generator's hidden sign is sampled per episode for persistent FIT/VALID, and independently every step for IID stress. **The hidden sign is NEVER passed to the learner or any equal-information baseline.**

Scoring must be prequential: predict from public current observation/action and only previous observed public record, then reveal and score current next state. VALID episodes and noise are disjoint from FIT; public state/action support is shared and not unfamiliar-input generalization.

Report per-seed RMSE for: static model, direct-history learner, conventional independently fully fitted lag-1 ridge, simple carry of previous public residual, and history-shuffled negative sourced from FIT history only. Report first-step and later-step errors separately, held IID rapid-switch error/regret, full checkpoint bytes/sha, cold parity, fit/eval CPU time and original source action count.

## Interpretation and hard falsification criteria

- Source-free engineering supported only if every seed has >=0.05 held *later-step* improvement over static, <=1e-8 prediction parity with the fully trained conventional lag-ridge, identical first-step prediction to static, shuffled-history negative worse than properly ordered history, strict public integrity/negative/cold tests PASS, and mandatory exact-final Linux+Windows root/NKR05/G29 PASS.
- Independently score the IID rapid-switch stress. If the learned memory **degrades** RMSE by >0.01 relative to static, classify **DEVELOPMENT_NO_GO_FOR_UNKNOWN_REGIME_PERSISTENCE**, even if the persistent development engineering tests PASS. This negative cannot be retuned away. No scientific gain over conventional lag-ridge is allowed to be claimed from a tie.
- Carry is an equal-information low-compute baseline that may beat either learner; report it even if inconvenient. Full whole-process setup/source/test costs remain separate from measured Python CPU.
- A success on the authored persistent process does **not** establish a generally reliable causal belief, natural regime diagnosis, action-selection autonomy, superior training efficiency, novel causal-world transfer or scientific first-use.

Reproduce source-free tests:

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-163 -p 'test_*.py' -v

The source-free project-branch workflow must run WSP159–163 focused suites on Linux and Windows, then generate exactly three source atlas files and run complete inherited 195-test root and six NKR05 tests on exact final source, plus independent G29 dual-platform acceptance.

**ENGINEERING:** pending dual-OS qualification.
**SCIENTIFIC:** original source 0; SCIENTIFIC_PASS=false; IID robustness pending.
**DEPLOYMENT:** none. Draft, unmerged.
