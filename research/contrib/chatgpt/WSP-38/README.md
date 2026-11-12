# WSP-38: ceiling-first training-free numerical world model

Research hypothesis: Can a bounded "knowledge base + instructions" system be compiled directly into numerical weights and execute a complete knowledge-and-reasoning workload without fitting gradients?

This is a **binary relational memory with a preauthored compositional interpreter**, *not a pretrained neural model*. The experiment deliberately tests the largest permitted memory first then backs off: 32,768 (resource screened), 16,384, 8,192, 4,096, 1,024, 256 entity slots; eight independently labeled relation types, three real outgoing edges per row, six-step compositions, cold restore, isolated interventions, and generalization to unseen relational queries.

The 32,768 level requires a nominal 1 GiB dense bit-matrix, exceeding the frozen 512 MiB ceiling. It must be reported as excluded, **not failed**. The 16,384 level has 2,147,483,648 nominal binary bit positions and 393,216 actual facts. Nominal capacity is not the same as intelligence or acquired knowledge.

The evaluator generates the entire graph independently, but construction receives only the supplied source-relation-destination records. It checks **complete positive and negative reachability sets** against an independent sparse-graph symbolic oracle (not just random true/false questions), 48 sampled queries and 24 never-before-used query compositions per world. Other controls test half-withheld facts, cold checkpoint integrity, atomic one-edge repair, and unaffected-memory preservation.

**Primary protocol**: 3 held-out worlds per level (seeds 1103, 1109, 1117). Prereg-only source commits: `627476b8af288de646ccc2fc2f08ba24734c04e6` and pre-primary tightened positive/negative test revision `edf9aeef91eeb76988a12ae8fe5cedc30e5d9c5d`. No primary data were used in development. Local DEV measurements were exploratory before prereg; scientific claims must be limited accordingly.

**Strong baseline:** exact sparse Python graph-walk oracle on the same observations, queries and runtime. This is not a matched trained neural model comparison. The preregistered cost-viability rule is numerical query time no more than 2.0× sparse reference per OS, with exact correctness, computed after full PRIMARY.

Commands from repository root:
```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s research/contrib/chatgpt/WSP-38 -p test_*.py -v
PYTHONDONTWRITEBYTECODE=1 python research/contrib/chatgpt/WSP-38/battery.py --cohort DEV
PYTHONDONTWRITEBYTECODE=1 python research/contrib/chatgpt/WSP-38/qualify.py
PYTHONDONTWRITEBYTECODE=1 python research/contrib/chatgpt/WSP-38/battery.py --cohort PRIMARY
```

**Scientific caveats:** No learning without supplied facts, no autonomous acquisition of missing facts or novel reasoning algorithm, no matched fully-trained network, no general-language intelligence; all ontology and interpreter logic are authored. Absolute times and 2× relative timings are machine-dependent, and should not be promoted to universal limits. This is public synthetic external research only: no accepted refs, merges, Yggdrasil/FORGE owner integrations, controllers, private runners, schedulers, deployments or paid APIs.
