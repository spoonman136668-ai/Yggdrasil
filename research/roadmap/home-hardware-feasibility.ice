TITLE: YG-R5 — Home-Hardware Feasibility Matrix
DATE: 2026-09-17
STATUS: PLANNING BASELINE
TRACK: DG-1
CONFIDENCE: PLAUSIBLE / ESTIMATED

QUESTION
Which Yggdrasil experiments are practical on ordinary home hardware, and where should scale be capped until smaller experiments justify expansion?

IMPORTANT
All capacity statements below are ESTIMATED planning guidance, not measured results. Actual feasibility depends on framework, tensor shapes, batch size, precision, activation storage, optimizer, operating system, and GPU architecture. Every implementation stage must replace estimates with measured peak RAM/VRAM and wall-clock data.

MEMORY REFERENCE
Approximate raw weight storage only:
- FP32: 4 bytes / parameter
- FP16/BF16: 2 bytes / parameter
- INT8: ~1 byte / parameter plus metadata/scale overhead
- 4-bit: ~0.5 byte / parameter plus metadata/scale overhead
Training requires additional memory for activations, gradients, optimizer state, temporary buffers, and framework overhead. Full-parameter Adam training can require many times raw weight memory. Frozen-core adapter training is therefore preferred for later home-hardware stages.

FEASIBILITY MATRIX

CPU ONLY
Best-fit stages:
- DG-1A small NCA reproduction
- DG-1B Boolean, consensus, synthetic-grid tasks
- small DG-1C specialization studies
- deterministic damage/regeneration sweeps with small grids
Recommended scale discipline:
- small batch sizes
- 16x16 to 64x64 grids as initial range
- small shared update networks
- short development horizons
Avoid initially:
- large pretrained seeds
- large hyperparameter sweeps
- high-resolution NCA
Expected bottleneck:
- training wall-clock rather than model residency
Verdict: SUFFICIENT for foundational science.

8 GB VRAM
Best-fit stages:
- all DG-1A/B/D experiments
- moderate multi-task DG-1C/E
- small module-cell DG-1F
- frozen small pretrained seed with parameter-efficient modules
Recommended strategy:
- mixed precision where stable
- gradient accumulation instead of large batches
- module-level sparsity
- checkpoint activations only if needed
- keep first pretrained seed substantially below the maximum model that can merely fit
Avoid initially:
- full fine-tuning of multi-billion-parameter models
- large expert populations resident simultaneously
Verdict: TARGET MINIMUM GPU TIER for the first complete DG-1 research loop.

12 GB VRAM
Best-fit stages:
- broader DG-1C/E sweeps
- module-cell experiments with more phenotype variants
- small-to-midsize frozen seed plus adapters
- early ancestor-adapter inheritance
Advantage over 8 GB:
- larger batch/sequence or more concurrent phenotype modules, improving experimental throughput more than changing the core research questions
Verdict: COMFORTABLE for most pre-language-scale DG-1 work.

16 GB VRAM
Best-fit stages:
- richer DG-1F/H developmental adapter populations
- small pretrained language/vision seed with several adapter cells
- broader continual-development sequences
- stronger static-router / hypernetwork baselines
Recommended discipline:
- preserve matched-budget comparisons; extra memory should increase experiment breadth before model size
Verdict: STRONG CONSUMER RESEARCH TIER.

24 GB VRAM
Best-fit stages:
- all earlier work with larger sweeps
- moderate pretrained core with developmental adapters
- more realistic ancestor-inheritance experiments
- simultaneous baselines and richer telemetry
- testing hibernation/wake with meaningful module populations
Risk:
- availability of memory can tempt premature scaling and hide inefficient developmental design
Verdict: HIGH-END CONSUMER TIER; sufficient for substantial DG-1G-I research without requiring data-center hardware.

MODEL-SEED POLICY
For DG-1G/H, choose the smallest pretrained seed that can express the test task well enough to isolate the developmental question.
Selection order:
1. task adequacy
2. reproducible local execution
3. frozen-core adapter support
4. memory headroom for developmental population + telemetry
5. only then parameter count

Do not choose the largest model that fits. Maintain at least enough memory headroom for:
- developmental modules
- optimizer state for trainable modules
- activations
- telemetry buffers
- damage/regeneration experiments

EXPERIMENT CLASS BY HARDWARE

CLASS A — MICRO
CPU or any GPU.
Tasks: XOR, parity, consensus, simple transformations.
Purpose: unit-test developmental mechanics.

CLASS B — CELLULAR FUNCTION
CPU or 8 GB GPU preferred.
Tasks: synthetic grids, MNIST-scale classification, small ARC-like transforms.
Purpose: functional specialization and regeneration.

CLASS C — CONTINUAL ORGANISM
8-12 GB GPU preferred.
Tasks: multiple small task families with growth/prune/hibernate.
Purpose: capability-vs-active-phenotype curves.

CLASS D — MODULE ORGANISM
12-16 GB GPU preferred.
Tasks: tiny MLP/adapter/micro-expert cells around a compact core.
Purpose: select useful neural cell granularity.

CLASS E — INTELLIGENT SEED
16-24 GB GPU preferred, with 8-12 GB variants where feasible.
Tasks: frozen pretrained core plus developmental adapters.
Purpose: prove development can augment existing intelligence.

CLASS F — ANCESTOR INHERITANCE
16-24 GB GPU preferred.
Tasks: multiple donor adapters / specialists, developmental regeneration from compact codes.
Purpose: test compact inheritance and compositionality.

RESOURCE ACCOUNTING REQUIRED ON EVERY TIER
- CPU model and core count when measured
- GPU model and VRAM when present
- system RAM
- precision
- trainable parameters
- total resident parameters
- batch size / sequence length
- peak RAM
- peak VRAM
- epoch/step wall-clock
- inference/development latency

SCALE-UP GATE
A larger hardware tier is justified only if the current tier has answered its question and the next question cannot be resolved by:
- longer run time
- smaller batch with accumulation
- reduced grid resolution
- fewer cells with matched-budget sweep
- smaller pretrained seed
- more efficient module representation

DECISION
Design DG-1A through DG-1F so that the core research remains executable on 8 GB VRAM and as much as practical on CPU. Treat 16-24 GB as acceleration and later intelligent-seed capacity, not a prerequisite for validating the developmental thesis.

OPEN QUESTIONS
- Which framework gives the lowest overhead for sparse dynamic cell populations on Windows/home GPUs?
- At what population size does dynamic graph bookkeeping dominate neural compute?
- How much real memory is saved by hibernating module payloads versus moving them to host RAM or regenerating them?

NEXT EXPERIMENT
During DG-1A-P0, record CPU-only and GPU peak memory plus step latency for at least two grid sizes. Use those measurements to replace the first estimated scaling assumptions.
