# FKP18-CB4 — Distinguish causal input from causal selector using paid mechanism interventions

**FINAL RESEARCH-ONLY DECISION: Interventional semantic-role identifiability PASS on this public synthetic source; algorithmic uniqueness NO-GO. SCIENTIFIC_PASS=FALSE. No native model promotion, acceptance, merge, workflow or deployment.**

## Why CB4 is different from CB3

CB3 identified the **correct unordered set of four relevant public features** in every one of its synthetic worlds, but it assigned the source-defined two CONTENT and two GATE roles correctly in only **5/16**; the frozen semantic-role test failed. This was not remedied by more passive action/reward observations: an unrestricted Boolean 16-bin table is invariant to relabeling its four input axes.

CB4 introduces a **new, separately measured consequence of a controlled intervention**, absent from CB3: after the model has identified four relevant public register bits, it chooses one to toggle. A source mechanism then reports the public binary mediator `M` **before and after** the actual bit-flip intervention, charging one synthetic probe. Source-private CONTENT bits physically affect the mediator; GATE bits alter the reward-selection law but not that mediator. Both learners are told **the same generic measurement semantics and two-of-four role cardinality** and have the same opportunity to choose up to three interventions. The hidden feature locations and source law formula remain only in `mediated_source.py`, not the learners.

This makes previously unidentifiable source roles identifiable **because the intervention adds new observational information**. It is not spontaneous invention of an absent rule and must not be confused with CB3's role criterion passing retroactively.

## Exact custody and frozen-first sequence

- Fork: Yggdrasil accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; predecessor isolated CB3 `df2bb0f1c986505c72992e6b38ca607c6cc1b027`.
- **Preregistration FIRST** at `89dd88e57b0ff78e42fd55cba011ab33ff1edfa8`, prior to new source implementation, tests or original full scoring; it freezes 32 new public worlds `82400..82431`, four source-private current-register feature configurations, a shared 515-action/512-earned-credit tape, 128 new-context score queries/world, three-probe cap, all negative controls, and exact superiority thresholds.
- `mediated_source.py` source commit `69e055bb4443ea9a38187d07fd1b7b9be395f213`.
- `role_interventions.py` candidate/conventional commit `3c035f749758cfd4035300af3625bff850a3e5c8`.
- Frozen full `run_public_dev.py` comparator commit `061becb664b12e7e1f7a17acebd39d542f564909`.
- Seven focused test cases commit `e35ab19dcd7b00fe8a3dd2a54d6cb1b4cffb532e`, **before the original 32-world outcome**.
- Original outcome sealed in `result.json`; exact Git blob, SHA-256, CI isolation and first-use custody are in `provenance.json`. The source, hypotheses, budgets, constraints, result thresholds, and test methods were **not retuned after scoring**.

All four newly committed Python files match their **exact local Git blobs byte for byte**, including `mediated_source.py=7a5e15f4a362723699c6009de9cd1acbf70481ff`, `role_interventions.py=fd602957cb5aa56c304234d1829c5f06a79febcc`, `run_public_dev.py=93265f58148d63a3d2ed1ef5eeabeff8c8f68d0a`, and `test_cb4.py=d32ffe4239c5805023406dea10f133bc59fc0e98`. Original CB3 feature search and independent conventional Boolean control, and CB1 delayed-credit extraction, are **reused unchanged** (runtime pinned by exact blobs). No duplicate native policy or training source has been introduced.

## Original new PUBLIC worlds — real charged synthetic probes

| Metric | Direct-written active | Independent conventional active | Frozen negative |
| --- | ---: | ---: | ---: |
| Correct unordered four relevant public bits | **32/32** | **32/32** | — |
| Correct two CONTENT + two GATE source roles | **32/32** | **32/32** | Passive CB3 grouping **8/32** |
| Paid source-state bit-flip interventions | **80 total** | **80 total** | Shuffled probe-effect attribution **0/32** correct roles |
| Intervention budget distribution | 16 worlds × 2, 16 × 3 | identical | Cap **3/world** |
| New-context binary action correctness | **4,096/4,096** | **4,096/4,096** | No new-context outcomes given during training |
| Logical cold-persistent checkpoint | 78-byte original CB3 + 74-byte role proof | Separate exact-support structure | SHA-covered byte-identity PASS |

**32 worlds × 515 actual common public exploration actions = 16,480 source actions**. Delayed feedback from action `t−2` supplies **16,384 actual earned credits**. Each learner then pays for **80** source-mediated, public bit-flip interventions, with a public mediator before/after value reported only after each chosen intervention. Each learner proposes **4,096** action predictions on unseen, read-only source-owner-scored contexts; these scoring truths are not fed back. Source-private actual role indices appear only in the final source-owner audit, never candidate/control model inputs.

**Frozen benefit over passive role assignment:** 32/32 versus 8/32, an absolute **+75 percentage points**, on the same 32 synthetic public worlds. Shuffling the public feedback to a different probed bit achieves **0/32** exact role assignments. Both models receive the same paid evidence, choose the same probes, and end with the same learned roles.

**The equally informed strong conventional control ties on all 32 worlds.** Paired 1,000-resample world bootstrap 95% interval `[0,0]` for candidate-minus-control role accuracy, so the preregistered +0.05 mean superiority and lower CI >0.01 gates **FAIL**. Therefore **SCIENCE NO-GO for unique native method** even though the intervention-based role-identification engineering capability succeeds.

## Reproduction and careful limitations

```sh
# From a full checkout of the research branch:
cd research/contrib/chatgpt/FKP18-CB4
python -m unittest discover -p 'test_cb4.py' -v
python -m compileall -q mediated_source.py role_interventions.py run_public_dev.py test_cb4.py
python run_public_dev.py
```

**Local environment:** Linux CPython 3.13.5, standard library only, exact source hashes. **7/7 focused tests PASS** covering real delayed public credit, source seed fence, all six source-role partitions, physical one-bit transitions, public-only schema with atomic rejection, one- to three-probe limits, checksum cold restore, and observational role ambiguity. The original complete development study was independently re-executed with the same **non-timing** world records and aggregate outcomes. Canonical full 32-world outcome SHA256 `1736a3df7c1d5bd50bd244b231ed42f15bc0807ea5b1905fb47d2e086ddf035b`; original full JSON file SHA256 `6d0a6111bdad8e0f7ff2a3950eb06b7989226d038963969bbe9f7cc39f50fed8`. `result.json` retains all frozen aggregate predicates and compact per-world receipt indices, and the pinned harness regenerates the complete per-world records.

Important boundaries:

- **Built-in causal prior:** the experiment provides the meaning of the paid mediator channel and asserts exactly two of four parents are CONTENT. This *additional information* makes the source's roles identifiable; it does not prove arbitrary natural causal structure can be discovered from passive experience.
- **Source choice:** four known-form synthetic Boolean environments, 32 disjoint newly exposed **public developmental** seeds; no independently withheld unseen law family, protected evaluation or science first-use.
- **Real actions:** training rewards follow actual attempted binary actions and are delayed; mechanism interventions are source-state single-bit flips with a common baseline reset, charged as **one synthetic paired probe**. This is not an externally physically measured or cost-qualified environment. Action-score audits on held contexts are read-only, not closed-loop policy returns.
- **Strong comparator:** conventional exact four-feature Boolean search plus independent categorical inference gets precisely the same observations, prior, budget and measured outcomes and performs **identically**. Fitting CPU/wall measurements alone cannot establish whole-process advantage or any architecture novelty.
- **Capacity:** 74 bytes is the new serialized role evidence/assignment, on top of 78 bytes of CB3 learned truth table; these are not Python heap/RSS measurements or full general memory.
- **Acceptance:** full exact-source final Ubuntu/Windows mandatory regression and G29 atlas **UNVERIFIED** for this new isolated branch. No native interface compatibility, fully trained recurrent comparison, interference retention beyond CB2, unfamiliar law transfer, or source-private science qualification.
- **Authority:** accepted `main` and active FKP-17 #1109 / FKP-18 #1114 PRs untouched, original FKP17 DEV `978500..978531` and TRANSFER `978600..978663` unopened, no scheduler/controller/runner, paid API, additional workflow, merge or deployment.

**Decision:** Freeze CB4's positive *interventional identifiability* and negative *unique learner superiority* result. Do **not** promote to native Yggdrasil. The next independent scientific challenge must remove hand-given mediator semantics/role count, use independently held active intervention-consequence dynamics, and compare on complete process cost, retained learning, unfamiliar transfer and stronger fully trained controls. Keep separate DG1 paid physical context research and ITD-02 nonlinear parent work under their existing owners.
