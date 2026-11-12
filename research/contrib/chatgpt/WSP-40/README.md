# WSP-40 — active discovery of nonlinear structure

Preregistered isolated contributor study, stacked on WSP-39 #930. Preregistration-only commit: `3e8b06f7eddcfe96eb59f64dc9f6c022e1be1723`.

This asks which state interventions reveal an unknown nonlinear action rule, then writes the selected support into binary numerical connection weights and a conjunction threshold. It is a direct-written numerical model with an external Python hypothesis search. Rotation, conjunction semantics, and the candidate family are supplied. This is **not** free invention of cognitive primitives or a complete general intelligence.

One broad PRIMARY: dimensions 16, 8, 4; pair, triple, hidden quartic and XOR-pair mechanisms; budgets 12 and 4 interventions per action; two actions; four disjoint seeds. Total 96 world/budget episodes, 6,144 one-step predictions, 2,304 composed sequences and 384 goal plans per arm. The active candidate set is degree <=3, up to 696 hypotheses per action at width16. This structural-search ceiling is a different resource dimension from WSP39's 1,024-bit affine runtime. Larger affine width is not evidence for scalable structure discovery.

Controls are random query selection, passive probes, independent set-based reconstruction from exactly the active transcript, fitted minimum-norm conventional monomial regression from exactly that transcript, and zero residual. The trained head uses a broader linear combination of the same degree<=3 feature vocabulary. It is not a neural baseline or capacity-matched nonlinear discovery algorithm. Training residuals and convergence are reported; a failed fit cannot support a superiority claim. Direct construction is expected to tie the strong identifier. Accuracy and whole-process time remain separate.

Evaluation states exclude all active training inputs, so active, strong and fitted controls are tested on unseen inputs. Random/passive controls may have observed some evaluated states; their seen counts are reported per episode. This potential advantage to those controls is explicit. Equal-budget comparisons are active4/random4 and active12/random12. The preregistered active12/random4 threshold is unequal-budget and cannot establish intervention efficiency by itself. All heldout misses count, including ambiguous, wrong or empty hypotheses. Evaluation labels never enter discovery or planning. A further real contradictory witness is used only after primary predictions; its cost and limited correction are separate.

Cold restore, deterministic replay, corruption rejection and isolation of a separately acquired world are verified. No changed protocol or post-result tuning. Quartic and XOR-pair failures are expected scientific boundaries, not infrastructure failures.

Reproduce from repo root:
```
python -m unittest discover -s research/contrib/chatgpt/WSP-40 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-40/qualify.py
python research/contrib/chatgpt/WSP-40/battery.py --cohort PRIMARY
```

PRIMARY runs on the established read-only hosted Windows/Linux workflow. DEV was explored locally (7 focused tests, 24 episodes) after protocol freeze; PRIMARY was not evaluated locally. Results belong in repository evidence and GitHub CI receipts. Draft only: no merge/main, official loop, protected first-use, private runner, controller, scheduler, paid API, integration, live actions or deployment.
