# MG93-AN — leave-one-episode-out public-history predictive sufficiency

Classification: RETROSPECTIVE CROSS-EPISODE PREDICTIVE SCREEN, NOT CAUSAL.

## Source and exact execution

- Original workflow: `41047254253`
- Immutable artifact: `12972852607`
- ZIP SHA-256: `9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a`
- Heldout JSON SHA-256: `0cdb155ce150717c3a678f6c536a81f5f4203dd96acafee459b2fdc1d2a36427`
- Script commit: `640d5324a08a7287aba43df8a01c0fdc426ae1ba`
- Script Git blob: `37151f3d352f397775af4cf05b7dcc8c0c2d4bfa`
- Script raw SHA-256: `0692c083c4c376e041b243cd2c7ac80f0644fb43c44d7db98526824dad228587`
- Result JSON SHA-256: `a434fb78911575a87693b9cf10c37049b32a4b7e7377f744404abf0e6b1b2ba7`

The local executed script's Git object SHA-1 matched the committed source blob exactly. The original ZIP and heldout JSON hashes were checked before execution. No original environment reset or step occurred.

## Method

For each policy role and task family, fit an exact-key table on two of the three held-out episode ledgers and predict the third episode's returned successor digest. Rotate through all three episodes (leave-one-episode-out). The table key is evaluated at four granularities:
1. Current public before-digest + action.
2. Plus previous selected action.
3. Plus previous public before-digest and action (the previous public transition context).
4. Plus the previous two selected actions.

A prediction is counted correct only when its exact key was observed in training and maps unambiguously to one successor digest. Report both coverage and conditional accuracy; abstentions are not silently counted as correct.

## Results — MG92 native feedback

| Context key | Covered decisions | Coverage of 3,906 | Correct | Correct / all decisions | Accuracy when covered |
|---|---:|---:|---:|---:|---:|
| Public state + action | 357 | 9.14% | 66 | 1.69% | 18.49% |
| Plus previous action | 134 | 3.43% | 66 | 1.69% | 49.25% |
| Plus previous public transition | 66 | 1.69% | 0 | 0% | 0% |
| Plus previous two actions | 132 | 3.38% | 66 | 1.69% | 50.00% |

The exact-history variants improve conditional accuracy only by abstaining on far more decisions. They do not improve the absolute number of correct held-out predictions. The previous-transition key is particularly poor: it covers 66 decisions and predicts none correctly.

## Other policy-role controls

- MG86 hand-coded teacher: public-state/action 26 covered, 18 correct; plus previous action 24 covered, 18 correct; previous-transition 14 covered, 8 correct; two previous actions 22 covered, 16 correct.
- MG91 frozen native prototypes: only 2 covered under the first two keys and zero correct; no coverage with richer keys.
- MG91 independent linear control: zero exact-key coverage under all four contexts.

These roles have different selected trajectories; they are diagnostic comparators, not matched randomized controls.

## Decision

**Negative for exact-key history augmentation.** A larger lookup key is not a learned belief state. It increases specificity and causes abstention; no prospective decision benefit follows from conditional accuracy on this tiny covered subset.

This does not falsify every learned compact belief-state mechanism. The more defensible future hypothesis is a bounded predictive belief that updates from actual prediction residuals and contradictions, retaining only information that changes subsequent forecasts or actions. It must be compared prospectively against memory-off, capacity-matched recurrent, and Bayesian/model-based controls, with real task reward, cold-restart retention and unfamiliar transfer as primary outcomes.

Three seeds per role/family and the policy-selected observational traces are insufficient for causal or generalization claims. Public observation digests may alias latent pose/inventory. There are no unselected counterfactual outcomes or randomized memory interventions. No original-world first-use or cohort admission is authorized; FSA-04 remains an independent blocker.

## Files

- `history_cross_episode_cv.py`: exact executable.
- `history_cross_episode_cv_receipt.json`: machine-readable summary.
- This file: interpretation and limitations.

No model, accepted source, protected cohort, policy, controller, queue or production runtime was modified.
