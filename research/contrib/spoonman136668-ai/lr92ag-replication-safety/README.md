# LR-92AG — Adaptive intervention replication and bounded rare-error risk

**Disposition: EXTERNAL DEVELOPMENT FEASIBLE for unchanged EIG; separately DEVELOPMENT NO-GO for the stability safety gate.** This is synthetic contributor research, **not** native Yggdrasil training, general-world causal intelligence, official scientific qualification, merge approval, or production deployment.

## Source custody and frozen prospective design

- Owning repo: `spoonman136668-ai/Yggdrasil`, contribution path `research/contrib/spoonman136668-ai/lr92ag-replication-safety/`; parent research PR #1277 (LR-92AF, previously fixed NO-GO).
- Main tree at branch fork: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- The protocol was committed **before any new primary data was scored**, SHA-256 of decoded `prereg.json`: `266d74d154c98bf839a9580c41fa1190e728b201a3fe810532346e57792f38f1`.
- Original new executable source SHA-256: `03951faf21167132a42b0d06b1090eb688a2f65a164f62002107ac5efc1ffd22`. Unmodified parent LR-92AF exact source SHA-256: `02ac5e7a51a46a97a18791a85298fd27d11bdd0b64cb8506018e31291827e098`. Both were pinned in the preregistration and GitHub-verified before the primary run.
- The twelve pre-primary tests passed on fixture-only seeds. Primary seeds 929200711/712/713/714 were used **once**, with no postscore threshold changes, reruns, or tuning.
- 640 new worlds: **320 familiar-mode** (160 q0 + 160 q1), **320 unfamiliar-mode** (q2), using different seeds than LR-92AF. Base truth-table IDs remain disjoint from historical training IDs. All modes lie within the existing **256-state, two-context Boolean grammar**; the q label is available to the synthetic evaluator.

## Fixed comparison and risk margin

EIG, balanced and uniform-random policies use the exact frozen LR-92AF learned prior and Bayesian 256-hypothesis inference with **112 context-0 + 64 context-1** fitting interventions and **256 fresh validation** outcomes per world. Their environment has identical action-conditional potential-outcome tapes; at each step a policy sees only the result of its selected action. Every acceptance retains the frozen posterior confidence **≥0.90** and *fit-only* misfit survival p >0.01.

Three safety controls reuse EIG's exact 64 selected outcomes, without adding data: (1) stability gate requiring the MAP candidate after 48 selected actions to remain the final MAP with intermediate probability ≥0.25; (2) seeded sham 5%-probability veto; (3) **prospectively** tightened 0.95 confidence cutoff. The latter is a diagnostic comparison, **not** a replacement of the previously frozen learner's threshold.

Before scoring we set the unfamiliar-risk limit to **at most 3% absolute observed false accepted mechanisms**, and required the **one-sided exact 95% Clopper–Pearson upper bound on paired *harmful discordance*** (EIG false while balanced not false) to be ≤4.5 percentage points. This bound deliberately ignores any balanced-only mistakes and therefore conservatively bounds relative harm; it is not proof of zero risk. The primary learner also had to gain ≥20 correct familiar accepted mechanisms over both balanced and random, improve held-out accuracy by ≥0.3 percentage points over balanced, and preserve exact cold-restored weights and equal observations.

## One-shot result

| Arm | Accepted correct familiar /320 | Accepted incorrect familiar | Accepted correct unfamiliar /320 | Accepted incorrect unfamiliar | Held-out prediction accuracy |
|---|---:|---:|---:|---:|---:|
| **EIG** | **73** | **2** | **19** | **2** | **63.5907%** |
| Balanced | 29 | 0 | 5 | 0 | 62.8461% |
| Random | 21 | 0 | 6 | 0 | 62.9327% |
| Stability-gated EIG | 73 | 2 | 19 | 2 | 63.5907% |
| Sham 5%-veto EIG | 69 | 2 | 17 | 2 | 63.5907% |
| Strict 0.95 EIG | 28 | 0 | 2 | 0 | 63.5907% |

EIG's **+44 exact familiar mechanisms** over balanced at the same action budget is replicated across all four seeds (+7, +11, +11, +15). The unfamiliar error rate is 2/320 = **0.625%** (balanced: 0/320). The one-sided 95% upper confidence bound on harmful discordance is **1.9543%**, below the **preregistered 4.5%** margin. All **7/7 EIG feasibility checks passed**.

The stability safety gate passed 3/4 of its own checks and failed to block either of the two errors, so it is a **DEVELOPMENT NO-GO**. The strict95 control blocked both unfamiliar errors but reduced accepted correct familiar mechanisms from 73 to 28. Neither gate is promoted. **The positive result belongs to the unchanged original EIG policy**, and does not reverse the historical LR-92AF NO-GO against its separate zero-error criterion.

## Independent engineering evidence and limitations

- Primary one-shot source and protocol SHA-256 checks PASS. Primary original complete raw result: **17,312,767 bytes**, SHA-256 `6a444346d395d5971386243174e47c4cfacc82d0c842ba74d3919e2cafd8e029`.
- Independently authored read-only auditor: **341,856 assertions PASS** across all 640 worlds, checking **122,880 selected counterfactual tape outcomes**, Bayesian posteriors, 64-action budgets, action choices, fit-only acceptance, validation, risk CI and frozen decisions. Original audit source SHA-256: `2b15766c20a2177386a643c5a8bf4ffa663c88c8a273b64f43d73a1b0699a7bd`.
- GitHub contains exact frozen parent and LR-92AG source, the preregistration, original auditor, all frozen checks, aggregates, and **a compact paired ledger for every one of the 640 worlds**. The binary ledger has 10,240 bytes, SHA-256 `b71c9cfeda00a8686353d804ca950a5892333b701f2af3c3ca56bab025ce4d24`, compressed as `paired_ledger.bin.zlib.b64`.
- The **complete original 17.31 MB raw observation and action-decision record is now published on GitHub** as the lossless `primary_result.json.zlib.b64` (794,521 bytes). GitHub readback of the entire encoded file matched Git blob SHA-1 `cc31ee5f75b2cf0812616f1bfdf8c7b64e06f97a` and encoded-file SHA-256 `5cb9ed2f2668315ca6772bd899255abb643aa2be77d525d18e279b0fd2d2b85c`. Its decoded original SHA-256 is `6a444346d395d5971386243174e47c4cfacc82d0c842ba74d3919e2cafd8e029`. The paired ledger independently captures the corresponding accepted/exact/false/MAP-correct flags and held-out-correct counts. Use the published raw record for read-only audit; regenerate only in a **different clean directory** for independent reproducibility.
- This tests a toy, fully specified causal grammar with known q-mode identity, not unfamiliar open-world causal mechanisms. This is one synthetic development cohort and **not** an external native Yggdrasil experiment or general safety guarantee. Full original repository regression and cross-platform scientific acceptance remain unverified. CI's G29 source atlas is known to fail for new indexed contribution files and must not be bypassed or mislabeled as scientific failure.

## Reproduce in an isolated empty directory

The five `*.zlib.b64` evidence/source files use standard base64 of zlib-compressed bytes. Decode the sources and protocol before running:

```bash
python - <<'PY'
import pathlib,base64,zlib
for name in ['prereg.json','lr92ag_run.py','lr92af_frozen.py','audit_readonly.py','test_preprimary.py']:
    p=pathlib.Path(name+'.zlib.b64')
    pathlib.Path(name).write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))
PY
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
python -m unittest test_preprimary -v  # 12/12 structural PASS
python - <<'PY'
import pathlib,base64,zlib
p=pathlib.Path('primary_result.json.zlib.b64')
pathlib.Path('primary_result.json').write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))
PY
sha256sum primary_result.json          # expect 6a444346d395d5971386243174e47c4cfacc82d0c842ba74d3919e2cafd8e029
python audit_readonly.py               # expect 341856 read-only checks
# For an independent primary replay, use a separate EMPTY directory
# containing the same frozen decoded sources and prereg:
# python lr92ag_run.py                 # refuses overwrite; compare original SHA PASS
```

**Paired ledger decoding:** decompress `paired_ledger.bin.zlib.b64` to 10,240 bytes, interpret 640 records × 16 bytes each. Each record starts with unsigned bytes `(seed_index, world_id, q, base_id)`, followed by six two-byte arm records in order `(eig, balanced, random, stability, sham_veto, strict95)`. Arm byte 1 contains flags bit0=accepted, bit1=exact accepted, bit2=false accepted, bit3=MAP exact; arm byte 2 contains the number of correct held-out outcomes (0..255) out of 256. Reaggregation should reproduce `result_summary.json`. The ledger is sufficient to independently check paired outcome comparisons, **not** the underlying observation-level audit.

**Decision:** EIG remains an independently promising development candidate. No native integration, merges, background tasks or protected scientific first-use were performed.
