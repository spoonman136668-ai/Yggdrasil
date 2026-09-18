TITLE: DG-1A-AR-01 — Seasonal Context Corruption Robustness Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX ROBUSTNESS AUDIT — NOT A YGGDRASIL SCIENTIFIC RESULT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-ar01-explicit-seasonal-modes-spec.ice

PURPOSE
Measure how the frozen two-scalar CIRCLE-2 seasonal context behaves under corrupted context before AR-01 implementation.

This audit asks:
- how much phase error can the compact context tolerate?
- how much attenuation/dropout can it tolerate?
- how sensitive is it to semantically wrong mode labels?
- can noise-augmented training improve robustness without adding parameters?

BOUNDARY
This is a synthetic local-policy surrogate.
It does not modify or execute Yggdrasil.
It does not spend STAB-18-R1.
It does not alter AR-01 preregistration gates.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

MODEL
Inputs:
8 local-state nuisance/control variables:
support
density
boundary
damage
energy
age
stability
recent_loss

plus:
2 seasonal context scalars

Network:
10 -> 32 -> 32 -> 4
tanh hidden activations
sigmoid output

Outputs:
growth
retention
repair
activity

Trainable parameters:
1540

Candidate and fixed control are exactly parameter-count matched.

CIRCLE-2
For mode m in 0..5:
phi = m * 2*pi/6

context:
cos(phi)
sin(phi)

FIXED CONTROL
The identical two context inputs are clamped to zero.

SYNTHETIC TARGET POLICY
All outputs are clipped to [0,1].

Let:
s = support
d = density
b = boundary
q = damage
e = energy
a = age
u = stability
r = recent_loss

AGE is intentionally a nuisance input and is not used by the target equations.

EXPANSION
growth    = 0.15 + 0.55*(1-s) + 0.20*(1-d) + 0.10*e - 0.08*b
retention = 0.45 + 0.35*s + 0.10*u
repair    = 0.10 + 0.20*q + 0.10*r
activity  = 0.72 + 0.18*e - 0.08*u

CONSOLIDATION
growth    = 0.05 + 0.22*(1-s) - 0.10*d
retention = 0.70 + 0.20*u + 0.08*s
repair    = 0.08 + 0.20*q + 0.08*r
activity  = 0.38 + 0.12*(1-u)

MAINTENANCE
growth    = 0.02 + 0.10*(1-s)
retention = 0.82 + 0.13*u
repair    = 0.04 + 0.18*q + 0.08*r
activity  = 0.17 + 0.10*(1-u) + 0.05*q

REPAIR
growth    = 0.08 + 0.28*(1-s) + 0.10*q
retention = 0.62 + 0.18*s
repair    = 0.18 + 0.52*q + 0.22*r + 0.08*(1-s)
activity  = 0.62 + 0.20*q + 0.10*r

DORMANCY
growth    = 0.01 + 0.02*(1-s)
retention = 0.91 + 0.06*u
repair    = 0.01 + 0.04*q
activity  = 0.025 + 0.025*(1-u)

REACTIVATION
growth    = 0.10 + 0.45*(1-s) + 0.10*e + 0.08*q
retention = 0.58 + 0.20*s
repair    = 0.12 + 0.35*q + 0.15*r
activity  = 0.78 + 0.12*e - 0.05*u

TRAINING
matched seeds:
0..7

per seed:
training samples = 9000
held-out samples = 4000
epochs = 180
optimizer = Adam
learning rate = 0.003
full-batch training

Candidate/control pairs start from identical initialized weights.

CLEAN RESULT
CIRCLE-2 candidate held-out MSE:
mean = 0.003735
sd = 0.000695
range = 0.003072..0.005144

fixed zero-context control MSE:
mean = 0.043589
sd = 0.000463
range = 0.042922..0.044539

fixed/candidate mean ratio:
approximately 11.67x

PHASE JITTER
Each sample receives uniform random phase error in [-theta,+theta].

theta degrees | candidate MSE
0             | 0.003735
5             | 0.003974
15            | 0.005959
30            | 0.013800
45            | 0.029047
60            | 0.045063
90            | 0.069193
180           | 0.075757

The candidate remains better than the fixed-control mean through the tested 45-degree condition.
At 60 degrees it is approximately at/slightly worse than the fixed-control baseline.

AMPLITUDE ATTENUATION
context amplitude | candidate MSE
1.00              | 0.003735
0.75              | 0.010433
0.50              | 0.035090
0.25              | 0.068394
0.00              | 0.088228

A half-strength signal remains somewhat better than the fixed control.
A quarter-strength signal is not sufficient.

CONTEXT DROPOUT
For a fraction p of held-out samples, both context scalars are set to zero.

dropout p | candidate MSE
0.00      | 0.003735
0.05      | 0.008053
0.10      | 0.012315
0.25      | 0.024751
0.50      | 0.046487
0.75      | 0.066925
1.00      | 0.088228

Clean-trained context remains useful at 25% dropout.
At 50% dropout it loses its advantage over the fixed-control mean.

WRONG-MODE CORRUPTION
For a fraction p of samples, replace context with a uniformly selected incorrect discrete mode.

wrong p | candidate MSE
0.00    | 0.003735
0.05    | 0.008546
0.10    | 0.012967
0.25    | 0.026262
0.50    | 0.048779
1.00    | 0.093887

This is more dangerous than modest analog noise because it supplies a confident but semantically incorrect control objective.

GAUSSIAN CONTEXT NOISE
Independent Gaussian noise is added to both context scalars.

sigma | candidate MSE
0.00  | 0.003735
0.05  | 0.004143
0.10  | 0.005399
0.20  | 0.010742
0.40  | 0.029825
0.80  | 0.061028
1.20  | 0.078862

The candidate remains better than the fixed-control mean at sigma=0.40.
It does not at sigma=0.80.

NOISE-AUGMENTED TRAINING
A second parameter-identical CIRCLE-2 model was trained with:
- uniform phase jitter ±15 degrees each epoch;
- 10% context dropout each epoch.

No parameters were added.

Clean MSE:
clean-trained = 0.003735
noise-trained = 0.005072

Therefore robustness training costs about 35.8% relative clean MSE in this toy.

DROPOUT ROBUSTNESS
dropout | clean-trained | noise-trained
0.10    | 0.012315      | 0.009691
0.25    | 0.024751      | 0.016251
0.50    | 0.046487      | 0.027495

At 50% dropout, noise-augmented training restores a clear advantage over the fixed-control baseline.

PHASE ROBUSTNESS
jitter | clean-trained | noise-trained
30 deg | 0.013800      | 0.013165
45 deg | 0.029047      | 0.027688
60 deg | 0.045063      | 0.043343

GAUSSIAN ROBUSTNESS
sigma | clean-trained | noise-trained
0.20  | 0.010742      | 0.009696
0.40  | 0.029825      | 0.025136
0.80  | 0.061028      | 0.053308

WRONG-MODE ROBUSTNESS
Noise augmentation did NOT materially solve semantic wrong-mode corruption.

wrong p | clean-trained | noise-trained
0.10    | 0.012967      | 0.013727
0.25    | 0.026262      | 0.026378
0.50    | 0.048779      | 0.047362

KEY FINDINGS
1. CIRCLE-2 is robust to modest analog corruption.
2. Missing/attenuated context degrades gracefully until signal strength becomes too low.
3. Confident wrong-mode context is the dangerous failure class.
4. Ordinary context-noise augmentation can improve dropout/noise robustness without increasing parameter count.
5. Noise augmentation cannot solve a semantically wrong regime label by itself.

ARCHITECTURAL CONSEQUENCE
AR-01 should distinguish:
- analog signal noise;
- signal absence;
- semantic mode error.

The last category requires:
- redundant independent sensing;
- temporal consistency;
- local consensus;
or
- endogenous veto/error detection.

Do not treat larger context magnitude or wider embeddings as a substitute.

LITERATURE CONSISTENCY
Stovold (ALIFE 2023), Neural Cellular Automata Can Respond to Signals:
NCAs can respond to internal and external signals, including signals presented to a single cell for a single timestep.
DOI: 10.1162/isal_a_00567

This supports feasibility of signal-conditioned NCA behavior but does not establish Yggdrasil robustness.

DECISION
Keep CIRCLE-2.

For real AR-01:
- start with the clean frozen signal path for scientific discrimination;
- record context sensitivity;
- do not silently add noise augmentation before seed-0;
- reserve robustness augmentation as a later matched ablation.

NEXT
Measure whether a small number of sensor cells can propagate a seasonal context locally within Yggdrasil-relevant timescales.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
synthetic_seeds = 8
trainable_parameters = 1540
