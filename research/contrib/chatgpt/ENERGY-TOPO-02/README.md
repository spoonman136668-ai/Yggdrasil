# ENERGY-TOPO-02 — Directed-topology discovery: source-free primary result

**Role:** Independent Yggdrasil contributor evidence only, attached to draft [PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346). No canonical learner, checkpoint, accepted-main, model training, runner, controller, or autonomous-loop changes.

## Question

Can a bounded, directed causal topology estimator infer unknown action-dependent six-state cycles from very few action/consequence observations, retain the inferred relationships after learning a second action, and outperform matched trained conventional and fully informed exact graph-Bayesian controls?

**Short answer: NO for superiority.** The candidate beat the fully fitted unstructured row-Markov control on unseen action/state rows but lost substantially to the exact Bayesian structured control. Its tentative 3.28x speed result covers only per-arm fit+evaluation CPU, not the frozen required whole process. Four of ten action-null worlds gave false action-effect reports. No native intelligence gain.

## Evidence and frozen identity

- Preregistration final commit before execution: `b06823224bce2b21533e932f7f590f08ea5a8b87`, [prereg.json](prereg.json).
- Executable frozen commit: `4ca7843a7a0e018f0f23d4f75570f1ef6a19174e`.
- GitHub blob SHA of executable: `91c5e6f30e5fc568d15391e53286ff4993b65bd9`. Local executable has exactly this Git blob SHA and SHA-256 `201b04580777b9b7a862ecee419becadb2c8c0243c63c6fe47e68f5510c1f23f`.
- Original local 41,311-byte `primary.json` SHA-256: `80e3c6cf0923f79eff0a1922dd775111d762584654499723f8cc0353835002d9`. **Raw per-world JSON has not been uploaded to GitHub**; [result.json](result.json) is a bounded transcription from the saved local receipt. The original log execution is not independently authenticated.
- Python 3.13.5, Linux-6.18.57 x86_64 glibc2.41. One primary cohort of 10 preregistered seeds x three worlds = 30 worlds, 540 training transitions, 23,040 disjoint held transitions. **Never rerun consumed primary seeds**.
- Execution preflight used an independent smoke seed 90301; the local smoke SHA-256 is `44e72dee075ad30aa6bd525cd952ce47ff33901cedc09e875f721e13d417f0fe`.

## Measured aggregate outcomes (multiclass Brier; smaller is better)

| Arm | Overall Brier | Unseen action-1 states Brier | Fit+evaluation CPU, seconds |
|---|---:|---:|---:|
| Local directed causal flux / MAP | 0.465444 | 0.774056 | 0.036268 |
| Exact structured graph Bayes | **0.228828** | **0.340636** | 0.119058 |
| Fully fitted conventional row-Markov | 0.623839 | 0.833333 | 0.020072 |
| Action-blind fitted rows | 0.629804 | 0.811458 | 0.019931 |
| Uniform no-learning | 0.833333 | 0.833333 | 0.019915 |

- INVERSE regime recognition: 9/10. SAME regime recognition: 6/10; **4/10 false action-effect declarations**. INDEPENDENT regime recognition: 4/10.
- Serialized prediction round-trip passed 30/30. This is **not** multi-world cumulative model retention.
- Worst action-0 familiarity Brier deterioration: 0.009167 (below the 0.01 tolerance, but not enough to qualify).
- Process CPU for the entire combined simulation and scoring: 0.281411 seconds. Ratio 0.119058/0.036268 = 3.2828 only measures separately accumulated fit+evaluation time for two arms; it does **not** establish a matched all-in 2x efficiency gain.
- Relative to exact Bayes, local flux Brier worsened by 0.236617; the permitted accuracy loss for a cost win is 0.005.

**Frozen category:** `MIXED` for unseen-row improvement over unstructured fitted Markov, **NO-GO for scientific superiority** and no accepted model integration. This is development-scale source-free evidence, not original Yggdrasil first-use or independent scientific qualification.

## Mechanistic diagnosis

The candidate chooses a **single discrete cycle and regime** after fixed bounded local search. When its structural guess is wrong, it predicts a high probability (0.9) for the wrong transition. The exact Bayes arm instead marginalizes across all 120 possible directed cycles and all three relationship families. Its calibrated uncertainty limits catastrophic errors and is a properly matched strong control. Under the specified world generator, exact Bayes also matches the data-generating hypothesis class. No scientific claim can rest on outperforming a weak unstructured baseline alone.

The next potentially productive question is **whether uncertainty-aware, streaming, persistent directed-relationship memory can approach Bayes calibration at materially lower total computation without false interventions**. Do not relabel a Bayesian posterior as energy. Compare retained native action-consequence readouts and strong conventional graph-learning controls; cost must include candidate inference and checkpoint restoration. Any new trial needs fresh preregistered worlds and an independently reviewed first-use gate.

## Reproduction and custody

A permitted **distinct smoke only**, on a checkout containing this exact frozen executable:

```bash
python research/contrib/chatgpt/ENERGY-TOPO-02/experiment.py --smoke --out smoke-check.json
```

This does not license replay of the original primary cohort or reinterpret the smoke as scientific acceptance.

The existing [G29 Atlas CI run](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44721882132) failed on Linux and Windows at `YGG_ATLAS_FAIL_CLOSED: indexed file set changed`. The check indexes new files under this branch against the branch's older pinned source atlas. It is an **atlas source-set custody failure**, not a measured learning failure. Atlas regeneration at an exact final candidate source commit, dual-platform regressions, independent reproduction, and central owner acceptance remain separate.

See [provenance.json](provenance.json) for hashes and limitations; [result.json](result.json) for aggregate measurements. No source files or frozen decisions have been edited after primary scoring.
