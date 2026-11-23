# WSCM-TRANSFER-02 — v7/v9 compatibility and exact-source native qualification

**Date:** 2026-11-23. **Disposition:** PR #1364 native v9 full regression **PASS** on exact Git tree; separate composition research overlay **focused local PASS**, full *combined* CI **UNVERIFIED**. No scientific gain, owner model acceptance, or deployment.

## Custody and exact source

- Research branch parent: `71c95cd7eb62a9a213d1d80abaaebb1e03716361` (tree `65f5646710d0624a96ed2fceb5968ac9e0ef344b`).
- Pre-execution v9 interop freeze: `bdd17208f3ca1f19a65945e9951564ae01e0ced0`.
- Test source: `bb980368bd7196bc311da538bbec8e360dd6a401` (tree `7768315f0f2c9b2371976b37733a299c4d559bff`). Test Git blob `784de2a7536ff622ddcee416c504ea764ada541b` matches local `git hash-object`.
- Native v9 PR #1364 current head: `9a1d09e09824ea9494db46b7f9970e0fdc1ee704`, tree `6e0f7cc626509a001cffbb87c4f1ff010df5c28a`. Its parent `26bb026dbb1e8e6c0ea55ecf78094623b25af15c` has **exactly the same tree**: the intervening commit was empty.
- Source blobs byte-verified in local Linux CPython 3.13.5: `native_episode_experience.py` `5a77232cdd4a0fda314e47278c9ba0ed109cfd50`, v9 sparse `1fda97c9a3c53e32d0be880353bda2ce02b32237`, native external identity `b31538c00cda5e7b526aa1178e883e86a26be0d4`, fixed-grammar readout `80d379f216279465f63879b38041f91f65b51cd0`, unrestricted safety readout `a29be47fa3531e01ad6215f82bac74f6f9ea4430`.
- The research readout files exist on a **separate research branch** and were intentionally overlaid onto locally reconstructed exact v9 native modules **only in scratch testing**. They are not bundled into PR #1364's tree.

## First-party full native CI evidence — PASS, not assumed

The [existing qualified native workflow run #45204694334](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/45204694334) used source `671e55bc6582885657520ed6ddc01027861b4c50` and generated atlas-only child `26bb026dbb1e8e6c0ea55ecf78094623b25af15c`. **Both native job logs explicitly print** `WSCM_CANDIDATE_SHA=26bb026dbb1e8e6c0ea55ecf78094623b25af15c` and `WSCM_SOURCE_SHA=671e55bc6582885657520ed6ddc01027861b4c50`.

| Runner | Full regression | Skip count | Result |
|---|---:|---:|---|
| Windows 2022 job `137797543292` | 623 tests | 5 | **PASS** |
| Linux job `137797543296` | 640 tests | 4 | **PASS** |

Both runner logs show `test_native_sparse_operator_integration.py` **9/9 PASS**, including the cumulative-learner public method check. Earlier isolated-source execution reached 8/9 and could not import `native_cumulative_learner` locally: this was **missing scratch dependency**, not a verified production regression; the complete repository CI resolves it. Additional regression/test groups in both jobs also reported OK. The [independent G29 run #45208116400](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/45208116400) passed Windows/Linux at head `9a1d09e`; this is atlas verification and not itself native acceptance.

Only generated atlas files changed between the native source commit and the current head. **This makes the full-native CI result valid for the v9 source tree**, without claiming the research overlay itself passed the native CI.

## New interop source-free tests — PASS locally

Using the exact pinned source modules in a reconstructed local Linux Python 3.13.5 tree:

- The previously prepared `tests/test_wscm_transfer02_*.py` subset yielded **36/36 PASS** in both normal and `python -O -B` modes, with the actual v9 `NativeEpisodeExperience` and the research-only readout.
- Newly frozen `v9-interop-dev-test.py` yielded **6/6 PASS** both normal (~0.017 seconds) and `-O` (~0.023 seconds). Cases: v7→v9 and v9→v7 envelope order, cold restore and consolidation, checkpoint and native binary forecast nonmutation, sparse fixture independence, unseen action ID abstention even when sparse evidence exists, and hidden-phase rejection after both envelopes.
- Conservative unknown-wire result remains `ABSTAIN` with `possible_next_bits=[0,1]`, not an arbitrary single-bit invention. On a matched set-valued symbolic control this does not demonstrate superior transfer or intelligence.
- The isolated scratch copy of `test_native_sparse_operator_integration.py` passed its other 8 cases and had one import error due to omitted local cumulative-learner dependencies. **Full exact-source original CI passed all 9**, independently. These are separate test scopes and must never be rolled into a false combined 9/9 local claim.

Run the new test only in a source overlay containing **exact** v9 native modules and both separate research readout files:
```sh
PYTHONPATH=".:research/contrib/chatgpt/WSCM-TRANSFER-02" python -B research/contrib/chatgpt/WSCM-TRANSFER-02/v9-interop-dev-test.py -v
PYTHONPATH=".:research/contrib/chatgpt/WSCM-TRANSFER-02" python -O -B research/contrib/chatgpt/WSCM-TRANSFER-02/v9-interop-dev-test.py -q
```
Do not run it directly on the research branch's older v7 episode source: it deliberately requires v9 interfaces that are not present there.

## ENGINEERING / SCIENTIFIC / DEPLOYMENT conclusion

- **ENGINEERING — original v9 PR source:** PASS, first-party dual-platform full native regression, G29, and original v9 interface 9/9.
- **ENGINEERING — added readout overlay:** focused local PASS 36/36 plus 6/6; **combined-commit full Linux/Windows CI UNVERIFIED**; research test and readout are not integrated into v9's native CI tree.
- **SCIENTIFIC — transfer:** UNVERIFIED, with known unrestricted-wiring non-identifiability. No measured gain vs equally informed symbolic control, no externally authenticated sequential interventions, no new held cohort or action-cost evidence.
- **DEPLOYMENT:** HOLD; original accepted main remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, draft PR #1364 remains open and unmerged, separate research branch remains additive only. No runner dispatch, source first-use, merge, live action, or owner acceptance was performed in this work.

**Next eligible gate:** after verifying lineage/authority, qualify a single combined exact-tree candidate with these research-only tests and original final full Linux/Windows suite; keep original v9 source isolated and do not count matching symbolic predictions as independent scientific improvement.
