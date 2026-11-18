# LR-92AD — Learned cross-context causal relations

**Disposition: EXTERNAL DEVELOPMENT NO-GO.** This is an independently conducted synthetic causal-learning experiment, **not native Yggdrasil training or official science**. It is a distinct successor to [LR-92AC PR #1263](https://github.com/spoonman136668-ai/Yggdrasil/pull/1263); prior negative results are unchanged.

## Preregistration and one-shot source

- `prereg.json` committed at **`ebf528a7454d2a60b9c08a4002402462c7cb8e80` before any primary scoring**, SHA-256 `7626377a32af6d84f80d3c9edad5b7d08f08d3084473b33f5fb9e413bafd2afd`.
- Exact source was committed before scoring at **`a6f9361526cd9cb11f5e8d462dea17e7d865bb30`** as `lr92ad_run.py.zlib.b64`, the standard base64 encoding of zlib-compressed original 12,861-byte Python source. Decoded source SHA-256: `32171291d945f7aedca941890b4137caef648a455bbb34a9c2478e3e36087b47`.
- Frozen training seed: 929200401; evaluation seeds: 929200411, 929200412, 929200413. All datasets are original procedural Boolean causal-world tasks, not external personal data.
- 128 historical training episodes, 12,288 historical action outcomes. Each episode has two contexts and four interventions. Training is restricted to base truth-table IDs 0–7; 240 evaluated worlds use **disjoint IDs 8–15**, including 48 with a completely unseen context-change mode.
- Seven arms all receive 128 fit observations per test world (112 in context 0, 16 in context 1), plus 256 independently generated validation observations. Total primary fit: 30,720; validation: 61,440.
- Context-sensitive learner estimates per-action cross-context outcome-change probabilities from historical observations, with Beta smoothing. These learned coefficients inform a 256-state causal-truth-table posterior. Conventional CART, RF16 and logistic learners are fully fitted on the same historical observations and receive the same test-world fitting observations.
- Model acceptance is fixed in advance: posterior >=0.9 **and fit-data** binomial goodness-of-fit survival p >0.01. Held-out validation outcomes are never used to decide acceptance.

## Frozen outcome

| Arm | Exact accepted familiar / 192 | Exact accepted unseen / 48 | False constructions | Held-out accuracy |
|---|---:|---:|---:|---:|
| Contextual learned relation | 0 | 0 | 0 | **62.3177%** |
| Global pooled relation | 0 | 0 | 0 | 60.8301% |
| Shuffled-context relation | 0 | 0 | 0 | 60.9082% |
| Independent uniform Bayes | 0 | 0 | 0 | 59.9349% |
| RF16 | 0 | 0 | 8 | 59.8177% |
| CART | 0 | 0 | 2 | 59.0592% |
| Logistic regression | 0 | 0 | 0 | 58.6882% |

**Four of seven criteria passed; three failed.** The method improved held-out prediction by +2.3828 percentage points versus independent inference (exploratory paired 95% bootstrap CI +1.989 to +2.806) and +2.50 points versus the strongest conventional arm. But **zero exact mechanisms were accepted** at the preregistered posterior threshold, so causal discovery qualification **failed**.

The independent auditor observed 123/240 correct but **unaccepted** raw maximum-posterior truth-table selections for the relation learner, versus 51/240 for independent inference. This is a descriptive after-the-fact diagnostic; it does not change the registered acceptance rule or the NO-GO verdict.

## Integrity, evidence and reproducibility

- Frozen original 6,260,761-byte `primary_result.json`: SHA-256 `a2e8144f48595168b4c741157e08dfb3584069c7822f0ec33c31fff209f7f035`. Full original primary raw observation record remains in isolated local custody, **not uploaded**.
- `result_summary.json`: primary aggregate results and learned weights; `scored_pair_ledger.json.zlib.b64`: all 240 seed/world IDs, true base IDs, seven-arm outcome counts, accept/exact/false decisions; decoded SHA-256 `7dcfd1c0c7790bbb45ff68d61c6aac5b840cbdbdb1b0a2e99d2125d9346cd5ed`, decoded length 25,766 bytes. The scored ledger **does not include raw fit/validation observations**.
- Independent read-only audit original source `audit_readonly.py.zlib.b64` decoded SHA-256 `834ace6a42c089a2325c9d131d6f716f019d3c4b6d8ceea7a8468d55929d4ac4`. Local audit: **22,154 assertions PASS**; frozen original audit receipt SHA-256 `afea3c224a6a1297ff80447b484fdf7ec52ab66bf9985bae36822a28ef0ec70e`.
- No scored rerun, additional evaluation cohort, post-result threshold change, hidden validation usage, or protected Yggdrasil scientific first-use.
- Local Python 3.13.5, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0; 1.277 s local end-to-end script wall time including 0.051 s model training, excluding dependency installation. This is **not a measured Yggdrasil whole-process speedup**.

### Reproduction in a fresh isolated directory

Decode both `*.py.zlib.b64` files using:

```bash
python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_text())))" lr92ad_run.py.zlib.b64
python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_text())))" audit_readonly.py.zlib.b64
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
python lr92ad_run.py           # refuses to overwrite any primary_result.json
sha256sum primary_result.json  # expect a2e8144f48595168b4c741157e08dfb3584069c7822f0ec33c31fff209f7f035
python audit_readonly.py       # expect read-only audit PASS, 22154 checks
```

Execute in a clean working directory with `prereg.json` and decoded scripts; keep the repository's already-committed summaries separate from the freshly generated raw file.

## Boundaries and next research

The controlled worlds are hand-authored conditional Boolean mechanisms, not open-ended environments. Training learned a probabilistic relational operator, but this is **not a demonstrated native trainable Yggdrasil learner**, JEPA, causal intelligence, cold native retention, or unfamiliar-family scientific validation.

The promising prediction signal justifies studying causal posterior calibration and richer grounded mechanisms in a **separate prospective protocol**, without changing the failed original. Do not promote or merge as scientific acceptance.

**CI limitation:** G29 source atlas currently rejects contribution `.json`/`.md` paths added after the pinned source snapshot. This existing engineering owner issue is distinct from the scientific outcome. No atlas weakening, native model changes or controller mutations performed.
