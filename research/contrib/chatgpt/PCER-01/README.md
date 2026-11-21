# PCER-01 — Predictive-Coding Error Residuals (read-only development negative)

**Status:** retrospective synthetic-development **DEV_NO_GO**; native-science **UNVERIFIED**; deployment **NONE**. This is a contributor diagnostic for the single existing [Amalgam coordinator PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278). It does not create a competing learner, admit a new episode, change G41, merge anything, restart training, or alter accepted main.

## Frozen identity and execution boundary

- Preregistration committed first at `606713e8dc6ba6b94aa40ab0e8b9f257b0c22560` ([prereg.json](prereg.json)), raw UTF-8 SHA-256 `a5151332459ffe4244debd570880c2f9a57d31a459059fc6c5a8b64ba2265fa0`.
- Parent source: Amalgam `86264b41a08d49f558418c0fba367f3a2636befa`, unchanged. Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Original **already consumed** [selection development trace](../CAUSAL-AMALGAM/selection-dev-01/trace.json): **96 episodes**, raw SHA-256 `36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114` (matches prior producer), source Git blob SHA-1 `9db0d3742fc8bd009c61d0864e4aba739a19e4e1`. Source evidence remains losslessly in the original immutable repository blob. **Zero fresh source actions**.
- Frozen chronological split: FIT 0–49; VALID 50–63; familiar-regime return HELD 64–95. This is **not unfamiliar causal-family transfer**.
- Frozen active replay quota: 10 of 50 FIT witness IDs: 7 highest prequential *native* transition residual, 2 rare/coverage preserving, 1 fixed-hash uniform. Matched 10-ID controls are pure error and uniform; full-fit history uses all 50. Only reference slots are reduced, not checkpoint bytes or archived evidence.

The selector consumes *already produced* native pre-outcome forecasts from the existing `selection_trial.py` witness trace, never hidden world laws or outcomes from VALID/HELD. The selected IDs can be handed to existing read-only witness retrieval. The current cell-score evaluator deliberately does **not** retrain `NativeCausalAmalgam`, touch its checkpoint or claim an 80% reduction in the actual learner state.

## Frozen outcome (read-only retrospective)

| Criterion | Full 50 history | Uniform 10 | Pure error 10 | PCER-01 10 |
| --- | ---: | ---: | ---: | ---: |
| VALID transition Brier (14) | 0.208976 | 0.262857 | 0.308393 | **0.354286** |
| Familiar return transition Brier (32) | 0.194191 | 0.232083 | 0.551641 | **0.375078** |

PCER vs full-history: **+0.145310** VALID and **+0.180887** familiar return, both far above the frozen **+0.02** maximum. Versus the better bounded replay control, PCER is worse by **+0.091429** and **+0.142995** respectively, rather than beating it by `0.005`. The measured **80%** saving is **only active replay reference slots (50→10)**. Full original witness evidence remains available. This experiment therefore **fails**, including the simpler uniform replay control.

Using three frozen paired bootstrap seeds (24,011 / 24,029 / 24,041) at 2,000 resamples per seed, approximate 2.5%–97.5% intervals for PCER minus full Brier were:

- VALID: about **−0.040 to +0.325**, wide and inconclusive individually.
- Familiar return: about **+0.082 to +0.275**, with all three lower bounds already above the +0.02 limit.

The underlying point-estimate selection was evaluated with an independent deterministic V8 implementation over the GitHub-connected, source-hash-verified archived trace. Paired bootstrap was computed separately with local Python 3.13 from the derived per-example loss differences. All exact values, identities, control metrics and receipt limits are in [result.json](result.json); [index-manifest.json](index-manifest.json) holds only selected IDs and provenance, not copied observations.

**Limitations:** The committed `pcer01.py` Python candidate has not yet been independently executed against the full archived trace or qualified in final dual-platform repository regression. The recorded result therefore does not constitute an exact-source Python qualification or native-lane scientific evidence. No unfamiliar transfer, fresh owner source actions, real native checkpoint cold restore, intervention value, or actual process-memory reduction was measured. Do not infer that an engineering script PASS would overcome the measured development failure.

## Reproduce without changing original evidence

From a checkout of the exact candidate branch, using Python 3.12+ and only the standard library:

```bash
python -B research/contrib/chatgpt/PCER-01/pcer01.py \
  --trace research/contrib/chatgpt/CAUSAL-AMALGAM/selection-dev-01/trace.json \
  --prereg research/contrib/chatgpt/PCER-01/prereg.json \
  --manifest /tmp/pcer01-index.json --report /tmp/pcer01-report.json
python -B -m unittest discover -s tests -p 'test_pcer01.py' -v
```

Output locations must be new; the original source stays unmodified. If the frozen source hash, source format, duplicate IDs, replay budget or cold-selection identity fails, this candidate stops. The generated evaluator report is different from the archival cross-language diagnostic receipt because execution/provenance categories are explicitly separated.

## Decision

**STOP PCER-01 as proposed.** Do not adjust the frozen selection weights or acceptance margin after seeing this failure. If testing a different memory utility criterion (e.g. prospective interference-aware gradient/forecast sensitivity or regime-diverse retention), register it as a new hypothesis and budget first, and independently qualify the same persistent native learner against fully trained matched controls, actual cold restoration, and unfamiliar-family transfer. Original source-owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) continues to block protected first-use.
