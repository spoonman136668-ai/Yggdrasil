# Native numerical public-event ABI P0 — frozen engineering protocol

**Purpose:** Provide a minimal, read-only, source-neutral *event representation*, not a learner or a native integration. Strictly retain a one-step 5-way public action, numerical before/after observations, scalar reward and termination/truncation without fabricating CKAD's two-stage binary `x1,s2,x2,y` sequence. No hidden task identity, environment `info`, owner authority, source-world calls, training, inference, or accepted native state changes.

## Pins and custody

- Original Yggdrasil sole coordinator PR #1278: `86264b41a08d49f558418c0fba367f3a2636befa`.
- Existing MHE-01 source fence draft PR #1334: `14d4c57e31cae6878492d536f76d295e1d06215c`; original MetaHighway upstream `a194c73b3261a137d84521e1520dfa4f4c690faa`, `meta_env.py` blob `ee4f09ad7e4348963ad50c2e25499eab0df6736d`.
- Original native episode blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`; direct native ABI invalid on five actions and numeric next observations by previously qualified MHE01-D tests.
- Protected original-world first-use owner issue #426: NO-GO. No source reset/step, world action, trained native model, runner, CI dispatch, or new owner process.

## Frozen contract (before implementing and executing tests)

1. Pure stdlib data holder admits only exact public packet keys: `source_sha256`, `identifier`, `step`, `before`, `action`, `after`, `reward`, `terminated`, `truncated`. Strict source and 64-lowercase-hex identifier, exact integer step starting at zero and increasing by one, 5 distinct exact-int actions `0..4`; no bool coercion, no numeric bins or implicit CKAD row.
2. `before` and `after` are fixed shape tuples of finite Python floats (preserve signed zero and bit pattern in canonical state), dimension 1..128; reward finite Python float, unit is left unchanged. Do not infer a reward classifier, next stage or hidden causal source. Input floats only: no implicit string/int to float conversion; output canonical representation preserves IEEE-754 binary64 bits and avoids Python JSON NaN values.
3. Ingest creates a new immutable history, preserving old event evidence and chronological ordering; source checksum remains the declared code pin, *not authenticated world provenance*. Stop at a fixed bound 2048 public rows; this is an independent research log limit, NOT a native CKAD capacity increase.
4. SHA-256 checkpoint seals exact typed public events; cold restore requires digest and schema/source/shape/count validation, no private metadata; malformed/replayed events fail before mutation. No `train`, `act`, `reset`, `native_admit`, `submit_owner_approval`, scheduling or environment methods. Explicit fail-closed `require_native_abi` raises for all valid packets.
5. Tests require five-way distinct identity, bitwise float/negative-zero retention, chronological no-gap constraints, immutable append, strict public shape/type, hidden fields/owner claims rejected, terminal stop, stale digest rejection, checkpointer cold parity, action count and 2048 bound, and zero source/model side effects. One fresh process test repeat; source/test Git blob readback.

**Classification:** focused engineering P0 only even if every test passes. Exact native import, complete Linux/Windows final regression and scientific gain all **UNVERIFIED**. No PR merge, accepted ref or source-world first-use.
