# Gate 14 — Prequential misspecification guard, conservative fallback

**Preregistered SCIENTIFIC MIXED/NO-GO.** Engineering synthetic primary finished; exact-head dual-platform CI has separate evidence. This is a contributor-only synthetic experiment, not native Yggdrasil learning or Amalgam model promotion.

## Frozen custody and reproduction

- [Protocol](./prereg.json), preregistered **before source execution** at `fdd63540c8ea475d253f592a80b7ecbc55fd8bf1`; blob `edd07d410f9f4da5d8d0fa9b94656b18b74b54d7`.
- [Source](./run.cjs), source frozen before primary scoring at `4f530f8573cfec059e49a0434c6f7f39e5ff7c91`; blob `ed8a7636bd7212b2dc070560cdd803da387fd625`. Prior Gate13 source reused without changing its existing active, balanced, random posterior/action behavior.
- [Sealed results](./result.json) committed at `9da4ea02a99e5b5e8cba6452d8ddabd7373b19fa`; blob `71521600808149331f46c6ecbe559001dd213073`.
- [Independent mathematical and receipt audit](./audit.cjs), committed `534c086369a99dcf11f75b871d957e8255d25083`. This audit checks experimental thresholds, sample sizes, cardinality and stored comparisons independently; it is **not** a second Bayesian implementation.
- [Provenance](./provenance.json) stores exact refs and exclusions.

To reproduce from repository root using Node (no added packages):

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate14/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate14/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate14/audit.cjs
```

## Mechanism

The hidden world uses 5 controllable binary inputs and a binary output. Each learner sees only its own selected action and observed noisy consequence, with 12 interventions in context A and 12 in B, and shared held labels for all 32 action settings in each context. The *same* known 113-hypothesis Bayesian mixture is used by all five policies (three null/constant, ten unary, hundred two-parent Boolean); three-parent parity and independent fair random outputs are out-of-class.

The **guarded policy** runs the Gate13 posterior-entropy information-seeking action choice, except it reserves intervention steps 3, 7, 11 for fixed balanced diagnostic probes. It stores whether pre-update assigned probability of an observed label is below `exp(-0.85)`. After 6 observations, at least three such surprises in a rolling 6-observation window trigger a *sticky* alarm. When alarmed, subsequent non-probe actions use the deterministic balanced schedule and held predictions mix 50% with fair null `p=.5`. This is a testable **heuristic**; the alarm does not demonstrate reliable detection of all unfamiliar structures.

The comparator arms are unguarded Gate13 active entropy search, deterministic balanced interventions, seeded uniform random interventions, and an *unconditional* damped-active posterior mixture (20% null). All five fit the same worlds, share 12 feedback opportunities, use the same hypothesis class/prior and intentionally compute 32 posterior predictions per action; fixed/random controls would be far cheaper without forced work equalization. **No real compute or energy advantage is measured.**

Source uses **fresh** cohorts: 64 seed pair worlds (34000–34063), 32 unary (35000–35031), 32 three-parent parity (36000–36031), 32 random-independent (37000–37031), each with two context worlds. Total **160 seeds, 320 worlds, 3,840 fit and 10,240 held consequence records**. No held labels were used in posterior updates or alarm logic.

## Frozen held Brier results (lower is better)

| Cohort | Guarded | Original active | Balanced | Random | Always-damped active |
|---|---:|---:|---:|---:|---:|
| Pair causal | 0.0869239037 | **0.0686045530** | 0.1111110642 | 0.1284853191 | 0.0808659479 |
| Unary causal | 0.0576653767 | **0.0518781076** | 0.0680961994 | 0.0588533231 | 0.0617922319 |
| Unfamiliar parity3 | 0.3148051617 | 0.3326628274 | 0.2987481341 | **0.2808122546** | 0.3026239705 |
| Independent random | 0.3027626159 | 0.3384223213 | 0.3009421874 | **0.2817520722** | 0.3075178541 |

**Positive but bounded:** On familiar pair worlds guarded remained better than balanced by **0.0241871605 Brier**, paired approximate 95% CI **[0.0092598495,0.0391144715]**, exceeding the preregistered +0.010 target.

**Three decisive negative criteria:**
- Guarded lost **+0.0183193507 Brier vs original active on pair worlds**, exceeding prereg max +0.008 (CI for active-minus-guarded **[-0.0275585951,-0.0090801062]**). The protection meaningfully weakens familiar-family acquisition.
- Guarded still lost **+0.0339929071** against random on unfamiliar three-parent parity, exceeding maximum +0.015. It did improve compared with original active by **0.0178576657**, meeting a separate criterion, but the best conservative control remains stronger.
- Guarded still lost **+0.0210105437** against random on independent labels, exceeding maximum +0.015. It improved on original active by **0.0356597054**, meeting a separate criterion, but fails the conservative benchmark.

The alarm fired in **17/128 pair contexts**, **2/64 unary**, **23/64 parity3** and **20/64 random** contexts. The false-alarm rate on genuine pair worlds is material. The fixed unconditional null damping arm actually beat the guarded arm on both pair and parity3 worlds in this development trial. That is a *negative control* against claiming novel sophisticated guard superiority.

**Same-process cold continuation:** Every policy uses 1,892 packed state bytes across A/B contexts, including posterior probabilities/log scores, action-visit counters, step counter, six-entry surprise window and alarm state. After A→B fit, A stayed immutable; two restored copies produced identical next four A actions, outcomes, state bytes and predictions. **160/160 seed runs PASS**, but this does **not** establish separate-process/native model cold continuation or persistent knowledge in Yggdrasil's actual learner.

## Disposition

- **ENGINEERING:** Protocol/source committed before scoring, primary deterministic synthetic trial, and exact sealed result PASS; full repository regression and dual-platform G29+Gate14 replay require final CI readback.
- **SCIENTIFIC:** **MIXED / NO-GO** against preregistered joint acceptance. Known-pair action selection still helps versus balanced; defended policy loses too much familiar accuracy and remains worse than the best conservative policy on both unknown-world tests. No open-ended model-order learning, transfer, autonomy or accepted science gain.
- **DEPLOYMENT:** NONE. The central Amalgam Yggdrasil learner, checkpoints, source main, first-use ledger, controllers and runners are untouched. Keep PR #1340 draft and unmerged.

Next hypothesis must be **separately preregistered** on entirely unused seeds and seek direct posterior model-adequacy tests/softly weighted alternatives rather than treating an action-entropy anomaly heuristic as reliable source-class discovery. Preserve these negatives as independent falsification, not post-hoc tuning data.
