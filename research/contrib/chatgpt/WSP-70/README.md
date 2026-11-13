# WSP-70 — Direct neural weight imprinting of reusable action-conditioned factors

## Custody and prospective hypothesis
- Frozen preimplementation hypothesis and controls: `prereg.json`, first commit `1fe7762b208ecd01300acf9819c6d11cfa76ef0e`. The frozen source, thresholds and seeds are never tuned after observing outputs.
- Parent [WSP69 draft PR #962](https://github.com/spoonman136668-ai/Yggdrasil/pull/962) exact SHA `3e16a34b888564e1ba316f3e5330c3851e69360e`. The earlier WSP69 failure is retained: 279/768 correct confident, just 6/307 unseen, 26 confidently wrong, and the equally sized random-prototype control reached 261/768; fully converged end-to-end MLP reached 446/768 confident correct. WSP69's mandatory full regression was still in progress when WSP70 branched.
- The new falsifiable question: can **learned selection of reusable sensor interactions**, encoded directly as executable hidden ReLU weights, predict physical consequences on never-experienced state/action contexts beyond equal-width randomly selected interactions and preserve existing knowledge?

## Learning substrate — directly written neural weights, no gradient
- Eight public binary neural inputs encode four visible sensor states and four action-channel indicators. Begin with identical fixed 32 source-independent ReLU neurons and raw skip connections, seeded `68182026`.
- Predefine 224 candidate action-conditioned ReLU interactions representing **signed two- or three-literal sensor conjunctions gated by a public action**. Each eligible candidate neuron is activated on at least one physically charged training input.
- At 48 actions and 96 actions, score candidates solely from the four-output residuals of actual charged input/action/consequence observations and write up to **12** top-ranked neurons per milestone. The resulting neuron weight vectors and biases are genuine neural matrices, not a symbolic rule table that executes inference.
- Each charged action updates the neural readout by rank-one recursive ridge numerical edits (λ=0.5). On hidden-layer growth, reprogram the neural output/covariance from previously charged public memories; never call the private physics source to construct neuron weights.
- Cold inference requires only numeric hidden matrices, biases, readout and posterior covariance. A canonical SHA256 snapshot contains **no charged ledger, rule names or hidden source**; restores must reproduce exact predictions, and tampered hashes must fail.
- **Important limitation:** the candidate grammar is *preprogrammed signed conjunctions*, not freely discovered representations. Selection is residual-guided but the structural vocabulary has been supplied. Success would only establish usefulness of selecting reusable neural factors inside that restricted grammar.

## Frozen source and adversarial controls
- Twelve new SELFTEST-only worlds 4401–4412, four each XOR/parity, three-way conjunction, and mixed negated/coupled effects, with shuffled hidden sensor/action roles and a fresh generator salt. Additional two worlds 4413–4414 use four-sensor parity as an explicitly declared **nearby out-of-basis negative**. Parity may in principle be represented by combinations of lower-degree ReLUs, so these worlds are not a mathematical proof of being outside the complete dictionary span.
- One physically continuous, no-reset, no-teleport, 96-action sequential source experience stream per world; Stage A after 48. One source-blind random action selector; candidate and all controls receive the **identical charged tuples**.
- **Equal-width random factor control:** independently sample 12 + 12 activated candidate ReLU factors from the SAME 224-member source-blind action-interaction dictionary without inspecting consequence labels or fitting residuals. Same 32 initial neurons, numerical ridge update, confidence thresholds, action data and compute accounting.
- Independent fixed-32-neuron ridge readout-only control, exact observation lookup, separately implemented depth-4 decision tree, zero-readout ablation and cold weight tamper control.
- Independently fully trained 8→32→4 conventional neural MLP control uses all same 96 charged observations, 3 Adam initializations and up to 6,000 parameter-gradient updates per initialization. Only call its baseline qualified when ≥95% exact training accuracy; report training-side score and new-source physical predictions regardless. A nonconverged conventional control is NOT evidence for weight-edit superiority.

## Primary evaluation, frozen without post-result tuning
- 12 × 16 physical source states × 4 actions = **768** evaluator-only physical outcomes, separated into genuinely UNOBSERVED state/action pairs versus contexts in the training stream. Also 12 × 32 = **384** two-action compositions from evaluator-private heldout labels. Two extra negative worlds contribute 128 physical audit outcomes.
- `SELFTEST_SIGNAL` requires **all**: ≥25 unseen confident correct; ≥12 more unseen than equal-width random factors; ≥300/768 confident correct; ≥25 more all-domain correct than random; ≤20 confidently wrong; ≥100/384 correct confident two-action compositions; ≥85% Stage A retained confident-correct outcomes after further learning; new hidden/readout weights in ≥10 worlds; 12/12 cold restore and tamper checks; ≤3× whole source-blind training and evaluation CPU of random-width control; and ≤6 confidently wrong physical outcomes across the two four-way negative worlds.
- Any threshold missed => `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`. No changing the confidence margin, prior grammar, source seeds, rubric, comparator, or curriculum after the experiment. Forced predictions and abstentions must be reported, alongside all model baselines even when stronger.
- Report charged action and source SHA256, independently heldout composition SHA256, selected-factor receipts, numeric snapshot hashes, learned neuron/parameter counts, per-world training and inference CPU, reference MLP convergence and CPU, knowledge retention, false confidence and out-of-family negative scores.

## What success would NOT establish
A positive synthetic SELFTEST is not proof of a new general representation grammar, genuine out-of-domain transfer, language learning, autonomous scientific discovery, general intelligence, or independent `SCIENTIFIC_PASS`. End-to-end fully trained neural models and the random same-capacity factors remain the main comparators. The known binary sensor/action encoding and small selected-conjunction grammar are strong experimental priors.

## Reproduction
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-70 -p 'test_*.py' -v
```

Exact-SHA Linux/Windows focused tests, source-pinned generated-only G29 atlas, and the full inherited two-platform regression are separate engineering requirements. Isolated SELFTEST only; no protected DEV/PRIMARY first-use, merges, official FORGE/Yggdrasil autonomous-loop mutation, controller/runner changes, paid APIs, scheduled tasks or deployment.

## Separate future idea: consolidation (not part of WSP-70)
The user supplied arXiv:2606.03979 on knowledge consolidation and dreaming. It provides a prospective motivation to evaluate a fast mutable parameter store and a cold-retained long-term parameter store with rehearsal/interference controls. **The paper does not change this frozen WSP-70 method or claim; such consolidation requires its own preregistered experiment and matched baselines.**