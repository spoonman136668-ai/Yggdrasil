# LR-92AF — Adaptive causal interventions at fixed evidence budget

**Disposition: EXTERNAL DEVELOPMENT NO-GO.** This is research from an independent contributor lane, **not** native Yggdrasil training, official scientific acceptance, first-use, integration or deployment. Its scientific negative result is not a CI failure.

## Preregistration before first use

- Exact parent: Yggdrasil `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; frozen predecessor raw LR-92AE SHA-256 `7b94587fafbf9ce2fcc4de84c594b1a02c9137a7c9cead39d928c30dbe0676b0` (PR #1272).
- Frozen `prereg.json` committed **first**, at `5f273a9a9d8171de95c81f501bc31c979784a978`; SHA-256 `eed5a93f70828565f25ce0f582a50e544f378dab5c39afef902eecdd86a86880`.
- Exact `lr92af_run.py` committed **before first primary scoring**, at `0db333045a125ea0b7f3e9fd295ebb93495f248b`; SHA-256 of decoded 9,730-byte source `02ac5e7a51a46a97a18791a85298fd27d11bdd0b64cb8506018e31291827e098`.
- Source and protocol GitHub readback SHA-256 PASS. Pre-primary structural tests 9/9 PASS, using fixture-only seeds.

## Experimental comparison

240 new synthetic worlds with distinct seeds 929200611–613. In each 80-world seed block, 32 use familiar context-change mode 0, 32 familiar mode 1 and 16 unfamiliar mode 2. Base truth tables 8–15 remain disjoint from training bases 0–7.

A learned context-conditional causal prior from prior LR-92AD is **frozen**; no new training. All policies use the exact same 256-state inference model and see the same 112 context-0 and **64 context-1** fitting interventions, plus 256 separate held-out observations. Each world contains a shared action-specific potential-outcome tape. Only the chosen action's next outcome is revealed to each policy—no future or held-out label leakage.

Five action-selection policies: (1) adaptive expected information gain (maximizing posterior predictive binary entropy), (2) randomized balanced four-action blocks, (3) random uniform choice, (4) nonadaptive stale information gain, (5) adaptive disagreement between top two hypotheses. All remain subject to the same preset accepted-mechanism cutoff: posterior ≥0.90 **and** fit-only misfit binomial survival p >0.01. Never optimize the threshold on held-out labels.

## Frozen one-shot results

| Policy | Correct accepted familiar / 192 | Correct accepted unfamiliar / 48 | False accepted familiar | False accepted unfamiliar | Held-out accuracy |
|---|---:|---:|---:|---:|---:|
| Expected information gain (EIG) | **37** | 6 | 1 | **1** | **63.6247%** |
| Balanced | 12 | 1 | 0 | 0 | 63.1201% |
| Random | 8 | 3 | 1 | 0 | 63.0485% |
| Stale EIG | 0 | 0 | 0 | 0 | 63.1885% |
| Top-two disagreement | 37 | 6 | 1 | 1 | 63.6637% |

Seven of eight frozen criteria met. **FAILED safety criterion:** expected-information-gain policy had one false accepted unseen mechanism, compared with zero for balanced. The unfamiliar false case was seed 929200612, world 41, base 14, posterior confidence 0.934794; a wrong complete mechanism was accepted.

The improvement in correct familiar accepted mechanisms over balanced selection was +25/192, positive in all three seed groups (+10,+10,+5). An **exploratory, postscore** paired-by-world bootstrap gave a 95% interval of approximately +16 to +34 accepted familiar mechanisms across 192 worlds. This does **not** override the frozen failed safety check or demonstrate general causal intelligence. No extra scored cohort, postresult threshold tuning or integration.

## Source, audit, full provenance

- Original 5,796,201-byte complete raw observation/decision result: SHA-256 `dcdddb974dbc0148a2f0550b19b1549cda3f2b803968adce7be7a90a0d6cb950`. **Not uploaded to GitHub**; locally preserved and reproducible using exactly pinned source, dependencies and seeds. Do not confuse the compact scored ledger with complete raw outcomes.
- GitHub includes `result_summary.json`, `audit_receipt.json`, `provenance.json`, and `scored_ledger.json.zlib.b64`. The compact ledger has all 240 paired world-policy exact/false acceptance flags, MAP exactness and held-out correct counts. Decoded JSON SHA-256: `e7a4e50196da76c596bfd1f00f407ca6e7345a530910646ec73d12796c342210`.
- Frozen runner and independent auditor source are in `lr92af_run.py.zlib.b64` and `audit_readonly.py.zlib.b64`; decode using the snippet below. Auditor source SHA-256 `1dd51f801ea88ec35f91629296f1b215d4a7a809fc64d374c1453fdb00c2162f`.
- Read-only independent audit: **170,471 assertions PASS** across **76,800** policy/world/action decisions; verified causal truth, original outcomes, action choices, per-action tape indices, posterior/confidence, fit-only acceptance, held-out score, all aggregate metrics. An initial auditor-only issue came from tiny floating-point differences in top-two-hypothesis tie ordering; the auditor was corrected to use sequential accumulation for decision checks, while independently verifying grouped likelihoods. **Primary experiment unchanged and not rerun.**
- Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0; local one-shot wall-clock about 4.1 s. This is *not* a native Yggdrasil speedup. Cross-OS full regression and science acceptance unverified.

```bash
# In a new isolated directory containing prereg.json and the two source archives
python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_text())))" lr92af_run.py.zlib.b64
python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_text())))" audit_readonly.py.zlib.b64
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
python lr92af_run.py          # one scored run ONLY; refuses overwrite
sha256sum primary_result.json # expected dcdddb974dbc0148a2f0550b19b1549cda3f2b803968adce7be7a90a0d6cb950
python audit_readonly.py      # 170471 independent assertion checks
```

## Isolation and next question

The 256-state grammar and q0/q1/q2 contextual patterns are fixed synthetic constructs. Equal numerical evidence budgets establish a useful experimental-design comparison, **not** autonomous general reasoning or unknown-world transfer. The next useful falsification should independently test a safety gate calibrated on training-only causal contradictions and unfamiliar modes, without revising this failed EIG experiment.

**CI:** G29 source atlas is pinned to the predecessor indexed file set and rejects new `.json`/`.md` contribution paths. No relaxation of source-index checks or native source edits in this contribution. Keep draft, do not merge as accepted science.
