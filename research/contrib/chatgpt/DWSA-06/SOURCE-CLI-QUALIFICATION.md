# DWSA-06 — pinned original Node CLI qualification seam

**Disposition:** engineering fail-closed CLI preflight **LOCAL PASS 2/2**; full pinned Node source execution **UNVERIFIED** (upstream raw files not available in current local runtime). No scientific retest, native checkpoint integration, source first-use, deployment or learner promotion.

## Exact repository/source identity

- Accepted `Yggdrasil main` remained `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` when this gate began. Work is solely under research contributor **draft PR #1347**, `research/dwsa06-weight-only-prototype-20261120`. The existing original experiment and result files were not rewritten.
- Pinned third-party MIT donor `MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`, with exact pre-existing Git blobs: `public/assets/digit-model.json@16ea8cf939bfa0f5f21e227d159b11d4ff578eca`, `src/models.js@6f95eea88422ceb01b3118e65cd45b9a4c065bd9`, `scripts/train.mjs@1776478a312781e0866f16e1ef237fcbc1092d1a`.
- Exact original contributor script blobs: `run.mjs@eee673dd0e8af3089bc5d1b686e4e00627940ead`, `untrained_ablation.mjs@2da6cecf437a67fc24b72c70de1874f147191840`, `layer_intervention.mjs@2c5db1d84206122abe53f6fed94caaa2ba1b3b0b`.
- `qualify_source_cli.mjs` locally verified Git blob **`abe2f20b4c4ca2b7317e42975ea0466080678566`** after a Windows-safe minimal environment correction. `test_qualify_source_cli.mjs` locally verified Git blob **`5762a9da8f9a73f4ce2e05ee046004dcec4357e7`**. Both were checked against the *actual committed GitHub blobs*.
- Original upstream model, source and training JS contents were inspected through the connected GitHub read tool with exact ref and blob identities, **not** downloaded to the local Node runtime, and **not** committed to Yggdrasil.

## What the runner will do, once exact inputs are staged by an authorized qualified route

From `research/contrib/chatgpt/DWSA-06` execute:

```bash
node qualify_source_cli.mjs /absolute/path/to/digit-model.json /absolute/path/to/models.js /absolute/path/to/train.mjs
```

In order: check 3 original upstream Git blob SHA-1 values over exact raw bytes (including Git blob-length prefix); check 3 original contributor script Git blobs before execution; launch only these three preexisting source-only stateless JS programs separately via exact Node executable using argument arrays, with 60-second bounded timeouts, 2 MiB stdout buffer and minimal nonsecret process environment for Windows/Linux; parse each JSON receipt; verify **1615/2000** trained / **1985/2000** matched supervised, 84B SHA-256 checkpoint `a32ff3ae95dbe040b87b9763a1586fdb4a2e459b5375de99fe9c7a8a8e444135`, **230/2000** exact seed-matched original initialization, best-of-16 untrained accuracy **0.2135**, full 16-mask series and best mixed mask 11 accuracy **0.6665**, cross-script checkpoint SHA agreement, cold restore/negative tests encoded in child outputs, zero teacher forward and zero original world actions.

The runner performs **no download**, no checkpoint write, no model execution, no source environment interaction and no training. Never substitute the historical donor ZIP, alternate source SHA, different seeds, simulated model data, or private original-world actor to force an apparent PASS. Original source training file is inspected as static text, never executed.

## What actually ran (Linux local; Node.js v22.16.0)

- `node --check qualify_source_cli.mjs`: **PASS**.
- No CLI arguments: **FAIL CLOSED**, nonzero exit, exact `DWSA06_QUALIFY_REJECT_EXPECT_MODEL_SOURCE_TRAIN_PATHS`.
- Three tampered/synthetic input files: **FAIL CLOSED**, nonzero exit, exact `DWSA06_QUALIFY_REJECT_SOURCE_BLOB_0`, before any original script is launched.
- `node --test test_qualify_source_cli.mjs`: **2/2 PASS**, zero failures/skips; recorded TAP duration approximately 213 ms (diagnostic only).
- SHA of exact local `qualify_source_cli.mjs` bytes matches committed GitHub blob; same for `test_qualify_source_cli.mjs`.
- **NO full original Node source CLI positive test occurred in this environment.** Public `raw.githubusercontent.com` could not be reached from the local container, and direct artifact staging of the source was unavailable. Connected GitHub content read verified sources and core computations but does not itself place byte-identical source files on the Node filesystem.
- Previously verified core `analyze` from the exact committed `run.mjs` independently re-evaluated against connector-read original donor text in isolated V8, reproducing 1615/2000 vs 1985/2000, and exact `untrained_ablation.mjs` core reproduced original initialization 230/2000 vs highest 21.35%. These are **V8 core recomputations, not positive Node CLI execution**.
- Earlier local actual *donor-derived checkpoint* Node codec replay (3 cold restores, 7 tamper negatives and 1615/2000 Hamming predictions) remains valid; it is **not** repeated here. See `DONOR-DERIVED-NODE-REPLAY.md`.

## Qualification boundaries and next eligible action

1. **ENGINEERING:** source-identity verification and CLI fail-closed negative checks LOCAL PASS. Full positive original Node CLI, exact-candidate Linux/Windows full regression **UNVERIFIED**. G29 generated-code-atlas source check on prior PR heads failed on both OS *before test entry*; do not misclassify as a DWSA-science failure or bypass the atlas.
2. **SCIENTIFIC:** no new source science performed. Historical DWSA-06 80.75% versus same-footprint fitted/symbolic 99.25% remains development-only on ten familiar synthetic templates. No unfamiliar causal world, independent knowledge transfer, cognitive retention, or scientific gain established.
3. **DEPLOYMENT:** NONE. Accepted `main` and unified Amalgam cumulative model remain untouched; no workflow/runner dispatch, source first-use, merge or promotion.

A qualified **owner-controlled local checkout with exact upstream raw bytes and appropriate custody** can run this existing command and collect its exact receipt, then regenerate the three atlas artifacts through the existing source-pinned workflow and run mandatory full final Linux/Windows candidate-SHA regression. Until then **UNVERIFIED means UNVERIFIED**, not a claimed completion.
