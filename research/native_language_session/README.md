# Yggdrasil native learned-state session

This is the first runtime component toward a native language prototype. It is
not a language model or language proof point. It exposes the existing R7 local
cell learner, independently from Wingless. It has no text parser/generator,
corpus, external model, controller, queue or automatic promotion.

The original source at `research/native/itd01/r7/native_cells.py` is unchanged:
Git blob `4c492a494ac5b25d5e9c49b98185be6a2c966b2f`, parent commit
`adb0ca9091762a110d65257ffe4bdcc8e90b46a3`. Its historical negatives and frozen
experiments are retained. Four local cells in each context use local plasticity,
slow consolidation and bounded neighbor messages. This small component does
not yet realize the full developmental/genome/phenotype north star.

From the repository root run:
`python -B -m research.native_language_session.runtime`.
The process reads JSONL on stdin and writes JSONL replies, each with
`language_capability:false`. Use a byte-stable LF checkout; the runtime checks
the exact original source blob and fails on source drift.

| Operation | Additional fields | Behavior |
|---|---|---|
| `predict` | `context`, `sensors` | Native prediction and selected `query_id` |
| `feedback` | `query_id`, `public_outcome`, `delay_steps` | One completed update for that pending prediction |
| `checkpoint` | none | Complete native cells, counters, source and sequence |
| `restore` | `checkpoint` | Restore into an unused process |

Context is `A` or `B`, sensors are exactly four booleans, outcome is boolean,
and delay is an integer at least 2. The caller remains responsible for truthful
public outcomes and actual delay: this API cannot authenticate either. Until
feedback arrives, another prediction/checkpoint is denied. Mismatched, repeated,
or early feedback does not mutate the cells. The update cap is 1,000,000.

Example first request:
`{"op":"predict","context":"A","sensors":[true,false,true,false]}`
Use its returned `query_id` in a feedback request, then checkpoint. Pass the
returned checkpoint object to `restore` in a fresh process to resume learning.
Checkpoint SHA256 supplies integrity only, not authentication, scientific
provenance, replay protection across forks, or accepted-model authority.

Run `python -B -m unittest discover -s research/native_language_session -p 'test_*.py' -v`.
Tests use invented engineering inputs. They check complete recovery in a new
process and invalid-feedback boundaries, not held-out language transfer. The
original R7 unit tests and the existing public regression must also run; G29
Atlas and independent scientific acceptance remain mandatory, unwaived gates.

Next research work must develop native language representations and output
with the developmental constraints, legitimate development data, frozen
transfer evaluation and equally informed trained controls. FORGE takeover
requires independently qualified language evidence and authorized integration.
