# ARCHIVE-COLD-COMPONENT-09 — retained old-world hypothesis reactivation on original CKAD22 checkpoints

**2026-11-20. Original historical CKAD22 already-consumed synthetic TRAIN+held. No original-world first use, new source episode, model inference/training, controller, acceptance or deployment.** Sole canonical Yggdrasil learner integration remains PR #1278. This contributor finding remains on draft PR #1326.

## Immutable inputs and freeze

- Frozen *before reading numerical posterior weights*: https://github.com/spoonman136668-ai/Yggdrasil/pull/1326#issuecomment-7038812542
- Original Linux run https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44266448951 artifact #14410228167, ZIP SHA256 `90362c075154ab936fc2e0a82716fbe5bd875585cd89aeed0b08b32831560fc4`.
- Original Windows same-run artifact #14411380648, ZIP SHA256 `e4fea224001f0b850a10cd1954e85262a41364b0f09734caf07175c9e3caa6f7`; Windows holds original scores and model-state receipts but not a second copy of the native checkpoint.
- Both original result stable semantics SHA256 `4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2`, and **all 12/12 per-seed/per-session native context state receipts are identical between Linux and Windows**.
- Source commit `e9aa921c57dca836c06c7125e52229cce728620a`, frozen CKAD22 prereg Git blob `b241189c50d259d38b631ade6bb7f3a534f76b76`; source-law fixture `CKAD-20/synthetic_world.py` Git blob `160001d60f2ce2ca7ca3e9ab5d14261ba9ce42a8`; unchanged native episode source Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`.
- Exact original worlds: session0 `terminal_switch/regime0`, session1 `invariant/regime1`, session2 **same complete terminal_switch/regime0** world returns, session3 `invariant/regime0` (different old reward law). Each session acquired 32 already-consumed public episode witnesses and scored 96 held source episodes. No new prospective test was run.

## What original saved native state actually demonstrates

The checkpoint is one native cumulative learner with an append-only 448-event ledger. We extracted the **historically learned 32-witness model from original first-world session0** at exact event range `[320,352)`. Its canonical event SHA-256 is present unchanged in session1, session2 and session3 source_ranges for **all 3 seeds × 3 later endpoints = 9/9**; each digest matches the final original native ledger's exact `[320,352)` event bytes. The original episode source stores frozen 32-witness context submodels and reweights them with new public action-consequence likelihoods; the source family/regime labels are only evaluator metadata.

| Source seed | Same original old-model weight after B session1 | Same model weight after A return session2 | Weight after different C session3 | Rank on return |
|---|---:|---:|---:|---:|
| 101 | 4.1105461283e-13 | **0.3036269447 (30.36%)** | 0.000020052724 | 3/13 |
| 202 | 9.4010732742e-20 | **0.9777063449 (97.77%)** | 0.000329176941 | 1/13 |
| 303 | 1.3256852074e-6 | **0.9906025728 (99.06%)** | 5.1776523044e-7 | 1/13 |

All exact original posterior weights use rational numerator/denominator pairs, sum to 1 at each endpoint, and refer to the same old block via exact source-range SHA. Session boundaries change model count and priors (12→13→14 candidates here), so this is **not** a controlled same-time gain from merely comparing raw weights. In session1 the old model was retained but assigned low weight as evidence favored B; during return session2 the preserved old model regained substantial weight after 32 actual original public consequence observations. This is posterior **reactivation, not erasure**. Its weight falls again after different world C, so this is adaptive context selection rather than permanent uniform preference.

## Original old-world witness support, not a full model prediction

For the 32 original old-world `[320,352)` training events in each seed, independent Laplace Beta(1,1) counts of public `P(s2=1 | s1,x1)` have the old transition action direction in **6/6 seed×public-s1 contrasts**, with both actions represented in every stratum. Exact observed counts (successes/total):

| Seed | s1=0,x1=0 | s1=0,x1=1 | s1=1,x1=0 | s1=1,x1=1 |
|---|---:|---:|---:|---:|
| 101 | 4/8 | 6/6 | 3/11 | 5/7 |
| 202 | 2/7 | 8/8 | 0/3 | 11/14 |
| 303 | 0/2 | 13/16 | 3/11 | 3/3 |

These are **original witnessed training events**, not actual native forecast outputs; small cells (including n=2 or3) limit confidence. The original source law supplies the expected action direction. No hidden source variables or per-witness IDs are published.

## Strong-control and cold-readout limitations

- **Actual original CKAD22 held reward comparison remains negative:** on returning complete old world session2, native 246/288, strongest eligible Beta/retrieval-only 257/288. Native versus independently computed exact-mixture control ties on all four recorded metrics across 12/12 seed/session records. Those original scored held cohorts were already consumed. See https://github.com/spoonman136668-ai/Yggdrasil/pull/1326#issuecomment-7038401793.
- **Zero-probe old-world competence remains unverified:** this audit reads stored **post-32-probe** posterior weights; it never asks the native learner for an old-law prediction before return-source evidence. Each original archival ZIP includes final full checkpoint per seed plus intermediate **state receipts and hashes**, not a separately stored full pre-return native checkpoint. Do not infer zero-probe competence, causal superiority, novel unknown-law discovery, independent retention advantage or whole-process efficiency.
- Source-specific zero-probe unannounced-world identification also has an information limit: https://github.com/spoonman136668-ai/Yggdrasil/pull/1326#issuecomment-7038651710. A cue-conditioned cold old-law readout and source-blind online recognition are different target questions.

## Auditable read-only computation

1. Verify ZIP SHA256 and exact member set: campaign-result.json plus seed-101/202/303-expanded-native.json. For each seed verify member bytes against `final_checkpoint_sha256`; extract nested `experience_ascii -> episodes`, length 448 and `context_start=416`.
2. Canonically encode events `[320:352]` as sorted-key compact ASCII JSON and SHA-256 it. In campaign-result.json for each seed, each session j=1,2,3, find one `source_ranges` entry with start320/stop352, assert exact hash match, read `weights[entry_index]` as `fractions.Fraction(numerator,denominator)`, confirm weights sum to 1 and report rank among candidate weights. Expected context starts 352,384,416.
3. Count original events at indices320–351 by `views[0][0]` and `x1`, with `s2` as binary outcome. Report 4-stratum successes/totals and separate Beta-1 sign; no model forward pass or source-world construction.
4. Compare Linux versus Windows `sessions[j].states.novel_active.experience.context` EXACTLY for all 3 seeds×4 sessions and semantic result stable SHA.

Sanitized deterministic result SHA256 `c2c47479558011f64573e492d5ff5d8e5cc3668e36466635b9f016a5475753e1` (canonical compact ASCII JSON). Local source-only validator SHA256 `7e74093198b24b8145fd7eeb5573801bcbe2b6e7de6c5b9fb2f4e73a0bc8c424`, 12 local focused/negative-control tests SHA256 `2c43943d5d6eaf5950f4e06be0d8d4ddb4fda41ff0fe994147b5b5d654426c6a`, **12/12 PASS locally**. These scripts/result JSON are **not committed**; the receipt plus exact original ZIP/source identifiers and above steps permit an independent auditor to implement verification. GitHub full native/regression CI was not run for this analysis.

**Decision: `RETAINED_A_COMPONENT_CUSTODY_PASS` (9/9 exact block identities), `WITNESSED_OLD_ACTION_DIRECTION` (6/6), original model reactivation POST-PROBE observed across all three seeds, `ZERO_PROBE_COLD_NATIVE_RECALL_UNVERIFIED`, `SCIENTIFIC_GAIN_UNVERIFIED`, `DEPLOYMENT_NONE`.** This is stronger evidence of preservation than just checking count/IDs, but it is conventional Bayesian context selection, **not** demonstrated novel intelligence. Existing failed Gate25 and G29 receipts untouched; original source first use still denied under issue #426.