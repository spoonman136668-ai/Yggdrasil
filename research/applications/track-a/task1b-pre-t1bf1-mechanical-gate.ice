TITLE: TASK-1B PRE-T1BF1 MECHANICAL GATE CLOSURE
DATE: 2026-09-22
STATUS: PASS / T1BF1 FREEZE AUTHORIZED
TRACK: DG-1 / TASK-1B

PREREGISTRATION:
d897551c140093d9e7ab7530069826f636d8e0d9

PARENT T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

CANDIDATE SOURCE

bytes:
12748

SHA256:
e8d409c5eb8e750123aae4979fd1091611a915c22f7cf977e420345186aef6b9

DETERMINISTIC PUBLICATION

gzip level 9;
mtime 0.

gzip bytes:
3650

gzip SHA256:
4cdcd93a3982d29f9fdef6e7735bad7caa9d0af6057af5865a7986ac7e8c6ebe

base64 chars:
4868

base64 SHA256:
6b2a61879f94ecfec63f708a800ec9a1b4bf11a66d72eecf778604e573cf7582

source chunk count:
3

chunk blob identities:
00 = 3ec132e0e8fe08f59a88848abc522ded90e14f4a
01 = c82b7c11e3b426dbb55da4add5b74be7765a1148
02 = bdb195ef5b307be9a05429f7d80f7c472be95e4f

All three repository blob identities
match the locally generated exact chunks.

MECHANICAL SEED:
TASK1B-MECHANICAL-V1

COMPLETE MECHANICAL SWEEPS:
2

compact output bytes:
36722

compact output SHA256:
9ae4425de5d5589a77f8b32177212249dc7009b65c53d23871b8435e586144e1

BYTE IDENTICAL:
true

MECHANICAL PROBES

duplicate_byte_identical:
PASS

matched_parent_parity:
PASS

fixed_parent_parity:
PASS

neutral_opposite_stream_sense_fixture:
PASS

downstream_still_stream_matched_fixture:
PASS

noncommitted_cannot_sense_fixture:
PASS

all_runtime_integrity:
PASS

PARITY NOTE

The first parity check compared the public arm label
MATCHED_SENSE against inherited EMERGENT_V0
and therefore reported a label-only mismatch.

The check was corrected before freeze
to exclude the presentation label.

No behavioral field differed.

After correction:
full matched-parent behavioral parity = PASS.

PUBLICATION HYGIENE

An earlier plaintext staging copy did not match
the mechanically tested source Git blob identity.

It was never frozen.

It was removed before T1BF1.

The authoritative Task-1B publication is only
the three verified deterministic source chunks
plus the fail-closed loader.

No Task-1B primary manifest exists yet.

No Task-1B primary execution has occurred.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
