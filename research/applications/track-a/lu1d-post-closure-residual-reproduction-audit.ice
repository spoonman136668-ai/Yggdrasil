TITLE: LU-1D POST-CLOSURE RESIDUAL REPRODUCTION-SENSITIVITY AUDIT
DATE: 2026-09-23
STATUS: DIAGNOSTIC ONLY / CANONICAL WEIGHT BYTES NOT RECOVERED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1DF1:
1609425b3144e66ab373fb5ca7239888883ba351

LU-1D CLOSURE:
f9625901264f32ad774d69378001a2c3a8a3b2ef

CANONICAL ACCEPTED WEIGHT SHA256:
2c8ee801e16dca803eb9a225dc7b711b168840ddb99cd7c93a058d4d4739a3eb

PURPOSE

Determine whether the residual family identified after LU-1B and LU-1C
is robustly reproduced by the exact LU-1D frozen source, seeds, dataset,
teacher, and held-out test world after the historical canonical weight
bytes are no longer available in the active sandbox.

This record is deliberately NOT an authoritative replacement
for an audit of the historical canonical weight bytes.

SOURCE / DATA RECONSTRUCTION

Exact frozen LU-1D source:
bytes = 13562
sha256 = 8d74638a49c3206f5fa7461967de1d2151be7ef87980a2de86f5d83076934b1f

Exact inherited LU-1B source:
sha256 = ecc52037e85ac684722e2a0ed2e01641e45e3d239134a5b4b104dc8dbfdd883c

Exact inherited LU-1A source:
sha256 = c493e9353b98563139fafb8c5dd5a46b8152b780f6148b248c7e17f57f304700

Exact Task-1 base source:
sha256 = 567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12

Frozen LU-1D seeds reproduced exactly.

Validation total equal-head loss under reconstruction:
1.2202576398849487

Historical accepted validation loss:
1.2202576398849487

Thus the dataset / teacher / validation path reproduces exactly.

NUMERICAL REPRODUCTION LIMITATION

The historical canonical weight bytes were not committed to the repo.

Re-running the exact frozen training source on the present sandbox
produces tiny CPU-kernel-dependent floating-point differences.

Three CPU capability paths were tested:

DEFAULT:
weight sha256 =
fc34f87de0300c8cfc9509a777ca17e323aac98c8b0c4dba6c35f317a39d2389

AVX2:
weight sha256 =
bf9b544b70e01870a9ceb7a3db03ec36f7f5c8dba81ed48b1316c3a10035b4c8

AVX512/current:
weight sha256 =
efa826c3b52beede5a599661f7e53a66c268cf5364b498999ee9d73cbdad31ff

None equals the historical canonical weight SHA.

Therefore:
do not call these canonical weights;
do not rewrite LU-1D;
do not reinterpret qualification;
do not use this diagnostic to claim a new quantitative canonical result.

AGGREGATE FINGERPRINT

Historical canonical LU-1D:
stay mean = 0.0231283040
stay p99 = 0.2005912924
stay max = 0.6327946782

Reproductions:

DEFAULT:
stay mean = 0.0231283013
stay p99 = 0.2005910563
stay max = 0.6327946782

AVX2:
stay mean = 0.0231283100
stay p99 = 0.2005912340
stay max = 0.6327946782

AVX512/current:
stay mean = 0.0231283046
stay p99 = 0.2005911160
stay max = 0.6327947974

The reconstructed models therefore reproduce
the accepted held-out aggregate to sub-micro scale,
while retaining distinct weight-byte identities.

RESIDUAL FAMILY — ROBUST ACROSS ALL THREE REPRODUCTIONS

CHALLENGE / ECHO DOMINANT:
mean absolute error approximately 0.037378.

CHALLENGE / NO ECHO:
mean absolute error approximately 0.030438.

ECHO-dominant challenge is harder in all three reproductions.

Mean signed bias in ECHO-dominant challenge:
approximately -0.016814.

Thus the student still under-predicts stay
when matching-side ECHO should protect a challenged committed cell.

SUPPORT / ECHO DOMINANT:
mean absolute error approximately 0.020219.

SUPPORT / NO ECHO:
mean absolute error approximately 0.013255.

ECHO-associated support examples remain harder
in all three reproductions.

NEUTRAL / ECHO DOMINANT:
mean absolute error approximately 0.037614.

NEUTRAL / NO ECHO:
mean absolute error approximately 0.005964.

This is the strongest surviving separation.

Mean signed bias in NEUTRAL / ECHO DOMINANT:
approximately +0.037119.

Thus the student still over-predicts stay
when matching-side ECHO is present
but the teacher's current mode is not CHALLENGE.

PRESSURE = 0

Mean absolute error remains below 0.01
in all three numerical reproductions.

Therefore the remaining problem is not
a simple pressure-zero hinge failure.

REPRESENTATIVE ROBUST WORST CASE

The same held-out row is worst
for all three numerical reproductions.

state:
S

mode:
NEUTRAL

opposition:
0.7599999905

own aligned evidence:
0.0889030993

qraw:
0

matching-side qecho:
0.8426420093

teacher stay:
0.2925738096

student stay:
approximately 0.9253685

absolute error:
approximately 0.6327947

Because the mode is NEUTRAL,
the exact V0.2 teacher does not use ECHO protection here.

The learned updater nevertheless behaves
as though the large matching-side ECHO strongly protects the cell.

DIAGNOSTIC ARTIFACT

local sandbox artifact:
lu1d_residual_replication_audit.json

bytes:
34941

sha256:
8dce32839b4041039db2ea5399e4842f1b8b550ae59301006f74d7eb3c4e8b14

INTERPRETATION BOUNDARY

This is a reproduction-sensitivity diagnostic,
not a canonical-weight audit.

The safe conclusion is qualitative:

the LU-1D residual remains concentrated
around exact categorical conditional relationships involving
focal side,
neighbor state,
Q_prev side,
and whether ECHO should participate in the stay law.

The explicit multiplicative gate improved the learned updater,
but did not remove off-mode ECHO leakage.

This agrees with the already-authoritative LU-1B and LU-1C
post-closure diagnostics and with the candidate direction
authorized by the LU-1D closure.

NEXT JUSTIFIED HYPOTHESIS

Test state-conditioned categorical relation routing
without adding information or teacher-derived quantities.

Expose the exact categorical relations already present in OBS-V1
more directly to the learned operator:

neighbor state category conditions
how neighbor B / LC12 / LS12 are transformed;

Q_prev_side remains an explicit existing categorical input;

focal-side canonicalization remains exact;

the learned multiplicative gate remains.

Do not precompute:

mode;
pressure;
opposition;
own aligned B;
qraw;
qecho;
qeff;
support margin;
teacher probability;
target.

PLAIN-SPEAK INTERPRETATION

The gate helped,
but the neural cell is still confused about
when memory is allowed to matter.

The clearest surviving mistake is:

the cell sees a large matching-side ECHO
while conditions are NEUTRAL,
and acts as though that ECHO should protect its commitment.

The hand-designed cell says:
ECHO protection is conditional.

The next model should not be larger
and should not receive the answer.

It should be shown the categorical local relationships
in a structure that makes
SELF / OPPONENT / OTHER
cheap to represent.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
