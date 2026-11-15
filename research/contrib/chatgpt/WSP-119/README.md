# WSP-119 — Internal microfeedback: does Yggdrasil learn what to investigate?

**Research-only synthetic calibration. No native admission, independent science, protected source or external data access.**

The previous experiments established that a larger foundation makes more predefined graph relationships inferable, but they did not demonstrate an internal process that **chooses experiments, compares expectations to observed consequences, and locally revises memory**.

This WSP-119 test directly operationalizes that hypothesis. We freeze a public background fact graph at **25%, 50%, 75% or 100%** visibility and give each learner the same opportunity to request **12 verified relationship examples** from a new, separate set of 24 synthetic worlds. The public source evaluator hides each world’s true three-hop relationship from the learner. Each learner must select its next subject **before** receiving that subject’s actual destination. A separate set of 24 held subjects is never available for requesting labels.

The candidate performs two kinds of **internal microfeedback**. First, it estimates uncertainty among its 216 possible three-hop laws and requests the unseen subject on which those hypotheses disagree most. Second, after the source reveals the true answer, it updates local integer **support and contradiction counters** on only the hypotheses whose required graph paths are visible. It does not treat its own guesses as verified facts.

At the same public graph coverage and the same number of real queries, we compare:

- **Direct active microfeedback:** bounded 216×2 int32 weights plus uncertainty-guided inquiry and local error updates.
- **Direct passive:** identical direct weights and one verified update per inquiry, but source-blind fixed-order questions.
- **Direct no update:** asks the same number of questions but never changes its learned relationship weights.
- **Independent symbolic active:** exact set-based law elimination and the same uncertainty-guided inquiry with the same source facts and answer budget.

The analysis measures the learned relationship type and truly held answer accuracy after **0, 1, 2, 3, 4, 6, 8 and 12** evidence requests, separately at four graph densities. It measures source-call counts, model error signals, cold weight restoration and 10,000-bootstrap paired per-world differences. Each arm has exactly the same legal 40 source candidates and 12 external answer calls; adaptive choices produce different observed examples, which is the intended intervention rather than a falsely claimed matched trajectory.

The frozen *development fixture* criterion demands that direct-active outperform direct-passive by ≥5 percentage points of held accuracy at **eight observations at both 75% and 100%** graph coverage, with the paired confidence interval lower bound above zero. This threshold was registered before running or seeing any WSP-119 source. Strong symbolic equality is an explicit finding of **no unique scientific advantage**; a negative is retained as a negative. A completely self-confirming feedback loop is prohibited because it would reinforce incorrect beliefs.

**Scientific boundary:** These are newly generated but purely synthetic public worlds. All 216 three-hop structures are **predefined**, not autonomously invented by the model. Even a positive result only demonstrates *sample efficiency of an internal feedback controller under known hypotheses*, not new relationship-type invention, AGI, lifelong memory, or a measured point in ordinary transformer training. Fully trained GRU/MLP, unknown-law families, real interventions, cold retention across distinct mechanisms, resource parity and owner-qualified independent first-use remain separate.

**Source custody:** WSP-119 public seeds 119000–119023 only. WSP-118 seeds 118000–118023 already consumed and never scored as WSP-119. Reserved 119800–119863, protected or real Wikidata data remain unopened. Native Yggdrasil accepted `main` remains unchanged.

Run source-safe tests:

```console
python -B -m unittest discover -s research/contrib/chatgpt/WSP-119 -p test_wsp119.py -v
python -B research/contrib/chatgpt/WSP-119/analyze.py
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

No new runner, scheduler, controller, paid API, native weight change or merge/promotion is authorized by this research fixture.
