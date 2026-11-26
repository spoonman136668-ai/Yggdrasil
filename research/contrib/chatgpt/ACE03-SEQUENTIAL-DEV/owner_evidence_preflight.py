"""Read-only ACE03 owner-side qualification evidence check, not admission.

The native owner must supply an authenticated, bounded GitHub GET transport.
A successful check binds the existing nonstudy evidence only. It does not
create a ledger, trust a caller's authority, or import/execute the learner.
"""
REPO = 'spoonman136668-ai/Yggdrasil'
BRANCH = 'research/ace03-sequential-contract-dev-20261124'
SOURCE = 'f8e814305fe53fc31fe535f4cb8786151543e637'
TREE = 'cb3d349e5def63e1dacdffdd7ae9ae7bd8df6bc5'
RUN = 45716022547
WORKFLOW = '.github/workflows/direct-research-qualification.yml'
PREFIX = '/repos/' + REPO
JOBS = {
    'windows': (139573542314, ('Checkout exact candidate',
        'Verify source lock and phase custody',
        'Full repository regression and frozen atlas check',
        'All ACE03 fixtures and syntax build',
        'Read back original started archive and verify bytes',
        'Read back original raw archive and verify bytes',
        'Final exact worktree')),
    'linux': (139574290127, ('Exact frozen source, atlas, full regression and ACE03 build',)),
}
ARTIFACTS = {
    15071052696: ('started', 'eccdcc2dfa2d922df270563cd88e381e46d2e76b5e7023589b41ad68c531ba05', 330),
    15071222485: ('raw', '7602066318394962f56f0504401f227f11627bc14081d9276aef64c8eee6eb52', 273015),
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def exact_index(doc, key, field, expected):
    values = doc[key]
    need(type(values) is list and doc['total_count'] == len(values) == len(expected),
         'incomplete or extra ' + key)
    index = {v[field]: v for v in values}
    need(len(index) == len(values) and set(index) == set(expected), 'wrong or duplicate ' + key)
    return index


def verify_evidence(get):
    """GET-only checks; transport authenticity is a separate native prerequisite."""
    commit = get(PREFIX + '/git/commits/' + SOURCE)
    need(commit['sha'] == SOURCE and commit['tree']['sha'] == TREE, 'qualified tree drift')
    branch = get(PREFIX + '/git/ref/heads/' + BRANCH)
    need(branch['ref'] == 'refs/heads/' + BRANCH and branch['object']['type'] == 'commit'
         and branch['object']['sha'] == SOURCE, 'study branch drift')
    base = PREFIX + '/actions/runs/' + str(RUN)
    run = get(base)
    need(run['id'] == RUN and run['head_sha'] == SOURCE and run['head_branch'] == BRANCH
         and run['head_commit']['tree_id'] == TREE and run['repository']['full_name'] == REPO
         and run['head_repository']['full_name'] == REPO and run['path'] == WORKFLOW
         and run['event'] == 'push' and run['run_attempt'] == 1
         and run['status'] == 'completed' and run['conclusion'] == 'success',
         'qualification run identity or outcome')
    jobs = exact_index(get(base + '/jobs?per_page=100'), 'jobs', 'name', JOBS)
    for name, (job_id, steps) in JOBS.items():
        job = jobs[name]
        need(job['id'] == job_id and job['run_id'] == RUN and job['head_sha'] == SOURCE
             and job['run_attempt'] == 1 and job['status'] == 'completed'
             and job['conclusion'] == 'success', 'job identity or outcome: ' + name)
        seen = {step['name']: step for step in job['steps']}
        need(len(seen) == len(job['steps']), 'duplicate step')
        need(all(s in seen and seen[s]['status'] == 'completed'
                 and seen[s]['conclusion'] == 'success' for s in steps), 'required step: ' + name)
    windows = jobs['windows']
    need(windows['runner_name'] == 'YGG-B-LINKDEADKB'
         and {'self-hosted','Windows','X64','yggdrasil','research-only'} <= set(windows['labels']),
         'qualification runner drift')
    artifacts = exact_index(get(base + '/artifacts?per_page=100'), 'artifacts', 'id', ARTIFACTS)
    for aid, (tag, digest, size) in ARTIFACTS.items():
        item = artifacts[aid]
        need(item['name'] == 'ace03-archive-fixture-' + tag + '-' + str(RUN)
             and item['expired'] is False and item['digest'] == 'sha256:' + digest
             and item['size_in_bytes'] == size and item['workflow_run']['id'] == RUN
             and item['workflow_run']['head_sha'] == SOURCE, 'qualification archive drift')
    return {'source_sha': SOURCE, 'source_tree': TREE, 'qualifier_run': RUN,
            'qualification_runner': windows['runner_name'],
            'qualification_metadata_verified': True, 'native_admission_verified': False,
            'registered_execution_permitted': False}


if __name__ == '__main__':
    raise SystemExit('NO_EXECUTION_CLI: native owner transport and admission required')
