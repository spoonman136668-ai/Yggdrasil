# CKAD18 fresh-world parallel synthetic development

**Status:** LOCAL DEVELOPMENT GATES MET / DUAL-OS ENGINEERING UNVERIFIED / SCIENTIFIC_PASS=false / DEPLOYMENT NONE.

This is an isolated candidate, based on the existing CKAD18 fresh-world preregistration at `03fc576270d197d0e6994ae43073b54aab3c9903`, itself one commit after CKAD17 `ba3a3b7513806d17e0a8f4b808e0055d18957555`. It does not edit the cumulative CKAD18 branch or accepted Yggdrasil model.

## Source and reproducibility

- Frozen protocol: `prereg.json` in this directory (unchanged).
- Candidate source: `experiment.py`, SHA-256 `90b40b70e7b095f97aeb282a909b331aa69ba8be255ab7184413f3167edc7a51`; Git blob `b74e10292f69e4a95002526cb43d6f9ef44093e7`.
- Candidate Git commit: `4276cde3b4e06404ccd404bd57992e05a692b9a8`; CI workflow commit `149f5fe4f573051d9ee57144fe1d20abbcc889a1`.
- Local runner: isolated Python 3.13.5, Linux, no paid API, no original source action, no protected first-use data.
- Command: `python -B research/contrib/chatgpt/CKAD-18/experiment.py > result.json`
- Canonical primary result, SHA-256 `ccb94d08555b028e423a6dc688e6847348237776074a9c5fc3a82e9cc836b06e`; two subsequent local exact-byte runs produced the same hash.
- Primary frozen design: 5 seeds × 2 families × 6 unseen held pairs = 60 cases; 5 training tasks × 6 observed interventions per case; 4 test interventions per case and arm; 16-context held forecast scoring.

## Local measured outcome

| Arm | Brier 0 | Brier 2 | Brier 4 | Decision regret after 4 |
| --- | ---: | ---: | ---: | ---: |
| Native meta + active | 0.18750000 | 0.14409722 | 0.06749132 | 0.00000000 |
| Native no-meta + active | 0.25000000 | 0.17586806 | 0.09379340 | 0.00000000 |
| Native meta + random | 0.18750000 | 0.12998566 | 0.08737352 | 0.01041667 |

- Meta + active Brier2 vs no-meta + active ratio **0.81934847**; frozen target <=0.85 met.
- Meta + active decision regret4 vs meta + random ratio **0**; target <=0.85 met (random regret denominator small).
- Fully matched independent per-law exact Bayesian test-control predictions agree within **3.33e-16**. **No advantage over exact Bayes**.
- Negative control: invert held domain family -> meta-active Brier2 **0.45850694**, substantially worse.
- Negative control: cyclically shuffle training labels -> meta-active Brier2 **0.14409722**, effectively unchanged. This diagnostic **does not establish sensitivity to that perturbation**, a limitation to investigate in the next distinct preregistered experiment.
- Random selection **beats active** at the 2-action Brier metric: 0.12999 versus 0.14410. Do not claim better causal intervention selection.
- Test is synthetic and the hypothesis class is specified in advance: no free-form structural discovery, real-world transfer or general intelligence established.
- One code assertion involving training/test action overlap is tautological; it does not establish leakage prevention. Independent validation is still required.
- The script's `engineering_contract_pass=true` is a local self-check, **not an external engineering qualification**. The frozen gates are development-only.

## CI and qualification

- GitHub Actions run [44217709232](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44217709232) was **FAIL before starting any jobs** (zero jobs returned). Root cause not verified; no hosted reproduction or dual-platform final regression occurred. This is an infrastructure/workflow initiation failure, not a measured training NO-GO.
- Workflow requests pinned Python 3.12 and exact result hash, then mandatory full inherited regression on Linux and Windows. Workflow has read-only permissions and cannot mutate accepted branches.
- Existing separate CKAD18 cumulative run [44215859139](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44215859139) completed 9/9 jobs successfully. Its results are not evidence for this fresh-world candidate.

**Next executable gate:** Diagnose the zero-job Actions failure, independently validate source-free negative controls and leakage boundaries, execute exact-source dual-OS qualification, then separately evaluate whether active selection delivers any advantage over strongest matched random/Bayesian controls. No merge, scientific first-use, owner/controller change or model deployment.
