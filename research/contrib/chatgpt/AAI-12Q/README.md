# AAI-12Q — native-style causal *effect invariants*, first source-only candidate

AAI-12Q is an independently preregistered **tokenless**, intervention-sensitive factorized causal-representation research candidate built on already qualified [AAI-12P draft #1074](https://github.com/spoonman136668-ai/Yggdrasil/pull/1074) exact SHA `abd374e7dc433981df991e103d8ebdff0b5eb093`. Original main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` and benchmark/controls remain untouched. **Preregistration commit before model implementation:** `8fd3fab547db14b997345f4d6dbc0aaaaf831e1a`.

### Distinct mechanism, same actual evidence

The baseline best conventional `causal_structure_recent8` uses the same eight most recent PUBLIC x/mediator observations and performs a deterministic per-output MAP search over the complete AAI-12P causal rule grammar (XOR/AND/OR, context switches, inhibitory and compensating DAGs). It achieves 2.673541667 actual mean reward and 43/97 oracle-attainable exact goals over the original 192 unfamiliar-world mechanical episodes. The privileged perfect-law oracle mean is 3.342291667. These are source-only prior observations, not independent scientific transfer.

The new `interventional_invariant_recent8` learner receives **only the identical public records**. It represents the four causal mediators as a *composed causal program*. It identifies adjacent, genuine one-bit public do-transitions exclusively from publicly visible x/goal/action counters; for every candidate structural rule it compares its predicted **change versus no-change in a mediator after intervention** against the actually observed mediator change, in addition to ordinary pre/post pointwise prediction mismatch. Frozen selection score:

`pointwise_bit_errors + 2 * real_intervention_delta_bit_errors`

Tie-breaks original candidate rule index. Stage-wise selected rules are composed into the exact original smoothing/forecast mechanism; all models use the **same original two-action `controls.choose`** with actual feedback. It does **not** read the generating family, true equation, hidden law, oracle, imagined consequences or paid model. Cold checkpoint holds at most the eight last complete public rows, **not** inferred rule weights, private annotations or historical world IDs.

For exact capacity and access control, `pointwise_equal_public8` stores the same eight complete public records and uses the **same grammar and planner** but excludes the transition-effect penalty. Its predictions must match original `causal_structure_recent8` pointwise on all inputs. This makes any effect attributable to **causal do-response constraints**, rather than more memory, observations or a private simulator interface.

### Frozen one-shot DEV before actual model outcome

Source-only test: two original mechanical fixtures, four common fit laws with 64 actual public pre/post intervention observations per arm, 12 unfamiliar source worlds with four common do-trial pairs and 8 original evaluation contexts per world/fixture = **192 actual consequential cold episodes per arm**, plus 64 independently cold familiar evaluations. All arms can execute at most two own real do-actions with public feedback only. Compare original strongest conventional `causal_structure_recent8`, same-eight-public-row ablation and new invariant model, with the original [AAI-12P full eight-control qualification](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43661187182) as exact source comparator.

ALL **predeclared** initial gates:
- New actual mean terminal reward ≥**2.753541667** (+0.08 over best conventional 2.673541667).
- Attainable exact-goal successes ≥**48/97** (at least +0.05 over best conventional 43/97).
- New model mean reward ≥**+0.03** above the equal-eight-record pointwise ablation.
- Oracle regret on the **95 unreachable** goals ≤**0.55** (source strongest .52 +.03).
- Familiar training-law cold return ≥**2.515** (source best 2.545 −.03).

If any fail, freeze `DEV_NO_GO_NO_SCIENCE` without hyperparameter retuning, another source world seed, repeated full eight-control qualification or scientific first-use. If all pass, *then* rerun all eight fully trained methods with identical actions/observations, require ≤**2× fastest actual full training+challenge+episode conventional process time** on each OS, and require corrupted intervention-to-consequence association negative not to outperform intact. Passing only the frozen mechanical screen still cannot qualify true learning, cold retention under interference or independent transfer without a separately authorized frozen science cohort.

### Authority and reproducibility

This is a source-only *research prototype*, not a modification to the native Yggdrasil model, a new research loop, a merge or autonomous deployment. Original AAI-11 negatives remain immutable; no continued tuning of previous eight-row posterior/window/value-of-information mechanisms. All source and qualification receipts stay in GitHub draft PR. Original main, FORGE, Wingless, Hybrid, owner/runners/controllers/queues/schedulers, paid APIs and user Library are untouched. `--primary` intentionally disarmed, no scientific seeds/worlds first used.

Full mandatory final immutable-source native regression on Ubuntu24.04 and Windows2022, original 54 native and new 10 focused tests each, G29 generated-only code atlas, source/prereg-before-model custody, negative outcome and whole-process cost disposition are required to close engineering.
