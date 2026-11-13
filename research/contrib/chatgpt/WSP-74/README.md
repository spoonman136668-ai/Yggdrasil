# WSP-74 — Repair neural representations through paid causal interventions

## Prospective scientific custody

The frozen experiment specification was committed FIRST as `prereg.json` at **`650fc1a703f95a264e0faeda82280ada0433eea2`**, before generating the fresh physical world, intervention learner, conventional control and outcomes. No postresult source, mechanism, threshold or family/seed retuning is allowed. Parent [WSP73 draft PR #970](https://github.com/spoonman136668-ai/Yggdrasil/pull/970), exact SHA `e822d88ee1a3b73a06924fab5aae88c2e8573e64`, remains scientifically NEGATIVE, isolated and unmerged.

**Motivating failure:** WSP73's postwrite confidence gate produced 390/768 confident-correct and 7 confidently wrong, but at identical answer coverage numerical-confidence ranking yielded 388 correct and 9 wrong. The current neural representations still lack accurate causal effects. Confidence filters alone will not repair wrong physics.

## New frozen hypothesis

An information-seeking policy can select **actual charged physical actions** based on disagreement between two source-blind learned neural models, then use the real action consequences to **directly modify the existing hidden ReLU input weights**, without gradients, to improve new states and preserve old capabilities. We test action *selection* and structural weight *repair* independently, with same-ledger controls.

## Source and physical cost

- Fresh SELFTEST-only 16 source-private role-shuffled four-sensor worlds, seeds `4801–4816`: four **four-way XOR**, four **majority-of-three threshold**, four **coupled multi-effect Boolean**, and four **nested Boolean negative controls**. The first three are newly varied from WSP73's earlier primary source family; all remain narrow fixed four-bit synthetic worlds, not open-world AGI.
- For EACH seed, simulate **TWO independent but source-identical physical world copies**, each beginning from its initial all-zero visible state and each independently charging **144 no-reset actions**. The first 96 actions in both copies are the **identical action sequence and identical public consequences**, but are *charged twice*. The last 48 physical actions differ according to intervention policy. There are exactly **16×2×144 = 4,608 charged physical actions** across both experimental arms. No reset/teleport inside either stream or arbitrary physical source query during training.
- A shared 96-action Stage-A public experience stream independently trains two unmodified WSP70 neural teacher policies: **residual-selected** and **random-selected** action-gated 2/3-sensor ReLU neurons, with their original 48/96 true hidden-neuron growth and numerical ridge-readout editing. Both weights freeze before the last 48 actions.
- The **active policy** chooses each real B action by maximizing Hamming disagreement between teachers' **forced** four-bit physical predictions at the current **real** visible state. The tie-break is frozen SHA256 of seed/step/action. The comparator chooses the next physical action by preseeded uniform random selection. Both are source-blind and take exactly 48 paid actions, but gather **different** actual observations. Do not call action matching equal-information comparison.

## Real numerical representation repair

- After 48 paid B consequences, a stage-A source-blind network has its **existing hidden ReLU weights directly edited**, with no new neurons and no symbolic rule interpreter. Restrict to up to **four** individual sensor input-weight coordinates of its grown hidden neurons, with each coefficient changed by exactly **+0.5 or −0.5**.
- Candidate select top eight previously grown neurons by their precommitted activation-weighted squared prediction residual on **only the charged B observations**, and consider ±0.5 moves along their four public sensor-coordinate weights. The objective is charged **A+B** four-output squared prediction error, B rows weighted twice, using the original numerical output readout and bounded discrete **finite-difference** search. No gradients or hidden source physics, no heldout oracle and no free new physical facts. A move must improve loss by more than `1e−9`; otherwise no edit. Never mutate the same coordinate twice.
- After all moves (including zero if no useful mutation exists), reset the numeric readout/covariance and reprogram it through rank-one recursive ridge edits using exactly the **144 charged public A+B observations**, `lambda=0.5`. Cold inference consumes only executable numerical hidden/readout matrices and covariance, not a ledger or symbolic table. Note that finite-difference loss search **is still optimization**, though it does not use backpropagation.

## Independent causal controls

- **Same active A+B physical experience, readout-only refit:** same frozen Stage-A features and readout update algorithm, with ZERO hidden edits. Isolates representation repair.
- **Same active A+B experience, randomly edited hidden numeric weights:** exactly four independently seeded randomly selected sensor-coordinate ±0.5 changes to originally grown units, then identical readout refit. Same neural width and edit count; random does not use physical label error to choose edits.
- **Random-action exploration plus the same full coordinate-repair algorithm:** same 144 paid physical actions under a distinct no-reset trajectory. Isolates policy value while acknowledging different actual information.
- Exact public experience lookup, independent depth-four decision tree, source-blind erased readout/cold snapshot tamper negative controls.
- An **independently implemented, fully trainable** 8→32-ReLU→4-sigmoid MLP using the identical **144 charged active-policy A+B experiences**, 3 separate seeded restarts and up to 6,000 Adam/backprop updates per restart, requiring >=95% charged training exact accuracy to be labeled converged. Report heldout forced/confident physical predictions and training compute; if underconverged, never claim direct-weight superiority. It is a conventional gradient control, not part of candidate learning.

## Heldout and frozen gates

After all numeric weights are frozen, each of the 16 worlds supplies **64 evaluator-only input/action physical truths**, plus **32 two-action composed outcomes**. The primary 12 worlds contribute **768 physical and 384 composed tasks**; four nested negative worlds contribute **256 additional physical truths**. Score each model's confident-correct, confidently wrong, abstained, and **genuinely never charged** input/action cases against the physical evidence seen by its own arm. Stage-A retention is scored evaluator-only: previously correct/confident Stage-A facts must remain correct/confident after action and weight editing.

The frozen `SELFTEST_SIGNAL` requires ALL: ≥320/768 confident correct, **+25** over same-ledger readout-only, **+20** over same-ledger random hidden edits, **+20** over equal-paid random-policy plus identical repair, ≥30 correct genuinely never paid physical contexts, ≤24 confidently wrong primary, ≥80% retained Stage-A true/confident knowledge, ≥110/384 correct confident two-action compositions, ≤16 confidently wrong across four nested negative worlds, genuinely changed hidden neural coefficients in ≥10 primary worlds, all 16 cold numerical snapshot/tamper parity, and ≤8× measured candidate whole-process CPU versus same-ledger refit-only. Any miss => `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`; no source/seed/weight-policy/threshold adjustments after outcomes.

Each run emits exact source and two-action SHA256 receipts, both action streams and charge counts/hashes, numerical Stage-A and repaired model snapshots, every hidden coordinate changed, training-loss diagnostics, action-policy time, full learner/MLP CPU, per-family metrics, retention, unseen outcomes, and frozen scientific gate booleans. **Engineering PASS and scientific success are separate.**

## Limitations and boundaries

Real action outcomes supervise the weight-search objective, so this is **direct numerical programming from experience**, not programming a complete mind without observations. The handcoded 2/3-literal WSP70 hidden feature grammar, four binary sensors and tiny worlds are strong priors; isolated SELFTEST gains would not demonstrate AGI, language, arbitrary representation discovery or independent `SCIENTIFIC_PASS`. More complete independent neural controls and real non-binary worlds remain required before any useful scientific acceptance.

**Reproduce:** `python -m unittest discover -s research/contrib/chatgpt/WSP-74 -p 'test_*.py' -v`.

**Qualification:** source-pinned exact candidate focused Ubuntu+Windows, generated-only three-file G29 source atlas, and mandatory full inherited regression across both operating systems. Draft PR stays unmerged. No DEV/PRIMARY protected first use, official FORGE/Yggdrasil owner-loop integration, merge, deployment, paid APIs, scheduled tasks, controllers or runner changes.