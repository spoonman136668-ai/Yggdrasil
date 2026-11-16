# NKR-09 — Native relationship-rule induction with explicit microfeedback

**Isolated development research. Neither autonomous verified knowledge discovery nor accepted native activation is established.**

## Meaningful next question

NKR-08 [PR #1135](https://github.com/spoonman136668-ai/Yggdrasil/pull/1135) qualified additive, cold-restorable fact memory against the already-built complete **21,343,681 historical training facts**, but only stored directly observed fixture facts and generated **unranked** path hypotheses. It did not update its internal relationship preference from a revealed outcome. NKR-09 tests **bounded adaptation of relation-rule hypotheses from explicit microfeedback** without converting hypotheses into stored truth.

The system remains a standalone non-transformer, non-token, source-pinned native numerical graph. This contribution does not touch actual autonomous controllers, accepted Yggdrasil main, original DG1 state, owner checkpoint, live actions, source-science cohorts, historical actual facts or new external datasets.

## Actual mechanism

`yggdrasil/native_relation_discovery.py::NativeRelationDiscovery` consumes only an already qualified `CumulativeNativeFacts` candidate and its frozen **synthetic-only** evidence checkpoint. From public training observations, it **induces rule templates automatically**: given explicit source-backed observed `X--p1-->Y`, `Y--p2-->Z`, and `X--p3-->Z`, it proposes `(p1,p2)=>p3` for later queries. It does **not** need a hand-written relation dictionary, and it does **not** invent a relation ID that has never appeared in training. Repeated distinct subjects determine an integer training-support count; absent edges are NEVER treated as negative outcomes.

For unfamiliar subjects it enumerates matching two-hop candidates through NKR-08's actual source-aware `hypothesize` path (which includes the full historical base when installed), ranks hypotheses by integer evidence, and marks them **unverified**. Frozen, caller-pinned `engineering_fixture_only` outcome feedback may strengthen/reduce specific template preferences by a precommitted +4/-4 integer increment; a new immutable NKR-09 checkpoint is produced. The historical 21.3M base, additive factual evidence checkpoint, and original YPC1 action-consequence counters remain byte-for-byte unchanged. All recorded feedback remains synthetic; input SHA proves only exact bytes, never authenticity of a real event.

The mechanism has explicit 4,096-fact, 250,000-path, 512-rule, 32-feedback, and 256-hypothesis bounds; exact canonical versioned provenance, duplicate feedback detection, no unauthorized owner sources, failed source rebind, cold replay and unknown-relation abstention.

## Frozen falsifiable experiment

**Prereg FIRST:** `219d94f2d535012c0569d5567e0b274925f4aca1`, before any implementation/fixture outcome.

A synthetic world contains **64 disjoint subjects** with two two-hop routes: A `p11/p12` and B `p13/p14`. In training subjects 1..32, typed target relation `p15` accompanies A 24 times and B eight times; `p16` accompanies B 24 times and A eight times. This supports four induced native rule templates, with no hard-coded learner mapping from p15/p16 to a path pair. Unreachable decoy `p29` facts must never produce a supported template.

Subjects 33..40 supply *explicit synthetic public target feedback* for `p15`, all eight outcomes pointing to B. Subjects **41..52** are unopened-to-the-learner cold probes (nine B outcomes, three A); static frozen learner should score **3/12 Hits@1**, feedback-adapted learner **9/12** (+6 correct), and an independent *fully fitted exact symbolic composition/counting learner receiving identical visible training and all eight feedback labels* should **tie the adapted learner 9/12**. Subjects 53..64 test unrelated `p16` retention: 9/12 Hits@1 before and after p15 feedback. Unsupported p29 must abstain. Cold exact checkpoint/legacy state must not change.

**Preset diagnostic threshold:** adapted p15 >=9/12, static =3/12, delta >=4, unrelated p16 >=9/12; no claim of scientific superiority if matched symbolic ties. These are **synthetic DEV** outcomes with the same developer controlling generation and evaluation; not original science or independent held-out generalization.

Execute:
```console
python -B research/contrib/chatgpt/NKR-09/experiment.py
python -B -m unittest discover -s tests -p test_native_relation_discovery.py -v
python -B -m unittest discover -s research/contrib/chatgpt/NKR-05 -p 'test_*.py' -v
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

## Additional original 21M-image interface corroboration

**Separate engineering-only, not preregistered independent science**: after all exact-source Linux/Windows root+G29 pass, reuse the **already available** NKR-05 [original GitHub artifact #14220169461](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43856374741/artifacts/14220169461) (expires December 16, 2026). Do not fetch/rebuild its historical Wikidata source, use official valid/test or request new paid compute.

`research/contrib/chatgpt/NKR-09/prove_real_image.py` installs that original source temporarily, confirms full checksum and first source triple `[1,361,3327819]`, induces a **synthetic** rule `(p901,p361)=>p903` supported by eight synthetic training examples, and retrieves a synthetic new subject's unverified two-hop `Q3327819` through **the real historical first triple**. It does not assert that the inferred p903 edge is true. Verify the original source and native causal cells unchanged, cold restore, then repeat mandatory source-safe root suite. Upload **only a small receipt**, not 256MB of duplicate data.

## Separate interpretations

- **ENGINEERING:** Induction/explicit feedback/retention source-safe and full regression can pass.
- **SCIENTIFIC:** Genuine relationship-family novelty, causal intervention learning, real-world correctness and sustained unfamiliar transfer **UNVERIFIED**. Strong matched symbolic baseline should tie. No original protected scientific source.
- **DEPLOYMENT:** Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged; owner-persistent native activation unavailable without verified directory, owner authority, durable custody and independently qualified model improvement.

No new runner, schedule, sidecar controller, model inference API, forced merge or main mutation. Independent scientific qualification on unseen families/real interventions remains required.
