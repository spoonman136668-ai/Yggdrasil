# ENERGY-24 GitHub evidence

This folder contains the **complete original local evidence package**, attached as a verified `tar.xz` Git blob. It includes exact preregistration, original frozen Python scorer, full scored aggregates, 768-world case-level results, independent audit, preserved initial audit failure, and the final audit result.

Run `tar -xJf ENERGY-24-full-evidence.tar.xz`, then `python -B ENERGY-24/experiment.py` and `python -B ENERGY-24/independent_audit.py` from the extracted directory. The frozen scorer writes `scored.json` and `per_world.json` by default. Ignore runtime/CPU seconds for byte-level comparisons because wall-clock timing is host-dependent. All seven source-file SHA-256s are listed in `custody.json`.

**Engineering:** local Python score & 62,263 audit checks PASS; **science:** DEVELOPMENT_NO_GO and native evidence UNVERIFIED; **deployment:** NONE. No existing Yggdrasil learning checkpoint, active research loop, or model source is edited in this PR.
