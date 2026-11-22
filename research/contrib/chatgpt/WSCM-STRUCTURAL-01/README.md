# WSCM-STRUCTURAL-01 — Historical native causal-cell version readback

**Disposition:** ENGINEERING focused PASS; independent live retention gain **UNVERIFIED**. This is research-only additive evidence on existing contributor PR #1364, beneath Amalgam PR #1278 at pinned parent `86264b41a08d49f558418c0fba367f3a2636befa`. No native production file, accepted main, controller, Genome, protected source or owner runner was changed.

## Verified destructive repair seam

The exact original `yggdrasil/native_episode_experience.py` (Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`) has a local repair branch in `_learn_local` which, after three contradictory observations, **replaces** the learned counter pair. The previous counts, new counts and three contrary witness IDs are saved in the native `info()["repairs"]` receipt and deterministically rebuilt from the witness ledger during cold `restore()`.

An original deterministic, **source-free synthetic engineering fixture** establishes the precise effect: 48 public observations establish transition context-0/action-0 counts `[24,0]`, a Beta(1,1) transition probability of `1/26` (**3.846%**). Three successive contrary witnessed transitions make the **actual original native repair** replace the cell counts with `[0,3]`, probability `4/5` (**80%**). Eight additional old-pattern observations move the **live** cell to `[8,3]`, probability `4/13` (**30.769%**). Original old counts `[24,0]` and the immediate reset `[0,3]` remain independently readable from the original repair journal, including after a cold checkpoint restore and native consolidation.

The new `repair_versions.py` is a small **read-only, witness-keyed** adapter over that *existing* original repair record. It exposes `before`, `reset` and `live` exact rational cell probabilities for publicly witnessed **transition** cells only. It rejects missing or invalid repair witness IDs, bad target/action/slot/version, invalid count structure and evidence not matching actual ledger identity, chronology or cell/outcome. Terminal/reward variants are intentionally unsupported until independently qualified.

**Crucial distinction:** The caller supplies the last original repair witness ID. This proves **historical evidence readback**, not autonomous causal-regime identification or an actual old-task forecasting advantage. It would be oracle leakage to evaluate `before` predictions on a return stage as if Yggdrasil knew when to select them. No W16, history-loss routing, new bank, teacher model, replay controller or memory promotion was introduced. The historical counts were **already stored** in the native receipts.

## Reproduction and qualification

`tests/test_wscm_structural01.py`: **9/9 local tests PASS**, Linux CPython 3.13.5, 2.31s wall, 107,352 KiB max RSS with source-pinned original archived checkpoint. Tests cover destructive original native repair, exact before/reset/live probabilities, two cold restorations, consolidation, eight old-pattern return witnesses, no-read mutation, forged identifiers/targets, disabled repair and checking that the authentic archived model produces **zero** repairs (no fabricated historical memories).

Reproduce on the pinned parent/checkpoint with:

```sh
WSCM_ARCHIVED_JOINT_PATH=/path/to/amalgam-joint-state.json \
  python -B -m unittest discover -s tests -p test_wscm_structural01.py -v
```

The native source module was loaded **byte-for-byte**, but helper modules `native_context_basis` and `PublicCausalCells` came from the existing limited **source-equivalent testing shims**, not the complete original dependency tree. Without `WSCM_ARCHIVED_JOINT_PATH`, the authentic archival checkpoint test **SKIPS** and must be reported as unverified, not PASS. Original archived Amalgam joint SHA256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`, containing 1,025 witnesses and **zero native repair receipts**. This source-free repair fixture is distinct from that old checkpoint.

**ENGINEERING:** original episode repair and archival readback PASS (focused), mandatory complete exact-SHA Linux/Windows regression **UNVERIFIED**. **SCIENTIFIC:** old function value can be recalled by explicit witness key, but measured live adaptation, automatic cold old-regime revival, unfamiliar transfer and superiority to fully fitted equal-information controls remain **UNVERIFIED**. **DEPLOYMENT:** unverified; draft/unmerged, no native production changes.

**Next qualified mechanism:** a bounded **non-destructive, versioned native transition write** with a source-observable, non-oracular retrieval method; then new frozen A→B→A trials with matched trained controls and source-authorized cold retention. The earlier W16/epoch-selector line remains stopped. Full regression and owner acceptance must occur before any native integration or deployment.
