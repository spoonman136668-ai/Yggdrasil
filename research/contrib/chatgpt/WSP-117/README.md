# WSP-117 — Can programmed knowledge induce an *unnamed* relation?

**Research-only source-safe calibration; no independent scientific first-use and no Yggdrasil native integration.**

## Why this gate exists

[WSP-116 draft #1108](https://github.com/spoonman136668-ai/Yggdrasil/pull/1108) qualified a substantial real historical relational foundation: 20,677,636 retained facts, three numerical source tiers, and **1190 vs 981** top-1 correct answers (full vs quarter) on 4,096 **previously consumed** masked TRAIN questions. The full graph numerics **tied an independently implemented exact symbolic two-hop ranker on all 4096 questions**. Larger interconnected information improves retrieval on the consumed diagnostic, but it does not prove the model created any new relation.

The next scientific question is whether an unlabelled relationship category can be **inferred from observed pairs, rejected when unidentifiable, and applied to unfamiliar entity pairs**, rather than simply executing a supplied predicate lookup. This WSP-117 branch is a *small interface and identifiability fixture* before spending new source budget.

## Preregistered before implementation

The immutable `prereg.json` is the first branch commit. Eight source-safe synthetic directed graphs (seeds 117000..117007), six primitive relation edge maps and 36 possible unknown two-hop operators. No FKP-series consumed data, archived Wikidata TRAIN, official validation/test, source-protected records, or reserved science seeds 117800..117863 are read.

`fixture.py` constructs each small graph only from public synthetic structure. It offers positive demonstrations `(source, observed target)` for a previously unnamed relation. The candidate writes direct integer contradiction counts into a **6×6 int32 numeric parameter matrix (144 raw bytes)** and enumerates candidate primitive-relation compositions. On disjoint, previously undemonstrated entity-pair sources it either predicts the composed destination or abstains when two or more relation hypotheses fit the evidence.

**A separate exact symbolic control** gets precisely the same visible graph and demonstrations; any tie is reported as a tie, not unique mechanism or intelligence. A deliberately nonidentifiable one-example condition makes two different relation laws observationally identical, so the candidate **must abstain**. Cold exact readback and tamper rejection are mandatory.

This fixture intentionally tests the interface, demonstrator sufficiency and ambiguity boundaries. It is **not** an unknown causal-law discovery benchmark: its two-hop operator family is known in advance to both candidate and control. No trained GRU/MLP, independent held causal family or generalization claim can be made until a separate preregistered native-owner source is qualified.

## Qualification

Focused fixture tests plus full inherited Yggdrasil root tests and source-derived G29 atlas must pass both Windows and Ubuntu at a pinned exact code/tree. No WSP-116 historical 21M-row source rescan, model write, new scheduler/runner, paid API, scientific first-use or accepted-ref mutation.

Expected classification is **ENGINEERING_FIXTURE_PASS** if mechanism/cold/source fences pass. There is **no SCIENTIFIC_PASS**, even if all source-safe cases pass. To progress, freeze an entirely new independent unseen real relation-family source, give all methods identical evidence/actions and budgets, train strongest conventional GRU/MLP models, compare to exact symbolic composition and test true transfer/interference/causal consequences. If symbolic equals candidate, stop making unique discovery claims.

Run locally on isolated checkout:

```console
python -B -m unittest discover -s research/contrib/chatgpt/WSP-117 -p test_wsp117.py -v
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```
