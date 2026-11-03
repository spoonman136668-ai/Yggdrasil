# Native whole-response text component

This component accepts complete UTF-8 input/response pairs, trains the project's
original native learner, and selects one complete response from the supplied
bank. It is **closed-response selection**, not novel-string generation, a
general language model, or the language proof point. Every response reports
`language_proof:false`; predictions also report `novel_string_generation:false`.

Limits: 2–16 examples, 2–8 distinct supplied responses, 1–256 UTF-8 bytes per
input, <=1024 input bytes total, <=128 UTF-8 bytes per response. No corpus,
external model, old scientific cohort, parser grammar, or hardcoded response is
embedded. All training examples are validated before native updates. Training
is from scratch. Prediction is read-only. Ties use deterministic bank order.

The retained state includes the response bank and **every native model's full
learned state**, source/schema/encoding pins, training-data digest and integrity
digests. Digests are not authentication, proof of legitimate data, or scientific
custody. Source drift and corrupted/foreign state are rejected.

JSONL operations:
- `{"op":"train","examples":[{"input":"aaaa","response":"amber"},{"input":"zzzz","response":"violet"}]}`
- `{"op":"predict","input":"aaaa"}`
- `{"op":"checkpoint"}`
- `{"op":"restore","checkpoint":<returned checkpoint object>}` in a fresh process.

The example strings are invented engineering fixtures. No linguistic
performance is inferred from them. New tests check native-state updates, score
influence versus untrained state, complete checkpoint/fresh-process identity,
prediction nonmutation and invalid inputs. Existing mandatory regression and
source-index acceptance remain required. Historical negatives remain negative.

Before any language proof: separately freeze legitimate development data and
genuine held-out unfamiliar transfer; train equally informed controls; compare
untrained, no-state and shuffled-label arms; establish prospective paired
retention measures; measure all state, training and inference costs. No such
scientific proof, architectural novelty, efficiency advantage or autonomous
FORGE development is claimed here.

Yggdrasil uses the unchanged R7 Colony and local-cell rule (blob
`4c492a494ac5b25d5e9c49b98185be6a2c966b2f`). Each UTF-8 byte presents high
and low four-bit sensory events to the original A/B contexts. A bank of at most
eight original colonies learns from completed example-level response labels;
all scores come from original bounded-neighbor predictions. At capacity this
is 64 local cells, with capacity and communication costs growing with the
response bank. It does not establish language understanding, useful genome
compression, growth, specialization, functional regeneration or repair.
The original DG-1 developmental substrate and research lineage remain intact;
this is a bounded input/output component, not a replacement cognitive foundation.

Run `python -B -m research.native_language_session.text_selector` for JSONL.
Check `python -B -m unittest discover -s research/native_language_session -p 'test_*.py' -v`.
The original R7 frozen retention gate remains required and currently negative.
