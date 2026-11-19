# CKAD46 — Unknown action-symbol grounding into persistent native causal learning

**Isolated research-sidecar development only.** Original binary `NativeEpisodeExperience` and `PublicCausalCells` remain unchanged. Original Yggdrasil `main` is unchanged. Parent [CKAD45 PR #1306](https://github.com/spoonman136668-ai/Yggdrasil/pull/1306), SHA `b9cdc894a7e499f8ba74fcbac64fbb824259daa7`. The preregistration `1fcd7e165e87561cc4f47ef7a0f71ebc3e1873ba` was committed **before the source code and new DEV scoring**.

## Actual architectural limitation and proposed experimental bridge

The original `PublicCausalCells._bit()` and `NativeEpisodeExperience.observe/forecast` require binary interventions `x1,x2 ∈ {0,1}`. Passing any new motor-action ID into those APIs is unsupported; merely evaluating an alias relabel without consequences would not prove action grounding.

The experiment first trains native `NativeEpisodeExperience(repair=True)` and exact-restoration `NativeInterventionRelations` on **96 genuinely observed** paired binary interventions with public contexts and stochastic consequences. The already trained source causal model is **frozen and preserved** as a prototype at episode 96; the live native and causal models continue their original episode chronology without resetting learned weights.

Next, 144 fresh intervention episodes use new public symbols `10,11,12,13` for both stages; none existed during pretraining. Each symbol has a **private**, unannounced binary actuator class. The two stages independently randomly permute balanced assignments `[0,0,1,1]`. These hidden classes exist only in the evaluator/physical world, not in any learner. The first action is chosen from the fixed public action stream; the genuine next state is revealed; a separately chosen second motor symbol then causes a genuine terminal reward. Only after that episode is witnessed can a learner update its grounded belief and its continuing native causal weights. The final 48 episodes return to original known binary interventions to measure cold retention.

**The task assumption remains binary underlying actuator semantics** (a known two-primitive physical system). This tests previously unknown **identities and action-symbol grounding**, **not** invention of new actuator physics, unseen affordance semantics, arbitrary language meaning, or a fully general intelligent agent.

## Source-trained experimental learner

The novel-symbol binder retains separate per-stage log-odds of whether each new symbol realizes latent primitive 0 or 1. It updates odds from real **prequential witnessed** transition/terminal likelihoods under the preserved frozen native causal prototype. Its current predictions integrate both possible binary actions; after actual next-state observation, its terminal prediction conditions the class posterior on that observed transition, never on future reward. Continued native and causal source training use the **pre-outcome MAP** inferred action class; a separate immutable raw-receipt map retains real source IDs and every original action ID, so no unobserved class is silently relabeled as source truth.

The strongest fitted independent control enumerates all **36** balanced mapping hypotheses (6 legal maps per stage) with a uniform prior, updates on genuine witnessed source likelihoods and integrates over exact posterior mapping uncertainty. This is a favorable exact probabilistic structural prior; it is not an oracle because it never receives the actual hidden mapping. It maintains separate native/casual states and same pre-outcome MAP training rule. Additional controls:
- Fully fitted conventional Beta(1,1) outcome counts keyed by **raw symbol IDs** and context, not mapped identity.
- A separate unmodified native learner with a deterministic identity-hash binary adapter for unknown symbols.
- Frozen source causal expert with equal 50/50 unknown symbol mapping and no inferred identity.
- **Privileged mapping oracle ceiling (not a trainable control)**, used only in evaluation to show unachieved knowledge, never to train candidate or controls.

All learnable arms see the same actual public source rows and actions, same stochastic exogenous outcomes and identical number of witnessed interventions. Extra exact Bayesian and separate source-model computation is **not matched compute**, and no efficiency improvement may be claimed.

## Frozen development gate

Two fresh registered DEV seeds `46111,46112`, 2 worlds each; 288 actual public episodes per world (96 known + 144 unknown + 48 old-action return). Other original seeds CKAD37–45 are excluded. Pilots `46211/46212` and primaries `46311/46312/46313` are reserved and **never executable** here.

Both DEV seeds must yield pooled late-unknown + cold-return paired Brier ≤0.150, and improve by ≥0.015 absolute over the **strongest nonprivileged, fully source-trained control** including exact Bayesian mapping. The first 32 unknown-action predictions cannot worsen by >0.015 against the best control. Original known-action cold return cannot worsen by >0.005 against the separate native hash control. All four unknown symbols must be actually witnessed in both stages. Existing source prefix, frozen 96-event causal checkpoint, byte-exact cold restore, raw action identity and conflict atomicity must hold.

Any failure => **DEV_NO_GO** and no same-seed science retuning or held pilot/primary first-use. Even a favorable DEV => **DEV_FEASIBLE_NOT_SCIENTIFIC**, not a scientific pass. Genuine new physical action classes, unknown mechanisms, independent held worlds, full repo regression, matched process costs and owner acceptance would remain necessary before any promotion.

## Safe DEV reproduction

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-46 -p test_ckad46.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-46/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-46/screen_dev.py
```

One isolated Actions workflow first runs only disjoint engineering fixture tests. It allows only the exact frozen new DEV cohort on Ubuntu and Windows, and emits all source checkpoint SHA receipts. It never invokes scheduled tasks, paid APIs, a new controller or official FORGE/Yggdrasil owner process. The accepted native binary API is not modified, no user File Library artifacts are created, and `main` is not merged/promoted.
