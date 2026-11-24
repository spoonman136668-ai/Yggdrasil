# Stage 7 — factor generation ablation

Frozen, isolated byte-LM comparison; not Yggdrasil's cognitive foundation. Same backbone and initialized Monarch function; routing disabled. Direct factors and rank-four residual tested separately. See prereg.json. Prior validation corpus has been inspected, so this is not unfamiliar transfer. Equal update count is not equal FLOPs. Runtime and quality claims need actual execution.

Reproduction from exact preregistration commit on an authorized CPU, with a separate pinned corpus checkout at 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9:

```
python -m experiments.procedural_event_stage7_capacity --corpus-root <pinned-corpus-root> --out research/contrib/chatgpt/stage7-capacity/result.json
```

Do not overwrite or rerun uncertain trials. Preserve runtime and source provenance. Primary not executed; focused tests only (engineering.json). Native/full repository qualification and independent review separate.
