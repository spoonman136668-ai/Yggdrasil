# NCI-SOURCE-07 — Real archived Amalgam ledger, public-input guard, and original-row provenance

**2026-11-19 — Independent Yggdrasil research contributor.** The sole integration coordinator is **Unified Causal Intelligence Amalgam Work**. This is a read-only audit of the **historical research** checkpoint. It is not the owner-controlled canonical learner, a checkpoint restoration by native Python, an accepted source, a trained-model change, or a scientific intervention.

## Pinned material

- Repository: `spoonman136668-ai/Yggdrasil`; historical Amalgam research PR #1278 HEAD `86264b41a08d49f558418c0fba367f3a2636befa`.
- Original [Actions run 44499793023](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44499793023), exact archived ZIP artifacts: Linux `14517860401`, Windows `14516669671`. The manifest pins both **outer ZIP SHA-256 hashes**, both **joint JSON SHA-256 hashes**, embedded native state SHA, embedded native-episode checkpoint SHA, source schemas and one original packet SHA. ZIPs are downloaded **read-only** using the existing GitHub connection. The ZIP bytes are **not duplicated into the source repository**.
- Source: `yggdrasil/native_causal_amalgam.py` Git blob `287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952`; `yggdrasil/native_episode_experience.py` Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`.
- Independent prior source receipt: `research/contrib/chatgpt/CAUSAL-AMALGAM/growth-result.json`, Git blob `298e769cea61e76c909f8dd1fdc2e1311cd90747`, **original public input packet SHA-256** `a45e297322b3040f9d89a1f2e79b0c1e24476f14f7d9e57f3847c4ebef9cba6a`.

## Observed result

- **Linux/Windows archived joint envelopes:** differ by trained specialist-head values; full joint SHA-256 Linux `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`, Windows `65b22e284b94fe022fb6345757e364e1a44f8156edf7f081e1b7420e5561f454` — *not byte-identical*. This is already known from earlier lineage archival work, preserved here for custody.
- **Native checkpoint:** byte-identical across platforms, SHA-256 `5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d`; exact embedded native episode checkpoint SHA-256 `9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4`.
- **Real retained research witness ledger:** **1,025/1,025** valid distinct 64-hex witness IDs, binary two-by-two views, and binary actions/consequences. All **1,025/1,025** have matching **first** coordinate across both views. **497/1,025** have *different second-coordinate view values*: the agreement is projection-specific, not a universal view-equality rule. The original checkpoint has growth limit **1,152** and hence **127** remaining unique witness slots on *this historical research checkpoint only*. This capacity fact was already recognized by the central coordination work; no new owner capacity is claimed.
- **Last added witness (index 1,024):** reconstructing its public row with `s1 = views[0][0]` and hashing the original canonical `[id, views, row]` exactly matches the independently archived original public packet SHA-256. Flipping `row['s1']` leaves the historical stored event projection unchanged (because the stored event omits `s1`) but changes the public packet SHA-256. This supports the proposed *Amalgam-only* source-bound input guard for the **specific final research witness** and demonstrates the need to pin the full inbound packet to verify provenance.
- **Critical limit:** For the pre-existing **1,024 parent witnesses**, the archived native ledger **does not persist the original raw inbound `row['s1']` or its original per-row packet SHA**. Their *reconstructed* `s1` values agree with the views by definition, but this **cannot independently prove** the originally submitted `s1` was correct. Historical 2,456 mixed source traces in NCI-SOURCE-05 are a different evidence set and cannot be silently treated as authentic parent-episode receipts.

## Reproduction

Use `audit_archived_joint.py` plus `manifest.json` on the two original named ZIPs:

```sh
python -B audit_archived_joint.py \
  --linux /path/to/Amalgam-shared-consequence-ubuntu-latest.zip \
  --windows /path/to/Amalgam-shared-consequence-windows-2022.zip
```

The standard-library verifier rejects wrong outer ZIP SHA, wrong joint/native/episode SHA, unexpected member paths, malformed input shape, reused IDs, divergent OS native witness records, wrong schema or an unmatchable last public packet. It does **not import Yggdrasil code, invoke native model restore, execute source actions, mutate weights or touch the owner**.

## Next exact native interface / scientific use

The narrow pre-admission initial-state consistency guard belongs only in **`NativeCausalAmalgam.observe_experience`**, before `NativeCumulativeLearner.observe_experience` and before the duplicate early return; it must **not** be globally inserted in `NativeEpisodeExperience.observe`, which permits alternative learned projections. Any future **durable audit of raw submitted `s1`** would need source-owner-authenticated packet-level custody for NEW events, rather than rewriting the old checkpoint or pretending a reconstructed row proves the historical input. The central coordinator owns any qualification/installation. Preserve all old research negatives and frozen first-use cohorts.

**ENGINEERING:** archived source-byte custody and reconstructed projection-0 ledger compatibility **PASS**, original final-source packet digest **PASS**; original source full native `restore` inside this gate **NOT EXECUTED**, historical 1,024 original inbound-row consistency **UNVERIFIABLE FROM THIS CHECKPOINT**, full final dual-platform CI **UNVERIFIED**. **SCIENTIFIC:** no improvement in causal learning/retention/transfer measured; `scientific_pass=false`. **DEPLOYMENT:** none, no training, no actor, no restart, no merge, no owner policy or accepted main changes. Source-owner issue #426 still denies new protected original-world first use.
