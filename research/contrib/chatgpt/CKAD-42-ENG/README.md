# CKAD42-ENG — Portable causal-weight checkpoint encoding

**Engineering-only repair**, forked from CKAD42's original `DEV_NO_GO` PR #1293 at `e8e1905d069f8fce092b71279a5bbc40aabfe33e`. Freeze: `protocol.json` at `30700bf17c75f1ef18354b82169f3b03c18c7b95` precedes the first repair source commit.

## Original gap

Original CKAD42 `290b9a7f0ccd351b62e1bfb8f1de762601663bf2` scored identical Brier metrics on Ubuntu and Windows, but one learned `NativeInterventionRelations` checkpoint differed in SHA-256 while all existing `NativeEpisodeExperience` checkpoints matched. The cause is **not proven**; a low-precision floating-point accumulation or library difference is a plausible hypothesis.

## Repair

The experimental CKAD42 class on this fork preserves the original numeric learning and prediction operations, all actual source event IDs, original `NativeEpisodeExperience`, and numeric relation hypothesis grammar. It changes ONLY the *serialized* checkpoint representation to canonical 12-significant-digit finite floats for full-history weights, short-timescale weights, action-masked control weights, and learned Hedge readout weights. Python `float(format(value, '.12g'))` provides a stable decimal boundary. Signed zero is normalized, and nonfinite values fail closed. Existing source SHA validation and exact cold-byte restoration remain mandatory.

The repair does not establish identical in-memory floats across operating systems; it aims to make clinically irrelevant sub-ULP differences in persisted weights immaterial, with a <=1e-8 cold forecast perturbation limit. A later scientific successor would require new disjoint seeds, full qualification, first-use authority and actual matched-policy scientific evidence.

## Fixture-only qualification

The dedicated `fixtures.py` creates three deterministic engineering-only **numeric** streams (`cycle`, `rule_shift`, `action_interactions`), each 480 source episodes. These are not copies of any CKAD37–42 science generators and never invoke the original CKAD42 `run(seed)`. At 160, 320 and 480 witnesses, compare full portable SHA-256, component digests, original unrounded diagnostic hash, byte-exact cold restore, and all grid forecast errors. All genuine fixture events are seen once, and duplicate/conflicting source IDs are tested. Separately unit-test a deliberate one-ULP perturbation; the unrounded source must change while the stable checkpoint must remain identical.

Both Ubuntu and Windows must pass the original CKAD42 unit fixtures and new engineering fixtures at **the same exact SHA and Git tree**. The output includes full checkpoint digest receipts per OS and per fixture; scientific held-out data is untouched.

**Scope:** No original CKAD42 scientific DEV replay; original pilot seeds `42211/42212` and primary `42311/42312/42313` remain untouched; no accepted ref, official native learner, core model, controller, scheduled task, paid API, or deployment changes. The full repo regression is a distinct later gate and is not implied by fixture qualification.

## Reproduce

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-42 -p test_ckad42.py -v
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-42-ENG -p test_portable_checkpoint.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-42-ENG/fixtures.py
```

If the frozen fixture digests differ across systems, the engineering repair is **NOT QUALIFIED** and evidence should be retained without promotion. CI job completion alone does not confer scientific acceptance.
