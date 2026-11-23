# WSCM-TRANSFER-02 — combined native v9 + read-only composition qualification

**Date:** 2026-11-23. **Result:** EXACT COMBINED TREE CREATED AND SOURCE-INTEGRITY VERIFIED; **FULL COMBINED-TREE REGRESSION UNVERIFIED**, G29 GENERATED-ATLAS REANCHOR REQUIRED. No scientific gain, accepted-model mutation, runner dispatch, or deployment.

## Reproducible custody

- Repo: `spoonman136668-ai/Yggdrasil`.
- Isolated research branch: `research/wscm-transfer02-v9-combined-qual-20261123`.
- Original v9 PR #1364 head **`9a1d09e09824ea9494db46b7f9970e0fdc1ee704`**, exact tree **`6e0f7cc626509a001cffbb87c4f1ff010df5c28a`**.
- Source from independent read-only research branch `research/wscm-transfer02-wire-preflight-20261123` at `ca5e2450a33e2e5e45048012598b2a5e8d009a6c`.
- Frozen combined-gate preregistration commit **`d6d112c860a9d03a10c2ced18a8dd6532146762d`**, tree `e44753a47f58720fcaab2e3ff87261e9d9533964`. Its parent is original PR #1364 head. Prereg blob `49179217834bd8e139ee95297461e8a5ab295476`.
- First combined candidate commit **`e362a49317ff4c7e7ab3c814264d07f151036fb1`**, Git tree **`a89380cb23b55f2e8e6e7cb1bcb83b1fecc34b61`**. Exactly **9 added paths** vs the original PR head: 1 frozen prereg, 2 unchanged read-only research modules, 5 unchanged research tests, and 1 v9 interoperability test adapted solely for root-level discovery. GitHub compare reports **zero existing-file modifications and zero deletions**; no original native module, workflow, G29 artifacts, PR source, or accepted main ref was edited.
- Original readout blobs `80d379f216279465f63879b38041f91f65b51cd0` (fixed grammar) and `a29be47fa3531e01ad6215f82bac74f6f9ea4430` (unrestricted safe readout) are unchanged from the research branch, as are all five copied test blobs. The new discoverable test `tests/test_wscm_transfer02_v9_interop.py`, Git blob `886a272ef4bc872b03a42d3df4c1fa4d613975bd`, is the old locally tested six-case v9 fixture plus an import-path setup; **it has not been executed at the combined exact Git SHA**.

## Prior independent qualification (source-subset evidence, NOT combined acceptance)

- [Native v9 qualification run 45204694334](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/45204694334) **PASS**, original child SHA `26bb026dbb1e8e6c0ea55ecf78094623b25af15c`, same v9 tree as current draft PR head:
  - Windows job `137797543292`: full 623 tests, 5 skipped, remaining PASS.
  - Linux job `137797543296`: full 640 tests, 4 skipped, remaining PASS.
  - Both platform logs explicitly print exact candidate/source SHAs and show native sparse integration 9/9 PASS.
- [Independent G29 run 45208116400](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/45208116400) PASS Linux + Windows at original PR HEAD `9a1d09e`.
- The separately run exact-source local readout and v9 overlay checks in the previous research gate were PASS (36 readout-focused plus 6 new cross-version fixtures). Those local checks used verified original source blobs; **they are not a fresh full regression of the combined Git tree**.
- At the creation checkpoint, the new combined branch has **0 GitHub Actions runs**. Thus **no Windows/Linux exact-combined acceptance receipt**, and no claim that the 56 possible new root-discovered cases ran together.

## G29 deterministic blocker — identified statically, not a CI run

The committed `.ice/code-atlas.ice` on this combined branch still says:
`SOURCE_COMMIT: 671e55bc6582885657520ed6ddc01027861b4c50`,
`FILES: 1154`.

The unchanged `scripts/build_code_atlas.py` at Git blob `cef1378fd3c47ebc74675bd9dde19a183775ceeb` requires in `snapshot()`:
`paths = files_at(root, source)` and `require(paths == files_at(root, head), "indexed file set changed")`.

The combined candidate now adds new tracked `.py` and `.json` source files beyond the atlas's pinned source commit; hence the old source-commit atlas cannot be accepted for the changed tree. Running the existing G29 check **without an authorized regenerated atlas** would fail closed on the indexed-file-set invariant. This is an **identified infrastructure/provenance qualification blocker**, not an observed failing CI run or scientific negative. It must not be bypassed by altering original workflow policy.

**Required eligible qualification steps:** from an authorized full original source checkout at the exact combined candidate SHA, independently verify the checkout and parent-tree diff, use the existing pinned builder to regenerate exactly the three `.ice/code-atlas.{json,html,ice}` artifacts using the new combined source SHA, commit only those generated artifacts as a child with documented source hash, then run the mandatory complete Windows/Linux regression and exact-head atlas check via an authorized existing route; recheck custody on any drift. No new controller, scheduler or source-world first use. Do not run the frozen old WSCM workflow on the wrong branch or relabel old CI as a combined PASS.

## Final classification

| Workstream | Status | Honest benefit or limitation |
|---|---|---|
| Engineering: additive source-tree integration | **PASS** | Read-only WSCM modules and tests now share an actual v9-anchored Git tree; zero native owner modifications |
| Engineering: prior original v9 dual-OS CI | **PASS — original tree only** | V9 interface baseline preserved |
| Engineering: exact-combined focused tests | **UNVERIFIED** | No tests executed at the newly committed exact SHA |
| Engineering: exact-combined Windows/Linux full regression and G29 | **BLOCKED/UNVERIFIED** | Generated atlas needs legitimate reanchor, no authorized combined-branch runner route |
| Scientific: unfamiliar causal transfer or retention | **NO GAIN VERIFIED** | Unknown wirings abstain; equally informed symbolic control matches the supported fixture |
| Deployment | **HOLD** | Draft PR #1364 and accepted main stay unchanged |

**Action:** Do not promote or merge; the branch is a development-only qualification candidate until full exact-source G29 and regression receipts exist.
