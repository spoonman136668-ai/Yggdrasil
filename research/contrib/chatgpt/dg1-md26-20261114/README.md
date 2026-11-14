# DG1-MD26 — paid-action causal site identifiability

**Disposition: TOY NO-GO; no registered first use; no native model change.** This is a separate, preregistered Yggdrasil external-research contribution stacked on sealed MD25 PR #1016. The original preregistration was committed at `4c4d34f305278fde8132a7be35ecba1ba9baee0d` **before** the experiment implementation and outcome.

## Falsifiable question

Can learned, physically observed pickup-clear/drop-occupies-cell effects select a **different paid physical drop-site action** and save steps in a previously unseen MiniGrid-BlockedUnlockPickup layout compared with an equally informed, same-navigator, right-first nonlearning control? We specifically forbid credit for internal counters alone, improvements from the shared scripted navigator, hidden room/grid data, mission strings, and unconstrained simulations.

The pre-registered toy cohorts are disjoint: DoorKey and UnlockPickup training on seeds 41,43,47,53,59,61; BlockedUnlockPickup evaluation on seeds 67,71,73,79,83,89. Official registered seed cohorts were separately frozen and **never used**. The inherited navigator is held constant for both candidate and blind control; learning can affect only the hypothetical occupancy used in a bounded BFS decision at a truly free two-site choice.

## Actual evidence

Original exact-source toy qualification: [GitHub Actions #43585625297](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43585625297), Ubuntu and Windows five MD26 tests PASS each, identical frozen toy metric output. The teacher completed 6/6 DoorKey and 6/6 UnlockPickup goals using 265 actual physical training actions; shared memory observed 18 pickup-clear and six drop-place effects. Candidate and strong blind achieved exactly 6/6 unfamiliar task goals, **191 real actions each**, with **0/6 distinct paired paid-action trace hashes**, **zero strict paired step wins**, and **0.0 mean action savings**. Prior MD25 causal site had identical 6/6, 191 steps. Permuted, fully trained tabular Q and fully trained recurrent imitation earned no unfamiliar goals.

The controlled constructed unit example demonstrated that a learned occupancy effect *can* select an actual left turn while blind selects right. This is necessary code correctness, **not** proof of real physical transfer; the independent heldout cohort did not expose a discriminating, useful site choice. Four of ten frozen toy conditions failed (actual learned decisive turn, paid action divergence, step wins, step gain). Classification is **TOY_NO_GO_NO_REGISTERED_FIRST_USE**.

## Engineering, science, and deployment

- **Engineering:** Exact-source toy and full inherited regression/G29 qualification must be separately confirmed on final derived atlas SHA. Do not call the whole repository green: unrelated legacy CKB proxy fanout has existing failures.
- **Science:** The causal intervention hypothesis fails the preregistered toy gating and cannot be promoted. Scientific first use was never started. Incremental mechanism advantage is **NOT demonstrated**; even though the goal-reaching scaffold works, this is not general reasoning or native Yggdrasil learning.
- **Deployment:** None. Main, accepted refs, owner controller, research loop and previous MD23/MD24/MD25 results remain unchanged. Retain this negative without postresult tuning.

## Next meaningful experiment

Do **not** keep selecting nearby MiniGrid layouts until one shows a positive. A useful successor must introduce a genuinely action-dependent environmental consequence (e.g., uncertain, costed interventions in a non-scripted dynamic environment), measure counterfactual action value against a strong equally informed model-free and hand-coded control, preserve cold retention and unfamiliar transfer, and freeze all protocols *before* primary evaluation. Keep any new task external and fully auditable.
