# ITD-01 R10 — Family-blind causal transfer preregistration

**Status:** PROSPECTIVE DESIGN ONLY / NO CODE / NO EXPERIMENT GENERATION / NOT ADMITTED.
**Repository:** `spoonman136668-ai/Yggdrasil`. **Frozen R10 parent:** R9 candidate `b60453d7a5100eea037dfb77b3660783139d11dd`. This must be the **first and only source change** on the R10 design branch; any later R10 implementation must keep this file's Git blob unchanged and prove it predates source generation.
**Authority:** The existing authenticated CKB-plane controller alone may authorize implementation dispatch, first-use reservations, experiments, qualification and promotion. A GitHub PR, its CI or this protocol grants none of those.

## 0. Retained predecessor evidence — do not rerun or tune

- R7 original native local-cell [draft #418](https://github.com/spoonman136668-ai/Yggdrasil/pull/418), source `f3cdabdb3420bb8604e41dda9903ae65eba008e7`: three frozen scientific NO-GOs, source results SHA-256 `5fef7ef0adf0d15283da090ffc4e81ec547e46105fa6ae34455dc83048f260ec`; inherited G29 Atlas fails ancestry qualification.
- R8 Mass Research [draft #420](https://github.com/spoonman136668-ai/Yggdrasil/pull/420): observational R7 public data cannot identify action effects absent an action-conditioned interface. Keep its negative.
- R9 native delayed public action learning [draft #421](https://github.com/spoonman136668-ai/Yggdrasil/pull/421) at parent above, [original two-OS run 39879697255](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/39879697255): A/B/C after FIT 1.0 accuracy but matched pairwise and episodic learners also 1.0; C zero-shot 43/96, 53/96, 46/96; 0 legal action changes attributable to neighbor messaging. Native checkpoint ~1,990–1,995 bytes; whole process RSS ~19–21 MB, not per-model normalized. Scientific family transfer and neighbor-benefit **NO-GO**. G29 Atlas separately fails. R9 source-free DEV cohorts 101/211/307 are CONSUMED and cannot be reopened for tuning.
- **No inference** of original H1/H2 or independent causal-transfer first use from the source-free results above.

## 1. Scientific question and rival hypotheses

**North Star stage:** experience -> learned representation -> persistent memory -> action-conditioned prediction/reasoning -> action -> unfamiliar-task transfer.

**H1 (transfer):** A family-blind, shared Yggdrasil learning state formed from two training causal environments enables lower-regret adaptation to independently unfamiliar causal structures using **the same 32 permitted public intervention episodes** as comparators. State must persist across a separately verified process restart and retain training-family skill after interference.

**H0:** Any apparent benefit can be matched or exceeded by equally informed trained recurrent, Bayesian, pairwise, episodic, or capacity-matched controls; or depends on prespecified family-specific lookup, task leakage, extra probes/resources, hardcoded graph rules, or test-source reuse. A failure to satisfy *any* prespecified scientific and integrity gate is a retained negative, not a reason to alter post-test thresholds.

**Competing mechanism variants, not mandatory additions:** local credit and consolidation with bounded neighbor messages; action-conditioned predictive state without messages; explicit causal hypothesis memory. An R10 algorithm is **not frozen or chosen by this prereg**. Implementations must be independently admitted, trained using FIT/VALID only, and frozen before any DEV/heldout consumption. Wingless remains independently implemented: no importing its model, learned weights or oracle.

## 2. Environment contract and identifiability gate

A separate independent Mass Research challenger must establish a signed, source-commit-bound **environment/interface contract before first use**:

- 4 Boolean observable sensors, 1 latent binary factor, action set `observe`, `probe_0`, `probe_1`, `commit_0`, `commit_1`. The public action, observation, terminal consequence and monotone event token are learner-visible; latent factors, graph topology, privileged causal labels and outcome law are evaluator-only.
- Public intervention consequences arrive after **at least two steps**, bound to exact source/event/action IDs. Reject premature, duplicated, reordered, wrong-family or forged feedback. Probe actions consume the same budget as decisions and have an explicitly logged reward/cost; no uncounted oracle queries.
- Sources must exhibit a learnable shared causal grammar but **different, independently documented non-isomorphic structural relations** between training and unfamiliar family graphs, not just new PRNG seeds, sensor names, label inversion or a prespecified A/B/C lookup bank. Permissible mechanisms can involve temporal mediation, competing causes, interventions and hidden-state persistence. A hidden family ID, graph shape or rule lookup must never be given as a predictor feature.
- **Before admission to a family**, an independent information-sufficiency challenger must provide an offline certificate from unconsumed source/logic that (i) at least two candidate hidden structural explanations are distinguishable by legal interventions within a 32-episode probe budget and (ii) meaningful policies outperform action-only chance when the relevant publicly identifiable information is used. If not, record `SOURCE_NOT_IDENTIFIABLE` and reject the family *before any learner FIT/DEV read*. Never repair identifiability by looking at protected evaluation answers.
- Freeze generator implementation, configuration, role-separated source SHA, birth/first-use ledger, allowed observation/action mask and environment checksum **before** FIT/VALID/DEV creation. The final family generator must be born independently of the model-authoring lane. A generator-law-aware Bayesian oracle may be a **privileged diagnostic only**, not an equally informed competitor.

## 3. Prospective budget and source roles (not yet instantiated)

Role-disjoint families `TRAIN_1` and `TRAIN_2`: 256 interactive FIT episodes each, then 64 FIT_VALID each. Model/epoch/hyperparameter selection uses only these FIT_VALID observations. All FIT experience including actions/rewards and exploration cost is identical in count and observability across candidates and baseline arms.

New `DEV_UNFAMILIAR` family: 32 public adaptation/probe episodes followed by 128 **read-only score** episodes with no training, feedback use, source-law queries or parameter changes. Distinct family `DEV_RETENTION`: 128 scored episodes of `TRAIN_1` **after** the unfamiliar experience. One evaluation lifecycle per prospective seed `401, 503, 607`. These seed values are fixed now but **no corresponding cohorts may be instantiated by this prereg or before independent admission**.

Two additional independently sourced, separately sealed and non-isomorphic `HELDOUT_U1`/`HELDOUT_U2` families: each has the same 32 adaptation + 128 score budget, plus its own after-transfer 128-episode training-family retention check. They remain unopened until complete model/config/hash freeze and separate first-use authorization **after** reporting DEV disposition (including a NO-GO). No tuning from DEV to heldout, even if DEV fails; do not consume heldout merely for a prettier story.

The fixed budgets above are **episodes, not wall-clock guarantees**. Register actual action, decision, reward and source roles in an append-only independent first-use ledger. Failed or interrupted runs consume their first-use reservation and are preserved, not simply replayed.

## 4. Information parity and mandatory baselines

All arms receive exactly the same public interface, legal actions, episode totals and train/valid split, and are allowed the same 32 public unfamiliar-family probes. At minimum independently fit:

1. Matched-capacity recurrent world model (action-conditioned recurrent state; non-privileged).
2. Learned pairwise/intervention-aware predictive-state or perceptron control.
3. Explicit episodic memory with identical public outcomes and legal probes.
4. Bayesian hypothesis updater **trained/inferred only from public evidence**, with no evaluator law, privileged graph family catalog or hidden labels.
5. No-state/current-only; erased-memory; same learner with shuffled source-family assignment (negative controls).
6. Native Yggdrasil no-message and shuffled-message-topology ablations with **action-preserving legality**.

Equalize and report total information access, exploration and optimization effort. Compare within matched budgets for parameter/state+optimizer+replay+cursor+RNG bytes, training updates, training/inference CPU, true child-process peak resident memory, checkpoint storage, message/event counts, bytes transmitted and disk/network I/O. The R9 process-inclusive Python RSS figure cannot be called per-model RSS. If no matched baseline exists or isolation fails, report `RESOURCE_PARITY_UNQUALIFIED`, not victory.

## 5. Primary decision rules frozen before first use

First require correctness and source integrity: all role boundaries, exact source identity, legally delayed feedback, deterministic replay, checkpoint error/tamper refusal, distinct child process cold restart and counter continuity, no hidden label/graph access and **zero hard false causal-transfer claims**.

If integrity passes, a **provisional DEV GO** requires, on *every* seed 401/503/607:
- Family-blind learner unfamiliar-family post-32-probe action accuracy **>= 0.70**, with no scorer training on the 128 score episodes.
- Mean score advantage across the three seeds **>= 0.10 absolute accuracy** over the strongest equally informed trained non-privileged comparator (picked per seed before inspection), with **positive** advantage on every seed.
- After unfamiliar-family experience, `TRAIN_1` retained accuracy decline **<= 0.05 absolute** from its frozen pretransfer validation result on every seed.
- Learned-state removal or legal action-history scrambling causes a **>= 0.05 absolute** mean impairment in unfamiliar-family score; otherwise memory/causal attribution NO-GO. Independently, neighbor messaging may be claimed helpful only if valid-action decisions change and mean success strictly improves over no-message; otherwise classify neighbor mechanism NO-GO even if transfer is positive.
- Full resource nonregression under a genuinely matched compute and memory comparison, counting all declared costs above. Missing cost evidence is `RESOURCE_UNQUALIFIED`.

Evaluation on sealed heldout after separately authorized first use uses the **same thresholds without further selection or retuning**, reported family-by-family and seed-by-seed. Success on DEV alone is **never** externally reproduced transfer. Failure on DEV retains a negative; do not revise this protocol or experiment family to turn a negative into a GO.

## 6. Engineering admission, isolation, and falsification

- This commit introduces **only this Markdown file**. No model, generator, tests, workflows, data, new controller, credentials, paid API, broker or production access. No workflow is triggered deliberately and no R10 sources are generated.
- Before actual R10 work, the controller must confirm current predecessor identities, read the immutable original R9 positive and negative evidence, authorize exact allowlisted new paths and secure independent source custody. Do not promote through inherited failing G29 or R7 tests: repair/source-qualify them without weakening ancestry or conflating NO-GO scientific outcomes with engineering errors.
- Prospective implementation qualification: frozen prereg-first ancestry; focused behavioral/fault/tamper tests; identical native seeds on Windows/Linux with matching non-timing digests; source-index fresh; one full regression + build; independent first-use witness for the challenger; no protected accepted-ref/first-use before authenticated permission. Retain all original and new negatives.
- A source-free emulator or authored candidate cannot assert actual independently sourced holdout transfer. If no independently sourced identifiable families or resource parity are available, terminate honestly as `R10_NO_EXECUTION_IDENTIFIABILITY_OR_RESOURCE_BLOCK`.

**Disposition at source birth:** `R10_PREREG_ONLY / FIRST_USE_NOT_PERFORMED / IMPLEMENTATION_NOT_STARTED / CKB_ADMISSION_NOT_OBSERVED / R9_NEGATIVES_PRESERVED`.
