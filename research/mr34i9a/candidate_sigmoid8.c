/*
 * MR34I9B — source-only, unintegrated native binary64 eight-wide sigmoid.
 * Independently pinned CORE-MATH cr_exp implementation is compiled separately
 * from src/binary64/exp/exp.c at blob 196e71ff8f00ab9df0802f3661cbe845ff8e118c.
 * This wrapper contains no upstream source and does not edit the S4C1 learner.
 *
 * The original CORE-MATH exp.c must retain its MIT license notice in the
 * downloaded/pinned external checkout and in subsequent distributions.
 */
#include <stdint.h>
#include <stddef.h>
#include <math.h>
#include <fenv.h>

#pragma STDC FENV_ACCESS ON

extern double cr_exp(double x);

int candidate_environment_ok(void) {
    return sizeof(double) == 8 &&
           sizeof(uint64_t) == 8 &&
           fegetround() == FE_TONEAREST;
}

/* Exact frozen ABI. Input/output must not alias, and input must be finite. */
void candidate_sigmoid8(const double input_u[8], double output_p[8]) {
    if (!input_u || !output_p || !candidate_environment_ok()) {
        if (output_p) {
            for (size_t i = 0; i < 8; ++i) output_p[i] = NAN;
        }
        return;
    }
    for (size_t i = 0; i < 8; ++i) {
        const double v = input_u[i];
        if (!isfinite(v)) {
            output_p[i] = NAN; /* Harness treats this as hard veto. */
            continue;
        }
        const double clamped = v < -35.0 ? -35.0 : (v > 35.0 ? 35.0 : v);
        const double negative = -clamped;
        const double exponential = cr_exp(negative);
        /* Explicit binary64 rounding points, no fused contraction. */
        volatile double denominator = 1.0 + exponential;
        const double probability = 1.0 / denominator;
        output_p[i] = probability;
    }
}
