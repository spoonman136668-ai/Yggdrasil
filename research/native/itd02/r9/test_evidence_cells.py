"""Source-only R9 evidence accounting, robust source identity, conventional checks."""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import unittest
from research.native.itd02.r7.learner import NonlinearLocalLearner
from research.native.itd02.r8.revision import RevisionCells
from research.native.itd02.r9.evidence_cells import EvidenceCells

TRIPLES=tuple(itertools.combinations(range(8),3))

def source_blob(path):
    source=Path(path).read_bytes().replace(b'\r\n',b'\n')
    assert b'\r' not in source
    return hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()

def prior_model():
    base=NonlinearLocalLearner()
    for i in range(192):
        for action in range(3):
            base.observe('public-world',action,i,0)
    base.fit()
    assert all(base.step('public-world',1,i)==0 for i in range(256))
    return base.checkpoint()

def cohorts():
    calibration=[(i,int(i<136)) for i in range(128,192)]
    zeros=[i for i in range(64) if i&7!=7][:28]
    ones=[i for i in range(64) if i&7==7][:4]
    discovery=[(i,0) for i in zeros]+[(i,1) for i in ones]
    assert len(calibration)==64 and sum(y for _,y in calibration)==8
    assert len(discovery)==32 and len({i for i,_ in calibration+discovery})==96
    return calibration,discovery

def independent_fit(rows):
    # Independently coded exhaustive 56-triple, 8-bit conditional outcome learner.
    model=[]
    for bit in range(8):
        best=None
        for pp in TRIPLES:
            pos=[0]*8; counts=[0]*8
            for before,after in rows:
                idx=0
                for j,p in enumerate(pp):idx+=((before>>p)&1)<<j
                pos[idx]+=(after>>bit)&1
                counts[idx]+=1
            loss=sum(min(z,n-z) for z,n in zip(pos,counts))
            if best is None or loss<best[0]:
                table=[int(2*z>=n) if n else 0 for z,n in zip(pos,counts)]
                best=(loss,pp,table)
        model.append(best)
    return model

def independent_step(model,before):
    out=0
    for bit,(_,pp,table) in enumerate(model):
        idx=sum(((before>>p)&1)<<j for j,p in enumerate(pp))
        out|=table[idx]<<bit
    return out

def trained_models():
    checkpoint=prior_model()
    r9=EvidenceCells(checkpoint,'public-world',1)
    r8=RevisionCells(checkpoint)
    calibration,discovery=cohorts()
    for x,y in calibration:
        r9.calibrate(x,y)
        r8.observe('public-world',0,x,y)
    assert r9.noise==0.125
    assert r9.stage=='discovery'
    for x,y in discovery:
        r9.discover(x,y)
        r8.observe('public-world',1,x,y)
    assert r9.stage=='validation'
    return checkpoint,r9,r8,calibration,discovery

def prospective_48(world):
    checkpoint,r9,r8,cal,disc=trained_models()
    assert r8.mode['public-world']['1']=='fast'
    conventional=independent_fit(disc)
    assert all(r9.candidate(x)==independent_step(conventional,x) for x in range(256))
    odds=0.0001
    noise=(1+sum(int(y!=0) for _,y in cal))/(len(cal)+8)
    assert noise==r9.noise
    used=set(x for x,_ in cal+disc)
    prequential={'r8':0,'r9':0,'conventional':0,'r7':0}
    trace=[]
    first_switch=None
    for t in range(1,49):
        x=r9.selected_query(used)
        assert x is not None and x not in used
        used.add(x)
        y=0 if world=='stationary' else int((x&7)==7)
        stable=0
        fitted=independent_step(conventional,x)
        pconv=fitted if odds>=1 else stable
        guesses={'r8':r8.step('public-world',1,x), 'r9':r9.predict(x), 'conventional':pconv, 'r7':stable}
        for name,guess in guesses.items():prequential[name]+=int(guess!=y)
        r8.observe('public-world',1,x,y)
        r9.observe(x,y)
        if stable!=fitted:
            if y==fitted:odds*=(1-noise)/noise
            elif y==stable:odds*=noise/(1-noise)
        if first_switch is None and odds>=1:first_switch=t
        trace.append({'step':t,'before':x,'after':y, 'guesses':guesses, 'r8_mode':r8.mode['public-world']['1'],
                      'r9_mode':'candidate' if r9.log_odds>=0 else 'stable',
                      'conventional_mode':'candidate' if odds>=1 else 'stable'})
        assert r9.predict(x)==(fitted if odds>=1 else stable)
    return {'world':world,'prequential':prequential, 'first_conv_switch':first_switch,
            'r9_changes':r9.mode_changes,'r8_revisions':r8.revisions,'informative':r9.informative,
            'r9_final_mode':'candidate' if r9.log_odds>=0 else 'stable',
            'r8_final_mode':r8.mode['public-world']['1'],
            'r9_final_errors':sum(r9.predict(x)!= (0 if world=='stationary' else int((x&7)==7)) for x in range(256)),
            'conventional_final_errors':sum((independent_step(conventional,x) if odds>=1 else 0)!= (0 if world=='stationary' else int((x&7)==7)) for x in range(256)),
            'r9_checkpoint':r9.checkpoint(), 'trace':trace}

class R9SourceOnly(unittest.TestCase):
    def test_exact_original_source_blobs(self):
        root=Path(__file__).resolve().parents[1]
        self.assertEqual(source_blob(root/'r7'/'learner.py'),'204ecd993b954b23e66d6d1e8b3568e7c93183c5')
        self.assertEqual(source_blob(root/'r8'/'revision.py'),'346fb9eb7462208a6cbd28cfb51716c22e5ec857')

    def test_calibration_and_proposal_held_out(self):
        cp,r9,r8,cal,disc=trained_models()
        self.assertEqual(len(r9.calibration_rows),64)
        self.assertEqual(r9.calibration_mismatches,8)
        self.assertEqual(len(r9.discovery_rows),32)
        self.assertEqual(r9.r8.online_events,32)
        self.assertEqual(r9.r8.original_checkpoint,cp)
        self.assertEqual(r9.noise,0.125)
        self.assertEqual(r9.log_odds,__import__('math').log(0.0001))
        self.assertEqual(r9.predict(7),0)
        self.assertEqual(r9.candidate(7),1)
        self.assertEqual(r8.step('public-world',1,7),1)

    def test_stationary_false_alarm_and_true_change(self):
        stationary=prospective_48('stationary')
        changed=prospective_48('changed')
        self.assertEqual(stationary['prequential']['r9'],stationary['prequential']['conventional'])
        self.assertEqual(changed['prequential']['r9'],changed['prequential']['conventional'])
        self.assertLess(stationary['prequential']['r9'],stationary['prequential']['r8'])
        self.assertLessEqual(changed['prequential']['r9'],8)
        self.assertEqual(stationary['r9_final_errors'],0)
        self.assertEqual(changed['r9_final_errors'],0)
        self.assertEqual(stationary['r9_changes'],0)
        self.assertEqual(changed['r9_changes'],1)
        self.assertEqual(stationary['r9_final_mode'],'stable')
        self.assertEqual(changed['r9_final_mode'],'candidate')

    def test_checkpoint_cross_python_and_tamper(self):
        result=prospective_48('changed')
        raw=result['r9_checkpoint']
        script="""import json,sys
from research.native.itd02.r9.evidence_cells import EvidenceCells
x=EvidenceCells.restore(sys.stdin.buffer.read())
print(json.dumps({'stage':x.stage,'n':len(x.validation_rows),'m':x.mode_changes,
                  'p':x.predict(7),'noise':x.noise}))
"""
        p=subprocess.run([sys.executable,'-B','-c',script],input=raw,capture_output=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(json.loads(p.stdout),{'stage':'validation','n':48,'m':1,'p':1,'noise':0.125})
        obj=json.loads(raw);obj['data']['log_odds']=999
        with self.assertRaises(ValueError):EvidenceCells.restore(json.dumps(obj).encode())

    def test_invalid_feedback_atomic(self):
        cp,r9,r8,cal,disc=trained_models()
        original=r9.checkpoint()
        for v in [(256,0),(0,-1),(-1,0),(0,0.5)]:
            with self.assertRaises(ValueError):r9.observe(*v)
            self.assertEqual(r9.checkpoint(),original)
        with self.assertRaises(ValueError):r9.discover(38,0)
        self.assertEqual(r9.checkpoint(),original)

if __name__=='__main__':unittest.main()
