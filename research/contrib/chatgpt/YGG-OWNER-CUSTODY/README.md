# Yggdrasil — accepted-owner native checkpoint custody, 2026-11-19

**Read-only owner/source verification. This is a checkpoint-custody gate, not another experimental learner or training dispatch.** No main change, owner process, self-hosted runner invocation, existing schedule change, new controller, accepted model read/write, paid inference, first-use or deployment is authorized.

The full machine-readable provenance, immutable Git tree/blob refs, negative evidence and **null for every missing owner-checkpoint proof** are in [verified_baseline.json](verified_baseline.json). The offline/optional read-only GitHub metadata verifier is [verify_readonly.py](verify_readonly.py); [test_verify_readonly.py](test_verify_readonly.py) ensures green CI cannot silently convert missing owner state to learned-model or science success.

## Verified authorities and state

| Item | Exact evidence | Meaning |
|---|---|---|
| Accepted repo main | `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; tree `180008502f6bdfe5a06c3d0d6f47f941dd01f20b` | The accepted main source is unchanged. `yggdrasil/public_causal_cells.py` is a bounded explicit causal-counting control (16 cells, 164-byte checkpoint), **not a native GI model**. `src/yggdrasil/training.py` exists on the protected *research* branch, not in accepted main. |
| Protected research owner ref | `research/autonomy-yggdrasil-active` at `92c421a5475a27015a390efb88c373eb5f15379d`, tree `e7a9cef8a7c31fd77f086915bab7c639411ac6cc` | The most recently checked protected owner research ref, last committed Oct. 16, is independent of CKAD and CAP sidecar branches. No takeover or source mutation. |
| Active owner status | `.research-autonomy/state.json` blob `27194d56d16fb318c5118fd2b1119695876256d6` on exact owner ref | Last recorded `preregistered-blocked`, experiment `EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-STAGE-STABILITY-ATTRIBUTION-096`, `last_completed_utc=2026-10-16T18:05:00.0902965Z`, `scientific_claim=false`. This records a blocked state **at that ref**, not proof that no other research occurred afterward on independent branches. |
| Existing research-only owner workflow | Main config blob `426f8b78ba5bb1cac1c6b1bff4f248da7778b62c`, `.github/workflows/research-auto-launch.yml` | Config says `research-only`; active branch above; (existing) scheduled wake is `50 * * * *`. We did not create or alter any scheduled task. |
| Last observed owner runner | [Actions #44522000519](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44522000519), Nov 19, exact `main` SHA; job `135552709494` on `YGG-A-LINKDEADKB` | Self-hosted Windows runner **executed and completed SUCCESS**, but actual log explicitly says `RESEARCH_AGENT_POLICY=GPT_CHAT_GITHUB_SOURCE_ONLY_NO_CODEX_NO_EXTERNAL_APIS` and `RESEARCH_EXECUTOR_UNATTENDED=NOT_CONFIGURED_NO_MODEL_INVOCATION`. **This particular scheduled run did not demonstrate native-model learning.** A green watchdog is NOT a training receipt. |
| Current owner-selected trained checkpoint | **MISSING EVIDENCE: UNVERIFIED** | No authorized model-owned checkpoint location, source/schema/parent SHA, cold readback, original source-ledger, old-capability baseline or owner acceptance receipt is established by the checked GitHub source. We cannot infer or manufacture an owner's private workstation path or authorization. |

## Positive independent cumulative research evidence — not the accepted owner

The parallel **CAP02 → CAP03** research branch has genuine **cumulative source-trained checkpoints** from existing source episodes, not a blank toy reset. [CAP03 original result](../YGG-CAP03/result.json) at candidate `78f9696794a9145a0de607dd870244ee49cd9fee` and tree `17e34cb9eed0721082f87f7be6ab734efe14a36d` cold-restore 1,086 and 1,061 prior synthetic episodes and append 32 new intervention episodes per seed (to 1,118 and 1,093). They preserve the original native source archive and readouts exactly.

The candidate **scientific DEV decision is NO-GO**: the contrast readout loses to the best fully source-trained controls. Its original Linux/Windows source-level checkpoint SHA and continued native checkpoint SHA differ between OS, despite matching aggregate predictions within numerical tolerance. The **[sealed CAP03 full final regression #44520940169](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44520940169)** passed on Ubuntu and Windows, but **regression PASS does not erase a negative science qualification or establish byte-identical learned weights**. CAP03 original result `c48a6928e8454e7f137518a70e6fb94b0a8b6859`, provenance `1e2b96079861ba7edff2b534880f5711332e0f70` and parity `4ee63c94cb6d4070b32d434e4a091c4001618169`.

The [CKAD41–49 audit PR #1320](https://github.com/spoonman136668-ai/Yggdrasil/pull/1320) separately establishes **nine scientific DEV NO-GOs** and no common accepted trained-state continuation across those isolated CKAD experiments. **That finding must not be generalized to deny the independent CAP02→03 cumulative research lineage.**

## Knowledge image is source-trained research data, but permanent owner installation is unknown

The [NKR07 source-safe installer candidate](https://github.com/spoonman136668-ai/Yggdrasil/tree/research/nkr07-owner-persistent-knowledge-install-20261116/research/contrib/chatgpt/NKR-07) at `efd0059f93b30072757c796eb905ec4d6e7609b3` documents a real prior historical knowledge artifact:

- **21,343,681 historical records, 828 predicates**, 256,124,172 bytes, qualified original [NKR05 source run #43856374741](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43856374741), artifact ID `14220169461`.
- Pinned image SHA256 `6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1`, archive SHA256 `c7265cabac91b8762fb5d65209eef44fa79a8fbf3d9a6f61300ef60ded0a5275`; documented artifact expiry **Dec 16, 2026, 11:20:20 UTC**.
- NKR07 installation flow **requires a genuine owner-selected existing persistent destination, original source/expiry checks and separate owner-execution custody**. The NKR07 prereg `research/contrib/chatgpt/NKR-07/prereg.json`, blob `e7510d7ccb3593c4205ab4a8eb98ddb6d6c65287`, expressly states `owner_persistent_installed=UNVERIFIED`. We did **not** download the large artifact, guess an owner path, launch an installer or integrate the image into accepted native Yggdrasil.
- A factual historical image is not automatically genuine native causal understanding. Native relation learning, retention and unfamiliar-world transfer still require separate science controls.

## Current qualification and missing owner receipt

**ENGINEERING READ-ONLY CONTEXT: PASS** only when exact fetched metadata and offline/online verifier checks pass. **OWNER PERSISTENT CHECKPOINT CUSTODY: UNVERIFIED. SCIENTIFIC ACCEPTANCE: UNVERIFIED / NOT PROMOTED. DEPLOYMENT: NONE.**

The null acceptance fields in `verified_baseline.json` must remain null until an independently authorized owner presents a **read-only** receipt covering actual original checkpoint SHA256 and bytes/schema, corresponding source/tree SHA, authorized runner/process identity, source ledger digest, old relationship baseline, unchanged original learned parameters after controlled cold restoration, access/resource envelope, and first-use governance. GitHub repository access and general standing research authorization do not grant access to the private owner runtime or approve a model restart.

**Next executable work, without a new artificial gate:** With a verified owner-side read-only route, inspect the existing checkpoint and source receipts *only*, compare to an actual accepted baseline, and report any drift. Do not select a private path automatically, start an unattended model, consume protected source, replay training or change the controller. If the owner readback route is unavailable, report **UNVERIFIED** without substituting CAP03/NKR07 research artifacts as accepted training state. After custody is verified, a separately preregistered cumulative learning test must use the exact prior checkpoint and unrelated retained-capability probes with strong conventional/exact controls and measured whole-process costs. Full required-platform regression and separately authorized acceptance are still required for any promotable change.

## Reproducible read-only audit

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/YGG-OWNER-CUSTODY -p test_verify_readonly.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/YGG-OWNER-CUSTODY/verify_readonly.py
# Optional source-only metadata verification in the existing GitHub Actions workflow:
# GITHUB_TOKEN supplied only by repository CI, existing read permissions; no model/owner filesystem:
python -B research/contrib/chatgpt/YGG-OWNER-CUSTODY/verify_readonly.py --online
```

The `--online` mode requests only exact pinned GitHub branch, commit/tree, source blob and run metadata, never any private model/checkpoint bytes or external provider credentials. Nothing executes on the owner's self-hosted runner in this audit. Source and failure evidence stays on GitHub, not the ChatGPT File Library.
