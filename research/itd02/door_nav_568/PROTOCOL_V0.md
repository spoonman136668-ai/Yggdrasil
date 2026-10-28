# ITD-02 DoorKey learned navigation — protocol v0 (DESIGN ONLY)

Issue: #568. Status: NOT ADMITTED; NO ORIGINAL SOURCE EXECUTION. This is a new hypothesis, not a retune of C31/C32/C37 or reuse of R12 DEV.

## Hypothesis
After the original DoorKey door opens, a native persistent action-conditioned public belief/memory mechanism can learn to select legal multi-step actions that improve authentic goal completion over the existing R12+scripted collector. Novelty requires beating equally trained recurrent, episodic-map and model-based/Bayesian navigators, not merely the scripted collector. No advantage on a tie.

## Information rights
Only original source-public observation, chosen legal action, observed next public observation, reward, done and time. No hidden grid/map, agent absolute position from source internals, private reward law, seed/task identity, goal coordinates or evaluator feedback. The policy must own post-door actions; no handcoded stage-goal choice or fixed front-goal override. Record exact native decision provenance.

## Before any source episode
- Independent reviewer must verify upstream original source commit and blobs, license, candidate integration surface, valid-action contract and preexisting original cohort/seed ledger. Freeze disjoint new FIT, model-selection and DEV source reset clusters with cryptographic manifest and no prior-used collision. Existing R12 12 FIT source episodes and C31/C32/C37 DEV cannot be reused as prospective evidence.
- Freeze all policy classes, training schedules, initialization seeds, exploration/action budgets, observation preprocessing, loss, hyperparameters, checkpoint formats, stop criteria, paired episode sampling and statistical tests. No changes after first source FIT.
- Verify native learned-state implementation can actually update from returned source actions and consequences and persist across a distinct OS process. Source-free tests must establish action legality and no privileged access. If not, FAIL CLOSED before episodes.

## Arms and falsification
1. Native learned public action-consequence belief plus endogenous goal-progress planner.
2. Same native learner with persistent state erased while preserving valid action rights.
3. Same native learner with FIT consequence-to-action association shuffled; legal action schedule unchanged.
4. Same native belief with learned planning disabled; still legal.
5. Fully FIT-trained recurrent navigator, equal public information and source-action budget.
6. Fully FIT-trained episodic map/planner, equal rights and budget.
7. Fully FIT-trained model-based/Bayesian navigator, equal rights and budget.
8. Original fixed collector for engineering reference only.

## Measurements
Primary: per-episode genuine original goal completion and returned cumulative reward on untouched DEV, cluster-paired uncertainty intervals and exact original action/observation/reward traces. Secondary: legal action fraction, native-owned post-door decision count, key/door success, visited public-hash repeats (not claimed latent-state equality), opposite-turn cycles, trajectory length, separate-PID cold checkpoint equality and resumed reward, model-state bytes, total process-tree CPU/RSS, source steps, disk and wire. Each arm must have equal training/exploration rights; no private oracle in learner inputs.

## Stop and custody
No native-owned post-door decisions, invalid action ablation, unverifiable source or checkpoint, seed collision, weak conventional training, or non-reproducible cross-OS identity => NO-GO. Native ties or loses to strongest equal-information trained conventional => no native architectural advantage. Preserve all negatives. Public source development and protected first-use require their existing independent authority; FORGE FSA #83 currently not an admission. Draft/unmerged, no controller or main changes, no paid API. Focused qualification first; only one final full Windows/Linux/G29 regression if independently eligible.
