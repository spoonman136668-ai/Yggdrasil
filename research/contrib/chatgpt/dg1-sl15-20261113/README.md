# DG1-SL15 — independently retrieved causal modules

**Experimental external synthetic DEV research only.** No native Yggdrasil weight/source, autonomy-loop, or accepted-ref modification. This is a draft, unmerged successor to DG1-SL14 PR #996, which remains scientifically NO-GO.

## Frozen question and hypothesis

The [pre-registered protocol](prereg.json) was committed **first** at SHA 54c6a289e2c4b862a026550624d0a6e585cade40, before new source, tests, or scientific result. Prior negative outcomes cannot be retuned.

SL14's full-bank archive helped returning B (168/192 versus 118/192 without retrieval) but hallucinated full-context return in previously unseen C, lost to conventional Bayesian controls, and consumed 5.27–6.31x their CPU. SL15 changes the hypothesis, not old thresholds: each of three independently learned action-conditioned causal rules has its own bounded archived evidence and paid physical witness gate. Sharing one module between contexts must **not** authorize activating an entire old context. Incrementally cache the best two gates per slot to reduce decision overhead.

## First-use physical qualification

- Fresh registered worlds only: cohorts ABAB, ABAC, MIXED, STABLE; eight independent seeds each from 108001 to 108032.
- Six independently charged arms at 96 steps each = **18,432 paid physical steps**, **14,784 real action consequences**, 3,648 charged exogenous input flips.
- Exact same physical state/action/outcome trace for the candidate and four separately executed controls: no module retrieval; frozen original SL14 whole-context fingerprint; independently implemented six-law decayed Bayesian; rolling rule fitter. Passive candidate pays the identical budget but sees a different post-step-48 action trajectory.
- Full evaluator-only held-out audit after steps 24,48,54,72,78,96; no audit labels used to train. Genuine returned-module and false-module evidence is scored **only offline**. Byte-identical cold checkpoints at 43,67,89, <=8192 bytes, all-prediction parity and tamper rejection.
- The engineering test suite contains **no registered-world scientific step**. The one prospective scientific first-use is in an explicitly fenced GitHub Actions workflow after source syntax, freeze and negative controls pass. Original per-world JSON is kept in GitHub Actions only, not ChatGPT Library.
- The preregistration fixes every primary metric, threshold, seed and classification. All primary gates must pass for a development signal. A synthetic success would still not establish native Yggdrasil improvement or AGI.

## Qualification commands

From exact branch source, Python 3.12 stdlib only:

    python -m py_compile research/contrib/chatgpt/dg1-sl15-20261113/sl15.py research/contrib/chatgpt/dg1-sl15-20261113/test_sl15.py
    python -m unittest discover -s research/contrib/chatgpt/dg1-sl15-20261113 -p 'test_*.py' -v
    python research/contrib/chatgpt/dg1-sl15-20261113/sl15.py > sl15-original-result.json
    python -m unittest discover -s tests -p 'test_*.py' -v
    python scripts/build_code_atlas.py --check-if-present

**Never promote this study on a green engineering check alone.** Preserve all nulls/failures, stop at frozen science verdict, and keep the native model, controller, Wingless/Hybrid/weight programming, workstation and main untouched.
