"""UJ-03A train-source-only development pilot. No official evaluation access."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import time
import unicodedata

import torch
from torch import nn

from learned_jepa import LearnedJEPA
from pair_controls import PairControl
from anchor_adapter import AnchorTrainingAdapter
from bounded_train import train
from grounded_eval import evaluate, jepa_scores
from checkpoint import representation_health
from symbolic_control import scores as symbolic_scores

SHA256 = '35b70c7cb1660c34d302bb932dfd3656ce3d05e8c982c797767fec31d7d1e0ba'
BYTES = 47570935
ARMS = ('mixture', 'pooled', 'aligned', 'sham', 'off', 'shuffled', 'recurrent', 'attention')
SEEDS = (1701, 1702, 1703)
N_TRAIN = 512
N_DIAG = 128
EPOCHS = 2
BATCH = 32
RATE = .001
ARM_SECONDS = 150
TOTAL_SECONDS = 3000


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def emit(event, **fields):
    print('UJ03A ' + canonical(dict(event=event, **fields)).decode(), flush=True)


def group(question):
    normalized = unicodedata.normalize('NFKC', question).casefold()
    normalized = re.sub(r'\d+(?:[.,]\d+)*', '#', normalized)
    normalized = ' '.join(normalized.split())
    return digest(normalized.encode())


def select(raw, expected, n_train=N_TRAIN, n_diag=N_DIAG):
    if type(raw) is not bytes or not 0 < len(raw) <= 64*1024**2 or digest(raw) != expected:
        raise ValueError('source digest or size')
    if type(n_train) is not int or type(n_diag) is not int or min(n_train,n_diag)<2:
        raise ValueError('selection size')
    counts = Counter()
    groups = {}
    for line_id, line in enumerate(raw.splitlines()):
        counts['input'] += 1
        try:
            obj = json.loads(line)
            question, options, answer = obj['question'], obj['options'], obj['correct']
            if (type(question) is not str or not question.strip() or type(options) is not list
                    or len(options) != 5 or type(answer) is not str or answer not in tuple('ABCDE')
                    or any(type(v) is not str or not v.startswith(k+')') for k,v in zip('ABCDE', options))):
                raise ValueError('invalid row')
            options = tuple(v[2:].strip().encode() for v in options)
            ctx = question.encode()
            if any(not v for v in options):
                raise ValueError('empty choice')
            if max(map(len,(ctx,)+options))>256:
                counts['excluded_length'] += 1
                continue
            if len(set(options)) != len(options):
                counts['excluded_duplicate_choice'] += 1
                continue
        except (ValueError, TypeError, KeyError, UnicodeError):
            counts['excluded_malformed'] += 1
            continue
        g = group(question)
        row = (expected+':'+str(line_id), 'math', ctx, options, 'ABCDE'.index(answer))
        counts['eligible'] += 1
        if g in groups:
            counts['excluded_group_duplicate'] += 1
        else:
            groups[g] = row
    counts['unique_groups'] = len(groups)
    if counts['excluded_malformed'] * 20 > counts['input'] or len(groups) < n_train+n_diag:
        raise ValueError('source schema or usable group count')
    order = sorted(groups, key=lambda g: digest(('UJ03A:20261124:'+g).encode()))
    tg, dg = order[:n_train], order[n_train:n_train+n_diag]
    tr, di = tuple(groups[g] for g in tg), tuple(groups[g] for g in dg)
    assert not set(tg)&set(dg)
    manifest = dict(counts=dict(counts), train_groups_sha256=digest(canonical(tg)),
                    diagnostic_groups_sha256=digest(canonical(dg)),
                    train_ids_sha256=digest(canonical([r[0] for r in tr])),
                    diagnostic_ids_sha256=digest(canonical([r[0] for r in di])),
                    train_count=len(tr), diagnostic_count=len(di))
    return tr, di, manifest


def check_deadline(deadline):
    if time.monotonic() >= deadline:
        raise RuntimeError('fixed wall budget exhausted; no replay')


class Guard(nn.Module):
    def __init__(self, model, deadline):
        super().__init__()
        self.model, self.deadline = model, deadline

    def objective(self, context, future):
        check_deadline(self.deadline)
        result = self.model.objective(context, future)
        check_deadline(self.deadline)
        return result

    def update_target(self):
        self.model.update_target()
        check_deadline(self.deadline)


def pairs_for(rows, arm):
    pairs = tuple((r[2], r[3][r[4]]) for r in rows)
    if arm == 'shuffled':
        targets = tuple(y for _,y in pairs)
        pairs = tuple((c, targets[(i+1)%len(targets)]) for i,(c,_) in enumerate(pairs))
    return pairs


def model_for(arm, seed):
    with torch.random.fork_rng(devices=[]):
        torch.random.default_generator.manual_seed(seed)
        if arm in ('recurrent','attention'):
            base = PairControl(arm)
            return base, base, base.scores
        base = LearnedJEPA(mode='pooled' if arm=='pooled' else 'mixture')
        fitted = AnchorTrainingAdapter(base,arm) if arm in ('aligned','sham','off') else base
        return base, fitted, lambda c,o: jepa_scores(base,c,o)


def measure(rows, scorer, deadline):
    def checked(c,o):
        check_deadline(deadline)
        return scorer(c,o)
    return evaluate(rows, checked)['all']


def run_arm(arm, seed, tr, di, overall_deadline, epochs=EPOCHS, batch=BATCH):
    deadline = min(overall_deadline, time.monotonic()+ARM_SECONDS)
    start, cpu_start = time.monotonic(), time.process_time()
    base, fitted, scorer = model_for(arm,seed)
    base.eval()
    pairs = pairs_for(tr,arm)
    expected_bytes = epochs*sum(len(c)+len(y) for c,y in pairs)
    original = pairs_for(tr,'mixture')
    assert Counter(y for _,y in pairs)==Counter(y for _,y in original)
    assert tuple(c for c,_ in pairs)==tuple(c for c,_ in original)
    before = measure(di,scorer,deadline)
    accounting = train(Guard(fitted,deadline), pairs, seed=seed, epochs=epochs,
                       batch_size=batch, rate=RATE, max_steps=epochs*len(pairs)//batch,
                       max_bytes=expected_bytes)
    if accounting['exposure_bytes'] != expected_bytes or accounting['steps'] != epochs*len(tr)//batch:
        raise RuntimeError('exposure mismatch')
    after = measure(di,scorer,deadline)
    seen = measure(tr[:min(64,len(tr))],scorer,deadline)
    health = None
    if arm not in ('recurrent','attention'):
        health = representation_health(base,[r[2] for r in di[:min(32,len(di))]])
    check_deadline(deadline)
    return dict(arm=arm,seed=seed,before=before,after=after,seen_after=seen,
                accounting=accounting,representation_health=health,
                shuffled_changed=sum(a[1]!=b[1] for a,b in zip(original,pairs)),
                wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu_start)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train',type=Path,required=True)
    parser.add_argument('--source-sha',required=True)
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.source_sha):
        raise ValueError('source SHA')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    deadline = time.monotonic()+TOTAL_SECONDS
    if args.train.stat().st_size != BYTES:
        raise ValueError('pinned train byte size')
    raw = args.train.read_bytes()
    tr,di,manifest = select(raw,SHA256)
    del raw
    emit('manifest',source_sha=args.source_sha,train_source_sha256=SHA256,
         torch=str(torch.__version__),scope='TRAIN_SOURCE_ONLY_DEVELOPMENT_NOT_SCIENCE',
         arms=ARMS,seeds=SEEDS,epochs=EPOCHS,batch=BATCH,rate=RATE,**manifest)
    count = Counter(r[3][r[4]] for r in tr)
    covered = [0]
    def symbolic(c,o):
        values,ok = symbolic_scores(c,o)
        covered[0] += int(ok)
        return values
    emit('reference',uniform=measure(di,lambda c,o:[0.]*len(o),deadline),
         frequency=measure(di,lambda c,o:[math.log1p(count[x]) for x in o],deadline),
         symbolic=measure(di,symbolic,deadline),symbolic_coverage=covered[0]/len(di))
    completed=[]
    for seed in SEEDS:
        for arm in ARMS:
            check_deadline(deadline)
            emit('arm_started',arm=arm,seed=seed)
            result=run_arm(arm,seed,tr,di,deadline)
            emit('arm_completed',**result)
            completed.append(result)
    means = {arm:sum(r['after']['accuracy'] for r in completed if r['arm']==arm)/len(SEEDS)
             for arm in ARMS}
    briers = {arm:sum(r['after']['brier'] for r in completed if r['arm']==arm)/len(SEEDS)
              for arm in ARMS}
    emit('complete',arms_completed=len(completed),mean_accuracy=means,mean_brier=briers,
         scientific_gain_verified=False,protected_evaluation_accessed=False,
         compute_parity_verified=False,baseline_convergence_verified=False)


if __name__ == '__main__':
    main()
