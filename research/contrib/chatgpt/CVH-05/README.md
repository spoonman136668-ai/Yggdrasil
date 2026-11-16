# CVH-05 — All-six-split robustness and off-policy identifiability of real public learning

**Research-only; retrospective previously-consumed FKP26 original MDP public actions; never original source first-use. DRAFT, no merge or owner deployment.**

## Why this gate is distinct from CVH04 and NKR19

CVH04 [PR #1164](https://github.com/spoonman136668-ai/Yggdrasil/pull/1164) established that the **unchanged CVH01** tokenless four-step earned-return memory could predict supported returns on 55/62 *historically consumed* held rows from genuine independent Causal-Gymnasium, modestly better than a training-only global prior. The strongest independently implemented exact symbolic conventional estimator made **identical predictions**, so scientific superiority and unfamiliar causal discovery remained unverified. NKR19 [#1161](https://github.com/spoonman136668-ai/Yggdrasil/pull/1161) independently analyzed **one-step** native Bayesian source-outcome probabilities on the **same consumed external source** and also tied a strong Bayesian model. Do not reimplement either learner or claim a second external original first-use.

**This separate gate asks whether CVH04's modest 5.1% gain survives *every possible* two-episode training/held split of the four actual source episodes, and whether those logged actions can identify the value of a *different action*.** It does not open any new original environment, change CVH01/CVH02/CVH03/CVH04, retune the original 5.1%, or claim a neural model is outperformed.

### Frozen provenance

- Exact qualified parent CVH04 `5836c5dcdb74a8a1a7c5c32097d02ee955a4b2c3`, tree `9ca402028f45c4ab1dcf8e276d02b0989df414db`. Frozen preregistration **FIRST** `75abed7e43f04d23cf54ae2ed34130c8a4c46a54`, before this sixfold code, tests or results.
- Original external source `CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf`, Apache-2.0, original real first use in FKP26 [#1158](https://github.com/spoonman136668-ai/Yggdrasil/pull/1158), GitHub run [#43930489602](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930489602), original public archive SHA256 `4c877a6df5685516cc7ba445b2b90c90afb3674537ab741fb67adb5453e5c9ef`. All 124 physical original `do` outcomes were already consumed in FKP26; **CVH05 performs zero additional source actions**. CVH04's derived public fixture verifies original per-episode SHA256 and full original public receipts.
- Original fixed-behavior public policy selects `action=(observed_before+chronological_index)%2`. This is **not a randomized evaluation**, and without additional interactions, the unchosen action's immediate reward and future consequences are **not identifiable**.

### Frozen sixfold retrospective falsification

Enumerate all **six** two-TRAIN-pair choices among source seeds `996100,996101,996102,996103`, in lexicographic order; the other two are historical held, **62 TRAIN + 62 held original public transitions** per fold, 372 total correlated held evaluations with **no new action**. This preserves the original CVH04 split as fold one, unchanged.

For each fold: fit the **unchanged original CVH01 EarnedReturnMemory** for 62 public records and freeze a SHA256 cold snapshot; independent exact conventional `batch_public_returns` fits **identical** action consequences and must match every supported CVH01 prediction. The learner only predicts within its two-observed-event-per-context threshold and abstains for unsupported addresses. Compare four-step actual earned returns `r0+.5r1+.25r2+.125r3` (truncated at world end) to the *TRAIN-only* global prior **on exactly the same supported held rows**; calculate all-row MSE with labeled global fallback separately, independent Bayesian shrinkage (two pseudocounts) and fitted four-cell (state, action) shrinkage baseline. All labels derived after freezing fold predictions; no original source private info ever used.

Preregistered **robustness PASS criterion**: at least 16 supported/62 in **every** fold; **at least five of six** folds positive native supported error reduction vs TRAIN-only global prior; pooled supported MSE reduction **>=.01**; worst fold >=**-.02**; and exact conventional parity, cold and cumulative numerical memory preservation on all six folds. If any fails, preserve `RETROSPECTIVE_SIXFOLD_DEVELOPMENT_ROBUSTNESS_NO_GO`. Even a PASS remains `scientific_pass=false` due tiny reused/nonblinded real source, four correlated episodes, exact strong-control tie and no original new policy action evaluations.

### Mathematical partial-identification negative control

For each of 124 unique logged episode/time histories, the unchosen binary action has **no observed reward**. Two hypothetical completions, assigning all such unobserved immediate rewards respectively **0** or **1**, match all 124 actual source outcomes and disagree on 124 unobserved rewards. These are *hypothetical data-only completions*, **not demonstrated alternative realizations of the Causal-Gymnasium SCM**. The test is a direct falsification of any assertion that the original fixed-policy tape alone identifies off-policy action reward or improved online causal control. Need genuinely new, owner-authorized and prospectively held interventions across unfamiliar environments to claim that.

### Qualification and boundaries

GitHub Actions branch-scoped source-safe development, full inherited exact-tree CVH01–CVH05+root regression and independent G29 both Ubuntu24.04/Windows2022. Generate only existing three derived `.ice/code-atlas.{html,ice,json}`; verify immutable final SHA/tree and canonical report-only rounded metrics identical between systems. No original CausalGym import/reset/do, protected source seeds, original first-use, historical 21.3M scan, scheduler/controller/runner, paid API, merged native main or accepted model activation. The independent Wingless, Hybrid, FORGE and Mind-Palace tracks remain untouched.

**Pass or fail, this experiment is a necessary retrospective robustness audit—not a substitute for a prospective science trial.**
