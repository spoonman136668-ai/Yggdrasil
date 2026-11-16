# FKP18-CB2 — Multiple causal bindings, selective contradiction repair, and cold retention

**Disposition: ENGINEERING CAPABILITY PASS (local only); STRONG CONTROL TIE; SCIENTIFIC_PASS=FALSE; native/accepted deployment NONE.**

This experiment follows the single-relation CB1 proof, not a retuning of [FKP-17 PR #1109](https://github.com/spoonman136668-ai/Yggdrasil/pull/1109). The separately qualified [FKP-18 temporal-trace draft PR #1114](https://github.com/spoonman136668-ai/Yggdrasil/pull/1114) already proves sparse conditional forks and ordered public-event storage on both operating systems. CB2 instead tests **genuine earned delayed action credit across four interleaved relationships, selective revision of one relationship, and preservation of the other three**. This branch has no native, source-owner, controller, runner, scheduled-task or accepted-main write.

## Provenance and frozen decision

- Original accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` remains unchanged.
- Based on isolated CB1 branch `84503c0b7a1e005bc05770d22a831772adce62fd`; it **reuses** byte-exact existing `binding.py` (Git blob `a2c2c64ada23d78ca1872725c31798a57b4f634a`) and separately coded conventional `strong_control.py` (blob `f9feb0491b0d9a67a3daf884ae347d57f222aa41`).
- Preregistration committed **first**: `196bab5c23183f911503037fe35779f222d9af37`. Frozen 4 modes, 8-mismatch trigger, 128-credit shadow, seeds `82210/82211/82220/82221`, actual observed source-only reward semantics and thresholds.
- Exact candidate code blob `91ed49d9d05979941d4619cfa9636782c85eaf1e`, source/harness blob `83f35a384b2a2945f58f2dbbeabeadf8c2fc0e25`, focused tests blob `5911a38f13b432f831a65b8c5ee14d70c092f1ab`; all **byte-for-byte equal** to the tested Python 3.13.5 Linux source. See `provenance.json`.
- The first public local diagnostic occurred after the preregistration and local code implementation; the committed harness subsequently added only the already-preregistered wrong-current-mode negative and a timing-independent digest. Candidate/strong-control source, underlying public laws, action tape, budgets and thresholds were not retuned. This is exploratory **public development**, not a source-owner-blind confirmatory test.

## Real observed delayed-credit stream (synthetic)

Public records expose eight uint4 registers, legal binary source actions 0 or 1 (a **subset** of the eight FKP-17 actions), public history up to sixteen steps, and a deterministic earned +1/−1 reward at step `t` for an action taken at `t−2`. The public state register `R7` low two bits visibly selects one of four contexts. This **gate is provided to the algorithm**: CB2 does not learn an unprovided task taxonomy. The four distinct feature-pair laws reside only in the source-owner `study.py`, not in candidate `context_bank.py`.

One continuous 515-step interleaved training sequence produces exactly **128 correctly credited public observations for each of four contexts** (512 total, after three warmup events). The gate at the actual reward time is **always different** from the gate on the credited action: a model that mistakenly uses the current state instead of the public state at `t−2` misroutes every training reward. No private source law ID, future outcome or counterfactual label is passed into the learner.

The candidate reuses four existing 75-byte CB1 learned relation snapshots, one per public context. It monitors post-fit rewarded action evidence, and after **eight consecutive contradictions for one context** begins a separate 128-credit shadow refit. Until that finishes, the original relation is unchanged; when fitting succeeds, **only that one context's checkpoint is replaced**. A separately implemented conventional exhaustive 703-feature-pair learner receives the exact same observations, routing key, contradiction trigger and repair budget.

## Original local results — new public contexts, 128 per mode per phase

| Evaluation | Direct CB2 | Equally informed conventional | Negative control |
| --- | ---: | ---: | --- |
| Before law change (4 × 128 unseen public queries) | **512/512** | **512/512** | Ignore context: **310/512** |
| After reversing mode-1 law (4 × 128 new public queries) | **512/512** | **512/512** | Ignore context: **339/512** |
| Changed law in mode 1 only | **128/128** | **128/128** | Frozen no-revision: **0/128** |
| Old laws in modes 0, 2 and 3 after revision | **384/384** | **384/384** | Old CB1 sealed source stays **384/384** |
| Misroute the delayed source label under current state | — | — | **236/512** initial-context predictions |

Exactly **1,115 public training actions** were executed (515 initial + 600 post-change), yielding **1,109 genuinely credited delayed consequences**. Each source law remains unchanged except mode1. Candidate and independent symbolic control predict **identically on all 1,024 new-context queries**, i.e. an exact **zero** gain over the strongest matched control. The result demonstrates robust scope-local retention and updating, **not unique intelligence, out-of-grammar discovery, autonomous recognition of the right gate, or superior causal reasoning**.

## Cold, budget, security and qualification

- Four CB1 snapshots contain **300 logical serialized learned bytes** (4×75); the canonical SHA-256-protected bank envelope is **774 bytes**. Bytes are not measured Python total RAM or whole-process model cost.
- Mode versions after repair: `[1,2,1,1]`. Exactly **one** source-earned repair fires. Modes 0/2/3 retain **byte-identical serialized original checkpoint receipts**; restored post-repair cold snapshot is byte-exact and predicts identically.
- Corrupted, noncanonical or extra-private-field records are rejected; initial source history continuity and delayed-credit attribution are tested; no snapshot is permitted during an unfinished shadow repair. **In-flight cold resumption is not proven**.
- **8/8 focused local tests PASS**, `compileall` PASS, two independent runs have identical non-timing result digest `f4290f7b4ba35b66e01fe06bfd4095d88225e27bc5b47f123cbab6d88b6d5f47`. See `result.json` and `provenance.json` for exact receipts and timings.
- The new branch has **not** received an exact-source full final Windows+Linux root regression or G29 generated-atlas qualification. Do not inherit CI PASS from FKP-18 PR #1114 or FKP-17 PR #1109 and do not merge or promote this branch without independently qualified science.

```sh
# Within a complete checkout of research/fkp18-cb2-interference-repair-20261115:
cd research/contrib/chatgpt/FKP18-CB1
PYTHONPATH=.:../FKP18-CB2 python ../FKP18-CB2/test_cb2.py
PYTHONPATH=.:../FKP18-CB2 python ../FKP18-CB2/study.py
```

The above Python module paths are research-only. No original FKP-17 protected DEV `978500..978531`, TRANSFER `978600..978663` or independent source-owner first-use was opened. No scheduled task, paid API, native-source edit, PR duplication or accepted ref change.

**Follow-on scientific question:** can the model autonomously *discover* which public context features to bind, learn several interacting relationships without preassigned 4-way slots or a prewritten 38-feature truth-table grammar, survive unseen operator families, and outperform an equally informed conventional learner on real consequential decisions with retained cognition? CB2 does **not** establish those claims.
