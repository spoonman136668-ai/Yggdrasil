# WSP-118 — When does a larger foundation make a new relationship inferable?

**Source-safe, preregistered research fixture. NOT independent scientific acceptance.**

This experiment directly follows [WSP-116](https://github.com/spoonman136668-ai/Yggdrasil/pull/1108) (20.68 million retained real historical relationships; increasing retained coverage improved consumed-query Hits@1, but exact symbolic methods tied), and [WSP-117](https://github.com/spoonman136668-ai/Yggdrasil/pull/1110) (a directly programmed numeric relation model learned names for two-hop compositions and abstained when ambiguous; symbolic exact tied).

## The test

We now extend the candidate's relationship *structure* from WSP-117's one/two-hop language to **new length-three compositions**. On 24 newly generated, source-safe public fixture worlds, each with six independently connected primitive relations over 64 entities, the evaluator chooses four target three-hop relationships that are **not equivalent to any one/two-hop law in the same world**.

Each learner receives only the same **12** publicly observed source→outcome demonstrations and a varying proportion of the world's labeled primitive graph facts. The same world, target law, demonstration sources and **24 disjoint held query sources** are reused at seven nested graph-fact densities: 0%, 6.25%, 25%, 50%, 75%, 87.5%, and 100%. Edge admission is SHA256-based on world seed, predicate and subject, never on the target response or learner success.

The candidate builds a bounded **216×2 int32 = 1,728-byte** numerical association bank. Its two learned values per possible three-hop composition are number of visible source observations supporting or contradicting that law. No backpropagation. A missing intermediate public edge yields **UNKNOWN**, not an invented demonstration. A law is identifiable only when at least three complete public examples support it, none contradict it, and exactly one law qualifies. The candidate predicts a held subject only if the inferred program and all three public path edges are available.

The **independent exact symbolic synthesizer** gets precisely the same source facts and positive demonstrations and uses its own Python dictionary/set implementation. It must match every candidate decision. The WSP-117 restricted one/two-hop grammar, source-label-shuffled demonstrations, source-only memorization, empty foundation and forced nonidentifiable program negatives measure shortcuts. Raw weights are SHA256 cold-restored and tamper-tested.

The numeric model is not a neural network. Its 216 three-hop hypotheses are **supplied by the new experiment design**, not autonomously invented. Therefore a perfect threshold curve would establish *information sufficiency for a pre-specified extended grammar*, not the moment a normal AI becomes generally intelligent or invents completely unanticipated relationship types.

## Frozen question and threshold

Did increasing a connected factual foundation unlock an entirely new triple-path relation versus the earlier two-hop learner, and where was a majority of target laws first identifiable?

Preregistered **fixture engineering** signal only requires 100% source graph ≥80% held accuracy (abstain counted wrong), 100%-versus-25% ≥20 percentage points improvement and a paired 10,000-resample bootstrap across worlds with strictly positive 95% lower bound. Exact symbolic parity, full cold restore, no held-label training, and zero restricted-source reads are mandatory. The report also publishes all other tiers, coverage, false declarations, incorrect labels, symbolic ties, source fact counts and time.

This is not SCIENTIFIC_PASS, even when those fixture thresholds hold. The hypothesis class, graph law and demonstration labels are intentionally controlled. We **do not** revisit WSP-116's 21-million-row archive, official validation/test, reserved experiment seeds 118800–118863, any owner-protected first-use source, or native Yggdrasil weights.

## Next independent science gate

Only after this calibration should a separately owner-qualified experiment use a novel *unanticipated* relation family not expressible in the originally programmed 3-hop grammar, an independent source/evaluator, fully trained conventional GRU/MLP and exact symbolic program-synthesis controls under equal information/compute, cold retention, unfamiliar-world transfer and action-consequence verification. The first-use cohort must remain untouched until that distinct protocol and authority are established. A simple graph-dose-response cannot by itself prove self-growing general intelligence.

## Local source-safe reproduction

```console
python -B -m unittest discover -s research/contrib/chatgpt/WSP-118 -p test_wsp118.py -v
python -B research/contrib/chatgpt/WSP-118/analyze.py
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

No GitHub PR acceptance, merge, promotion, controller/queue action, scheduler, paid API or native accepted-main ref mutation is authorized by this research-only fixture.
