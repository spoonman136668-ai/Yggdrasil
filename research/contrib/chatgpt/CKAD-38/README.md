# CKAD38 — Contradiction-triggered read-only native causal-memory recall

Research-only experimental branch from qualified CKAD37 [draft #1260](https://github.com/spoonman136668-ai/Yggdrasil/pull/1260). **Not accepted-model promotion, not Forge/controller operation and not actual-world grounding.**

CKAD37 trained the existing NativeEpisodeExperience stream on genuinely observed **synthetic** two-stage A→B→A episodes. It improved pooled late-rule Brier against the strongest Beta controls but failed its frozen >=0.025 absolute margin and one return-retention condition. CKAD38 tests one specific native mechanism hypothesis with fresh seeds and a stronger conventional adaptive control, rather than replaying old worlds or moving the goalposts.

## Native change

An opt-in, pure-read method `NativeEpisodeExperience.context_forecast_recall()` was added only on this isolated research branch. It reuses the SAME existing native source ledger, context block library, source-outcome-fitted posterior and stream contradiction detection. Within 24 actually witnessed episodes after a recorded internal detection it squares the existing context-model posterior weights and normalizes (posterior concentration / historical regime recall). Outside that event-triggered window it calls the unchanged native context mixture. Both transition and observed-next-state-conditioned terminal forecasts are prequential. The method cannot write to the model, invent outcomes, read hidden source labels, or alter checkpoint schemas. Retained source coefficients, episode IDs and prior cold snapshots remain untouched.

The experiment trains one existing immutable source learner through `observe()` for every actual public event. It compares two readouts of that same learner (default vs recall), a distinct source-identical repair-disabled ablation, the original nonstream native cumulative learner and conventional controls; it does not create multiple competing research architectures.

## New causal worlds

Two independent worlds per seed; two structural variants (private seed/world parity), with genuinely changed transition and delayed terminal causal functions, not merely bit relabelings. Each public episode contains paired numeric views, first intervention, observed next-state, second intervention and observed delayed binary consequence. The stable causal view coordinate is mixed with independently varying nuisance bits. Rule changes occur without any model-visible boundary ID; private A→B→A phase labels are evaluator-only.

Two initial 48-event warm memories then one uninterrupted stream; independently chosen source actions are identical for every arm. A period varies 88–104 observed events, B 64–80, A-return 64. Score each stage's Brier **before** revealing its corresponding consequence.

## Controls and measurement

Strong conventional controls use all same observed action-outcome information: independent Beta(1,1) per public causal cell with full history, fixed windows 12/24/48, exponential discounts 0.85/0.95, and a prequential online Hedge mixture (fixed eta=4) selecting among all six genuinely trained conventional experts from prior consequences. Equal-source unmodified native stream, native repair-disabled stream, global native and constant 0.5 sham are separately logged. All original public steps, model forecasts, cold SHA/bytes, native stream detections and evaluator scores are preserved in Git.

Primary metric is pooled late-B plus late-A-return prequential binary outcome Brier, averaged over transition and terminal. On BOTH fresh original pilots, native recall must achieve Brier <=0.145 and >=0.025 absolute gain over BOTH default native stream and the strongest conventional model including Hedge, plus no worsening early B or late A-return, source-only evidence integrity, exact native cold and unchanged original first 48 source memories/archived block, and independent event+control reconstruction. Otherwise `SCREEN_NO_GO`. A first-use seed is never retuned/replayed, regardless of result; a pilot GO still does not authorize SCIENTIFIC_PASS or primary run.

### Provenance and safeguards

- Pre-source prereg: `e06f9ec931f7454b45e05ecd23299c3695e2a40f`.
- DEV-only fixtures `88511/88512`; original pilot `14181/14182`; reserved primary `24181/24182/24183`; earlier CKAD37 original `14071/14072` forbidden to replay.
- Both preflight operating systems must pass the new full native development fixture and independent strong-control reconstruction before the exact source Git blob lock and original two pilots.
- Original pilot results, SHA receipts, independent audit, and final full regression on **both Linux and Windows** must pass on the exact evidence candidate commit.
- No merge, main update, owner first-use, network-paid data, scheduled tasks, runtime promotion, controller edits, live operation, or claims of general intelligence.
