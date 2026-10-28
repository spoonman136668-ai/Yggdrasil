# ITD-02 V29 — preregistered observational-equivalence and action-information sufficiency

**Immutable source and reason for this gate.** This record is frozen **before V29 executable code or test outcomes**. Parent is unmerged Yggdrasil V28 PR #614 at exact commit `e226cf23ef7c130f7edb72822052e88d52059766`. V28 exact-host witness #40679983471 2/2 PASS its diagnostic, but `V28_CONTEXT_DIVERSE_REACTIVATION_NO_GO__NO_SCIENCE`: T2 return takes five observed rewards (limit four), unchanged-T1 causes four false source selections. V26 independent PR #611 produced rapid synthetic reactivation but failed its combined strong-control action-regret/prediction utility gate. Those results remain immutable and mutually distinct. **Do not** change detector parameters or count reused V25–V28 traces as fresh validation.

## Primary question, not a proposed new switching threshold

Can *any* agent that observes only the same selected public terminal reward histories distinguish a genuine return to the source reward law from an adversarially different law that agrees on every observed selected action? If not, is additional action-level observation necessary to resolve the difference and improve decision quality? This is a deliberately constructed finite toy **identifiability / information sufficiency** falsification, not new evidence of unknown-world cognition or independently discovered causal structure.

### Exact frozen construction

Use original V23 source train routine: `train_source()["pretrained_shared"]` exactly 16 source epochs ×36 public context/action histories = **576** selected terminal source feedback events. It produces the same pretraining source bytes in each paired arm, no new model weights or special knowledge. The public 12-case selected-action history after source pretraining is exactly the immutable `target_split()[0]` in original `research/itd02_v23_unfamiliar_mapping_audit.py`. It visits all 12 distinct `(cue,actual_first)` contexts, with exactly one selected-second action each and **never** samples their two alternative second actions.

Define source environment A reward `R_A(cue,first,second) = target(cue,first,second,nonlinear=True)` from unchanged original V18 audit. For each cue and actual first action, identify the selected second action `s` from the immutable twelve-case history. Define alternate environment B reward, **externally in the evaluator only**:
- If candidate second action is the selected `s`, `R_B = R_A` exactly.
- Otherwise let `preferred = ACTIONS[0]` when `s != ACTIONS[0]`, else `ACTIONS[1]`. This preferred action is ALWAYS an **unobserved second action** and NEVER `ACTIONS[2]`.
- For preferred, `R_B = +4.0`; for the other unobserved second action, `R_B = -4.0`. Both within existing public reward bounds.

A's optimal second action is `ACTIONS[2]` in each cue+first context because its three second-action coefficients are (-0.5,0,+0.5); B's uniquely preferred second action differs in all 12. **No hidden labels, unselected rewards or regime identifiers enter a candidate, control, model or selector** before the explicitly separate optional probe.

### Frozen observations, comparator arms and impossibility metrics

Construct independent, same-source, cold-initialized pair of V26 calibrated protected slow/fast ring learners (from V26 PR #612), matched original V25 public selector, native V22 scratch learner, and conventional V26 **full 80×80 recursive least squares + CUSUM** control. Each paired arm sees exactly the 12 selected public events `(cue,first,s,R_A)`; the B evaluator returns `R_B` on exactly the same chosen `s`, which by definition equals `R_A`. Train solely through ordinary `accept_second(selected,observed_reward)` or the original conventional `observe` API. Neither source nor fast model sees `preferred`, offline world name, an unselected reward, or a switch notification.

For every paired arm require byte-for-byte identical **public histories, prospective selected-action predictions, feedback residuals, active selector traces, and model checkpoints**, and identical conventional RLS/CUSUM prediction/decision state (with exact finite value checks). Freeze all models after 12 common observations. For each of the twelve cue×first contexts, evaluate the chosen second action from the frozen active policy in BOTH A and B, offline, without learning or counterfactual reward delivery. Report total regret A and B, the contextwise theoretical joint lower bound `L = Σ_context min_action[(max R_A - R_A(action)) + (max R_B - R_B(action))]`, and verify `L > 0`, different optimal actions in **all 12**, and `observed_total_regret_A + observed_total_regret_B >= L`. This pairwise impossibility is a constructed observational-equivalence statement, **not** a general bound for arbitrary stochastic unknown worlds or adaptive action exploration.

### Independently accounted optional 13th selected-action probe

The post-hoc **separate, explicitly observable intervention** is the first observed `(cue,first)` paired with its `preferred` previously unobserved second action. Same chosen probe in both arms; no regime label. Its source reward and B reward must be unequal. That additional **one** legal selected action and actual public terminal reward may then be given to the V26 candidate and conventional controls, and the paired checkpoints / observed-history hash must diverge. This proves only that the specified probe **could reveal distinguishing information** at an additional feedback cost. It does **not** claim the native learner autonomously selected the probe, inferred the environment, improved regret or passed genuine unfamiliar-world transfer.

### Hard negative and custody tests

- If B differs on any of the original twelve selected-action rewards, fail as invalid construction; no result.
- If a learner or control sees `preferred` or an unselected outcome before the separate 13th probe, fail.
- Offline renaming A/B without changing selected feedback must have no effect on models, public SHA or output; withheld counterfactual changes must change an evaluator-only **environment manifest SHA**, but not the observed-history SHA or model states.
- Negative-control alternate B0 with `R_B0=R_A` for all 36 contexts must yield identical optimal actions/regret and no information dilemma.
- The source frozen bank SHA remains immutable; source/fast cell original identities, model checkpoint cold restore, canonical checksums, and existing reward-range constraints hold; exactly 326 stored learned scalars in dual bank (163 target trainable); checkpoint <=12,288 bytes.
- Exact Git ancestors (V28, this preregistration) and original V22/V24/V25/V26 native blob pins, original V28 evidence untouched; canonical case+policy SHA must match Windows 2022 and Ubuntu 24.04 independent CI, with machine-specific CPU/wall/memory separately recorded.
- One bounded native regression for affected V26/V25/V24 and original V22 mechanism, plus use of existing qualified native V25→V12 source. No waiver if any required check fails.

## Ordered frozen classifications

1. Source custody, selected-history equality, deterministic controls, checkpoint/size, manifest equality protection, probe provenance or cross-host qualification fails: `V29_INFORMATION_WITNESS_ENGINEERING_BLOCKED__NO_SCIENCE`.
2. Paired **actual selected** histories and all predictive states fail to match, observed-world optima do not differ in all 12 contexts, `L<=0` or joint regret lower bound fails, or one additional legal selected probe does not distinguish A/B: `V29_OBSERVATIONAL_EQUIVALENCE_NOT_WITNESSED__NO_SCIENCE`.
3. Only if all primary equalities, mismatched optima, positive bound, negative control and optional probe separation pass: `V29_SYNTHETIC_PUBLIC_INFORMATION_INSUFFICIENCY_WITNESSED__NO_SCIENCE`.

A positive V29 classification is **only a synthetic negative identifiability witness**, not a model improvement, not a novel learned exploration policy, not scientific first-use, and not a new claim about original unknown worlds. The appropriate future experimental question is how to acquire informative actions under a matched exploration and cost budget. This V29 gate does **not** authorize a new native model, controller, FORGE or CKB-plane work, original-world operation, V25–V28 threshold changes, merge, model promotion, G29/proxy waiver or acceptance.
