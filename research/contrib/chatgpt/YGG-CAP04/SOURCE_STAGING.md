# CAP04 prospective-source staging (no scientific first-use)

This source-only staging branch is based on Yggdrasil CAP04 last independently qualified SHA \`8ea46213e081d6f5ca89a38ff919ae54015d8ed2\`; it does **not** advance draft PR #1324 while separate owner work modifies fixture audit and atlas coverage.

- \`prospective_source.py\` defines a bounded deterministic A/B/A, 96-event, four-action-pair source construction. Public rows contain only id, current public views, chosen action, witnessed intermediate sensor, reward, and actual post state.
- Registered DEV seeds \`99917/99931\` and all reserved pilot/primary seeds **cannot be generated**; the registered first-use function deliberately rejects them. Only two disjoint engineering fixture names are allowed.
- \`test_cap04_prospective_source_contract.py\` checks registered-source fail-closed behavior, deterministic chronology and public input shape, action coverage, budget and seed-domain isolation. A local isolated standard-library preflight passed 3/3 tests. **No exact-repository or dual-OS CI acceptance is claimed for this staging branch.**
- The frozen \`prereg.json\`, accepted \`main\`, original native/JEPA checkpoints, and official source/runner authority are untouched. No new scheduler or controller.
- Stage outcomes are engineering fixtures, never predictive accuracy, scientific confirmation, transfer, or native cumulative-training evidence. Before integration into PR #1324, reconcile with its live SHA and active fixture-audit changes, regenerate the source-exact G29 atlas, then perform mandatory full two-platform final regression. A separate owner-qualified authorization is required before any registered first-use.

This staged source is intentionally **not** a usable scientific generator. The source construction must be frozen and independently reviewed before a later scoped first-use unlock, with no after-outcome tuning.
