# Y2-SCDR04-WSCM-GRID5 — Read-Only Sinkhorn Epistemic Observer on Native `grid5` Evidence

**Status:** Isolated, source-free engineering compatibility candidate (`DEV_ENGINEERING_COMPATIBILITY_ONLY`), targeting `research/wscm-epistemic-guard-integration-20261123` (PR #1368).  
**Authority:** Read-only observer only — zero edits to `yggdrasil/native_grid5_evidence.py`, `WSCM-EPISTEMIC-GUARD-01/guard.py`, `main`, or `.ice`. Always preserves `action_admissible=false` and `family_authenticated=false`.

## What This Adds to `WSCM` PR #1368

In `NativeGrid5Evidence`, `public_role_forecast` assumes a global 120-permutation Grid5 family, so a single contradicting action (e.g., `action 0`: `(0,0)->(1,0)` then `(1,0)->(0,0)`) collapses `role_family_status` to `CONTRADICTION` globally across **all 5 actions**.

`SCDRGrid5Observer` wraps WSCM's `unfamiliar_family_readout` directly (preserving all native validators, fail-closed safety, and byte-exact `evidence.checkpoint()`) and adds **per-action Sub-Stochastic Sinkhorn Soft-Exclusion** with an un-competed `NOVEL_OR_CONTRADICTED` column:
- Isolates the contradicting action cleanly (`scdr_action_novel_abstain > 0.85`, `NOVEL_OR_CONTRADICTED`).
- Preserves clean role identification on the other 4 consistent Grid5 actions (`PLUS_Y`, `MINUS_X`, `MINUS_Y`, `STAY`; `abstain < 0.05`).

## Run Native Compatibility Tests

```bash
python3 -m unittest discover -s research/contrib/gemini/y2-scdr04-wscm-grid5 -p "test_*.py" -v
python3 -m unittest discover -s tests -p "test_wscm_epistemic_guard01*.py" -v
```
