# Mass P0F-C1C — matched-capacity history-availability causal ablation

**This frozen protocol is the FIRST modification**, stacked on the unchanged P0F-C1B original-source engineering candidate `2add84058d5c5466562a6a6c00e99ac4d90389b8`, original code `research/p0fc1b/full_public_controls.py` and prior P0F-C1/C1B FIT/SELECT and publicly disclosed DEV receipts. **Never evaluate, open, or retrain on the old P0F-C1B DEV seeds (3203…3301) or any protected H1/H2.** This is a follow-up diagnostic on lawful already-public FIT/SELECT roles, not a newly independent source-family test, native cognition or scientific first use. The two original author sources (Farama MiniGrid DoorKey8 `7f5853792ea7f04f75614661006d87fcf949f26d`, DeepMind Pycolab Apprehend `6504c8065dd5322438f23a2a9026649904f3322a`) are unchanged.

## Discriminating hypothesis

The original P0F-C1B fully trained history-input model lost on both sources, but differed in width from the current-only model and its history loss was worse **already on TRAIN and train-only SELECT** in Pycolab, whereas in MiniGrid it was lower on TRAIN but worse on SELECT. Therefore directly control architecture/capacity: **same history-aware input dimensionality, same 32 hidden units, same optimizer seed/learning rate, FIT interactions, output vocabulary, training epochs, public frames, losses and parameters** for two arms:

1. `history_visible`: legitimate current public input/action and two previous public frames/actions (same unchanged original C1B history features).
2. `history_masked`: identically sized history-input vector and same 32-unit neural network; **both previous input/action blocks are deterministically set to zero for FIT and SELECT**, leaving exactly the same lawful current public input/action. Same update budget and weight count, no capacity advantage to the history-visible arm.

Freeze selection hyperparameters **from the previously documented TRAIN/SELECT-only chosen P0F-C1B history learner**, not DEV: Pycolab `lr=0.02, init_seed=17`; MiniGrid `lr=0.02, init_seed=31`. Both arms use 24 epochs, batch 64, same ordering and Adam/L2 as frozen C1B. Exactly the prior 24 public FIT resets and 6 disjoint public train-only SELECT resets per original source; source-native legal random action stream unchanged. No new FIT/SELECT seed role discovery or selection variants. Evaluation on FIT and SELECT only, no DEV input sampling, no model checkpoint promotion.

## Measurements and stop rule

For each source report true original per-reset-cluster source action/outcome SHA and counts; both model FIT and held-out **train-only SELECT** log losses on complete next-public frames; paired 6-cluster selection differences `masked_loss − visible_loss`, source-native FILT+SELECT event count, both learned checkpoint identities, parameter counts, checkpoint bytes, train/inference CPU and whole-process peak RSS. Compute paired bootstrap with 1000 preregistered resamples seed 2901 at reset-cluster level. Avoid pseudoreplication. Validate identical original source FIT/SELECT target bytes and equal source custody across Linux and Windows.

- If history-visible improves FIT loss but loses to history-masked on SELECT, classify `HISTORY_EXTRA_FEATURES_OVERFIT_OR_GENERALIZE_POORLY` for the present data/capacity; that result does not identify the ultimate cause, nor show all recurrent memory fails.
- If history-visible loses on FIT and SELECT, classify `HISTORY_INPUT_NOT_EFFECTIVELY_FITTED_UNDER_FIXED_BUDGET`; do not infer training-data insufficiency uniquely.
- If history-visible wins on BOTH with positive lower 95% paired selection bootstrap, classify `TRAIN_SELECTION_HISTORY_SIGNAL_WITH_MATCHED_CAPACITY`, still not prospective heldout or native advancement.
- Otherwise classify `MATCHED_CAPACITY_HISTORY_BENEFIT_INCONCLUSIVE`. **No retuning after viewing SELECT**; report losses and all negatives regardless of winner.

## Boundaries

Three additive files only: this prereg, original-source train/SELECT-only scorer and source-free focused tests, plus one separate GitHub-hosted dual-OS workflow (four total paths). Existing P0F-C1B source, model class, seed roles, control, G29, original scientific negatives and 12 disclosed DEV cohorts remain immutable. No FORGE/F139/FSA/Optimizer/L9/CKB-plane repository or runner interaction, controller/queue/scheduler mutation, protected first-use, merge, paid API, new model capacity, hidden source/oracle fields, synthetic substitute environment, or external scientific claim. The workflow is filtered to the branch/paths and uses GitHub-hosted runners with read-only contents. One bounded fit/selection diagnostic, archive all originals; G29 separate integration may remain red.
