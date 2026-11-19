# WSP188 — exact physical light-tunnel archive metadata diagnosis

The independent WSP187 light-tunnel experiment stopped **before training** because the first source CSV `actuators_white` did not match its frozen original 10,000-record requirement. This branch freezes a NEW **metadata-only** source inspection at `56c73b5220f22e9ff6887bb5dea70ab75af8d98d`. It reports original **row counts, column names, malformed/empty record counts and immutable SHA256 fingerprints**, without parsing numeric sensor outputs or training/scoring any model.

Original CC BY 4.0 physical data source `juangamella/causal-chamber@967d59a42956872f37463cc561ecf6e9ceab9364`, `lt_walks_v1`, authors Gamella/Peters/Bühlmann 2025, DOI 10.1038/s42256-024-00964-x, published ZIP MD5 `dcad019186661a56de7a2d1db97fc2f0`. It enumerates exactly `actuators_white`, `color_mix`, `smooth_polarizers`. Existing WSP185 roster code is reused read-only; no duplicate parsing infrastructure or rewriting WSP187's source/model/prereg.

No new original physical actions, protected source-owner first-use, paid APIs, scientific fitness assertions, controller/runner schedule changes, deployment or merge. WSP187 remains frozen source-admission STOP; an independently pre-registered later study might reuse genuinely existing public observations only after this diagnostic establishes the physical recordings actually present.
