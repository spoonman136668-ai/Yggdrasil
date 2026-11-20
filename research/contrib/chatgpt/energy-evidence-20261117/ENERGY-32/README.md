# ENERGY-32 evidence custody

Contained artifacts are development-only. This is NOT native Yggdrasil training.

- `protocol.json`, `experiment.py`, `independent_audit_v1.py` — frozen before primary scoring, with SHA256 recorded in `freeze.json`.
- `smoke.json`, `audit_smoke.json` — separate pre-score smoke evidence.
- `scored.json` — immutable original 240-case primary result, including the 9 floating tie classifications.
- `audit_original_stdout.txt`, `audit_original_stderr.txt` — original independent audit failure, preserved without hiding.
- `numerical_tie_certificate.py`, `numerical_ties.json` — post-score exact-integer certificate for ambiguous half-posterior readouts.
- `postscore_independent_audit.py`, `audit_postscore_result.json` — post-score independent reaggregation with explicit 9 exact ties.
- `replay_verification.json` — semantic score identical on a second execution after excluding time field.
- `REPORT.md` — scientific/provenance diagnosis and failure disposition.

No primary seed or scoring threshold modified. No native checkpoints, original-source actions or scientific first-use.
