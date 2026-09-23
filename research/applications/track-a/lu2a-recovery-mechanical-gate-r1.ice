TITLE: LU-2A RECOVERY MECHANICAL GATE / INVALID FREEZE RETIREMENT
DATE: 2026-09-23
STATUS: PASS / INVALID LU2AF1 RETIRED / REPLACEMENT FREEZE AUTHORIZED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
bdd6bc440635597e1fec64cc1c5124dfc1e0369b

ORIGINAL PRE-FREEZE RECORD:
aef30f92af5bf395f0e868a7618237ae703422b4

INVALID FREEZE:
d6d9302b114b7ddac6cf43871878be47a1a177a1

INVALID DERIVATION BINDINGS:
01411fa52adf9d609700cbf2e17edece3363fdd7
d229f9089a95802a8109d68e0ad48385c935338a

REASON FOR RETIREMENT

The source payload recovered into Git after transient-sandbox loss
does not match the source identity recorded by the original pre-freeze gate.

Original pre-freeze candidate identity recorded at aef30f92...:

bytes:
27655

sha256:
be2af2e8a496532122957011e15ebbaf83bf55004caadb3e61931a2ed85e555e

Actual surviving/recovered candidate identity:

bytes:
23066

sha256:
251fcb655a04b109dc9716a021acef9f956333ca265685246f41868923627f35

Therefore the d6d9302b... loader,
which expected the original pre-freeze identity,
cannot execute the staged recovered payload
and is not a valid scientific freeze.

No scientific primary was executed from that invalid freeze.

No full primary manifest body was materialized from that invalid freeze.

No TEACHER_V02 or HYBRID_HU primary arm was executed.

The replicate-key derivation records tied to d6d9302b...
are retired and must not be used.

RECOVERY EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

SURVIVING CANONICAL WEIGHTS

bytes:
55917

sha256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

Exact accepted LU-1E canonical weight identity:
PASS.

RECOVERY MECHANICAL DUPLICATION

Recovery mechanical evidence file 1:

bytes:
12063

sha256:
5ecde1d1bae267a0a75f68b1f4a2578c13352135270f93a190dd0f8add91394c

Recovery mechanical evidence file 2:

bytes:
12063

sha256:
5ecde1d1bae267a0a75f68b1f4a2578c13352135270f93a190dd0f8add91394c

byte-identical:
TRUE.

Internal paired mechanical duplicate payload:

bytes:
47202

sha256:
7d80ff35a23e10e04d118dc7aeb2769886928db8ca0a620a14efa612a666225f

RECOVERY MECHANICAL PROBES

D2:
PASS.

ECHO_PHASE:
PASS.

G5_OFF:
PASS.

H mapping exact:
PASS.

LOCAL_HEDGE:
PASS.

NO_POOL:
PASS.

OBS width 70:
PASS.

U mapping exact:
PASS.

canonical weight SHA exact:
PASS.

C/S plus refractory exact parity:
PASS.

no learned query in C/S plus refractory fixture:
PASS.

duplicate mechanical byte identity:
PASS.

learned outputs finite / bounded:
PASS.

model parameter count 13694:
PASS.

no model RNG:
PASS.

no optimizer / training invoked:
PASS.

learned queries restricted to H/U:
PASS.

request-bound handoff:
PASS.

TEACHER_V02 parent parity:
PASS.

all recovery probes:
PASS.

MECHANICAL CAUSAL ACTIVITY

H evaluations:
0

U evaluations:
1702

U learned-vs-teacher TV > 1e-6:
1702

U realized differing transitions:
34

mean U TV:
0.0230557322

maximum U TV:
0.0795253592

first causal divergence epoch:
0

epochs with different state vector:
153

trajectories later reconverge:
TRUE

This is a mechanical activity check only.

It does not satisfy the LU-2A primary causal gate,
which still requires natural H exposure
across the five fresh primary worlds.

DECISION

The recovered 23066-byte candidate
passes the complete LU-2A mechanical contract.

A replacement implementation freeze is authorized.

The replacement freeze must use:

source bytes:
23066

source SHA256:
251fcb655a04b109dc9716a021acef9f956333ca265685246f41868923627f35

canonical learned weight SHA256:
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

After replacement freeze:

derive a completely new five-world primary set
from the replacement freeze identity.

Do not reuse replicate keys bound to d6d9302b....

PLAIN-SPEAK INTERPRETATION

We caught the recovery mistake before it touched the experiment.

The first frozen LU-2A loader pointed at source bytes
that were no longer the bytes actually staged in Git.

That freeze is invalid.

The good news is that the surviving candidate itself
was still in the isolated sandbox.

We reran the full mechanical contract on those exact surviving bytes.

Everything passed.

The neural cell still only controls H and U.

Committed cells still use the trusted rule.

The same random numbers are still used.

The teacher arm still matches the parent.

So we can safely issue a new freeze identity
and start the five fresh worlds from that new identity.

No primary science was contaminated.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
