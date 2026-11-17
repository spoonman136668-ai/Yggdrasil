"""Explicit witness-preserving repair of a quarantined native relation.

A disproved model's unobserved implications are not witnessed knowledge.
Only outcomes at its recorded observed inputs may seed a wider model class.
This is engineering-only migration, not real-world source authentication.
"""
from yggdrasil.native_context_basis import (
    _Profile, canonical, digest, feature_row, pin, require, SOURCE_MODE, SOURCE_KIND,
)
from yggdrasil.native_context_accumulator import NativeContextAccumulator, MAX_BATCHES
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_relation_memory import NativeRelationMemory, NativeRelationReadout
from yggdrasil.public_causal_cells import PublicCausalCells


def repair_quarantined_basis(raw, expected_checkpoint_sha256, address, batches, *,
                             max_degree, retained=False, source_mode=SOURCE_MODE,
                             source_kind=SOURCE_KIND):
    """Return an immutable repaired candidate plus explicit lineage receipt.

    batches contains dictionaries with exactly records and sha256. The first
    batch must be the pinned evidence that invalidated this address. Failure
    at any point returns no candidate and cannot change the original bytes.
    Old raw outcome rows are deliberately absent from this interface.
    """
    require(source_mode == SOURCE_MODE and source_kind == SOURCE_KIND,
            'REPAIR_CAUSAL_GROUNDING_OR_SOURCE_AUTHORITY_ABSENT')
    original = NativeContextQuarantine.restore(raw, expected_checkpoint_sha256)
    slot = PublicCausalCells._address(address, retained)
    old = original._native
    previous = old._model._profiles[slot]
    require(bool(original._failures[slot]), 'REPAIR_REQUIRES_QUARANTINE')
    require(type(max_degree) is int and previous.degree < max_degree <= old._model.context_bits + 1,
            'REPAIR_REQUIRES_STRICT_BASIS_EXPANSION')
    require(type(batches) is list and 0 < len(batches) <= MAX_BATCHES
            and all(type(p) is dict and set(p) == {'records', 'sha256'}
                    and pin(p['sha256']) for p in batches), 'REPAIR_BATCH_PACKETS')
    require(batches[0]['sha256'] == original._failures[slot], 'REPAIR_MISSING_REJECTED_EVIDENCE')
    # Byte validation precedes reconstruction. Normal public-tuple validation
    # is also enforced by unchanged stage_update before candidate admission.
    require(all(type(p['records']) is list and digest(canonical(p['records'])) == p['sha256']
                for p in batches), 'REPAIR_SOURCE_PIN')
    basis = {}
    seen = old._seen[slot]
    for packet in batches:
        for row in packet['records']:
            require(type(row) is list and len(row) == 3, 'REPAIR_PUBLIC_ROW')
            context = old._model._context(row[0])
            action = PublicCausalCells._bit(row[1], 'ACTION')
            PublicCausalCells._bit(row[2], 'PUBLIC_OUTCOME')
            require(not seen & (1 << (context | (action << old._model.context_bits))),
                    'REPAIR_OLD_RAW_ROW_REPLAY')
    for mask in range(1 << (old._model.context_bits + 1)):
        if not seen & (1 << mask):
            continue
        # Only these inputs were actually observed. DO NOT seed the wider
        # basis with all predictions or zero-padded old support equations.
        context = mask & ((1 << old._model.context_bits) - 1)
        action = mask >> old._model.context_bits
        outcome = old.predict(address, context, action, retained=retained)
        require(outcome is not None, 'REPAIR_OLD_WITNESS_NOT_IDENTIFIED')
        NativeRelationMemory._insert(basis, feature_row(mask, max_degree), outcome)
    require(bool(basis), 'REPAIR_NO_RETAINED_WITNESSES')
    coefficients = 0
    for pivot in sorted(basis):
        row, rhs = basis[pivot]
        coefficients |= (rhs ^ ((coefficients & row).bit_count() & 1)) << pivot
    support = NativeRelationReadout._reduced(row for row, rhs in basis.values())
    profile = _Profile(max_degree, coefficients, support, previous.source_sha256,
                       previous.source_records, previous.unique_inputs)
    expanded = NativeContextAccumulator(old._model.context_bits)
    expanded._model._profiles = old._model._profiles[:slot] + (profile,) + old._model._profiles[slot + 1:]
    expanded._seen = old._seen
    expanded._batches = old._batches
    # Validate the migrated support against the recorded input mask using the
    # existing cold contract before introducing any additional observations.
    lifted_raw = expanded.checkpoint()
    expanded = NativeContextAccumulator.restore(lifted_raw, digest(lifted_raw))
    for packet in batches:
        expanded = expanded.stage_update(address, packet['records'], packet['sha256'],
            max_degree=max_degree, retained=retained, source_mode=source_mode, source_kind=source_kind)
    candidate = NativeContextQuarantine(expanded)
    candidate._failures = original._failures[:slot] + ('',) + original._failures[slot + 1:]
    receipt = {'schema': 'yggdrasil.ckad.witness-preserving-repair.v1',
        'old_checkpoint_sha256': expected_checkpoint_sha256,
        'new_checkpoint_sha256': candidate.checkpoint_sha256,
        'slot': slot, 'old_degree': previous.degree, 'new_degree': max_degree,
        'retained_observed_inputs': seen.bit_count(), 'old_raw_rows_received': 0,
        'new_source_batches': [p['sha256'] for p in batches],
        'rejected_evidence_admitted': original._failures[slot],
        'new_observed_inputs': expanded._seen[slot].bit_count(),
        'source_mode': SOURCE_MODE, 'scientific_pass': False, 'accepted_native': False}
    return candidate, receipt
