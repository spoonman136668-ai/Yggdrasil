# WSP94 — causal slot binding from interventions and unseen action compositions

**Isolated, synthetic, non-deployed original research. No accepted Yggdrasil model or official FORGE loop changes.**

WSP92 and WSP93 were genuine public-language-learning negatives: the direct reader scored 0/24 and 1/24, respectively, with poor training fit. The original SQuAD DEV cohorts **remain unconsumed**. This project does **not** retune or reuse those public questions. Instead, it tests whether weight-space programming can at least support independently falsifiable **action → consequence → planning**, an ability needed before any general reasoning claim.

## Prospective hypothesis and true scope

**Preregistration-only commit:** `195d2c6c284831a7019fd858dc0b972ca6fd83c3`, before WSP94 generator, numeric writer, control code or experimental use. The frozen `prereg.json` fixes both cohorts, seed lists, complete intervention budgets, hidden dynamics, goals, controls, thresholds and full qualification before data can be used.

Each world has **five opaque actions**, **five observable causal output bits** and **three separately identified exogenous nuisance sensor bits**. The hidden world samples a full-rank 5×5 binary action-to-output effect matrix with a deterministic seed. It is not available to learners. Every arm sees **exactly five actual action interventions**, one per action, with output and nuisance observations **before and after**; the target goals are hidden until all probes finish. After learning from those observations, the model must choose 0–3 actions to reach target outputs from new starts. **All ten unseen two-action and ten unseen three-action compositions** are scored per world. The system is never trained on a combined intervention or its outcome.

The candidate directly writes the five observed XOR effect bits as numerical weights per opaque action. A fixed algebraic planner then composes learned effects. This is *directly written evidence*, not a learned neural world model: **the output delta is already identifiable from the before/after observation**. It does not prove deep causal discovery under confounding or unknown sensor semantics.

## Strong controls and negatives

- **Independent exact symbolic dictionary:** stores the same observed action→effect transitions and independently composes plans. A perfect tie is expected and **cannot count as superiority**.
- **Fully trained conventional model:** 350 epochs of ordinary five-output one-hot logistic gradient fitting on the **same five interventions** and effect labels, with training-fit checks, CPU cost and same goal budget. This conventional control is deliberately fully qualified, not undertrained.
- **Wrong-action association:** uses exactly the same observed effects but cyclically shifts the action IDs. A negative action-binding test.
- **Passive-observation ablation:** gets the same observed state changes but loses the action labels; this has less information, so it is only a negative mechanism diagnostic, not a matched-information science baseline.
- **Deterministic random planner:** no learned map; selects one of the same 26 plan subsets with an immutable SHA256 seed, on every identical target.
- **Cold and integrity controls:** numerical snapshot checksum, exact restoration, no replay, unknown action abstention, source/schema validation, fixed five-action trial budget, separate nuisance counts and frozen plans hashed **before** executing them.

No model sees the hidden matrix or original target-producing action subset. The scorer actually executes all frozen plans in the hidden world. The hidden world fingerprints are recorded for audit **after** outcomes are scored, not consumed by the model.

## Admission and truth conditions

- Public: **10 new worlds ×20 never-explored compositions = 200 goals**, original source seeds 94011–94020. Frozen success needs at least 190/200 correct, exact symbolic parity and fully trained conventional performance, all 250 observed signature bits learned correctly for both candidate and conventional, cold/tamper/unknown PASS, strong separation from wrong-binding, passive and random, and complete resource receipts.
- Reserved development: **20 separately preregistered world seeds ×20 goals = 400 goals**, seeds 94101–94120. Never evaluate them in public tests or create worlds from them before the final exact-source gate. Success needs at least 380/400 correct and substantial gain over wrong action binding. This is *only unregistered development novelty*, **not independent protected science**, since synthetic seeds and algorithms are public.
- Negative scientific outcomes must be reported as `PUBLIC_CAUSAL_SLOT_NEGATIVE` or `DEV_CAUSAL_SLOT_NEGATIVE` with unchanged original thresholds, never repaired post-reserved first-use.

The presence of a successful numerical causal effect table **does not demonstrate AGI, compositional language understanding, general-world dynamics, long-term model training, independent causal invention, or an intelligence advantage over explicit symbolic planning**. In this simple GF(2) world a fully trained one-hot ordinary classifier is expected to tie too. The aim is a trustworthy primitive plus concrete limits, not declaring general cognition.

## Qualification and custody

1. Original prereg SHA frozen before implementation, parent WSP93 negative preserved and **no WSP92/WSP93 protected DEV first-use touched**.
2. Focused WSP94 public-only structural, ordinary comparator, negative, cold and planning tests on Ubuntu and Windows. Scientific negative is an engineering-valid outcome and stops reserved first-use.
3. Only on a verified positive public outcome, record a source-controlled `PUBLIC_PASS.json` referencing both exact GitHub CI jobs and original source SHA. **This is development evidence, not acceptance authority.**
4. Source-only G29 atlas reanchor after public qualification: exactly `.ice/code-atlas.{json,html,ice}`; no source or accepted edits.
5. Mandatory **full WSP80–WSP94 focused suites**, complete Yggdrasil root regression and source-pin G29 on Ubuntu and Windows at the exact final candidate SHA. An original **one-shot** reserved DEV job can run only after both pass, with source/pass receipt validation and no attempt retries.
6. Preserve all original numerical metrics and outcome classification in GitHub; no ZIPs or evidence dumps to the user's ChatGPT Library.

No new controller, alternate scheduler, runner, paid API, owner-loop dispatch, accepted source, main ref, merge, live action or production deployment is authorized here.

**Next scientific direction if this primitive ties controls:** Increase causal difficulty prospectively through hidden confounders, partial observability, longer multi-step interventions and unfamiliar structure, with a stronger trained world-model baseline, identical actual action budgets, cold-retention interference and whole-process cost. Never extrapolate the result to language understanding.
