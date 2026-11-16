# NKR-12 — Native cumulative intervention memory bank

**Status: `ENGINEERING_DEV_PASS_SCIENCE_UNVERIFIED`.** Opt-in Yggdrasil source code and bounded custody only; **not activated in the accepted native model**, autonomous research loop, other architectures, or any production environment.

## What is new, and what is NOT

Existing NKR-11 [PR #1145](https://github.com/spoonman136668-ai/Yggdrasil/pull/1145) already learns each source-pinned intervention relationship, detects a public contradiction, fits a bounded 10-feature GF(2) causal signature, and cold-restores it. Its 12-world engineering result reached **192/192** held predictions and retained **384/384** prior consequences, but a fully fitted 1,024-signature symbolic conventional control **tied**. NKR-11 is *not* a new unrestricted causal-grammar invention.

NKR-12 **does not rewrite or retrain that solver**. It adds `yggdrasil/native_cumulative_action_bank.py`: a persistent, opt-in container with the existing **seven active and nine retained Yggdrasil native addresses**. It stores 16 immutable existing `NativeInterventionRepair` checkpoints and supports public-source-pinned warm installation, at most one contradiction-triggered immutable repair per slot, old versus repaired forecasts, integrity-checked process-cold restore, global source identity/ref non-rebinding, explicit absence/underidentification abstention and bounded checkpoint size.

The caller **supplies the exact native slot**, which is *not learned task identity*. This test does **not** prove automatic memory routing, cross-family zero-shot transfer, new mathematical relation operators, low-compute advantage versus symbolic knowledge stores, or model deployment. The original YPC1 164-byte `PublicCausalCells` checkpoint remains unchanged.

## Frozen protocol and scope

Preregistration was committed **first** at `6f9ac6a40cb0ee50e5b45433d9c4c9fe8416418d`, based on independently checked NKR-11 SHA `e67a24af2cff1d9b4599c5bb7681813e6740aa05`. The original implementation and 18 focused tests existed at `b4c1e7ef3cbd93c78c6772e80ea922b4876e596f` before any development tests.

This is an **engineering test on the already-exposed NKR-11 synthetic fixtures**, not a new protected science cohort or a re-run of NKR-11 original first use. For 12 sequential fixture worlds, each with one separate native slot (the first seven active and five retained), reveal the same 32 earlier public action outcomes and 16 post-change actual public action observations as NKR-11. Install and repair in the SAME bank, freeze/cold restore the bank after all twelve, and return to all earlier and later rules without fresh training. Compare to unchanged per-world native reference objects and the existing independently implemented, fully fitted exhaustive 1,024-signature conventional symbolic model on the same public observations. Deny cross-slot source/ref identity replay, fabricated acceptance flags, corrupted SHA, invalid addresses and excess capacity.

Frozen required checks: **384/384** old correct, **192/192** repaired unseen-context correct, **192/192** exact reference agreement, identical conventional symbolic results, 12-member cold restore, untouched YPC1 checkpoint, global nonrebind, no forged acceptance, at least 12 negative/focused tests, **zero** protected first-use uses.

## Measured result

[One-shot exact-source qualification, run #43899226285](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43899226285) completed **SUCCESS** on GitHub-hosted Ubuntu 24.04 and Windows 2022:

| Check | Ubuntu | Windows |
|---|---|---|
| Focused tests, including denial/negative controls | 18/18 PASS | 18/18 PASS |
| Old consequence return after interference | 384/384 PASS | 384/384 PASS |
| Repaired-consequence cold return | 192/192 PASS | 192/192 PASS |
| Strong 1,024-signature symbolic comparator | 192/192 TIE | 192/192 TIE |
| Identical source digest, full prediction trace | PASS | PASS |
| Original native causal 164-byte state unchanged | PASS | PASS |
| First-use denial and source worktree clean | PASS | PASS |

Single bank checkpoint for 12 stored warm+repaired models: **24,773 bytes**, bounded at 262,144 bytes. Public source SHA256 `caf7ae6b1b3af283ca9af2a1d852f95d25cdd8638281fb37b77d6b72b7990acc`; prediction trace SHA256 `67d985ab77a562221b52cd015f48cfe09f1350ee9006f151b6f1e7da16e7e427`. The same digests match Windows and Linux. These are source-only debug/reuse fixtures; the digest certifies bytes, **not** authenticity.

**An initial preflight [run #43898910264](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43898910264) failed an entry-point packaging assertion:** 17/18 tests passed on each OS; directly executing the evaluator omitted the repository root on `sys.path`, so even its `--primary` denial command raised `ModuleNotFoundError` before argument parsing. This is **engineering infrastructure FAILURE**, not a cognitive or research failure. The only post-first-score correction, at `c610e31e9284dccdfd36be059af6552bbdc8dce6`, prepends the repository root to the **source-only evaluator's** module lookup. **The native learner, bank, frozen tests, source data, seeds, thresholds and acceptance logic were untouched.** Both OSes then passed the complete frozen source-only development screen.

## Reproduce, controls and qualification

From the repository root on a Python 3.12+ runtime using only standard-library dependencies:

```sh
python -B -m unittest discover -s tests -p test_native_cumulative_action_bank.py -v
python -B research/contrib/chatgpt/NKR-12/dev.py --source-dev
python -B research/contrib/chatgpt/NKR-12/dev.py --primary  # must refuse
```

See `prereg.json`, `result.json`, `provenance.json`, native implementation and 18 frozen tests for exact repeatability. Current code is on an **isolated draft research branch**, not accepted main. Full inherited Windows/Linux regression and authoritative G29 generated-code-atlas qualification are separate engineering gates; do not describe the focused tests alone as full final qualification.

**ENGINEERING:** Useful bounded, immutable multi-world retention interface on an existing non-token causal learner, without changing its semantics.

**SCIENTIFIC:** **UNVERIFIED.** The exact matched conventional symbolic control still ties; no independently new source, authentic causal environment, invented operator, learned task identification, autonomous novel-law transfer or statistically supported relative gain was tested. Original NKR-11 negatives remain intact.

**DEPLOYMENT:** **NONE.** No main commit, native accepted-state promotion, autonomous-loop integration, production memory, owner/runner/controller/scheduler action, or unrelated model change. Independently admitted scientific first-use and explicit owner-native acceptance are separate future steps.
