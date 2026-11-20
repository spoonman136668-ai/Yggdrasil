# NCI-SOURCE-02 — Actual public-source mapping and native initial-state consistency

**November 19, 2026. Independent Yggdrasil contributor, NOT central Amalgam coordinator.** Scope is read-only source / schema / negative-control audit. No original-world environment reset, `do` action, source lease, native checkpoint update, trainer, runner, merge or accepted-ref modification.

## Original source proof and non-overlap

The preceding [NCI-DISJOINT-01](../NCI-DISJOINT-01/README.md) showed an exact loss when a *hypothetically* public fourth state bit `u` is omitted. It **did not** show that such a bit is publicly available in the admitted Causal-Gymnasium source or actually dropped. NKR-14 already covered underdetermination from eight sampled contexts; do not re-run those worlds or call this a new scientific study.

This gate inspected the independently authored **original source** `CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf` (Apache-2.0, same pinned source accepted for earlier source-only research) and the unchanged FKP-24 public MDP adapter, and compared them with the actual research Amalgam observation methods. Source readback identity is Git's SHA-1 **blob** identity, not claimed producer authenticity.

| Interface/source file (exact commit as above) | Git blob | What ordinary learner can see |
|---|---|---|
| Upstream `causal_gym/envs/dtr.py` | `6af2371dce21804140ea141ccb7be14e003ba275` | Public DTR `do` callback receives initial `S1`, or at second stage `(S1,X1,S2)`; reward `Y` follows second action. No independent public `u` input. `see_policy` can access `u` but **must not** be confused with the public interventional `do` policy |
| Upstream `causal_gym/envs/mdp.py` | `6264ec5450754c009e98c3e85f6d5927ece0a9ab` | Public MDP `do` callback receives one state `S`; its 5-tuple result contains next `S`, reward, terminated, truncated, diagnostics. Confounders `u1,u2,u3` are sampled privately, not returned as public variables |
| Upstream `causal_gym/core/pch.py` | `ff37780c6b791877c70583b8d5f699be7fcd8817` | `info` may contain auxiliary/private diagnostic fields, so treating all `info` as learnable input is unsafe |
| FKP-24 `research/contrib/chatgpt/FKP-24/native_public_mdp.py` at `f99552f29947767eb8764c68ba72518327c3d25c` | `4424eadef179996ff491911efadfbe4e07761062` | One observed `(before,action,reward,after,terminated,truncated)` event/`do` action, policy receives only current state and already-witnessed history; `info` is intentionally never read |
| Amalgam `yggdrasil/native_episode_experience.py` at `86264b41a08d49f558418c0fba367f3a2636befa` | `5a18b00a4c4131526e71f51d63dfd9eb9471c81e` | Requires `ROW_FIELDS=(s1,x1,s2,x2,y)` and two `(bit,bit)` views. It **validates but does not use the value of `row['s1']`** when encoding a ledger event |
| Amalgam `yggdrasil/native_causal_amalgam.py` at same head | `287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952` | Requires `views[0][0]==views[1][0]`, but does not compare either to `row['s1']`; cold restoration reconstructs `s1` from `views[0][0]` |

**Correction to last stage:** None of the original DTR/MDP source evidence supports claiming that the *hypothetical* `u` exists in this public adapter. The **actual** source-specific integration challenge is honoring stage/role and provenance semantics: DTR is a two-stage completed episode, MDP is a rolling, one-stage transition. An automatic cast of MDP rows to DTR five-field rows would invent a second action and should be refused until an owner-approved explicit mapping exists. The existing FKP-24 MDP adapter is source-only and does not install those episodes into the cumulative Amalgam.

## Precisely located native source-record consistency gap

At the research Amalgam head, the **actual native** `NativeEpisodeExperience.observe(identifier,views,row)` source computes:

```python
bits = [PublicCausalCells._bit(row[name], name.upper()) for name in ROW_FIELDS]
event = (identifier, views, *bits[1:])
```

The first value `bits[0]`, namely `row['s1']`, is discarded. The only cross-view check in `NativeCausalAmalgam.observe_experience` is `views[0][0] == views[1][0]`; restoration reconstructs an `s1` value from `views`, *not the original row*. Thus when `views=((0,0),(0,1))`, rows with identical `(x1,s2,x2,y)` and the same identifier but `s1=0` or `s1=1` map to **the same stored event**. Repeating with the changed `s1` is accepted as an idempotent replay, rather than a conflicting source row, when the caller supplies the matching recalculated `packet_sha256`.

This is a **source-row consistency / lineage-proof hole**, not a demonstrated native forecast degradation, a real source attack or a scientific result. It occurs in the **unmerged research** NativeEpisode path; it does not establish a defect in the accepted `main` YPC1 control or the upstream DTR/MDP source.

**Smallest proposed validation at the existing native ingestion interface:** require `row['s1'] == views[0][0] == views[1][0]` *before* accepting a new event; preserve exact existing checkpoint schema, all currently consistent rows, source ledger prefix and idempotency; reject conflicting source records and mismatched paired views; never ingest source-private `u`, diagnostic `info`, hidden simulator graphs or labels. Add exact native frozen-source negative tests and full dual-OS final regression on a separately authorized candidate SHA. This contributor **does not patch** central Amalgam model code, and does not invent a new actor or source bridge.

## Reproducible evidence

Standalone `verify_public_ingress.py` has eight public-source-free contract tests and an optional **strict pinned original-source audit**. The default execution tests only invented rows and a proposed validator: **8/8 PASS**, outcome `PROPOSED_CONTRACT_FIXTURE_ONLY`. An additional local isolated AST execution of the exact displayed original `observe` method excerpt with an in-memory ledger stub showed the collision, unchanged replay, and correct nonbinary rejection; this is **not** a full native import/cold-restoration test. No training or original source actions occurred.

```bash
python -B verify_public_ingress.py --report newly-created-result.json
```

When an **independently qualified read-only checkout** of the exact original five sources is available, execute:

```bash
python -B verify_public_ingress.py \
  --native-episode /pinned-amalgam/yggdrasil/native_episode_experience.py \
  --native-amalgam /pinned-amalgam/yggdrasil/native_causal_amalgam.py \
  --upstream-dtr /pinned-original/causal_gym/envs/dtr.py \
  --upstream-mdp /pinned-original/causal_gym/envs/mdp.py \
  --public-mdp /pinned-fkp24/research/contrib/chatgpt/FKP-24/native_public_mdp.py
```

It **fails closed** on any unexpected Git blob, source signature, invalid field or incompatible method, then extracts/executes *only* the actual original `NativeEpisodeExperience.observe` Python AST method with a small ledger-only stub and checks two distinct public `s1` values map to the same event. This is execution of a source method, **not** native Amalgam training, native full integration or authenticated original-source physics. No local clean full-source checkout was available during this contributor gate; this strict five-source mode remains **UNVERIFIED** despite independent GitHub Git-blob readbacks. The upstream original source is publicly licensed, but protected first-use is still denied by [source-owner issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426).

**Native integration interface:** existing `NativeEpisodeExperience.observe` / `NativeCumulativeLearner.observe_experience` / `NativeCausalAmalgam.observe_experience` and their exact checkpoint replay; no new learner type needed. Submit for independent review by the *sole* central **Unified Causal Intelligence Amalgam Work** coordinator. The contributor must not merge, activate or promote the proposed guard independently.

**Disposition:** ENGINEERING source readbacks PASS; local contract fixture 8/8 PASS; strict five-source executable mode UNVERIFIED; scientific new-law/retention/transfer gains UNVERIFIED; DEPLOYMENT NONE. Existing ENERGY-67/69/71 NO_GO outcomes unchanged. Separate existing G29 atlas baseline CI failure on archive PR #1210 is not part of this causal-source proof.
