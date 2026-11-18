# WSP-174 — Source-free chemistry public-evidence boundary

**Engineering only.** This is not a learner, a source-first-use job, a source lease, a training recipe, accepted Yggdrasil source, or scientific qualification. Original source resets/steps/interventions in this branch: **zero**.

## Original-source pin

- Independent upstream: `dido1998/CausalMBRL@2c595988b06b3d568fdde53213029e97841acb03`.
- `envs/chemistry_env_rl.py` blob: `58af54d7e7e30f8abe059df3d68565845a5b2c51`.
- MIT `LICENSE` blob: `cff393fe08ddf5fdd6fa4b8f509df9789bf54900`.
- Original source public `get_state()` produces a `(25,5,5)` one-hot object/color/position representation. Original `reset()` returns current and target (goal) public states; original `step()` returns public next state and reward `matches/5` plus `done=False`. The 25 actions select one of five objects and one of five colors; descendants are updated by source-owned MLPs and graph. This code does not fetch those private weights or graphs.

## Bounded bridge, not the simulator

`PublicEvidence.from_public(current_state=..., goal_state=..., action=..., next_state=..., reward=..., done=...)` accepts only pure Python lists/tuples from a future **independently approved** owner's public extraction step. The owner alone is responsible for converting NumPy arrays using `.tolist()` and for pinning exact dependencies/source and counting physical source actions. The bridge imports only Python's standard library and makes **no** source calls.

It checks 25x5x5 shape, exactly one color/position per object, unique positions, 0..24 discrete action, fixed object positions through the intervention, acted object's selected resulting color, literal source-`done=False`, reward increments and equality to the public returned goal/next state. All test tensors are fabricated negative-control fixtures, **not protected original results**.

`policy_input()` provides only current and publicly shown goal coordinates/colors; it does not disclose action consequences or reward before execution. `learning_record()` includes the public action and observed consequence **after** the step, with deterministic immutable ASCII JSON and SHA256 restore. No hidden source DAG, MLP weights, source random states, `actions_to_target`, evaluator labels, source seed or lease is accepted. A caller cannot reconstruct independently hidden graph truth just because it can inspect public reward.

## Important limitations and denial rules

- The original source's `step()` never sets `done=True`; an **owner-governed** externally imposed cap must be logged separately, without recoding a truncation as original termination. This gate never chooses such an execution cap.
- The target goal is an actual **public reset output** in this source; other environments must not assume goals are public.
- The bridge's scene extraction intentionally omits raw image features; all comparator arms must be granted the same registered public representation before any scientific test. This is an interface convention, not a trained encoder or representation-learning result.
- This guard checks *structural agreement of a purported public record*, not authenticity of a physical source action. Only a source-owner effects journal, signed first-use lease and independently qualified actor can attest original data origin.
- The upstream source's global `numpy`, Python `random` and PyTorch RNG usage remains unqualified. No original runtime, GPU, 10-step episodes, fully trained controls, new-world transfer or convergence is evidenced here.
- The 13,312 original action conditional maximum is **not** permission; CVH-10 first-use remains denied.

## Qualifier

Focused test: `python -B -m unittest discover -s research/contrib/chatgpt/WSP-174 -p 'test_*.py' -v`.

The branch-only CI follows existing WSP-169 architecture: isolated focused tests and inherited WSP-159–169 regression both OS; one bot-generated G29 atlas (only three derived files); then exact-final full root/NKR05 and independent G29 on Windows+Linux. A source-boundary engineering PASS cannot be promoted as a scientific PASS or approval to call an original source. Nothing in native `yggdrasil/`, CKAD, Forge, source owner, main or live runner is edited.

Source-owner work item: https://github.com/spoonman136668-ai/Yggdrasil/issues/426
Original WSP-169 parent: https://github.com/spoonman136668-ai/Yggdrasil/pull/1227

**Status at authoring:** local isolated source-free tests passed 8/8. CI, exact-final G29 and full dual-OS qualification pending; science first-use NO-GO / deployment NONE.

## WSP-176 — five-action goal-completion saturation veto

**Actual original-source law proof, not a simulator run.** Inspect pinned `dido1998/CausalMBRL@2c595988b06b3d568fdde53213029e97841acb03:envs/chemistry_env_rl.py` Git blob `58af54d7e7e30f8abe059df3d68565845a5b2c51`. Its `reset()` returns the goal state as PUBLIC. Its `step(action)` sets the selected object color via `translate(obj_id, color_id)`. `translate` calls `sample_variables(idx)`, which loops exclusively over indices `v in range(idx + 1, num_objects)` to recalculate descendants. **No action at index i can modify any object with an index less than i**, regardless of hidden DAG, source MLP parameters, color dynamics or random seeds.

Therefore a completely untrained deterministic policy that chooses in ascending object order `i=0,1,2,3,4` and sets color `goal[i]` must have all first `i+1` objects matching the goal after step i (straightforward induction). After five interventions, all five match. The original returned reward is `matches/5`, hence the **step-five reward is exactly 1.0, its maximum**, for all valid original source worlds obeying these lines, provided the standard external evaluation allows five actions. Any larger horizon contains a fifth-step reward of 1, but this says **nothing** about sum of earlier rewards, shorter-than-five plans, action penalties, or novel causal transition prediction.

The pure-stdlib executable baseline `goal_veto.py` uses **only the public target scene and public step count**; it never sees the DAG, MLPs, source environment, target intervention actions, next outcomes, or hidden state. `test_goal_veto.py` exhaustively checks all `2^10=1,024` possible lower-triangular five-node DAG edge masks under multiple deterministic opaque downstream causal functions, and checks wrong goal/action/step input refusals. These are synthetic *proof stress controls* only; they are **not 1,024 independent source-world experimental actions or newly trained models**. Exact source pinned methods are the primary proof, and source-family first-use authority remains with the existing source owner.

**Scientific decision:** Final/terminal goal-success and fifth-step reward are **SATURATED BASELINE / NO-GO** for original first-use claims of causal learning superiority. This veto does NOT rule out intermediate cumulative return, shortest intervention sequence, calibrated action→descendant transition prediction, held-out graph-family inference, or cold retention. Only those unsaturated objectives could merit an owner-independent prospective headroom check and fully fitted baseline before first-use. Never treat WSP-176 as source first-use, model training, license, lease, owner authority or evidence of intelligence gain.

The existing WSP-174 dual-OS engineering receipts apply to old SHA `ff06acd6b69231b98fc020ca46cdb7692a66dcc4`; after this code change, **both mandatory full regression and independent G29 must be requalified on the new final candidate SHA/tree**. Preserve the old receipts as historical, not reclassify them as current. No live source actions or deployment.

## WSP-177 — stochastic downstream learning qualifier (no original source actions)

**Actual pinned source finding:** `dido1998/CausalMBRL@2c595988b06b3d568fdde53213029e97841acb03:envs/chemistry_env_rl.py` (`58af54d7e7e30f8abe059df3d68565845a5b2c51`) defines `MLP.forward` with `torch.softmax` and `torch.distributions.one_hot_categorical.OneHotCategorical(probs=x).sample()`. The original environment's descendant color updates are therefore **STOCHASTIC**; the same public state+action can have different outcomes, even at unchanged source graph/MLP weights.

**Proper objective:** Do not score the explicitly set object or unaffected lower indices as causal learning; their next state follows directly from the action and source index order. For source-public action `a`, score only `v > a//5`, with the five-class **proper multiclass Brier** of the prospectively predicted next object color distributions, averaged over those descendants. An action on object 4 has no descendants and is **UNSCORABLE** as evidence of causal transition discovery (score `None`, not a perfect zero). These actions still spend *physical original action budget* when authorized. The public `goal` remains uniformly visible to all arms; private graph/MLP/source RNG remain out of model inputs.

**Reusable engineering controls:** `stochastic_controls.py` implements deterministic source-free identity and uniform zero-learning reference forecasts and an exact one-pass-to-convergence five-category **conditional Dirichlet** control keyed only by (`action`, `downstream object index`, `pre-action object color`). Its alpha=1 posterior predictive is explicit `(count+1)/(n+5)`; `fit_observed()` consumes post-step **public FIT records only**, then `freeze()` permanently rejects attempts to update from held outcomes. Forecasts require only the original public current/goal state and chosen action (never next state). This is a legitimate trained **categorical baseline within its restricted model class**, **not** the strongest conventional recurrent/graphical/neural control and **not** yet a model-superiority experiment.

**Qualification:** New source-free tests use fabricated public-format observations, verify that direct-action/lower indices never inflate learning scores, check Brier probability validation and 0-downstream exclusions, test conventional FIT/freeze and no-held-update, and enforce no original simulator imports or hidden fields. They are developer checks, not original-source episodes. Prior WSP174/176 and WSP169 checks stay in the same branch and CI. Re-run the complete Windows/Linux regression and independent exact-final G29 on the new code SHA/tree before claiming engineering qualification.

**Prospective scientific stopline:** The owner of any actual first-use experiment must first freeze a scored descendant-probability gain threshold relative to **the strongest** fully fitted conditional tabular/Bayesian/graphical/neural/recurrent reference with the SAME public evidence and protected action budget, plus cold retention and truly unfamiliar source family transfer. Do not optimize Brier on unopened HELD/TRANSFER. Current source first-use remains denied by owner issue #426; no first-use lease, action actor, source reset, train run, merge, deployment or scientific PASS is generated by this source-free code.

## WSP-178 — original-science-ready direct categorical weight interface (engineering only)

**New mechanism:** `direct_color_weights.py` is a bounded, source-free, tokenless explicit model with five directly programmed probability weights per (intervention action, strictly downstream object). Only after a *public FIT* transition does it update its implicated weights in exact rational arithmetic: `p_new[k] = ((5+n) * p_old[k] + 1[k==observed]) / (6+n)` from a symmetric one-per-color prior. The model freezes and forecasts only from original public current/goal and action; checkpoint is a canonical SHA-256-bound aggregate of observation counts, without hidden original source, graph, seed or raw world observations.

**Mandatory falsification:** This update is **mathematically equivalent** to a conventional five-category Dirichlet(1,..,1) posterior conditioned on the same (action, downstream object) feature key. `test_direct_color_weights.py` independently constructs that matched-feature conventional estimator and proves EXACT prediction equality on source-free samples. Rebranding identical Bayesian sufficient statistics as "direct weight programming" cannot generate a scientific performance gain. A stronger existing *context-conditioned* `ConditionalDirichlet` control can beat this pooled model in a public-only constructed context-dependent case; that negative is preserved. This deliberately prevents a false science promotion and identifies **representation/feature discovery**, not numerical update style, as the scientific gap.

**Actual capability:** The code is now able to consume the WSP174 public source-outcome format, update its own weights on previously admitted FIT evidence, freeze before scoring and emit strict-descendant categorical predictions for WSP177's proper Brier metric. It does **not** import, instantiate, reset or step upstream chemistry, and its tests use fabricated inputs, never untouched original science. Frozen conventional comparisons must be fitted offline on the SAME admissible public FIT, not on magic evaluator truths; the source owner alone provides distinct authorized cohorts and effect receipts.

**Scientific decision:** Direct weights with same feature/statistical update as matched Bayesian has NO intrinsic statistical advantage. Neither that nor a negative fabricated-context test proves a real-source NO-GO for new feature representations. Further mathematical reimplementations of the same statistics are discouraged. Real next objective: structurally new causal features with nontrivial held-family headroom, fully trained conventional controls and owner-approved actual action consequences. Source owner issue #426 still denies first-use, action ceiling 13,312 is conditional only; engineering acceptance does not permit protected activity, source actor, deployment or merge.

New code changes require fresh final Windows/Linux full regression and independent G29 acceptance on exact candidate SHA/tree. Previous WSP174-WSP177 results remain historical and valid only for their own SHAs.

## WSP-180 — complete offline fit / freeze / held-only score path

**Engineering closure of the missing integration seam; NOT more source-free scientific scoring.** `offline_compare.py` consumes only preexisting `PublicEvidence` rows from WSP-174 with caller-supplied **unique event IDs**; it never constructs a world, requests protected source data, dispatches a runner or calls the upstream `CausalMBRL` simulator. Event IDs are bookkeeping claims (not source-owner signed custody), and bit-identical stochastic public records with distinct event IDs are *not* automatically duplicate source actions.

The evaluator fits the existing **WSP-178 direct-programmed categorical weights** and existing **WSP-177 conditional Dirichlet** from a supplied *FIT* list only, then freezes both before any *HELD* outcome is scored. On each held event every arm receives only the original current/goal public scene plus action, and only then is its forecast compared with the observed next state. The comparator arms are direct, conditional Bayes, zero-learning identity and uniform, all scored on the SAME held public events. Calculations use **potential-downstream object-slot weighted multiclass Brier**, not episode averages which can conceal differences in number of downstream opportunities. Interventions on last object count as observed events but have **zero scored slots**; no all-unscorable cohort can get a passing or numeric result.

Each FIT/HELD list has a deterministic SHA-256 input fingerprint bound to caller event IDs and public record SHA-256, with no original-world source proof inferred. Duplicate event IDs within/across splits are rejected; identical content with **different owner IDs** is allowed because stochastic outcomes can coincide. This is only split-integrity/measurement engineering; real origin, virgin source membership, actor, no-replay effects, fitness rights and matched fully optimized conventional baselines still require independent SOURCE OWNER qualification.

**Result is deliberately stamped `DEV_ONLY_UNATTESTED_ORIGINAL_SCIENCE_NOT_RUN` and `scientific_pass=false`.** The best of the three provided restricted controls is NOT the globally strongest fully trained conventional model. The report also refuses to represent old-law retention, unseen-family transfer, authenticated source origin or source actor authority as done. The harness never submits an order, source action, first-use lease, queue job or new controller. No sealed original FIT/HELD consumed. It enables a future owner-provided public evidence comparison without repeatedly rebuilding the evaluator from scratch, but it is not an owner authorization by itself.

Source-first-use remains blocked at [owner issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426), CVH10 `first_use_execution_allowed=false`. Next actual scientific decision requires a verifiably virgin law cohort, source-owning actor, matched conventional/gradient/graphical/recurrent references, frozen gain threshold and action/time accounting. No improvement claim is made for this PR until those are independently demonstrated.
