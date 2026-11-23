# WSCM-VERSIONED-02 — bounded copy-on-write transition versions

**Disposition: ENGINEERING focused PASS; SCIENTIFIC gain UNVERIFIED.** Additive research-only component under [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) and existing [WSCM PR #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364). No accepted `main`, production native code, Genome, controller, .ice or protected source mutation.

## What changed

`versioned_transition.py` wraps the original immutable `NativeEpisodeExperience.observe()` and constructs a bounded, **copy-on-write** historical transition-function version from each original **source-witnessed** local repair. The previous value is frozen as a distinct immutable public-context/action pair and is addressable only by the real third repair witness ID. The original native live cell **still overwrites its active counts**: this prototype safeguards a *sidecar historical readout*, not the production native write mechanism.

The sidecar:
- Observes only true original native repair journals/ledger events; rejects contradictory witness IDs, mismatched public contexts/actions/transition outcomes, chronology, count bounds, forged receipts and unpinned historical addresses
- Fails closed rather than discarding history when the 16-version sidecar budget is exceeded; never invents historical versions if original repair receipts are absent
- Exposes existing original **live full-conditioning forecast** unchanged when no historical version ID is explicitly supplied; old-version retrieval requires a valid witness ID, **not** an oracle regime label or automatic router
- Produces two independent deterministic checkpoint objects: the original native checkpoint and a small canonical version manifest pinned to its SHA-256
- Rebuilds/compares every version against the **actual cold restored native repair journal**, refusing forged counts, altered native source or noncanonical manifest bytes
- Preserves original native idempotence, consolidation and checkpoint replay without an additional scheduler, agent, or control plane

## Source-pinned focused fixture

The original native episode module (`yggdrasil/native_episode_experience.py`, parent blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`) admitted **48** public synthetic engineering witnesses, then **3** contrary transition witnesses and **8** old-pattern return witnesses. This reuses the previously investigated structural repair shape; it is not a new or independent scientific cohort.

| Public transition cell | Failure : success counts | Exact transition P(s2=1) |
| --- | ---: | ---: |
| Frozen old version, before repair | 24 : 0 | 1/26 = 0.038462 |
| Original live immediately after repair | 0 : 3 | 4/5 = 0.800000 |
| Original live after 8 old-pattern outcomes | 8 : 3 | 4/13 = 0.307692 |

The old `1/26` historical readout survives both further native training and cold restoration, while the original native live cell changes normally. The sidecar manifest uses **544 bytes** alongside a **5,534-byte** original native checkpoint after this 59-event synthetic fixture. Old history was *already present* in original native repair receipts; this adapter adds a checked typed version store and deterministic cross-checkpoint read path, **not novel memory content**.

Original archived Amalgam Actions artifact `14492525071`, `amalgam-joint-state.json` SHA-256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8` contains **1,025 witnesses with zero native repairs**; its version store correctly stays empty. This authentic artifact has **not** been treated as new scientific source first-use.

## Qualification

- Source code `versioned_transition.py`, standalone tests `tests/test_wscm_versioned02.py`, machine summary `result-summary.json`
- **14/14** new focused Python 3.13/Linux tests PASS on exact original native episode code with previously declared source-equivalent helper shims; including honest archived fixture read, tampered manifest/native checkpoint rejection, witness/action mismatch, original native unchanged, idempotence, cold identity, consolidation, return-event readback
- **31/31** local focused regression tests PASS across the existing WSCM-COLD-READ-01 (8), WSCM-STRUCTURAL-01 (9), and WSCM-VERSIONED-02 (14) fixtures; no skips with the archived fixture explicitly present
- Complete original `native_context_basis.py` and `public_causal_cells.py` modules were **not** loaded; existing source-equivalent helper shims remain a qualification limitation. No full exact-candidate Linux+Windows regression or CI run, independent held-out trial, original-world action, GPU training, memory/transfer gain, merge or owner acceptance occurred
- No adaptive selection is implemented, no privileged old-regime knowledge is passed to the native learner, no proposed improvement over strongest trained conventional controls is claimed

### Reproduction

With the pinned parent code and its authentic archived checkpoint available, and the research directory on the same checkout:

```sh
WSCM_ARCHIVED_JOINT_PATH=/path/to/amalgam-joint-state.json \
  python -B -m unittest discover -s tests -p test_wscm_versioned02.py -v
```

The `WSCM_ARCHIVED_JOINT_PATH` case is **SKIP**, not PASS, when the original archive is missing.

## Next decision

The essential separate capability is **non-oracular readout selection**. For a law change in which current public context/action is observationally identical across regimes, an immediate switch to the old branch without new informative evidence would be an oracle. Do **not** turn this source-accessible version into another rolling-loss W16 selector, which previously failed on new development seeds. The next candidate requires a pre-frozen, independently qualified observable discriminator (or explicit abstention/diagnostic action), matched fully fitted Bayesian baselines, cold A→B→A retention, unfamiliar transfer and charged cost. Production native integration needs separate full regression and owner authority.

**ENGINEERING: focused PASS / full regression UNVERIFIED. SCIENTIFIC: no new gain verified. DEPLOYMENT: UNVERIFIED.**
