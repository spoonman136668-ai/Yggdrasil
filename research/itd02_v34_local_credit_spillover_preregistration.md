# ITD-02 V34 — preregistered native local-credit spillover and capacity diagnosis

**Freeze before executable V34 audit.** Source is V33 draft PR #623 at `5bb6d0cfe095cddce438028cdd30d934239c4de7`, exact-source Windows+Linux run #40707582111, behavioral result `V33_UNSEEN_WORLD_LEARNING_GAIN_NOT_ESTABLISHED__NO_SCIENCE`. V33's U1/U2/U3 toy reward laws, 576-source selected-feedback pretraining, 12 original selected contexts, 3 novelty choices at context positions 0/4/8 and diagnostic outcomes are immutable. V32's retrospective A/B source-return positive **does not imply general transfer**; V33 native novelty improvement occurred in U2 but not U1 or U3. V34 tests *why* a fixed native learner may fail, without retuning any previous policy or external selector. The other research lane's sealed Q1/Q2/Q3 holdout is out of scope.

## Only V34 scientific-development question

Does the existing original eight-cell V22 `shared` ring distribute credit from one **actual selected** reward across inappropriate unseen cue/first/action outputs (interference), or does its 163-parameter fixed representation fail to change action ranks with sparse updates even when local credit is correctly routed? Run a bounded *source-only* mechanism diagnostic and one pre-existing V22 `action_partition` **ablation** under the identical legally selected feedback. The ablation is not a new autonomous learner and is not a promoted model.

## Fixed setup and intervention

For each U1/U2/U3 frozen V33 evaluator-only law (unchanged), instantiate from cold start:
1. unchanged V32 source-protected selector and its original V22 FAST shared bank, plus unchanged V30 public-count novelty chooser. This arm alone chooses its next public action prospectively.
2. a separate fresh original V22 FAST `mode="shared"` **mirror** learner (same 163 learned scalars), receiving precisely that arm's actual selected feedback sequence;
3. a separate original V22 FAST `mode="action_partition"` partition ablation (also 163 learned scalars), receiving the **same exact** sequence, not separately chosen actions;
4. an independently cold-initialized V22 `mode="shared"` negative control receiving the selected events using `learning=False`;
5. original online full 80-feature conventional `RidgeCUSUM` receiving **that same actual** public sequence as a strong diagnostic (plus use already independently chosen RLS V33 results solely as separately labeled historical comparisons).

No parallel model influences which actions V32 selects; no selected-event reward is supplied until after V32's prospective choice. The 12 initial selected cases are original immutable `selected_map()[0]`; the 3 extra chosen public second actions occur at context indices (0,4,8), with chosen actions frozen before evaluator law calls. **Total: 15 legal target-selected feedback observations per world, plus original source bank's 576 pretraining observations only for V32 and RLS.** No 12-source-return phase for this isolated V34 credit experiment; V33 original return tests remain unchanged and authoritative.

## Frozen measurement

At time 0 (before target feedback), after the 12 base rewards, and after **each** of the three selected novelty probes, freeze clones of V32 FAST, shared-mirror, action-partition ablation, negative no-learning V22 and conventional RLS. For all 12 `(cue,first)` public contexts and three second actions, obtain prospective predictions from each clone **without learning**, plus the argmax-selected action vector, 12-context regret against that world's offline evaluator-only full reward table, sum of absolute prediction error and exact model parameters SHA. The full world table is consulted **only after frozen predictions** and is never given to any learner or chooser.

Each of the three probes additionally records:
- selected public (cue,actual-first,selected-second), actual selected terminal reward, and three arms' pre-update prediction errors;
- shared/partition pre/post selected-action prediction delta; pre/post same-context two unselected-action prediction deltas; pre/post other-11-context predictions across all three actions; *signed and absolute* spillover with mean and maximum, all from frozen snapshots;
- source-bank SHA, original native cell identities, forward/reverse neighbor messages, V32 current gated SOURCE/FAST state, 163-per-learner weight SHA change, cold-restore bytes, updates and CPU/wall/peak memory;
- deterministic ratio `spillover_ratio = sum(abs(delta) over 33 OTHER-context outputs) / (abs(delta on selected action) + 1e-9)`. This is a diagnostic of coupling, **not** a learned causal mechanism or universal threshold.

Compare the FAST selected-output regret and action rankings at budget0 vs budget3 for V32 FAST, shared-mirror, and partition. Validate shared mirror **exact parameter SHA** of V32 FAST after every public update (nonlearning mirror must not change). Partition is a preexisting fixed alternative with identical public rewards, counts and parameter budget, not proof of superiority without independent new-family testing. RLS conventional diagnostics reflect the **same chosen feedback**; V33 independent-action RLS baselines remain separately cited, never conflated.

## Frozen ordered classification

1. If prereg ancestor/source blob/pins or no hidden-world observation rules fail; V32 FAST differs from identical shared-mirror learned parameters; selected feedback differs by arm; any original source parameters change; no-learning negative changes; 163-parameter/8-cell/4-hop native invariant or checkpoint ≤12288B fails; any requested per-probe 36-output delta, spillover, message, alternative RLS, resource trace or frozen-output digest is missing; Windows/Linux canonical evidence hash differs; or focused V33→V22 original regression fails: `V34_CREDIT_DIAGNOSTIC_ENGINEERING_BLOCKED__NO_SCIENCE`.
2. If partition budget3 regret beats original shared FAST regret by **at least 10% in ≥2 of U1/U2/U3** and does not increase the three-world mean 12-context regret: `V34_ACTION_PARTITION_LOCALIZATION_DIAGNOSTIC_POSITIVE__NO_SCIENCE`. This means only a bounded identical-action *ablation signal*, not validated improved model or transfer.
3. Otherwise: `V34_FIXED_LOCAL_CREDIT_ABLATION_NO_RESCUE__NO_SCIENCE`. Regardless of label, report all per-family fast ranks, regret, observed local credit and collateral spillover and conventional RLS. Do not reassign the label afterward.

No source weights copied into target, no global teacher, no new native learned identity or fitness criteria, no threshold tuning, no original-world first-use, no claims of native scientific acceptance, no merge, no changes to FORGE/CKB-plane/controller, no accepted model/checkpoint promotion, G29/proxy waiver or deployment. This gate is a **forensic synthetic diagnostic**, not autonomous self-improvement.
