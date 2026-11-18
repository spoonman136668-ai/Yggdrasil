# WSP-166 — Paired public action consequences and direct causal-contrast weights

**Source-free exploratory engineering only, NOT native Yggdrasil scientific first-use or deployed model. Keep PR DRAFT/UNMERGED.**

## Research question

Do *directly programmed* numerical weights acquire a new action-conditioned causal effect when given matched public outcomes from taking each of two actions at the identical synthetic public state? What happens when the new law includes a held relationship absent from the frozen feature grammar? Can direct-written trained state become **byte-identical across Linux and Windows**, unlike prior WSP163–165 float/JSON checkpoints?

Prior WSP165 [PR #1221](https://github.com/spoonman136668-ai/Yggdrasil/pull/1221), final SHA eb547e6b717ed7e1710e52f7a08ca526204ad48b (tree 02a82b74074607538919d1ed7e14c1d64169aab6), passed exact final dual OS #44273961538 + independent G29 #44273968440, yet **FAILED** the frozen persistent/transfer criteria and matched conventional Bayes, with new action-dependent rotated law worse than static. All earlier WSP/CKAD evidence remains untouched.

**WSP166 preregistration SOLE FILE FIRST:** Git SHA 9721ab830228634ae3955fefa2145286be3b5aa1, parented directly on qualified WSP165. The new mechanism is fixed at 70420dfc9456ad91813ca32149d495b1dc89af32. Frozen tests SHA 891e2022130a961c01a5ce40979b95e90db2b097 before first scored CI. Engineering and results must be associated with exact commit/tree and no postscore threshold tuning.

## Bounded source-free methodology

A pure Python investigator creates a deterministic grid of 256 public 4D dyadic states. Three frozen seeded replicas 2663/2777/2887 select 48 distinct TRAIN state contexts and 48 disjoint held VALID state contexts each. For each state the investigator supplies two **separate synthetic public transition records**: one for selected action 0 and one for selected action 1. This is simulated matched alternative intervention evidence, not a real-world ability to reset a causal environment to an identical state or privately query counterfactuals.

First fit the unchanged WSP160 4D action-conditioned public-state ridge model on **96 historically synthetic old-family FIT transitions** (48 contexts, both actions). Freeze the parent and verify its state is not modified by later adaptation.

The alternate authored family keeps action-0 dynamics identical but changes action-1 effects by a state-conditioned polynomial with a **preauthored eight-feature basis**:

    phi(s) = [1, s0, s1, s2, s3, s0*s1, s1*s2, s0*s3]

For each new matched public pair, compute the four-vector of separately witnessed next-state differences, *y(action=1) - y(action=0)*, and directly update 4x8 weights and 8x8 inverse ridge normal matrix using classical rank-one recursive least squares (ridge lambda=1). All exact binary-fraction public inputs and targets are converted to \`fractions.Fraction\`; covariance, weights, order invariance and canonical numerator/denominator checkpoint YPE1 are **exact rational**. This is known linear algebra, no new operator invention, hidden-oracle family label, gradient descent or tokenizer/transformer architecture.

The readout leaves **parent action 0** forecasts identical and substitutes the new learned public action contrast for action 1. The immutable parent checkpoint remains a separate prior-family reference. The readout does NOT infer when the original old action-1 relationship should return; old-world action-1 return error must be reported as an honest retention limit.

## Frozen three-seed comparisons

Each seed: 96 old-family public FIT actions, 96 new-family public paired FIT actions, 96 new-family held public VALID actions, plus 96 *unexposed structural OOD* held actions. All synthetic. New-family held states are disjoint from FIT while using a shared known finite value grid. The OOD evaluator introduces a new third-order action term \`s0*s1*s2 × (1,-0.75,0.75,-0.5)\`, which the fixed eight-feature direct programmer does **NOT** represent and has never observed.

Strong controls:
- **Independent fully fitted batch conventional ridge of the exact same eight-feature paired public contrasts**, built by Gaussian elimination, expected numerical tie; no superiority claim possible.
- **Independently fully fitted 16-feature joint action-conditional regression** trained on the same 96 new FIT public rows (and native original base's historical evidence separately reported).
- Fully FIT action-erased eight-feature conventional regression on both new actions (shows whether action observations matter).
- Frozen original WSP160 pre-adaptation action-conditioned predictor; original prior-world return errors, action0 exact nonregression, no pair/no action negative, reversed source row order and cold restore across a **separate Python process**.
- Tamper, forged correctly rehashed private fields, noncanonical Fraction, count cap, invalid public action/state and unmatched state/action flags must fail closed.

Development thresholds locked before first score: new action-1 VALID RMSE <=0.08 AND improvement >=0.10 versus unadapted WSP160, all seeds; action-0 max drift 0, independent same-FIT conventional action-effect forecast gap <=1e-8. Structural OOD third-order VALID RMSE <=0.08 is an independent **transfer signal** threshold; failure remains DEVELOPMENT_NO_GO, not a prompt to retune. A strong conventional tie is an expected engineering validation, *not* scientific gain.

All reported synthetic model-state checkpoint hashes must be compared across Linux/Windows. The direct effect checkpoint deliberately excludes the untouched old floating-point WSP160 base, so byte-identical new effect state does **not** imply every native model byte or original source context is portable. Report whole-process costs separately; test-only CPU time is not an end-to-end efficiency claim.

Original upstream CausalAILab/Causal-Gymnasium first-use resets/steps/do/ctf_do = **zero**. CVH10 original actor/virgin source-owner custody remains externally unverified. This synthetic paired intervention access is not equivalent to its real source-first-use lease; no protected science is permitted here.

## Reproduction and qualification

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-166 -p 'test_*.py' -v

Branch workflow runs focused WSP159–166, mandatory complete inherited root regression and NKR05, generated G29 source atlas and independent G29 both OS on exact final candidate SHA. Neither CKAD/native model, accepted main, external source owner nor controller/scheduler is altered.

**ENGINEERING:** pending first Linux/Windows focused qualification.
**SCIENTIFIC:** toy known-basis effect learning, standard conventional control; SCIENTIFIC_PASS=false.
**DEPLOYMENT:** NONE, keep draft/unmerged.
