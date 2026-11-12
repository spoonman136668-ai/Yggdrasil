# WSP51 — grounded micro-language via direct numerical weight writing

Preregistration frozen **before implementation or any WSP51 run** at `73d5dc26b3fc7e8414dec8f73d3776167d6a1291`. This is an isolated external synthetic contributor experiment based on qualified WSP47 `9e6374119602ea57e479a1b36a35a5c0e932b4e1`. It is **not** an official Yggdrasil research-loop result, general language understanding, or an accepted/promotion candidate.

## Question and design

Does a learner need expensive repeated optimization to acquire a **small set of grounded new meanings**, if it can instead write addressable numeric associations directly? The world supplies four distinguishable physical entities, two destinations and two observable action mechanisms (place versus avoid). Eight independent unfamiliar single-byte acoustic pulse forms are grounded by **10 genuine experiences**: four observed noun pointings, two destination pointings, four action consequences. A fixed three-slot utterance format is shared by all arms, but none of the 16 full three-frame instruction combinations is taught. An action is scored by its actual effect on the next world state, not by string prediction.

The direct learner writes equality-gated numerical bitplane weights for the observed acoustic addresses (a simulated finite gate circuit). A matched exact evidence table and 100-epoch, one-hot linear softmax trained head see **the same experiences**. A no-evidence arm is negative control. Full nominal capacity, update counts and source resets are reported. This is a synthetic grounding proof-of-feasibility, not independent acquisition of grammar, vocabulary segmentation, concepts or arbitrary neural algorithms.

The evaluator independently generates three pulse-encoding conditions for each seed. It also tests unknown pulses, role-swapped utterances, a newly learned noun synonym, a contradictory pointing that must invalidate only the affected form, and tamper-evident cold restoration. First-use PRIMARY seeds are distinct from DEV. Public synthetic data are programmatically generated without external datasets.

## Preliminary development result (local, not qualified)

On DEV seed 103 across three encodings, **7/7 focused local unit tests passed**. All three non-erased arms got **48/48 composed actions correct**; the erased control got **0/48**. Unknown/slot-order examples abstained, learned facts survived an added synonym, contradictory grounding invalidated its old address, and the checkpoint passed cold parity and tamper rejection.

**Scientific result: no demonstrated advantage over a trained or literal table control.** Even a flawless synthetic PRIMARY would not establish general-language understanding or independent `SCIENTIFIC_PASS` when the exact table ties. DEV is exploratory, not a sealed external scientific result. The best next test after qualification is an unfamiliar syntax/segmentation setting where the same hard-coded compositional mechanism cannot solve the task.

## Commands

```bash
python -m unittest discover -s research/contrib/chatgpt/WSP-51 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-51/battery.py --cohort DEV
python research/contrib/chatgpt/WSP-51/qualify.py
python research/contrib/chatgpt/WSP-51/battery.py --cohort PRIMARY
```

A valid engineering claim requires the complete inherited regression on the exact candidate, cross-platform qualification and the G29 atlas. PRIMARY results are not implied by this README. No main merge, official scientific first use, accepted ref, scheduler, paid API, private data, model integration, or deployment is authorized by this contribution.
