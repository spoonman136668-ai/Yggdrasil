"""NCI04 frozen A-B-A observational predictive state probe."""
import json, math, os, unittest
from predictive import PredictiveColony, LocalOnly, RecurrentControl
MASK=(1<<32)-1
class RNG:
    def __init__(self,seed):self.v=(seed*747796405+2891336453)&MASK
    def next(self):
        v=self.v;v^=(v<<13)&MASK;v^=v>>17;v^=(v<<5)&MASK
        self.v=v&MASK;return self.v
    def value(self):return (self.next()%10000)/10000
def operators(seed,stress):
    r=RNG(seed);out=[]
    for _ in range(2):
        m=[[0.0]*4 for i in range(4)]
        for i in range(4):m[i][i]=.65+.1*r.value()
        for i in range(4):
            a=r.next()%4;b=r.next()%3
            if b>=a:b+=1
            sign=-1 if r.next()%2==0 else 1
            m[a][b]+=sign*(.20+.09*r.value())
            if stress:m[b][a]+=sign*.08
        out.append(m)
    return out
def world(seed,stress):
    operators_=operators(seed,stress)
    r=RNG(seed^0x51943af)
    x=[.8,-.4,.3,-.7]
    result=[tuple(x)]
    for t in range(72):
        k=1 if 24<=t<48 else 0
        v=[sum(operators_[k][i][j]*x[j] for j in range(4)) for i in range(4)]
        if t%9==0:
            j=r.next()%4;v[j]+=.06*(2*r.value()-1)
        x=[max(-1,min(1,z)) for z in v]
        result.append(tuple(x))
    return result
def mse(a,b):return sum((v-w)**2 for v,w in zip(a,b))/4
def evaluate(seed,stress,erase=False):
    c=PredictiveColony();local=LocalOnly();strong=RecurrentControl()
    x=world(seed,stress);scores={}
    for t in range(72):
        if erase and t==48:c.erase_phenotype()
        observed,next_=x[t],x[t+1]
        phase='A1' if t<24 else 'B' if t<48 else 'A2'
        for name,model in [('candidate',c),('local',local),('strong',strong)]:
            key=phase+'_'+name
            scores[key]=scores.get(key,0)+mse(model.predict(observed),next_)/24
            model.learn(observed,next_)
    return scores
def results():
    m={}
    for name,start,stress in [('train',41000,False),('development',42000,False),('stress',43000,True)]:
        for seed in range(start,start+32):
            v=evaluate(seed,stress)
            for k,value in v.items():m[name+'_'+k]=m.get(name+'_'+k,0)+value/32
            if name=='stress':
                erased=evaluate(seed,True,True)
                m['stress_A2_erased']=m.get('stress_A2_erased',0)+erased['A2_candidate']/32
    candidate=m['stress_A2_candidate']
    control=min(m['stress_A2_local'],m['stress_A2_strong'])
    gain=(control-candidate)/control if control else 0
    lesion=m['stress_A2_erased']-candidate
    qualified=(gain>=.05 and lesion>=candidate*.10
               and candidate<=m['stress_A1_candidate']*1.10)
    return {'schema':'nci04.yggdrasil.predictive_state.sourceonly.v1',
            'result':'PASS_DEVELOPMENT_SIGNAL_ONLY' if qualified else 'NEGATIVE',
            'metrics':m,'relative_gain':gain,'memory_erase_extra_error':lesion,
            'shared_genome_weights':3,'phenotype_cells':8,'neighbor_degree':2,
            'matched_local_weights':3,'strong_recurrent_weights':32,
            'hidden_causal_matrix_exposed':False,'context_label_exposed':False,
            'supervised_intermediate_causal_answers':False,
            'hardcoded_graph_traversal':False,'entity_binding_proven':False,
            'scientific_first_use':0}
class NCI04Tests(unittest.TestCase):
    def test_bounded_neighbor_only_and_query_readonly(self):
        c=PredictiveColony()
        x=(.5,-.5,.3,-.3)
        old=(list(c.phenotype),list(c.genome),c.updates)
        for _ in range(4):c.predict(x);c.rollout(x,2)
        self.assertEqual(old,(c.phenotype,c.genome,c.updates))
        with self.assertRaises(ValueError):c.predict((float('nan'),)*4)
        with self.assertRaises(ValueError):c.rollout(x,0)
        c.learn(x,(.3,-.2,.1,-.1))
        self.assertEqual(len(c.phenotype),8)
        self.assertEqual(len(c.genome),3)
        before=list(c.genome)
        c.erase_phenotype()
        self.assertEqual(c.genome,before)
        self.assertEqual(c.phenotype,[0.0]*8)
    def test_frozen_source_free_aba_and_negative_retained(self):
        r=results();self.assertIn(r['result'],('NEGATIVE','PASS_DEVELOPMENT_SIGNAL_ONLY'))
        self.assertEqual(r['scientific_first_use'],0)
        self.assertEqual(r,results())
        out=json.dumps(r,sort_keys=True)
        print('NCI04_Y_RESULT='+out)
        if name:=os.environ.get('NCI04_EVIDENCE'):
            with open(name,'x',encoding='utf8') as f:f.write(out+'\n')
if __name__=='__main__':unittest.main()
