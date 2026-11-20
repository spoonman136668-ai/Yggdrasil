# ENERGY-34 — Learned sparse causal-energy contrastive factors

**2026-11-18:** **DEVELOPMENT_NO_GO**. Native Yggdrasil learner was not run, integrated, accepted, or deployed.

## Why this gate
ENERGY-22–33 chiefly used normalized finite Bayesian posteriors expressible as energy functions. That equivalence could not demonstrate a distinctive energy advantage. ENERGY-34 instead **trains a 12-coupling sparse structured max-margin energy** from witnessed action-consequence observations and compares strong fully fitted conventional controls using equivalent information and (for OMP) the same factor support budget. This is independent, source-free, low-cost synthetic development; not proof of Yggdrasil intelligence.

## Source, freeze and boundaries
- Frozen source: Git blob `73a8a24fad2afca8a93afd3e241e420ed849917e`, SHA-256 `716f090f935184763f2d882a1aa6743867af0e2f3422946e789839b3ff3a0419`, commit `ab77c4747e6d59ea4c3d97920a91e246c83cf0ea`.
- Frozen preregistration: commit `18b4c5651db82db12a3d21253f26386f097a7aca`, **before primary scoring**. Separate smoke seed 99059 excluded. Primary seeds 7117/7129/7151.
- **216 worlds:** 3 seeds × 8 world IDs × 3 causal families × 3 conditions (IID 10% noise; shifted x0=0 training/x0=1 held at 10% noise; IID 30% training noise).
- Per world: 96 witnessed fitting interventions and 64 disjoint held interventions out of 256 possible 8-bit actions; causal function is a hidden majority of three signed factors, with 190 parity/AND candidate features available to trained methods.
- Energy: learned structured margin E(y|x) = −y (w·φ(x)), 64 update epochs, top-eight gradient updates, hard top-12 support pruning, one-step binary energy decision; not a normalized Bayesian relabeling. **Source grammar and input feature dictionary are designed, not autonomously invented.**
- Strong trained controls: OMP12 using the identical 190 features and at most 12 active coefficients; logistic regression, ridge on identical features; RBF SVM and decision tree on identical raw interventions; shuffled-label energy and majority prediction as negative diagnostics. No held labels are passed to fitting, hyperparameters were not tuned against primary results.

## Primary scored outcome

| Cohort | Learned sparse energy | Best fully trained conventional | Frozen +3pp / nonregression gate |
|---|---:|---:|---|
| IID, 4,608 held bits | **4,262 (92.49%)** | OMP12 3,977 (86.31%) | **PASS (+6.18pp)** |
| x0 distribution shift, 4,608 held bits | 2,709 (58.79%) | **OMP12 2,862 (62.11%)** | **FAIL (−3.32pp)** |
| 30% label noise, 4,608 held bits | **2,935 (63.69%)** | OMP12 2,720 (59.03%) | **PASS (+4.67pp)** |

In primary source seed 7129, sparse energy beat OMP under x0 shift (908 vs 864), but lost on the other seeds (854 vs 899; 947 vs 1099); the preregistered two-of-three joint IID/shift condition fails.

**Learned-versus-shuffled controls PASS** in all cohorts (IID 4262 vs 2403; shift 2709 vs 2456; high noise 2935 vs 2374). This supports dependence on witnessed labels rather than purely hard-coded outcomes.

**Timing:** 216-world local run, sum of fitted/predicted component times: sparse energy 1.26408 s, fastest conventional trained tree 0.37667 s, OMP12 0.42887 s, logistic 3.28472 s. Sparse energy is **3.36× slower** than the fastest trained control in this local implementation, failing frozen 2× speed requirement. Whole Python experiment wall 8.32824 s, external process wall 10.69 s; these **do not** establish end-to-end energy cost gain.

**Frozen gates: three PASS and three FAIL:** IID margin PASS, shifted margin FAIL, high-noise non-regression PASS, two-of-three-seed stability FAIL, learned-vs-shuffle PASS, efficiency vs fastest trained control FAIL. **Classification: DEVELOPMENT_NO_GO.**

## Engineering evidence, reproduction and custody
- Primary `scored.json` (210,584 bytes) SHA-256 `e079583a5ccbc60126d7eaab6f7b17912ebc41bc1917bcb91cd640da23d70add`. Full original JSON is not deposited in this archive. Exact source can regenerate its semantic content (timings differ).
- **All 216 primary case receipts deposited** in `case_receipts.csv.xz`, 2,544 bytes, Git blob `bdf5499d2e6be53da4f9464e0b24dc1a2d009b2c`; xz SHA-256 `93a21cd993da67bfdb8081f32be8fd1d8a7532c062f9a6f2a42f82326d4fabb0`; expanded 12,298-byte CSV SHA-256 `030ed837f791e05d2a551c1dea1e4f8e8e02773517e6191c7cf1b9efee98a0b6`.
- Independent scalar `audit.py` reconstructed action splits, source families and noise without importing the scorer; validated no training/held overlap, all 216 identities, fixed budgets, factor capacity, per-seed/aggregate counts and frozen gates: **5,775 checks PASS**. It **does not independently retrain all arms** and cannot prove each held prediction.
- Exact-source replay matched all non-timing semantic fields, canonical SHA-256 `f250a455850dd7c1beb79dcc43f9e6b62aaa60b07b3fc5691bc270077270c8e4`.
- Local Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0; CPU only; no paid inference or project runner. Native full Linux/Windows regression, independent scientific acceptance and project owner first-use **NOT RUN**.

From a clean evidence-branch checkout:

```bash
cd research/contrib/chatgpt/energy-evidence-20261117/ENERGY-34
python -B experiment.py --smoke --out smoke.json
python -B experiment.py --out scored.json
python -B audit.py scored.json
python -c "import lzma,hashlib; b=lzma.open('case_receipts.csv.xz','rb').read(); assert hashlib.sha256(b).hexdigest() == '030ed837f791e05d2a551c1dea1e4f8e8e02773517e6191c7cf1b9efee98a0b6'"
```

## Research conclusion
**The model learned a useful bounded representation and handled noisy familiar-context inference better than all tested controls, but failed the more important unfamiliar-context and efficiency criteria.** Preserve the failed frozen result. Do not tune the consumed cohort. A separate fresh ENERGY-35, only if pursued, should target **structural causal invariance across intervention context shifts** rather than adding more threshold epochs. It needs independent source cohorts and a preregistered full-cost comparison. No accepted source, controller, autonomous training, promotion, or deployment changed.
