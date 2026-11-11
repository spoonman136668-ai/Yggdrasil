# WSP-35 — Blank-weight numerical circuit construction

**Research objective.** Starting from 216 zero bits per world, compile eight primitive Boolean operations and their DAG topology into one-hot numerical synapses. After cold restore, a generic rule-neutral runtime computes 8 target outputs from each of 256 **PRIMARY** circuits (2,048 target outputs) with no gradient optimization in the direct arm. DEV uses 64 separate chain-template worlds; PRIMARY uses interleaved/skip template worlds. Every primitive gate truth table and every parent is supplied to the compiler, so this tests **complete program compilation**, not intelligence or unknown-rule discovery.

- Independent provenance: preregistration-only commit `ad447decf89513681cb5dd878eccac17a067334f` (must precede implementation/results).
- Base: WSP-34 `e7c73a39ba8b604983d503858b2fcc68932ac925` (engineering qualified dual OS; WSP-34 science remains MIXED).
- Reproduction: `python research/contrib/chatgpt/WSP-35/run_dev.py --cohort DEV` (non-primary)
- Primary: `python research/contrib/chatgpt/WSP-35/run_dev.py --cohort PRIMARY` (one-shot after freeze)
- Focused controls: `python -m unittest discover -s research/contrib/chatgpt/WSP-35 -p test_*.py -v`.
- Complete existing tests and frozen assays: `python research/contrib/chatgpt/WSP-35/qualify.py`.

**Controls.** Zero blank weights, noncompositional last-table lookup, fully trained four-logit sigmoid/BCE primitive truth-table control (exact cache), and independent symbolic evaluator. Strongest trained control gets exactly the same source-provided primitive gate evidence and graph topology; it should be competitive, and a tie is expected. No target labels are available to the learner.

**Capacity.** 8 gates x (11 + 11 routing bits + 4 truth bits + 1 enable) = **216 writable binary bits**, initialized to zero. The numeric interpreter and compiler are authored source code and must be included in whole-process cost. Checkpoints are not 216 bytes; report their full serialized size. The trained comparator uses 4 float logits per primitive table and a different amount of storage.

**Important limitations.** This extension is not a new unknown-rule learner, no real-world generalization claim, no information efficiency/speed superiority claim, and no independent SCIENTIFIC_PASS; WSP-06 already demonstrated a narrower task-specific fully numeric circuit. WSP-33 negative and WSP-34 mixed findings are immutable predecessors.

Current README describes the implementation contract and does not itself claim a PRIMARY score, CI qualification, promotion or scientific acceptance.
