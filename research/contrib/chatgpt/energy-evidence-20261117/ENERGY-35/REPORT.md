# ENERGY-35 — Disjoint causal-bridge interventions with learned sparse energies

**November 18, 2026.** Frozen, source-free synthetic research; **DEVELOPMENT_NO_GO**. No native Yggdrasil checkpoint trained, scientific first-use consumed, accepted model changed, or deployment made.

## Question and mechanism
ENERGY-34's source exposed a fundamental identifiability problem: fitting exclusively x0=0 intervention states does not in general identify which causal functions apply at x0=1. ENERGY-35 directly tests a new data-collection and learner mechanism: **16 witnessed paired action-consequence bridges** differing only in x0, with a contrastive sparse-energy learner constrained by observed paired label differences.

Source uses 8-bit intervention patterns, hidden majority of three signed causal parity/AND factors, a known 190-factor grammar, and independent 10% observation corruption. The candidate learns a support<=12 max-margin energy, E(y|x)=-y*w·φ(x), with 48 updates, top-eight gradient selection and a *frozen pre-primary* light pair-difference constraint. The contrast is learned from actual observed labels; hidden true factors and held noise-free action consequences remain evaluator-side. This is **not** open-ended causal primitive construction or a novel native architecture.

## Source/prospective freeze
- Earlier ENERGY-34 archive head: `f3bf4e8f93cd713b24493c4f71b68eace5af265a`.
- Frozen `experiment.py` source commit: `061ac19ac7d411b6bf1858b3a76d5d1ddf212359`; blob `fc65b0f5aa224397ea94f22753c25ee27996a305`; SHA-256 `dde9f68ea1f86e7e09b291859adffec78d33cfb6dd1197e8fdf25e92e4bdca9c`.
- **Preregistration committed before primary**: `ded9bc2dd96a2b14c0abac15cb80c1f0d91aa6b9`. The smoke-only seed 99079 was excluded; two pre-freeze contrast weights were tried before selecting the source. No primary test seeds used for tuning.
- Primary: seeds 7307/7331/7349, eight worlds per seed, three rule families, two intervention-allocation regimes = **144 learner-world/regime evaluations**, 72 distinct underlying causal source worlds. Every arm receives **96 witnessed training action/outcome pairs per evaluated world**, and scores 16 disjoint x0=0 familiar-context and 48 disjoint x0=1 shifted-context actions.
- `bridge16`: 80 x0=0 observations and 16 paired x0=1 intervention outcomes. `no_bridge`: 96 x0=0 observations instead. These are **different information allocations** despite equal 96-label budgets; differences between allocations cannot be attributed solely to a learning algorithm.
- Strong conventional fully fitted controls on the **same 96 labels and actions within each regime**: OMP12, paired OMP12 using the same observed-delta rows, paired Ridge, logistic regression, RBF SVM, and depth-8 tree. Also plain-energy no-contrast ablation and shuffled-label negative.
- Frozen seven development predicates require shifted +3pp over the strongest conventional control, <=1pp old-context regression, +2pp pair contrast benefit over plain energy, +5pp bridge effect, positive shifted margins in >=2/3 seeds, advantage over shuffled labels, and <=1.5x fastest conventional local fitting+predict cost.

## Primary evidence

| `bridge16` held metric | Paired energy | Strongest conventional | Plain-energy ablation |
|---|---:|---:|---:|
| New/shifted x0=1 (3,456 held actions) | **2,782 (80.50%)** | OMP12 2,774 (80.27%) | **2,816 (81.48%)** |
| Old x0=0 (1,152 held actions) | 1,050 (91.15%) | OMP12 1,018 (88.37%) | 1,079 (93.66%) |

Paired energy beats conventional OMP12 by **8 of 3,456**, or **+0.23 percentage points**—far below the frozen +3pp gate. Removing the new pairwise gradient **improves** shifted held accuracy by 34/3,456 (+0.98pp), so the proposed contrastive mechanism is not responsible for the observed gain. The old-context retention gate against the strongest conventional control passes, but removing the new penalty also improves old accuracy.

The equal-label-budget `no_bridge` paired energy achieves **2,023/3,456** shifted correct; `bridge16` achieves **2,782/3,456**, an apparent **+21.96pp** benefit from **new intervention coverage**. Conventional OMP12 also improves substantially (2,174 to 2,774), so do not confuse increased action information with an energy-specific improvement.

Seedwise paired-energy minus strongest conventional shifted held correct: **+15, −31, +15**. Two positive seeds satisfy the frozen stability predicate despite losing on the aggregate +3pp gate. Shuffled-label energy scores **1,754/3,456**, supporting genuine learned label dependence.

**Measured component fit+held prediction time:** paired energy 0.27524 seconds aggregated over 72 bridge cases; fastest conventional decision tree 0.05390 seconds, **5.11× faster** than paired energy for this implementation. Original full experiment wall 2.40829 seconds for all arms/regimes/source generation, not a controlled full-process speed ratio. The +1.5x component-cost gate fails.

**Seven frozen gates: four PASS; three FAIL**. PASS: bridge information value, old retention versus conventional, positive shifted margin in 2/3 seeds, shuffled negative. FAIL: shifted +3pp over strongest conventional, pair-constraint ablation +2pp, and component fit-cost. Overall **DEVELOPMENT_NO_GO**; no post-primary retuning.

## Custody, independent audit and reproduction
- Complete **144-case score receipts**, including all 9 fitted arms' old/new accuracies, are byte-preserved in `case_receipts.csv`, Git blob `1271a455ae7fa827b4ec25b06d7aa08f0ee498e7`, SHA-256 `c6ba7aec571c1d590121cf2fe0eaf9e4a0f1079a8a5efb19b5357c956cadcfa3`, 11,775 bytes.
- The original **227,730-byte `scored.json` is not in GitHub**; its SHA-256 is `96f1bffc8117764b1bc9fdd2110107a8f212591be80f119a1fdcded7aacba435`. The exact committed scorer recreates all semantically meaningful fields; wall/runtime timing fields differ. Non-timing deterministic semantic replay SHA-256: `ae81d9d06be1ce685f370aab4ca2d6a691ac56ba92f788c21027c74a6ac3bae8`.
- Independent `audit.py`, without importing the scorer, reconstructed all source worlds, action allocations, label corruption, refit all nine model arms from identical witnessed inputs, compared every held score and learned support, reaggregated all metrics and frozen gates: **5,052 assertions PASS**. It uses the same scikit-learn library for conventional solver implementations; this does not imply an independently implemented sklearn. Source Git blob `b4fc8e626df00ef8ae686333d39ee489a9b2b362`.
- Local Linux CPU, Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0, explicit single-threaded BLAS. Full Linux/Windows repository regression, G29 atlas acceptance and native scientific first-use **not performed** for this external evidence.

From a clean checkout of the pinned archive branch at this evidence commit:
```bash
cd research/contrib/chatgpt/energy-evidence-20261117/ENERGY-35
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out scored.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored.json
```
The program writes `audit_result.json`; the recorded original JSON hash will differ on newly measured timing fields. Match aggregate and case score receipts, the code source hash and non-timing semantic replay.

## Conclusion
Bridge interventions address a real information-coverage deficit, but **energy-specific pairwise contrastive learning did not outperform its own simpler ablation or cost-efficient conventional controls**. Preserve the negative result, no adaptation of consumed seeds. The next rational research experiment, if continued, should focus on **minimal discriminating intervention selection / causal witness efficiency** with a frozen no-bridge, random-bridge, optimized-bridge comparison, not yet another gainless posterior/gradient restatement. That experiment remains separate from Yggdrasil native qualification.

**ENGINEERING:** external local scorer and independent audit PASS, native full-regression/CI unverified. **SCIENCE:** DEVELOPMENT_NO_GO. **DEPLOYMENT:** NONE. Accepted main, model, controller, scheduler, research loop and other projects unchanged.
