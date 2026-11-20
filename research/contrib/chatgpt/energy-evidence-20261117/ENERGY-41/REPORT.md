# ENERGY-41 — Contradiction in structured energy learning, invalid primary

**2026-11-18; disposition: INVALID_IMPLEMENTATION.** This is a frozen prospective primary whose candidate implementation was found **wrong after scoring**. Do not treat its unfavorable numbers as a valid scientific falsification of correctly signed structured-energy learning. The original scorer and pristine prereg remain unchanged.

## Freeze and execution
- Previous ENERGY-40 baseline: `d8d23bb2c093c486e03dd532bdbd9d4844ff8677` (unmerged archive PR #1210).
- Original frozen scorer+auditor commit **BEFORE primary**: `f92697824a1aa129c5651c5848dd251d54a1aa1a`; experiment SHA-256 `e96f2328366792773e3b1e234faba45ead16f13922173b727ec3253c22167ab8`; auditor SHA-256 `a741ed5fdc741ae41242dbc3b5213c84604a751dd5b950565ded0b5307d18227`.
- Eight prospective gates and disjoint primary seeds `[8407,8423,8431]` preregistered **before scoring**: `c7bf0c44c2a1a9928183986f78ec64355bbe3300`; smoke seed `99741` excluded (16 test graphs, 22,802 repeatability checks).
- Primary 3 seed cohorts × 16 supervised training graphs (n20; erdos+modular) × 16 disjoint evaluation graphs (12 cold unseen n36/n52 and 4 old n20). Across 48 evaluated worlds, each of six arms predicted 40 hash-held node-pair XOR relations; 1,440 cold novel and 480 old relations per arm. Included matched Bayes, logistic, uniform and group-shuffled controls; non-matched true noise oracle was diagnostic only.

## Newly verified semantic defect
The intended structured-learning feature is `d_g = V_g(x with vertex toggled) - V_g(x true)`, where `V_g` is the number of group-g violated constraints. The committed source uses:

```python
d[g] += 1 if violations(e, x) else -1
```

But when toggling either endpoint of an XOR constraint, **an initially satisfied edge becomes violated** (+1) and **an initially violated edge becomes satisfied** (-1). Consequently the correct expression is `+1 if NOT violations(e,x) else -1`. The frozen code uses **the negative of the true energy difference**.

An independent direct-count checker evaluated all **48 training graphs × 20 vertices × 3 groups = 2,880** cases: **2,217 nonzero mismatch checks**, with **2,880/2,880 exact sign inversions**. Concrete counterexample: seed 8407, erdos, vertex 0, group 0 had frozen model delta **−2** versus actual change **+2**.

This produces strongly inverted structural preferences. Frozen score model parameters repeatedly favored noisy long-distance edges (`[0.051,0.051,2.898]`) instead of the demonstrably more reliable ring/group-1 factors. This is an implementation defect in the target candidate, not evidence that correctly signed contrastive energy cannot learn reliability.

## Preserved primary results — INVALID, not development NO-GO
The original frozen scorer printed `DEVELOPMENT_NO_GO` (7/8 frozen gates failed), but its target mechanism was invalid. Retain this raw computation without accepting its scientific classification. On 1,440 held cold relations, frozen erroneous structured-energy scored **912**, Bayes **964**, logistic **978**, uniform **893**, shuffled-energy **940**, and oracle (privileged ceiling) **966**. Old-domain retained 235/480 versus matched Bayes/logistic 423/480. These values diagnose the incorrect objective; **no causal/scientific learning comparison can be qualified from this candidate**.

The independent local audit reconstructed both the erroneous source and its refit/inference behavior (68,729 checks PASS), but had the **same incorrect sign convention**, so it was a consistency/reproducibility audit, not a semantic mathematical invariant. The newly authored `defect_check.py` independently checked the first-principles XOR sign and detected the flaw. Treat **engineering correctness as FAIL**, despite replay consistency.

## Evidence and custody
- Raw original 1,076,680-byte primary JSON SHA-256 `0da31d294659a0f6a71d0f454d2a4a952b519b3895e1607007a3c03f596b40eb` remains in isolated local research workspace, not deposited in this PR.
- Committed `case_scores.csv.bz2` contains **all 48 world-level scores for all six arms**, held-world IDs and 16-hex-digit SHA-256 prefixes for each world’s public edge constraints, true assignments and held probes. Source code and exact seeds regenerate complete predictions; **the original full per-world state byte strings are not deposited** in this smaller receipt artifact. The uncompressed 4,528-byte CSV SHA-256 is `9aecdf075c1e025305e5d1c7a60ad66ac15acfe3b098dda1dcfc792e5b5f86f7`, packed SHA-256 `70abeda54a628a4f64f0c1949bdbf912cc0acf4f023e1e74d133fd6999ccbbce`.
- `result.json` preserves fitted group weights, scorer gate outcomes and measured local per-arm policy elapsed time. `provenance.json` records frozen source, auditor, receipt identity and local runtime. `defect_result.json` and `defect_check.py` reproduce a deterministic counterexample.
- SciPy not used for this ENERGY-41 test; independent auditor shares NumPy and sklearn algorithms with scorer. No native Yggdrasil runner, original model training, scientific first-use, accepted-ref mutation, merge or deployment.

## Qualified next action
**No tuning or rerunning these consumed primary seeds.** Freeze **new ENERGY-42 source** with a one-line sign repair and a strengthened auditor independently checking `V(flip)-V(truth)` **before primary**. Run only on disjoint source/version seeds, same originally frozen hyperparameters and eight gate thresholds and matched controls. Report success or failure as a distinct experiment; do not rewrite the ENERGY-41 historical source/prereg and do not claim engineering reproducibility is scientific learning.

**ENGINEERING: FAIL semantic contrastive invariant; consistency audit PASS. SCIENCE: INVALID_IMPLEMENTATION. DEPLOYMENT: NONE.**
