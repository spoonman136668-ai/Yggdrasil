# MG95-C exact-blob order-ablation execution receipt

Classification: SYNTHETIC ENGINEERING DEVELOPMENT ONLY.

Executed from GitHub-fetched source files in isolated Linux Python. `git hash-object` matched each fetched source blob exactly:
- `order_confound_ablation.py`: `f3a99810cee8d067b62d3cfddc0f0ee9cefebfdf`
- `conditional_memory_control.py`: `b7f450e58922649a31354766b102cb4c02d040ca`
- `intervention_memory_screen.py`: `8707c3be5954cf28e97fe4dc43a7a97dd9df0aff`

Command: `python order_confound_ablation.py`
Result: PASS; all assertions completed.

| Training order | Full conditional lookup | Action-only lookup | Context-only lookup |
| --- | ---: | ---: | ---: |
| Forward | 8/8 | 6/8 | 4/8 |
| Reverse | 8/8 | 6/8 | 4/8 |

The context-only stored output entries differ by order, while aggregate scores do not. Full lookup remains 8/8. This demonstrates memory-state order sensitivity but **does not demonstrate order-dependent accuracy**. The original MG95-C assertion incorrectly expected action/context accuracy to differ; it failed and was replaced with assertions on the actual observed property. Corrected source was re-executed and passed.

This is synthetic, deterministic, tiny lookup-table engineering evidence, not learned native causal cognition. No held-out unfamiliar original-world trials. Official owner CI and mandatory full regression UNVERIFIED. No acceptance or promotion.
