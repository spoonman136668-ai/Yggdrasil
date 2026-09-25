TITLE: YGG-A8 Branch-Local Damage Preregistration FIXA
DATE: 2026-09-25
STATUS: PREREGISTRATION FIX / BEFORE ANY A8 EXECUTION
PARENT_PREREGISTRATION: b33bbf51a2aa7ba2b1715b0a64886a81694ef999
LANE: YGG-A

DEFECT
The original branch-damage schedule ranked all request IDs 0..159.
That can select requests arriving too near the frozen epoch-159 horizon to reach PROCESSED_BC, making the preregistered requirement of exactly eight applied branch damages per world impossible for a scheduling-horizon reason unrelated to the branch-repair hypothesis.

FIX
Change only the candidate pool for branch-damage selection.

Original candidate pool:
all request IDs 0..159 excluding inherited terminal-corruption IDs.

Corrected candidate pool:
request IDs 0..63 inclusive excluding inherited terminal-corruption IDs.

Within the corrected pool retain the exact original ranking:
h64("YGG-A8-BRANCH-DAMAGE", seed, rid), then rid.

Retain:
- select exactly first eight ranked IDs;
- first four receive B damage;
- next four receive C damage;
- zero overlap with terminal-corruption IDs;
- all damage event, repair, task, horizon, scheduler, capability, integrity, duplication, and success gates unchanged.

RATIONALE
The first 64 requests arrive by epoch 63, leaving at least 96 subsequent epochs inside the frozen run for the request to traverse the already-accepted fork/join pipeline.
This makes damage exposure a property of the experiment rather than an accidental late-arrival coverage failure.

BOUNDARY
No result has been observed for A8.
This FIXA does not respond to scientific evidence.
No threshold, service capacity, task graph, horizon, repair mechanism, developmental arm, or acceptance gate changes.
