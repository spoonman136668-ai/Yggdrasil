# WSP-209 — Was cumulative learning suppressed by the write gate?

**Verdict: `INFORMATION_LIMIT` (synthetic development; not real-source science).**

We preregistered the four worlds and decision rule at `da819cdc4f0883a71fd6e3c044e6a1489d69c893`, **before** executing or inspecting new outcomes. We reused the rank4, lambda10, initialization, four-stage source-free learner from WSP-200, without opening original GFP values, modifying WSP-200, or running native Yggdrasil.

The fixed worlds use two hub graphs and two complete graphs, seeded 20911–20914. Every method sees the same cumulative FIT groups; no RESERVED group label is ever computed. We compared contradiction gating, always-write, converged rank4 refit and no-update, measuring B0 witnessed MSE after each training stage, address writes and novel held group RMSE.

**Result:** In **4/4 worlds**, both contradiction and converged refit have essentially **1.0 B0 MSE**, with gain well below the preregistered 20% threshold. Both yield held predictions close to the zero-interaction baseline. Contradiction changed only 1.37%, 1.56%, 7.00% and 2.08% as many addresses as always-write. The frozen decision rule therefore classifies `INFORMATION_LIMIT` rather than `UPDATE_SUPPRESSION`. We **cannot** blame the selective gate alone. This suggests stronger investigation of regularization, address identifiability and factorization before any further speed optimization; it does not diagnose which of those factors causes the limit.

**Cross-platform receipt:** [Full frozen diagnostic](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44614622932) (**PASS Linux+Windows: 54/54 root, 39/39 inherited WSP200, 3/3 new WSP209 each OS**) and [G29 atlas](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44614623190) (both OS PASS). Each OS reached the same classification and numerically matching per-world metrics.

Exact evidence: [`result.json`](result.json), [`provenance.json`](provenance.json), `prereg.json`, `diagnostic.py`, `test_diagnostic.py`.

To reproduce: `python -m unittest discover -s research/contrib/chatgpt/WSP-209 -p 'test_*.py' -v`, using Python 3.12 and the exact PR SHA. Output includes `WSP209_FABRICATED_SUMMARY`.

**Boundaries:** No scientific pass, no original data first use, no native-model learning, no PR merge, no Forge/Yggdrasil owner runner. The **WSP-200** frozen original-data protocol remains unchanged and source-first-use-blocked. This result is a transparent **negative synthetic development finding**; no thresholds/seeds were adjusted after inspection.
