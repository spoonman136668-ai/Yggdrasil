# WSCM-TRANSFER-02 — public action-identity DEV gate (2026-11-22)

Status: SOURCE-FREE ENGINEERING ONLY; no scored trial, native bridge, CI qualification, or scientific first-use.

Starting branch: PR #1364, cb3863052a8d7d6ef966d67da2fc7352094d64de, tree 0c925ce0c726dc0ada1635cd7083a70f12325c3f.
Coordinator: #1278, 86264b41a08d49f558418c0fba367f3a2636befa.
Native source: yggdrasil/native_episode_experience.py, blob 5a18b00a4c4131526e71f51d63dfd9eb9471c81e. Its binary x1/x2 and engineering_fixture_only interface does NOT admit authenticated arbitrary public action IDs.

The new public_action_identity.py is a research-only, immutable store of publicly witnessed outcomes for opaque external action IDs. A 4-bit signature requires observations on every one of the four binary input pairs, rejects contradictory cells by abstaining, and does not import the illustrative law or role map. Identical completed truth tables across changed IDs establish only observational equivalence, not novel causal composition or native transfer. Witness ID replay is idempotent if identical, conflicting if changed. Canonical SHA-256-pinned checkpoints restore byte-identically. Limits: 16 distinct action IDs and 256 observations, no eviction. No independent source authentication or process isolation is implemented.

Focused local command: python -m unittest discover -s tests -p 'test_wscm_transfer02_action_identity.py' -v
Platform: Linux CPython 3.13.5. Result: 12/12 PASS; no skipped tests and no scientific seeds consumed.
Exact locally tested Git blobs: source 4f83742336bb528282dabe5f28f0763b06a20feb; tests 859f3ab98a6fe96fe7877339aac1d8bf557cb820.
Coverage: insufficient-evidence abstention, renamed-ID equality, changed law inequality, contradictory witnesses, replay conflicts, metadata leakage, invalid types, cold-restore parity, corrupted/duplicated checkpoint rejection, non-evicting capacity limits, and no direct oracle import.

ENGINEERING: focused DEV PASS, native integration and complete Linux/Windows regression UNVERIFIED.
SCIENTIFIC: no scored results and no measured long-term learning or transfer gain.
DEPLOYMENT: none; draft contributor PR only.

NATIVE_ACTION_ID_INTERFACE_BLOCKED remains. Next qualifying gate is independent native external-action admission sourced from authenticated charged interventions, with no role oracle, matched fully fitted controls, fixed scorer, dual-OS exact-candidate regression and distinct owner first-use authorization before any scored experiment.
