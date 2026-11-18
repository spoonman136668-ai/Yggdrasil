# WSP-162 — Identical-public-input causal conflict: falsification certificate

**Research-only, source-free falsification of a narrow static-input weight representation. No original-source access, deployment, main alteration or scientific promotion.**

## What is being falsified

WSP-161 successfully learned an additional linear relation without changing old predictions because the new law occupied the only two previously unused public feature dimensions. That is an engineered, orthogonal-support result, not arbitrary continual learning.

WSP-162 constructs the opposite case: **exactly the same public state and chosen action** have two incompatible next-state outcomes under different unobservable simulated regimes. No hidden regime identifier, timestamp or future consequence enters the learner input. Only the evaluator holds both labels.

For one four-dimensional pair y_old and y_new, any single-valued input-only predictor p obeys:

    0.5*(||p-y_old||^2 + ||p-y_new||^2)/4
      = ||p-(y_old+y_new)/2||^2/4
        + ||y_old-y_new||^2/(4*4).

The minimum achievable paired four-output RMSE is sqrt(||y_old-y_new||^2/16). For frozen delta (0.4,-0.3,0.2,-0.1), the floor is sqrt(0.3/16), approximately 0.13693. This is a mathematical information limit, independent of training algorithm, if the two target outcomes must both be predicted from the exact same public input.

A model with **public history**, explicit context evidence, a calibrated distribution or a diagnostic intervention policy can be evaluated under a separately frozen contract; the result here cannot prove those more capable systems impossible. The midpoint oracle has access to both labels at evaluation and is only a *lower-bound mathematical certificate*, never an eligible prospective control.

## Exact provenance and source boundary

- Parent [WSP-161 PR #1214](https://github.com/spoonman136668-ai/Yggdrasil/pull/1214), qualified head c884e673d559c661b21da1d05eb7bed6a7fa90d8, tree 19e18550d5e65efba302dec215769a3c85e369af. Inherited WSP-160 numerical weight programming, WSP-161 protected projection and WSP-159 strict public records are reused without source changes.
- WSP-162 sole-file, PRE-implementation preregistration SHA dda52b32fa5fa60254fbd54ce6332d5fbf2fbd4a.
- The investigator-authored fixtures do **not** use the external simulator or its protected source. CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf is static background only, not called.
- CKAD independently continues cumulative native training. WSP162 does not edit CKAD, the accepted Yggdrasil tree, native research baselines, owners/runners/controllers or source-first-use rights.

## Frozen development protocol

Three seeded order variants, 1019/1231/1429. Each contains the same 16 distinguishable public inputs: eight signed (s0,s1,s2) corners, s3=0, and both actions. Per seed: 96 old FIT, 64 old held rows, 96 new FIT, 64 new held rows. The held rows have the *same seen input identities* and the two incompatible labels; they are **not** unfamiliar inputs or novel-world transfer. The three seeds vary order, not the underlying law.

- Fit unchanged WSP-160 direct numerical weight program on old FIT.
- Protect the exact 16 previously witnessed state/action input identities using the WSP-161 projected repair subspace (rank eight).
- Observe all 96 new FIT action consequences that contradict previously observed outcomes at the same public inputs, without any externally supplied regime label. Record refusal count and byte-exact original checkpoint preservation.
- On joint old and new held labels, score original frozen old program, standard continued WSP160, and **independently fitted full-batch Gaussian-elimination ridge** reused from WSP160's qualified comparator. All competitors receive the same actual public values appropriate to their method, never hidden simulator data.
- Independently calculate the exact square-loss lower bound from witnessed contradictory target pairs. Ex-post midpoint reaches it exactly but **is not a qualified deployable control**.
- Freeze negative controls for no-contradiction zero bound, shuffled-order invariance, unmatched/duplicate public keys, mismatched public reward and flags, privileged wind and malformed model outputs. SCIENTIFIC_PASS is always false.

If this gate passes, it **falsifies** the claim that a single deterministic static-public-input weight mapping could *simultaneously* recover both incompatible consequences with zero error. It does not falsify hidden-state inference, probabilistic prediction, intervention planning or conditional remembered regimes.

## Source-free run

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-162 -p 'test_*.py' -v

Expect one JSON diagnostic record WSP162_FROZEN_OVERLAP_RESULTS. This has no source acquisition cost, real CartPoleWind reset/step/do, learned original-source data, GPU or paid API.

Final engineering qualification requires unchanged WSP159, WSP160, WSP161 and WSP162 focused suites, mandatory complete inherited root+NKR05 regression, G29 check on exact SHA/tree and independent dual-platform G29 acceptance. Preserve original WSP161 success and this separate negative boundary, without replacing either result.

## Interpretation and next meaningful experiment

**Source-free observability boundary**: if old and new worlds are observationally aliased, preserving old deterministic predictions and fitting new deterministic outcomes is logically incompatible at equal input. Direct weight edits cannot manufacture missing information. Rather than simply increasing weights or retuning a failed model, the next proposed work is to **learn a public-history context representation or select a discriminating intervention** and compare with fully trained memory-conditioned/change-point controls. That scientific protocol remains separately unapproved without original source-owner virgin family/source custody.

**ENGINEERING:** pending final exact Linux/Windows+G29 qualification.
**SCIENCE:** no original causal source, no unknown-world transfer, no superiority; falsification applies only to static single-valued predictors.
**DEPLOYMENT:** none; draft and unmerged.
