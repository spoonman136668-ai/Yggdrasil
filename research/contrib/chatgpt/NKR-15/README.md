# NKR-15 — Separate what is learned from what remains unknown

## The actual gap this corrects

NKR-14 [draft PR #1151](https://github.com/spoonman136668-ai/Yggdrasil/pull/1151) showed the exact NKR-13 model fails outside its prespecified conjunction family. The **original frozen NKR-14 result is preserved unchanged** at `8018fd4d08e155efccd7bc0524ca83aa9645b4e2`: 12 genuinely different Boolean action-effect families, **10/12 no qualified new candidate**, **2/12 misleading conjunction fits**; source-bound changed-world predictions **26/192 correct**, **6 confidently wrong**, **160 abstentions**. Independent unlimited truth-table version-space baseline found **256** valid functions per world after only eight paired action contexts and safely predicted **96/192 action-0 outcomes, zero wrong**, abstaining on 96 unseen action-1 effects. All prior knowledge remained **384/384**.

That experiment uncovered a **specific engineering loss**: the NKR-13 loader had verified the new action-independent baseline, but discarded it when *no new action-dependent operator* matched its grammar. There is no technical reason to discard both pieces of evidence together.

**This is an engineering repair for partial knowledge, not another claim of autonomous unlimited relation invention.**

## Frozen prereg and exact source

- **Prereg FIRST** `f15ea766c011d225eb4f0cd8e0642becb056b47f`, frozen before modifying the native module, tests or scientific results.
- Parent exact NKR-14 `8018fd4d08e155efccd7bc0524ca83aa9645b4e2`, tree `c5dd682344d7e7484bdafc8aeee317ec0af06e75`. Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged. No original historical 21.3M image download, official validation/test source, new paid API or native owner operations.
- The two already-frozen procedural worlds are reused as **engineering regression**, NOT independent scientific first-use: NKR-14's 12 out-of-family contexts and NKR-13's 12 conjunction contexts, original 16 public action outcomes/world and sealed cold labels. Separately run four existing single sensor-flip negative worlds.

## Smallest coherent behavioral patch

In `yggdrasil/native_operator_discovery.py` only:

1. After at least **two source-visible contradictions** with the old frozen mechanism, infer and validate the **action-0 parity baseline** from all eight observed action-0 consequences. If no positive-conjunction operator can fit the action-dependent effects, persist the supported baseline and an **empty operator candidate list** in a **new immutable, SHA-pinned checkpoint** instead of dropping all evidence. A single sensor-bit mismatch remains insufficient for a new model or persistent baseline.
2. Preserve existing **family-conditional** `predict(context,action)` for all old NKR-13 callers and original conjunction qualification. With an empty operator candidate list, it can predict identified action-0 baseline values, while action-1 returns `UNKNOWN_ABSTAIN`. No causal historical or YPC1 records are written.
3. Introduce explicit opt-in **`predict_unrestricted(context,action)`**. This mode assumes ONLY the verified four-bit **action-zero parity** family. It returns an action-0 baseline on an unseen context, returns an already **directly observed** outcome when one exists, and abstains from **unseen action-1 effects** regardless of any fitted conjunction. If source evidence did not qualify a changed-world checkpoint, it refuses to reuse the old mechanism's prediction as if it were a new observation. Predictions are classified as unverified, assumptions disclosed, `native_accepted=false`, `scientific_pass=false`.
4. `operator_supported` explicitly means the conjectured action-effect family has at least one supported candidate. The inherited `operator_discovered` flag still indicates that a research repair checkpoint was staged for compatibility; it must **not** be read as proof of a novel operator when `operator_supported=false`.

Source-checkpoint cold restore independently recomputes baseline, candidate set and canonical source hashes. A forged support mask, changed source byte, duplicate replay or attempted native acceptance is denied.

## Preset source-safe benchmarks (development only)

Re-run all **12 original NKR-14 unseen Boolean worlds**, no changes to their context splits, hidden operators, action budgets or labels. Preset outcomes are intentionally differentiated by their assumption set:

| Readout | Expected cold correct / 192 | Confident wrong |
|---|---:|---:|
| Frozen NKR-14 NKR-13 grammar prior (original SHA, NOT overwritten) | 26 | 6 |
| **New family-conditional mode**, now retaining baseline-only evidence | **98** | 6 |
| **New unrestricted-effect mode** (safe parity action-0 assumption) | **88** | **0** |
| Independent conservative 256-completion truth-table control | 96 | 0 |

Nine previously unsupported worlds should qualify **baseline-only** repair, two worlds retain existing fitted conjunction rules and one true changed world must refuse repair because its observations show **only one contradiction**, indistinguishable from a single bad sensor measurement. That conservative no-repair gate explains why the new safe readout scores **8 fewer** than the mathematical controller, which assumes source effects are noise-free.

On NKR-13's earlier conjunction worlds, the **legacy family-conditional** readout must remain exactly **129/192 correct, 0 wrong**. Four single-bit-noise cases must still trigger **zero** false persistent repairs. Original 384/384 prior outcomes retained in both experimental cohorts. Cold restore checks and no owner-state mutations are required.

**No scientific PASS is possible:** even the unrestricted readout still assumes a four-bit parity action-zero model; this is a bounded engineering mechanism, not a guarantee against novel action-independent functions, real sensor noise or adversarial inputs. The strong source-equivalent symbolic and exact conservative controls are not outperformed. Real independent action outcomes, genuinely unforeseen operator families and matched conventional trained baselines remain necessary.

## Engineering acceptance and deployment

Development on existing GitHub-hosted Ubuntu + Windows, then generated-only G29 atlas and mandatory **full original root regression** with inherited NKR-05 tests on both OS at **the same exact candidate SHA/tree**. Do not rerun/rebuild/download the 21.3M historical image—no relevant interface change requires it. Preserve all NKR-14 original negative evidence separately from the new descendant.

This source is an **isolated draft**. No accepted main merge, original Yggdrasil native owner execution, scheduled tasks, paid models, new control loops, persistent knowledge image install or production/cognitive promotion. Owner-controlled activation is still a separate acceptance/authority gate.

**Plain-English outcome sought:** keep what was actually learned even when the system cannot explain the rest, and say *unknown* instead of issuing an unsupported new causal prediction.
