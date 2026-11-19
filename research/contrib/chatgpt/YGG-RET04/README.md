# YGG-RET04 — exact staged prequential score receipts

**Engineering candidate only. No source-owner first-use or new scientific
evaluation.** Existing RET03 original native+six-head continuous learner and
its retained RET02 score/readout are unchanged.

Parent: [RET03 draft PR #1295](https://github.com/spoonman136668-ai/Yggdrasil/pull/1295)
at `a075b323557ed4f5cf600b8eef50bc34c8e1866b` (Linux and Windows
final complete engineering PASS; science UNRUN). Frozen engineering contract
committed **before** code and tests at
`28a8ebb4b69b767230f852de8663735b99585101`.

## Why this stage is necessary

An inherited RET02 readout's complete-event Brier update is calculated
after a first consequence has been seen. RET03 successfully split
prediction calls into the correct two public observation clocks, but
that does **not** on its own establish that subsequently reported
losses equal the probabilities actually emitted before each outcome.

`yggdrasil/native_staged_score_receipts.py` adds
`StagedScoreReceipts`, an **opt-in measurement wrapper, not a new learner
or policy**. Its calls delegate to the same already-qualified RET03
`StagedTemporalReadout`, with the identical original native weight and
specialist updates:

- `begin` returns immutable (to the receipt) first-transition
  archive/live/temporal probabilities before first-stage consequence.
- `record_transition` witnesses public s2 without native update.
- `choose_second` records archive/live/temporal reward probabilities
  after public s2 and chosen second action, strictly before future y.
- `complete` witnesses public y and admits the existing native update
  **once**; only then records an event source ID, earlier issued
  probabilities, witnessed s2/y, separately computed first/second
  squared losses, the averaged two-clock Brier and the exact underlying
  RET02 trained-model/readout checkpoint SHA before and after update.

The score uses direct ordered `error * error` arithmetic and **never
recomputes the forecast after either observation or native training**.
A receipt's hashes bind to data integrity but **do not authenticate a
source owner's permission**. All receipts remain marked
`source_owner_authenticated=false` and `scientific_pass=false`;
original external source first-use remains blocked by #426.

An outer canonical checkpoint preserves the **byte-for-byte original
RET03 checkpoint**, plus the new score ledger. Cold restore independently
replays all completed source witnesses and any pending stage through the
unchanged original native model and confirms *both original checkpoint
bytes and every score receipt*, rejecting rehashed tampering.

Seven bounded engineering tests include:
1. two-clock score calculated from actually returned probabilities;
2. equality with original RET03 native progression, original stored
   memory, and specialist weights after each admitted witness;
3. early-stage probabilities not depending on future reward;
4. cold resume during each stage and after two completions;
5. rehashed loss/forecast/model checkpoint corruption rejected;
6. forged pending transition forecast rejected despite hash changes;
7. invalid stage/reused source cannot mutate native or ledger.

The inputs are hand-constructed public-shaped mechanical records
and existing immutable trained checkpoints, **not** new source
interventions, previously consumed development seeds or held data.
Tests establish interface and receipt correctness only.

## Stop / separate future scientific acceptance

No independent source-owner virgin TRAIN/VALID/HELD/TRANSFER admissions,
source actor effects journal, physical causal source training, matched
fully fitted history-aware conventional comparison, unfamiliar-family
transfer, tokenless intelligence improvement, or reduced whole-process
resource cost is established. The previous failures in RET01/RET02,
CKAD42 and other Yggdrasil research are preserved.

Source owner [#426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426)
continues to block protected original-world first-use. Genuine future
science requires preregistered stage-by-stage prequential timestamps,
public source custody and authorized actions, strongest fitted
Beta/Bayesian/recurrent/symbolic controls under equal knowledge/actions/
compute, old-context cold retention, unseen transfer, historical
interference and resource-cost stop criteria before any new original
first-use. Keep this as **DRAFT, SCIENTIFIC_PASS=false, no promotion,
no Forge/CKB/controller/scheduler changes, no merge or deployment**.
