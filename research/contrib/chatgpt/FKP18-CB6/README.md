# FKP18-CB6 — Exact decision-theoretic bound on CB5 sensor probes

**Outcome: a retrospective, source-verified reduction of 11 logically unnecessary probes; no new actual source actions; no unique intelligence advantage.**

## Preregistered and frozen

- Accepted Yggdrasil `main` remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Isolated predecessor CB5 `a932f8e3d20516753d658496deb570370aa06b2c`. No changes to predecessor, active FKP-17/18 PRs, native model, DG1, ITD-02, controller or scheduler.
- CB6 protocol frozen FIRST at `618b3de7e4c4ccdb0c7312513aee5d5c2d110b33` before writing the decision policy or reducing the archived results.
- Original evidence is **the already consumed public synthetic CB5 outcome**, *not* a new preregistered primary science run: `research/contrib/chatgpt/FKP18-CB5/result.json`, Git blob `852e75d7f84bac5f7e090514cda57b1c394327a6`. New archived reduction refuses any other Git blob in the CLI.
- Exact-tested and checked Git blobs: `probe_bound.py=6c9b6da764e0083ddb26fd7efd08333bcf3927f2`; `test_probe_bound.py=46d14c1ee3d3b008bf7494f88453f360ed177519`. Local Linux Python focused **10/10 PASS**, compile PASS.
- A six-column CB5 per-world archive-parser correction and exact-blob custody guard were introduced before the final archive readback. Neither the original CB5 observations nor the decision-theoretic algorithm, thresholds, hidden laws, or original 32-world outcomes changed. See `provenance.json`.

## Decision rule and exact conventional control

CB5's synthetic source guarantees **exactly one causal sensor among six candidates**. Each downstream paid source action tests one named candidate. If an earned reward reversal appears, that channel is identified. If five distinct tests return negative, then the sixth channel is known by exclusion and **testing it is redundant**. A two-byte logical direct mask stores candidates still possible and which were actually probed.

This is not a novel algorithmic advantage: a separate exact conventional Bayesian dynamic program with six possible hidden channel identities and the **same public observations, known cardinality, probabilities and costs** makes the same inference. The DP computes the minimal expected future charged actions after every possible negative outcome and permits stopping with one survivor. With uniform prior and unit downstream costs, both policies achieve:

| Measure | Original confirm-positive | New exclusion / exact Bayesian optimum |
| --- | ---: | ---: |
| Paid downstream probes for sensor ranks 1..6 | 1, 2, 3, 4, 5, **6** | 1, 2, 3, 4, 5, **5** |
| Uniform-prior expected downstream probes | 3.5 | **3.3333333** |
| Worst-case total actions (4 upstream + baseline + downstream) | 11 | **10** |
| Correct identity under source's exactly-one guarantee | 6/6 | **6/6** |

The exact Bayesian reference additionally accepts unequal priors or unequal costs; fixed ascending candidate order is **not** claimed optimal on those distributions. The null/multiple-causal-world negative **fails closed**: without an exact-one source guarantee, the last survivor cannot be asserted as confirmed.

## Archived results — no source replay

The independent read-only GitHub audit of the byte-verified original CB5 `result.json` finds 32 public worlds `82500..82531` with the following distribution of original **total** charged actions per world:

| Charged actions originally | Worlds |
| ---: | ---: |
| 6 | 5 |
| 7 | 4 |
| 8 | 5 |
| 9 | 2 |
| 10 | 5 |
| 11 | 11 |

Original total **287**, of which **11** are sixth-sensor confirmation actions. With exactly-one source guarantee and the other unchanged public outcomes, the result is **276 derived necessary paid actions**, a **3.8328%** reduction. These are derived costs from consumed evidence, **not new measured environment actions saved**. The source already identified the true channel in 32/32 worlds, and the last-by-exclusion policy is correct on all six logically possible channel identities. It does **not** establish a new physical intervention deployment or source-observed accuracy on a new cohort.

The full pinned original per-world audit is retained in `result.json`. No original CB5 science conclusion was revised: direct sensor identification and conventional inference previously tied 32/32 with the same costs. CB6 now ties the stronger **optimal Bayesian stopping** rule on the model's exact uniform/equal-cost hypothesis class. Scientific superiority **NO-GO**.

## Reproduce, authority and next action

```sh
cd research/contrib/chatgpt/FKP18-CB6
python -m unittest -v test_probe_bound.py
python -m compileall -q probe_bound.py test_probe_bound.py
python probe_bound.py ../FKP18-CB5/result.json
```

The CLI checks the **exact original Git blob** and rejects tampering or a different archived cohort. In this turn, local exact-file focused tests **10/10 PASS**, and original CB5 archive reduction was executed independently using a read-only GitHub file fetch. The full checkout CLI was **not run against a locally mounted copy of the original private repository**. Candidate-specific full final Linux/Windows root regression, G29 derived atlas, and independent science remain **UNVERIFIED**.

This line has reached an important boundary. **Given the same sufficient hypotheses and charged observations, direct-written exclusion cannot improve on Bayes-optimal identification cost under this source.** More toy variations of the same six-candidate problem are not evidence of new native intelligence. Existing DG1 paid causal probing and WSP-120 source-controlled active learning are separate lanes and should not be duplicated.

**Next meaningful scientific test:** independently held unfamiliar worlds where intervention outcomes can change goal value and vary by cost; learned policy must beat **fully trained conventional and Bayes-optimal decision-value controls** on retained consequences, unfamiliar transfer and whole-process cost, with prospective frozen source/seeds and independent owner qualification. No accepted Yggdrasil native change from this retrospective audit.
