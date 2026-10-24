"""MR34J3L read-only package and upstream scientific-custody snapshot verifier.

This code cannot issue seed leases, authenticate a signer, run sources, dispatch,
or convert R234/R243 draft successes into a protected-main execution permit.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys, importlib.util, re

ROOT = pathlib.Path(__file__).resolve().parent
PACKAGE = ROOT
RUN_R243 = '40084791494'
R243_SHA = '3e5a7acd6877cd8133e99d3bc669c22d3c2f58a4'
R234_SHA = 'dd879bb99603d77bbdef525bb18a9a2fdc5a0061'
REQUIRED_SOURCE_SHA = '7f5853792ea7f04f75614661006d87fcf949f26d'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_package(package=PACKAGE, evidence=None):
    package = pathlib.Path(package)
    if evidence is None:
        evidence = json.loads((ROOT / 'upstream_readonly_evidence.json').read_text())
    problems = []
    try:
        manifest = json.loads((package / 'MR34J3J_LOCAL_RECEIPT.json').read_text())
        intent = json.loads((package / 'MR34J3J_PROPOSED_ATTEMPT_INTENT.json').read_text())
    except (OSError, ValueError) as exc:
        return {'schema':'mr34j3l.read-only-reconcile.v1', 'status':'HOLD',
                'reason':'LOCAL_PACKAGE_UNREADABLE', 'detail':type(exc).__name__,
                'scientific_admission':False, 'execution_permission':False}
    if manifest.get('source_sha') != REQUIRED_SOURCE_SHA:
        problems.append('SOURCE_SHA_DRIFT')
    if manifest.get('scientific_admission') is not False or manifest.get('source_resets') != 0:
        problems.append('PREVIOUS_RECEIPT_FALSE_AUTHORITY')
    if manifest.get('authoritative_consumed_source_lease_verified') is not False:
        problems.append('CUSTODY_FIELD_UNEXPECTEDLY_ASSERTED')
    for name, expected in sorted(manifest.get('file_sha256', {}).items()):
        file = package / name
        if not file.is_file() or sha256(file) != expected:
            problems.append('LOCAL_FILE_DRIFT:' + name)
    if len(manifest.get('file_sha256', {})) != 15:
        problems.append('FILE_MANIFEST_SET_DRIFT')
    if intent.get('proposed_total_physical_attempts') != 8480 or intent.get('distinct_seed_values') != 1168:
        problems.append('ATTEMPT_PLAN_DRIFT')
    if intent.get('admission') != 'NO' or intent.get('execution_authority') is not False:
        problems.append('INTENT_MUST_NOT_ADMIT')
    phases = intent.get('counts_by_host_phase', {})
    expect = {'PREFLIGHT':16,'FIT':2304,'DEV':640,'HELD':1280}
    if phases != {'ubuntu-24.04':expect,'windows-2025':expect}:
        problems.append('HOST_PHASE_TOTALS_DRIFT')
    # R234's exact proposal-only lane-and-seed namespace: heldout seeds are unique
    # per lane, not per arm or OS host. Never create these refs from this audit.
    if evidence.get('r234',{}).get('proposal_head') != R234_SHA or evidence.get('r234',{}).get('active') is not False:
        problems.append('R234_PROPOSAL_PROVENANCE_DRIFT')
    r243 = evidence.get('r243',{})
    if (r243.get('qualified_head') != R243_SHA or
        str(r243.get('qualified_run')) != RUN_R243 or
        r243.get('conclusion') != 'success' or
        r243.get('synthetic_only') is not True or
        r243.get('live_writer_authenticated') is not False or
        r243.get('live_activation') is not False):
        problems.append('R243_INACTIVE_BOUNDARY_DRIFT')
    # Explicitly refuse inference from a green synthetic test to a real lease.
    outstanding = ['CKB_AUTHENTICATED_WRITER_IDENTITY',
                   'CKB_PROTECTED_ADMISSION_AND_SOURCE_ROLE_LEASE',
                   'CKB_PER_SEED_HELDOUT_CLAIM_AND_PER_ATTEMPT_CONSUMPTION',
                   'EXACT_RUNTIME_WHEEL_INSTALL_AND_CROSS_OS_RECONCILIATION',
                   'OWNER_FINAL_FULL_REGRESSION_AND_SIGNED_EXECUTION_PERMIT']
    return {'schema':'mr34j3l.read-only-reconcile.v1',
            'status':'HOLD' if not problems else 'BLOCKED_INVALID_SOURCE',
            'source_candidate_integrity':'PASS' if not problems else 'FAIL',
            'violations':problems,
            'verified_r243_synthetic_gate':'PASS' if not problems else 'NOT_ACCEPTED',
            'r243_qualified_run':int(RUN_R243),
            'r243_qualified_head':R243_SHA,
            'r234_heldout_proposal_head':R234_SHA,
            'claimed_distinct_seed_values':1168,
            'planned_reset_attempts':8480,
            'outstanding_authoritative_gates':outstanding,
            'scientific_admission':False,
            'execution_permission':False,
            'original_source_executed':False,
            'repo_mutation_performed':False}


if __name__ == '__main__':
    print(json.dumps(audit_package(),sort_keys=True,indent=2))
    sys.exit(1 if audit_package()['violations'] else 0)
