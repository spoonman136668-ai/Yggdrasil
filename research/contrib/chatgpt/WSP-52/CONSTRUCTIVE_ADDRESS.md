# WSP52 — constructive raw-acoustic addressing (exploratory successor)

**Classification:** Engineering/SELFTEST-only successor diagnostic, **not** a preregistered WSP52 study arm. The original `prereg.json` and its immutable source/threshold/seed policy remain unchanged. Prior SELFTEST outcomes (including the failed 64-step veto-only warmup) motivated this design, so results on those same fixtures are *exploratory*, never confirmatory.

## Mechanistic hypothesis

The previous 64-step RNN encoded entire action outcomes but used its representation only to **veto** the direct writer. Therefore it could not increase recall. A useful warmup must instead influence **where physical consequences are numerically written**. In this new diagnostic, 64 gradient steps fit a raw 4–6-bit-substring/entity association from the physical entity whose location observably changed. The fitted continuous margins select a raw acoustic address for grounded integer association writes. Unobserved objects' meanings are not supplied. After A, gradient updates freeze and six B consequences may add more integer writes, with no extra environment actions.

The model enumerates candidate *unlabeled* partitions but receives no token boundaries/IDs, true codewords, role annotations, hidden triples, evaluator targets or primary data. It assigns no privileged syntax. A supplied **unordered pair** effect address assumes the simulator's commutative destination-plus-verb action consequence; it may be misleading in any order-sensitive world. This is an explicit, unfavorable-to-novelty prior rather than evidence of discovered grammar.

## Fixed engineering knobs

- 36 A + 6 B environment consequences, **exactly 64** deterministic gradient updates, fixed rate **0.35**, eight output entity classes, zero extra intervention/query/reset.
- Six-valued 4–6-bit-partition family as before, **2-support** threshold, address margin **0.004**, 1% top-margin tie abstention, unanimous numeric-outcome support, and 2× top-vs-runner-up confidence rule. No post-test tuning in this branch.
- Zero-gradient ablation routes through the same learner but cannot write via the learned address; this controls whether gradient-written weights exist, **not** equal-capacity semantic quality.
- The prior strongest symbolic comparator and the independently trained 632-parameter raw recurrent comparator remain unchanged. Capacities and whole-process costs are **not matched**.
- Tests cover all six existing SELFTEST conditions, retain *every* negative, check exact action/gradient counts, invalid source, contradictory evidence, cold restoration and tampering. No DEV or PRIMARY evaluation is invoked.

## Qualification/evidence and scientific boundary

Run:
`python -m unittest discover -s research/contrib/chatgpt/WSP-52 -p 'test_*.py' -v`

Required engineering gates: inherited full WSP01–47 Linux/Windows regression and exact-source G29 atlas (Linux/Windows). Record exact SHA, results and any infrastructure failure in PR #943, not in the user's Library. No merge, official autonomy/controller integration, acceptance, deployment, paid service or scheduled tasks.

Only a **prospectively frozen**, independently meaning-identifiable successor source with order-sensitive counterworlds, matched controls and unbiased first-use evaluation could support a scientific claim about learned representations versus conventional/symbolic methods. Exploratory SELFTEST performance, positive or negative, does not confer that claim.


## Follow-up mechanism-control clarification

The gradient arm's initial six-fixture result was viewed before this additional control was implemented. The additional **count-only address control** therefore remains exploratory and cannot retroactively establish a confirmatory scientific result. It uses the identical three-part raw-stream hypothesis family, raw observation budget, commutative effect keys and numerical write/readout rules; it selects addresses using unanimous observed-frequency support rather than 64 learned gradient updates. Record the full six-fixture outcomes and persistent bits for both without changing thresholds or discarding negative outcomes. This control deliberately avoids the earlier structurally trivial zero-gradient ablation (which could not write at all). Capacity and total CPU/search work still differ and must not be claimed matched.
