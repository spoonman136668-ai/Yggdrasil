"""R8 source-only original-native online belief revision and conventional veto."""
import hashlib
import itertools
import json
import math
import random
import subprocess
import sys
import unittest

from research.native.itd02.r7.learner import NonlinearLocalLearner
from research.native.itd02.r8.revision import RevisionCells

TRIPLES=tuple(itertools.combinations(range(8),3))


def source_law(w, a, state, changed=False):
    seed=9101 if w=='w0' else 9102
    y=0
    for bit in range(8):
        shift=1 if (w=='w1' and a==1 and changed) else 0
        p=(bit+a+shift)%8
        q=(bit+a+2+shift)%8
        r=(bit+a+5+shift)%8
        val=(((state>>p)&1)&((state>>q)&1))^((state>>r)&1)^((seed+bit+a+shift)&1)
        y|=val<<bit
    return y


def independent_fit(rows):
    # Strong conventional exhaustive same-class three-parent 56-structure learner;
    # does not import R7 triples, indexing, fit, or learned models.
    answer=[]
    for bit in range(8):
        best=None
        for subset in TRIPLES:
            hits=[0 for _ in range(8)]; pos=[0 for _ in range(8)]
            for x,y in rows:
                k=0
                for j,parent in enumerate(subset):k|=((x>>parent)&1)<<j
                hits[k]+=1;pos[k]+=(y>>bit)&1
            errors=sum(min(p,n-p) for p,n in zip(pos,hits))
            if best is None or errors<best[0]:
                table=[int(p*2>=n) if n else 0 for p,n in zip(pos,hits)]
                best=(errors,subset,table)
        answer.append((best[1],best[2]))
    return answer


def independent_step(model,x):
    out=0
    for bit,(parents,table) in enumerate(model):
        ix=sum(((x>>p)&1)<<i for i,p in enumerate(parents))
        out|=table[ix]<<bit
    return out


def make_evidence():
    order={}
    for wi,w in enumerate(('w0','w1')):
        for a in range(3):
            order[w,a]=random.Random(821700+wi*100+a*13).sample(range(256),256)
    native=NonlinearLocalLearner()
    for w in ('w0','w1'):
        for i in range(192):
            for a in range(3):
                x=order[w,a][i]
                native.observe(w,a,x,source_law(w,a,x))
    native.fit()
    return native,order


def new_evidence(r8,order):
    for w in ('w0','w1'):
        for i in range(192,240):
            for a in range(3):
                x=order[w,a][i]
                r8.observe(w,a,x,source_law(w,a,x,changed=True))


class R8Tests(unittest.TestCase):
    def test_original_source_immutable_and_initial_exact(self):
        import pathlib
        path=pathlib.Path(__file__).resolve().parents[1]/'r7'/'learner.py'
        source=path.read_bytes()
        # Windows Git worktrees may contain CRLF; authenticate the canonical
        # LF Git object, rejecting any non-CRLF stray carriage return.
        canonical=source.replace(b'\r\n',b'\n')
        self.assertNotIn(b'\r',canonical)
        blob=hashlib.sha1(b'blob '+str(len(canonical)).encode()+b'\0'+canonical).hexdigest()
        self.assertEqual(blob,'204ecd993b954b23e66d6d1e8b3568e7c93183c5')
        n,order=make_evidence()
        self.assertEqual(n.events,1152)
        for w in ('w0','w1'):
            for a in range(3):
                self.assertTrue(all(n.step(w,a,x)==source_law(w,a,x) for x in range(256)))

    def test_exact_public_contradiction_selective_relearning_and_conventional(self):
        n,order=make_evidence(); r=RevisionCells(n.checkpoint())
        new_evidence(r,order)
        self.assertEqual(r.online_events,288)
        self.assertEqual(r.revisions,1)
        self.assertEqual(r.mode['w1']['1'],'fast')
        self.assertTrue(all(r.mode[w][str(a)]=='stable' for w in ('w0','w1') for a in range(3) if (w,a)!=('w1',1)))
        unseen=[(a,x,source_law('w1',a,x,changed=True)) for a in range(3) for x in order['w1',a][240:]]
        old=sum(n.step('w1',a,x)==y for a,x,y in unseen)
        revised=sum(r.step('w1',a,x)==y for a,x,y in unseen)
        self.assertGreater(revised,old)
        self.assertEqual(sum(r.step('w0',a,x)==source_law('w0',a,x) for a in range(3) for x in order['w0',a][240:]),48)
        data=[(x,source_law('w1',1,x,changed=True)) for x in order['w1',1][192:240]]
        fitted=independent_fit(data)
        conventional=sum(independent_step(fitted,x)==source_law('w1',1,x,changed=True) for x in order['w1',1][240:])
        native=sum(r.step('w1',1,x)==source_law('w1',1,x,changed=True) for x in order['w1',1][240:])
        self.assertEqual(native,conventional)

    def test_change_reversal_reuses_stable_old_knowledge(self):
        n,order=make_evidence(); r=RevisionCells(n.checkpoint());new_evidence(r,order)
        self.assertEqual(r.mode['w1']['1'],'fast')
        for x in order['w1',1][48:96]:
            r.observe('w1',1,x,source_law('w1',1,x,changed=False))
        self.assertEqual(r.mode['w1']['1'],'stable')
        self.assertEqual(r.revisions,2)
        self.assertEqual(sum(r.step('w1',1,x)==source_law('w1',1,x,changed=False) for x in order['w1',1][240:]),16)
        self.assertEqual(r.original_checkpoint,n.checkpoint())

    def test_checkpoint_integrity_and_cold_python_process(self):
        n,order=make_evidence();r=RevisionCells(n.checkpoint());new_evidence(r,order)
        raw=r.checkpoint();self.assertEqual(RevisionCells.restore(raw).checkpoint(),raw)
        src='import json,sys;from research.native.itd02.r8.revision import RevisionCells;r=RevisionCells.restore(sys.stdin.buffer.read());print(json.dumps({"m":r.mode["w1"]["1"],"r":r.revisions,"n":r.online_events,"step":r.step("w1",1,37)}))'
        p=subprocess.run([sys.executable,'-B','-c',src],input=raw,capture_output=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(json.loads(p.stdout),{'m':'fast','r':1,'n':288,'step':r.step('w1',1,37)})
        corrupted=json.loads(raw);corrupted['body']['mode']['w0']['1']='fast'
        with self.assertRaises(ValueError):RevisionCells.restore(json.dumps(corrupted).encode())

    def test_invalid_feedback_transactional(self):
        n,order=make_evidence();r=RevisionCells(n.checkpoint());original=r.checkpoint()
        for ev in [('w1',5,0,1),('w1',0,256,1),('w1',0,2,-1),('w_not_known',1,0,1)]:
            with self.assertRaises(ValueError):r.observe(*ev)
            self.assertEqual(r.checkpoint(),original)


if __name__=='__main__':unittest.main()
