# GKD-05 — GPT donor prior against authentic published intervention-condition measurements

**Research-only public development experiment.** Frozen source/preregistration FIRST: `aafab21d6b8997ffafd355de528c9eb1cd7dfa0a`. Baseline accepted Yggdrasil `main@5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; GKD-04 final PR head `bf66726249af7ce3b3c0fb60c54af5ab7fd80726`. This successor is isolated to this draft research PR; never modifies the native accepted Yggdrasil learner, controller, queue or weights.

## Why this experiment, and what it measures

GKD-01 through GKD-04 showed engineering feasibility for preparing and maintaining small structured GPT-donated numerical rules, but their **synthetic experiments tied strong exact symbolic controls**. GKD-05 tests whether a **GPT-authored two-parent graph prior** helps a conventional fitted 2-input model predict real measured proteins in **previously unseen experimental conditions**, compared with fully fitted conventional controls.

The source is the **public, already-published Sachs et al. (2005)** single-cell flow-cytometry data, in [Zenodo v2](https://zenodo.org/records/7681811) (curator: Mathematical Research Data Initiative, CC BY 4.0 by original authors' permission). Source identity `sachs.zip`, publicly advertised MD5 `d50ccd7f88bb3705bcf6eda3978bcc41` (archive SHA256 is captured independently after byte verification). Citation: Sachs et al., *Causal Protein-Signaling Networks Derived from Multiparameter Single-Cell Data*, *Science* (2005), DOI `10.1126/science.1105809`.

**Cohort honesty:** The curator explicitly marks **five intervention CSVs as *simulated***; they are entirely excluded. Only the nine published experimental-condition groups are eligible. The source also contains a graph file; the scorer never opens, trains on, or selects from that graph. Original source acquisition is a **public historical DEV** (not virgin independent discovery), and no new physical interventions or protected Yggdrasil #426 causal-world actions are performed.

**Frozen causal candidate (not accepted fact):** `Erk <- Raf,Mek`; `Akt <- PIP3,Erk`; `P38 <- PKC,Plcg`; `Jnk <- PKC,Plcg`. These are GPT-authored sparse prior guesses that may have been influenced by published literature/model pretraining, and the assistant viewed source high-level documentation before freezing them. **They are not evidence of novel causal discovery.**

For each target, observe the **other ten proteins measured *in the same cell*** and predict the target's concentration. FIT uses five original intervention groups, VALID uses two, and public DEV uses two different groups, as specified exactly in [prereg.json](prereg.json). All standardization, source feature selections and fitting occur on FIT only; hyperparameters and conventional arm winner are chosen on VALID only, while DEV is scored **once**.

**Task caveat:** The other ten simultaneously observed protein measurements can carry noncausal correlations and downstream effects. Even a positive holdout result here would be **cross-condition conditional prediction**, **NOT an intervention-effect estimator, DAG correctness, or action-consequence learning**.

## Controls and stop rule

Four fully fitted ridge families: the donated 2-parent mask, complete ten-protein linear ridge, quadratic ridge with 65 fit-only features, and FIT-correlation-selected top-2 parent ridge. A separately fitted **same-mask conventional ridge must tie the donor** exactly; a wrong-parent donor-shift sham and FIT-mean baseline are negative controls. All use the same FIT labels and public information. Alpha grid `[0.001,0.1,1,10,100,1000]`; VALID chooses alpha and strongest conventional arm.

The frozen `PUBLIC_DEV_SIGNAL` gate is intentionally demanding: at least 5% lower group-balanced normalized RMSE against the VALID-selected strongest conventional **and** donor-shift sham; at least 6/8 group/target comparisons nonregressing, none worse than +5%. Failures are archived; no tuning after seeing DEV. If exact source archive MD5/CSV schema/row minimum fails, classify **SOURCE_PACKAGING_NO_GO**, do not substitute a mirror or quietly rewrite the protocol.

Use `python research/contrib/chatgpt/GKD-05/admit.py --selftest` and `python research/contrib/chatgpt/GKD-05/score.py --selftest` for source-free checks on both platforms. The protected public-score step, when separately ready, runs only on a **single exact commit-subject-marked pull-request SHA** on GitHub-hosted Linux, after full regression. It downloads the bounded original public ZIP into memory and prints one immutable `GKD05_PUBLIC_ORIGINAL_DEV_RESULT` or an exact source admission blocker to the GitHub job logs. It must never automatically run on every later archive/atlas edit.

**No science/deployment overclaim:** no original virgin first-use, no real-time GPT calls, no independent scorer model weights, no native cumulative checkpoint, no certified causal transfer, no source-identity admission for arbitrary uploaded user data, no merge or deployment. Even a positive public DEV result is NOT `SCIENTIFIC_PASS`. Preserve source no-go and negatives.
