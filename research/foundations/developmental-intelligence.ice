TITLE: YG-R1 — Developmental Intelligence Literature Map
DATE: 2026-09-17
STATUS: ACTIVE RESEARCH BASELINE
TRACK: DG-1
CONFIDENCE: SUPPORTED

QUESTION
What prior work most directly constrains Yggdrasil's thesis that compact developmental information can grow useful, repairable, resource-bounded neural phenotypes?

WORKING THESIS
Cellular/developmental intelligence is the primary Yggdrasil architecture. Existing literature establishes important ingredients independently, but does not establish the full Yggdrasil claim. The research program must therefore test the composition: local developmental rules + functional computation + structural plasticity + regeneration + continual retention + resource pressure + ancestor-derived capability.

EVIDENCE — ESTABLISHED PRIOR RESULTS

1. NEURAL CELLULAR AUTOMATA / MORPHOGENESIS
Mordvintsev et al. (2020), Growing Neural Cellular Automata, showed that a shared differentiable local update rule can grow a target morphology from a seed, persist, and regenerate after damage when trained for those behaviors. The canonical system uses local perception and a shared update rule over cell state.
Relevance: establishes compact shared developmental dynamics and regeneration, but the target is morphology rather than general computation.

2. DISTRIBUTED FUNCTIONAL COMPUTATION
Randazzo et al. (2020), Self-classifying MNIST Digits, showed that NCA cells using local message passing can coordinate to classify the global digit shape and can recover classification after changes to the underlying digit.
Relevance: demonstrates that NCA dynamics can perform nontrivial distributed computation, not only visual growth.

3. DEVELOPMENTAL PROGRAMS THAT GROW NETWORKS
Najarro, Sudhakaran, and Risi (2023), Towards Self-Assembling Artificial Neural Networks through Neural Developmental Programs, investigated neural developmental programs operating through local communication to grow task-performing neural networks across supervised and reinforcement-learning settings.
Relevance: directly supports treating development as a mechanism that constructs functional neural topology.

4. GENOTYPE-TO-PHENOTYPE WEIGHT GENERATION
Ha, Dai, and Le (2016), HyperNetworks, showed that one network can generate weights for another and explicitly framed the relationship as analogous to genotype and phenotype. Later continual-learning work with task-conditioned hypernetworks showed that generated task-specific weights can be retained through compact conditioning and output regularization.
Relevance: supports the possibility that persistent information can encode multiple phenotypes more compactly than storing each full task network independently. It is not, by itself, cellular development.

5. DIFFERENTIATION / PROGRAM MODULATION
Hernandez, Vilalta, and Moreno-Noguer (2021), Neural Cellular Automata Manifold, showed a higher-level encoding can modulate NCA parameters to generate different developmental outcomes from a shared system.
Relevance: suggests a tractable route from genome-like conditioning to distinct phenotypes.

6. PRIVATE MEMORY / DEVELOPMENTAL MODULATION
Guichard et al. (2025), EngramNCA, introduced visible state plus private cell-internal memory and a second NCA that modulates private genetic memory.
Relevance: supports separating externally interacting phenotype state from persistent or semi-private developmental state. Evidence is early and must not be treated as proof of scalable cognitive memory.

7. DEVELOPMENTAL REASONING PROBES
Guichard et al. (2025), ARC-NCA, and Xu & Miikkulainen (2025), Neural Cellular Automata for ARC-AGI, explored NCA update rules on ARC-style transformations.
Relevance: indicates current interest in developmental computation beyond morphology. These are early proof-of-concept results and do not establish general reasoning or continual development.

8. STRUCTURAL PLASTICITY / DYNAMIC SPARSITY
Evci et al. (2020), RigL, showed that changing sparse connectivity during training can achieve strong sparse-network performance. Structured dynamic sparsity work has also shown that hardware-realizable structured sparsity matters because theoretical parameter sparsity does not automatically become practical speed or memory savings.
Relevance: Yggdrasil must distinguish logical sparsity from realized hardware savings. Growth/prune operations require resource-aware representations.

9. CONDITIONAL COMPUTATION / EXPERT ROUTING
Shazeer et al. (2017) and Switch Transformers (Fedus, Zoph, Shazeer, 2021) established sparse expert routing as a strong baseline for increasing total capacity without activating all parameters on every input.
Relevance: this is a direct conventional competitor to Yggdrasil's active-phenotype thesis. Development must outperform or add capabilities that routing alone does not provide, such as regeneration, developmental reuse, repair, or compact inheritance.

10. PARAMETER-EFFICIENT ADAPTATION
Hu et al. (2021), LoRA, established low-rank adapters as an efficient way to add task capability around a frozen pretrained core.
Relevance: LoRA-like cells are a promising later phenotype granularity for DG-1F through DG-1H. Static LoRA and learned adapter routing are mandatory baselines.

11. CONTINUAL LEARNING
Continual-learning literature consistently identifies catastrophic forgetting and the stability-plasticity tradeoff as central constraints. PackNet demonstrated one structural approach: iterative pruning can reserve parameters for old tasks and free parameters for new tasks.
Relevance: Yggdrasil must measure acquisition, retention, reuse, interference, and total versus active capacity. A growing system that merely allocates fresh parameters per task is not sufficient.

ANALYSIS
The strongest evidence for Yggdrasil is compositional rather than direct. Prior work establishes:
- local shared rules can coordinate global behavior;
- local rules can regenerate damaged morphology;
- developmental programs can construct functional networks;
- compact generators can parameterize multiple task networks;
- sparse routing can decouple active compute from total capacity;
- adapter-style modules can add capability around frozen pretrained intelligence.

What remains unestablished is the Yggdrasil conjunction:
A compact persistent genome learns to develop task-relevant neural modules, reuse prior structure, retain old capabilities, repair damaged function, and keep active resource growth substantially slower than accumulated capability growth.

CRITICAL RISKS
- Development may collapse into an ordinary centralized controller that happens to emit "cell" parameters.
- Cells may differ representationally without acquiring useful specialization.
- Regeneration may restore geometry or activation statistics without restoring task function.
- Growth may solve forgetting by unbounded parameter accumulation.
- Communication overhead may erase savings from sparse activity.
- Re-generating a phenotype may cost more time/energy than storing it.
- Local credit assignment may become unstable as structural actions become discrete.
- Consumer hardware may fail to realize theoretical sparsity gains.

DECISION
Proceed with DG-1 as a staged falsifiable program. Start by reproducing known NCA dynamics and then move quickly to functional regeneration. Delay large pretrained-model integration until cell state, developmental update, measurement, and resource accounting are experimentally stable.

OPEN QUESTIONS
- What minimum cell representation can support functional differentiation without hiding a centralized network inside each cell?
- Should early cognitive phenotypes use grids, fixed graphs, or learned sparse graphs?
- Which information belongs in genome parameters versus persistent cell state versus regenerable phenotype weights?
- How should developmental cost be priced relative to resident bytes and active FLOPs?
- Can a regenerated phenotype recover capability from genome + compact state without replaying full training data?

NEXT EXPERIMENT
Reproduce a small canonical NCA growth/regeneration system, then run a functional NCA task with explicit damage and functional recovery metrics before introducing structural growth.

PROVENANCE
- Mordvintsev, Randazzo, Niklasson, Levin. Growing Neural Cellular Automata. Distill, 2020. DOI: 10.23915/distill.00023
- Randazzo, Mordvintsev, Niklasson, Levin, Greydanus. Self-classifying MNIST Digits. Distill, 2020. DOI: 10.23915/distill.00027.002
- Ha, Dai, Le. HyperNetworks. arXiv:1609.09106, 2016.
- Hernandez, Vilalta, Moreno-Noguer. Neural Cellular Automata Manifold. CVPR 2021. DOI: 10.1109/CVPR46437.2021.00989
- Najarro, Sudhakaran, Risi. Towards Self-Assembling Artificial Neural Networks through Neural Developmental Programs. arXiv:2307.08197, 2023.
- Evci et al. Rigging the Lottery: Making All Tickets Winners. ICML 2020.
- Hu et al. LoRA: Low-Rank Adaptation of Large Language Models. arXiv:2106.09685, 2021.
- Shazeer et al. Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer. ICLR 2017.
- Fedus, Zoph, Shazeer. Switch Transformers. arXiv:2101.03961, 2021.
- Mallya, Lazebnik. PackNet. CVPR 2018. DOI: 10.1109/CVPR.2018.00810
- Guichard et al. EngramNCA. arXiv:2504.11855, 2025.
- Guichard et al. ARC-NCA. arXiv:2505.08778, 2025.
- Xu, Miikkulainen. Neural Cellular Automata for ARC-AGI. arXiv:2506.15746, 2025.
