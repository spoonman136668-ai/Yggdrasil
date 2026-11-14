# WSP-101 — Paired-world causal transfer task

**State: Development task construction only. No model training, original first-use or scientific superiority.**

## Plain English

Each pair of simulated machines looks *identical when merely observed*. A useful action changes hidden memory, but the two machines still look the same right afterward. After another step, their observed behaviors diverge. This gives us a controlled task where **intervention, observation of consequences, and keeping track of history** are necessary to identify which mechanism is operating.

Unlike WSP-100's 256/2,048-program practice catalogues, WSP-101 first tests whether different causal laws are truly indistinguishable without acting. A later gate must determine whether the problem remains challenging yet identifiable for fully trained recurrent and independent broad symbolic learners under a fixed eight-action intervention budget. This development gate does not make that scientific claim.

- WSP-101 prospective high-level design commit: `2e7c31d8579efca478b883de5a4c60aa9af729f5`
- Detailed fixture rules frozen **before code** at: `385b3a9b3dcbcf8509e7bc6609b3d3f4e74481a2`
- DEV contexts: 0..7, two hidden-law modes per context. Only these may be generated.
- Original FIT 101011–101026, TRANSFER 101101–101132, NOVEL 101201–101216, and RESERVED 101301–101332 **are blocked/unconsumed**.
- Mode is not part of any learner-facing source record; observers expose only `reset` and `step`. The Python interface is **not** a security boundary against malicious introspection—training code must consume only source episodes and never an oracle reference.
- Six four-valued visible channels, two four-valued hidden memory latches, four actions. Action 0 passive is exactly neutral for hidden memory; 16 matched passive four-step episodes per paired context. A causally relevant non-passive action has a **delayed** visible effect that differs across paired mechanisms.
- The evaluator-only witness and no-latch negative control are **not** learner inputs. Equal observation is not equivalent to equal causal behavior.

Run only the development unit tests: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s research/contrib/chatgpt/WSP-101 -p 'test_*.py' -v`.

**Next:** Freeze active intervention source policies, broad symbolic and trained recurrent baselines and strict matched budgets **before** any original-first-use. No promotion into accepted Yggdrasil or autonomous loop.

## Large-first capacity test and original negative

This is a separate **synthetic association-capacity DEV track** within WSP101; it does not replace the protected paired-world original scientific plan.

- First frozen concept: `704d7d876ca1fea5a709a3614fd2afb31b951025`.
- Largest tier: **64×64×4096 = 16,777,216 possible** links, **32,768 actually observed** source links and **524,288 intended unseen one-hop** queries plus 8,192 two-hop queries. These are synthetic, generated laws, NOT real-world factual knowledge.
- [Original max-tier DEV execution 43623476680](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43623476680) **FAIL: SOURCE UNDERIDENTIFIED** before any heldout scoring. Multiple admitted operator programs fit the eight source examples but disagree on some unseen input. The weight writer refused to pretend it had learned the answer.
- Preserved immutable run source, SHA, classification and the frozen smaller tiers in `WIDE_MAX_NEGATIVE.json`. The direct-weight and independent symbolic fitting rules and synthetic truth generator remain unchanged.
- The explicit `--fallback-only` harness now executes **32×32×2048** then **8×8×1024** only if needed. Neither changes the eight observations per relation or uses the already consumed max tier as fresh science.
- Even a successful fallback means bounded operator compilation and exact symbolic competition, not AGI, true novel causal discovery or a demonstrated end-to-end weight-programming advantage.

**Next real knowledge phase:** Wikidata structured triples are CC0; select a frozen verifiable CC0 subset, independent property splits and cross-domain relation composition. ConceptNet CC BY-SA needs separate licensing and attribution/share-alike custody. Do not mix sources without provenance.
