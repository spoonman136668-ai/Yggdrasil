# WSP-105 — frozen historical TRAIN-only subject-specific two-hop control (DEV)

This stacked, isolated research experiment checks whether subject-specific two-hop graph paths add information beyond the broad WSP-104 relation-frequency heuristic. **It does not train a conventional KGE neural embedding, demonstrate a new direct-weight mechanism, prove task identifiability, or promote Yggdrasil's model.**

**Parent:** WSP-104 PR #1053, exact engineering-qualified source `308aacf8c5dbae6d7bb8dfaa506db009a3a7b0fa`, tree `d4a3c955215663fc4ed4dfe26133d5c01f8be859`. The original DEV source is a separately sealed historical Wikidata-derived mirror, not the official canonical Wikidata5M benchmark or current 2026 facts.

**Prerecorded before implementation:** `prereg.json` at commit `7121316f5ed5c922158f5e22a7cd6eea966f80fa`. It holds fixed all 4,096 WSP103 query groups, the complete 1/32 subject–predicate mask, WSP103 frozen answer witness and exact WSP104 baseline scores and rank digest. Missing or modified evidence must fail closed. Protected WSP101 worlds and official archive validation/test rows are never opened.

**Source-only controls:**
- Relearn **exactly the same per-relation 64 candidate sets** from all 20,677,636 retained training triples as WSP104, with two-pass Misra–Gries and retained-only exact recount. Verify the original WSP104 frequency rank digest and its previously measured Hits@1/10, and the reverse-ranking negative, before accepting a result.
- For each source query subject, select at most **32 retained outgoing neighbor edges** by a frozen digest ranking, without reading answer labels. Scan the retained source for two-hop paths from these neighbors to candidates in the **same** WSP104 relation candidate list; never count any hidden edge in a training signal.
- Compare frequency-only, reversed, path-only with abstention, and path-first with a frozen frequency fallback. Score macro any-answer Hits@1, Hits@10, best-answer MRR, supported query counts, CPU/wall and source custody; do not tune the path rule after seeing results.
- Interpret all outcomes as **DEV evidence only**, positive, null or negative; the strong independent fully trained conventional KGE and matched direct-weight learner remain separate uncompleted scientific comparisons.

**Engineering:** Only `research/contrib/chatgpt/WSP-105`, this workflow, and generated G29 atlas artifacts may change. Focused Linux and Windows fake-source tests run before final exact-tree full regression and any original masked TRAIN-only scoring.

**Authority:** Research branch only, draft/unmerged, no accepted model, official first-use, scheduling, runner control, FORGE/CKB control, paid API, model promotion, or deployment.
