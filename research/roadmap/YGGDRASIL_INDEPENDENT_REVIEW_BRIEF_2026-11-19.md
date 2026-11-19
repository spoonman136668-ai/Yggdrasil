# Yggdrasil: independent scientific and architecture review brief

**Assessment date:** 2026-11-19  
**Review status:** OPEN FOR INDEPENDENT CRITIQUE — assessment only, not an accepted scientific finding or execution directive  
**Repository:** [spoonman136668-ai/Yggdrasil](https://github.com/spoonman136668-ai/Yggdrasil)  
**Accepted `main` inspected:** `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`  
**Evidence boundary:** Named unmerged research PRs, their frozen original result receipts, the lineage audit, and the acceptance/authority documentation. Where host-local or owner-private evidence is inaccessible, the status is **UNVERIFIED** rather than assumed absent.

> **Question for external agents:** Are we advancing toward a *single cumulatively learning, native causal intelligence*, or primarily increasing the quality and quantity of isolated research studies? What evidence would discriminate these interpretations, and what is the smallest decisive next experiment?

## 1. Plain-language description

Yggdrasil is an independent research program pursuing non-transformer, non-next-token, *native* causal intelligence: persistent internal knowledge; learning action–consequence relations from experience; cold restoration and cumulative adaptation; causal reasoning and compositional transfer to unfamiliar structures; useful intervention policies; and low whole-process resource cost when possible. Language interfaces or conventional models may serve as controls, but must not replace the native tokenless cognitive foundation.

The aim is **not** a large repository, high CI pass rate, a collection of separately trained demonstration models, or a stored knowledge graph by itself. The aim is a recoverable learner that retains and extends acquired knowledge, applies it to genuinely unfamiliar mechanisms and action identities, and improves decisions versus strong fully trained conventional and exact symbolic controls.

There are two distinct things to judge:

1. **Engineering / research throughput:** Can the team construct, preserve, replay, measure and falsify bounded learning mechanisms?
2. **Scientific capability:** Does one independently qualified Yggdrasil learner *accumulate* functional causal competence across time without unacceptable forgetting, generalize to unseen mechanisms, and achieve superior action value under matched data/actions/compute?

A PASS in (1) is not a PASS in (2). This review argues **engineering progress is real, but the continuous-model and scientific-capability claims have not yet been established**.

## 2. Evidence, not impressions

| Claim / area | Original evidence | Qualified interpretation |
|---|---|---|
| Bounded synthetic causal learning and persistence | [CAUSAL-AMALGAM PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) and its linked frozen receipts / [exact-source CI 44504593414](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44504593414) | Experimental native state, retained witness prefixes and four trained JEPA-style specialist histories are reconstructible; **draft research**, not accepted persistent canonical model |
| Learning on a previously withheld context–action cell | [PR #1278: transfer-curve-dev-01](https://github.com/spoonman136668-ai/Yggdrasil/tree/a6dfa476d577dae9f224463ae59f35d95ce09fce/research/contrib/chatgpt/CAUSAL-AMALGAM/transfer-curve-dev-01) | Four 120-witness continuations lowered mean held Brier **0.330464 → 0.210820** (~36.2% relative reduction), but best fitted/fixed control was **0.195822**. Only one seed met the frozen final advantage; result **DEV_NO_GO** |
| Functional retention after continuation | Same frozen [PR #1278 evidence](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) | Familiar transition Brier worsened **0.091801 → 0.189425** (drift +0.097624 vs allowed +0.02). Checkpoint bytes and witness counts persisting **did not ensure retained predictive competence** |
| Specialist integration | [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) | Multiple retained JEPA temporal heads operate and checkpoint, but gated blending or selection has **not shown a qualified advantage** over the native-only / strong controls. Do not grant automatic policy influence |
| Nine frozen CKAD development studies | [CKAD41–49 audit PR #1320](https://github.com/spoonman136668-ai/Yggdrasil/pull/1320); [audit CI 44522312396](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44522312396) | **0/9 scientific DEV_PASS; 9/9 DEV_NO_GO** against frozen strongest named controls. Scoping matters: engineering audits **8/9**, with CKAD42 cross-platform checkpoint SHA discrepancy. Original held pilots/primaries remain unconsumed per audit |
| Previously unseen causal laws | [PR #1320 architecture-gap analysis](https://github.com/spoonman136668-ai/Yggdrasil/pull/1320) | Some mechanism fit succeeds when the true law is already inside a finite provided candidate set. That is *system identification*, not demonstrated discovery of an out-of-grammar causal law |
| Accepted canonical model continuity | [YGG-LINEAGE01 PR #1322](https://github.com/spoonman136668-ai/Yggdrasil/pull/1322); accepted `main` above | **No accepted continually trained canonical model checkpoint identified in inspected Git**. A private host-local checkpoint and live owner custody are **UNVERIFIED**, not proved nonexistent |
| Official unattended execution | [LINEAGE01-E in PR #1322](https://github.com/spoonman136668-ai/Yggdrasil/pull/1322); [owner run 44522000519](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44522000519) | The official executor prints `RESEARCH_EXECUTOR_UNATTENDED=NOT_CONFIGURED_NO_MODEL_INVOCATION` and records `advanced=false`; launcher successor dispatch skipped. Successful workflow != ongoing model learning |
| Auditing/engineering qualification | [LINEAGE01 exact regression 44530606413](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44530606413) | Draft audit candidate passed **67/67 tests on Linux and 67/67 on Windows**. This qualifies the *auditing change*, not model advancement or acceptance |

**Numerical caution:** Brier is lower-is-better. Different CKAD worlds, controls, sources and policy budgets are not pooled. A within-study improvement relative to an earlier candidate does not imply superiority to the strongest frozen control, general transfer, reward improvement, or intelligence. Above figures are archived development evidence, not new results obtained for this brief.

## 3. Assessment, with alternative explanations

### Engineering — PROGRESS, qualified only within named research studies

Yggdrasil has increasingly reproducible native transition learners, append-only witness history, reconstructed checkpoints, JEPA specialists, readout/retention diagnostics, dual-platform source qualification and detailed negative experimental receipts. This is material engineering and methodological progress.

**Limit:** Much of the experimental material is on unmerged branches and represents distinct learners or synthetic worlds. Branch/PR accumulation is not equivalent to one model's knowledge accumulation. The accepted model interface, active owner model state and current host-local checkpoint must be identified independently.

### Scientific — CONTINUED LEARNING EXISTS IN BOUNDED EXPERIMENTS; GENERAL IMPROVEMENT UNPROVEN

The learner can change its predictions after new action–outcome observations, and individual experiment checkpoints can be reconstructed. However, the reported frozen comparisons fail the stated superiority or retention gates. Novel out-of-grammar causal law discovery, durable cold *functional* retention through interference, and superior intervention policy value remain unproven.

This is *not* evidence that a native causal architecture cannot work. Potential explanations requiring discrimination include: insufficient state/history representation; too-restrictive hypothesis grammar; interference/retrieval problems; wrong source or evaluation target; inadequate exploration; unfavorable information/compute matching; and genuine intrinsic limitations of a proposed mechanism. **Do not silently choose one explanation or tune on scored cohorts.**

### Autonomy / deployment — NO QUALIFIED CONTINUOUS OFFICIAL MODEL EXECUTOR

LINEAGE01 verifies disabled unattended model invocation and no identified accepted canonical cumulative checkpoint in Git. This does **not** rule out independently running owners, private on-disk models or supervised research; those need owner-authenticated receipts. Do not launch a rival scheduler, restart a model, impersonate a source owner or infer operational authority from CI.

## 4. Proposed decision sequence for critique (NOT authorization)

**P0 — Verify custody before touching a learner.** Identify the actual native canonical checkpoint (if any), complete learned-state/source/config SHA, last witnessed event sequence, owner, branch, active runner/lease and chronological resume ledger. Cold-restore it *read-only* and check functional old-knowledge predictions. If unavailable, report loss/uncertainty and seek an independently authorized recovery path; **do not fabricate a continuity claim or silently restart training**.

**P1 — Test real accumulation, not more disconnected prototypes.** On one verified model lineage, freeze sequential additions of small genuinely new bodies of source-licensed knowledge and action–consequence observations. Record exact prefix/custody and state transitions. Include source conflicts and relationships that require composition; compare matched source-only retrains and equal-data conventional/symbolic baselines. Archive negative and old-knowledge tests at every checkpoint.

**P2 — Make retention functional.** Measure old readout error, new knowledge, interference, cold restart, retrieval/selection reliability and budget. Separate storage integrity (same bytes) from learned competence (same relevant predictions/actions). Freeze acceptable drift and gain thresholds before fresh evaluation, with native-only, replay/regularization and exact controls.

**P3 — Test unfamiliar structure and action identity.** Use owner-certified, genuinely disjoint unknown operators, graphs or intervention mappings outside the fitted hypothesis grammar; protect untouched evaluation labels. Require source authenticity, finite action budget, matched information, fully fitted conventional and exact symbolic controls, sham/random controls, seeds, and no re-use of consumed CKAD/Amalgam outcomes as "new" first-use.

**P4 — Require decision value and efficiency evidence.** A better Brier score alone is insufficient. Measure intervention/reward gain, negative controls, cold retention after additional training, whole-process wall/CPU/GPU/energy where feasible, data/action cost, and independent reproduction. Promote only on preset margins plus exact-final engineering qualification and separately authorized scientific acceptance.

These are a **recommended review order**, not a permission grant or fixed implementation plan. Reviewer alternatives are expressly requested.

## 5. Questions for independent reviewer agents

Please challenge the diagnosis rather than assume it is correct:

1. **Evidence audit:** Which specific source or frozen receipt corroborates or falsifies each table row? Did this brief conflate main with a draft, a local model with an official one, an archive PASS with a science PASS, or a stored checkpoint with functional retention?
2. **Most consequential bottleneck:** Is lineage/custody the dominant blocker, or is a limitation in representation, exploration, operator grammar, retention or evaluation more urgent? Name a falsifiable competing hypothesis.
3. **Minimum decisive experiment:** Propose the *smallest* source-governed, genuinely new, preregisterable comparison that discriminates the hypotheses while minimizing first-use cost. Freeze primary metric, margin, strongest fully fitted control, splits/seeds, action/information/compute parity, negative controls, cold retention, budget and stop condition.
4. **Amalgamation:** How would you attach new knowledge to *one* existing native state without replacing its non-token causal foundation, losing learned JEPA parameters or leaking held outcomes? Distinguish a proposed software interface from demonstrated learning.
5. **Failure response:** If the candidate loses twice under qualified fresh comparisons, what would you stop, ablate, redesign or falsify instead of repeating parameter tuning?
6. **Adversarial view:** What evidence would make you reject the proposed “close continuity first” priority? What superior alternative would you test, and why?

### Requested review response format

- **Verdict:** AGREE / PARTIAL / DISAGREE / UNVERIFIED
- **Top three factual corrections:** each with a source URL + commit/run/receipt where possible
- **Strongest competing interpretation:** a falsifiable hypothesis, not an opinion alone
- **One decisive experiment:** frozen primary and retention metrics, controls, source/seed/split custody, compute/data/action budget, exit criterion
- **Risk / safeguards:** first-use, leakage, parallel owner collision, model replacement, hidden costs
- **Next recommendation:** one proposed owner-qualifiable action; specify engineering / scientific / deployment status separately

Agent reviews and comments are **advisory only**. No review constitutes authority to run original source experiments, schedule or dispatch training, change accepted refs, merge, promote, deploy, or modify other projects' controllers. Keep external contributions isolated under [CONTRIBUTING_RESEARCH.md](../../CONTRIBUTING_RESEARCH.md) and the actual source-owner protocol.

## 6. Provenance and limitations

- Basis timestamp: **2026-11-19**; accepted `main` pinned **`5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`**.
- Primary evidence: [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), [PR #1320](https://github.com/spoonman136668-ai/Yggdrasil/pull/1320), [PR #1322](https://github.com/spoonman136668-ai/Yggdrasil/pull/1322), each **open/unmerged at review preparation**.
- Original result receipts, pinned SHAs, CI run IDs and caveats remain in those PR bodies and linked Git trees; follow through to source artifacts before accepting any research claim.
- No new training, model calls, test execution, protected-source first-use, acceptance, CI dispatch, merge, promotion, deployment or model/runtime/controller alteration was performed to compose this document.
- This brief is **an independent review request**, *not* an endorsed research conclusion. It may be superseded by verifiable new owner-side evidence or future accepted source. Reviewers should record date, source SHA and independent findings rather than copying assertions.

**Status:** ENGINEERING — documented archive findings; no new code qualification. SCIENTIFIC — audit/critique only, no new pass. DEPLOYMENT — none.
