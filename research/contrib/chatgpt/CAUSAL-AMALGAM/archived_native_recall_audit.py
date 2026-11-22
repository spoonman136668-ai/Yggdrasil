"""Read-only source-mirror diagnostic for pinned, already-consumed CKAD26/Amalgam P0.

This mirrors only NativeEpisodeExperience's witness/block prediction arithmetic,
NOT its real class/restore/checkpoint ABI, and is NOT scientific first-use.
No protected source actions, outcomes generated, or checkpoint writes.
"""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
import sys
from zipfile import ZipFile

ZIP_HASHES = (
    'b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d',
    'bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6',
)
NATIVE_SHA = '5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d'
EPISODE_SHA = '9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4'
LINUX_JOINT_SHA = '576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8'
PUBLISHED_ANCHOR = (0.1443993732160158,0.7864317781394096,
                    0.1530560248052734,0.6696158228675264)

def read_zip(path, expected):
    raw=open(path,'rb').read()
    if sha256(raw).hexdigest()!=expected:raise ValueError('ARCHIVE_SHA256_MISMATCH')
    with ZipFile(path) as z: joint=z.read('amalgam-joint-state.json')
    outer=json.loads(joint)
    native=outer['native_ascii'].encode('ascii')
    if sha256(native).hexdigest()!=NATIVE_SHA:raise ValueError('NATIVE_SHA256_MISMATCH')
    obj=json.loads(native)
    if obj['accepted_native'] is not False or obj['scientific_pass'] is not False or obj['source_mode']!='engineering_fixture_only':raise ValueError('UNEXPECTED_MODEL_STATUS')
    episode=obj['experience_ascii'].encode('ascii')
    if sha256(episode).hexdigest()!=EPISODE_SHA:raise ValueError('EPISODE_SHA256_MISMATCH')
    data=json.loads(episode)
    if (len(data['episodes']),data['context_start'],data['stream_start'],data['refresh_start'])!=(1025,891,448,832):raise ValueError('UNEXPECTED_LEDGER_BOUNDARY')
    return sha256(joint).hexdigest(),native,data

class WitnessBank:
    def __init__(self,repair=True):
        self.repair=repair;self.ledger=[];self.projection=None;self.mismatch=[0,0]
        self.t=[[[0,0] for a in range(2)] for s in range(16)]
        self.r=[[[0,0] for a in range(2)] for s in range(16)]
        self.tloss=[Q(0),Q(0)];self.rloss=[Q(0),Q(0)];self.streak={}
    @staticmethod
    def choose(loss):return 0 if loss[0]<loss[1] else 1
    @staticmethod
    def prob(bank,s,a):
        f,y=bank[s][a];return Q(y+1,f+y+2)
    @staticmethod
    def add(bank,s,a,y):bank[s][a][y]=min(65535,bank[s][a][y]+1)
    def context(self,views):
        if self.projection is None:return None
        a=views[0][self.projection]
        return a if a==views[1][self.projection] else None
    @staticmethod
    def terminal_slots(c,a,y):
        return (12+y,12+y) if c is None else (c+2*a+4*y,8+c+2*y)
    def forecast(self,view,a,y=None,b=None):
        c=None if self.projection is None else view[self.projection]
        if y is None:
            s=2 if c is None else c
            return self.prob(self.t,(s,2)[self.choose(self.tloss)],a)
        s,p=self.terminal_slots(c,a,y)
        return self.prob(self.r,(s,p)[self.choose(self.rloss)],b)
    def local(self,target,bank,slot,action,outcome,identifier,selected):
        key=(target,slot,action);f,y=bank[slot][action];run=self.streak.get(key)
        if run is None and self.repair and selected:
            n=f+y;majority=int(y>f)
            if n>=12 and max(f,y)*5>=n*4 and outcome!=majority:run=(majority,(),(f,y))
        if run is not None:
            majority,ids,prior=run
            if outcome==majority:self.streak.pop(key,None)
            else:
                ids+=(identifier,)
                if len(ids)==3:
                    bank[slot][action]=[3 if outcome==0 else 0,3 if outcome==1 else 0]
                    self.streak.pop(key,None);return
                self.streak[key]=(majority,ids,prior)
        self.add(bank,slot,action,outcome)
    def projected(self,ev,c,rt,rr):
        eid,_,a,y,b,reward=ev;s,p=self.terminal_slots(c,a,y)
        self.local('transition',self.t,c,a,y,eid,rt)
        self.local('terminal',self.r,s,b,reward,eid,rr)
        self.add(self.r,p,b,reward)
    def observe(self,ev):
        eid,views,a,y,b,reward=ev
        c=self.context(views);s=2 if c is None else c
        rt=self.choose(self.tloss)==0;rr=self.choose(self.rloss)==0
        f,p=self.terminal_slots(c,a,y)
        for i,k in enumerate((s,2)):self.tloss[i]+=(self.prob(self.t,k,a)-y)**2
        for i,k in enumerate((f,p)):self.rloss[i]+=(self.prob(self.r,k,b)-reward)**2
        self.add(self.t,2,a,y);self.add(self.r,12+y,b,reward)
        if c is not None:self.projected(ev,c,rt,rr)
        self.ledger.append(ev)
        if len(self.ledger)<=8:
            for k in (0,1):self.mismatch[k]+=views[0][k]!=views[1][k]
            if len(self.ledger)==8 and self.mismatch[0]!=self.mismatch[1]:
                self.projection=int(self.mismatch[1]<self.mismatch[0])
                for old in self.ledger:
                    prev=self.context(old[1])
                    if prev is not None:self.projected(old,prev,False,False)

def audit(linux,windows):
    joint_a,native_a,e=read_zip(linux,ZIP_HASHES[0])
    joint_b,native_b,other=read_zip(windows,ZIP_HASHES[1])
    if joint_a!=LINUX_JOINT_SHA or native_a!=native_b or e['episodes']!=other['episodes']:raise ValueError('CROSS_PLATFORM_NATIVE_PARITY_FAILED')
    ledger=e['episodes'];start=e['context_start']
    models=[]
    for begin in range(0,start,32):
        rows=ledger[begin:min(begin+32,start)]
        if len(rows)<8:break
        m=WitnessBank(repair=e['repair'])
        for row in rows:m.observe(row)
        models.append(m)
    historic=len(models);models.append(WitnessBank(repair=e['repair']))
    prior=[Q(7,8*historic)]*historic+[Q(1,8)]
    weights=list(prior)
    # Three types of entirely pre-action selection; no present episode outcome in route.
    keys_seen=defaultdict(int);loss_by_key=defaultdict(lambda:[0.0]*historic)
    losses=defaultdict(list)
    for row in ledger[start:]:
        eid,views,a,y,b,reward=row;view=tuple(views[0]);key=(view[0],a)
        forecasts=[m.forecast(view,a) for m in models]
        mixed=sum(w*p for w,p in zip(weights,forecasts))
        top=max(range(historic),key=lambda i:(weights[i],-i))
        local=(min(range(historic),key=lambda i:(loss_by_key[key][i],i))
               if keys_seen[key]>=8 else top)
        preds=dict(global_mix=mixed,uniform_historical=sum(forecasts[:historic],Q(0))/historic,
                   global_best_prior=forecasts[top],contextual_prior_select=forecasts[local],
                   constant=Q(1,2),novel_only=forecasts[-1])
        for k,p in preds.items():losses[k].append(float((p-y)**2))
        for i,p in enumerate(forecasts[:historic]):loss_by_key[key][i]+=float((p-y)**2)
        keys_seen[key]+=1
        # Refresh and the novel expert consume the outcome only AFTER scoring.
        likelihoods=[]
        for w,m in zip(weights,models):
            p=m.forecast(view,a);q=m.forecast(view,a,y,b)
            likelihoods.append(w*(p if y else 1-p)*(q if reward else 1-q))
        norm=sum(likelihoods)
        weights=[Q(31,32)*l/norm+Q(1,32)*p for l,p in zip(likelihoods,prior)]
        models[-1].observe(row)
    cells=(((0,0),0),((0,0),1),((1,0),0),((1,0),1))
    final=[float(sum(w*m.forecast(view,a) for w,m in zip(weights,models))) for view,a in cells]
    if any(abs(a-b)>1e-14 for a,b in zip(final,PUBLISHED_ANCHOR)):raise ValueError('PUBLISHED_ANCHOR_READOUT_PARITY_FAILED')
    windows={'first8':(0,8),'first32':(0,32),'first64':(0,64),
             'whole_suffix':(0,len(ledger)-start),'last64':(len(ledger)-start-64,len(ledger)-start)}
    return {'schema':'yggdrasil.original-p0.readonly-recall-mirror.v1','scope':'retrospective exploratory source-mirror only',
            'source_first_use_actions':0,'native_runtime_imported':False,'scientific_gain_verified':False,
            'experiment_anchor_joint_sha256':joint_a,'windows_joint_sha256':joint_b,
            'cross_platform_native_sha256':NATIVE_SHA,'cross_platform_episode_sha256':EPISODE_SHA,
            'original_witnesses':len(ledger),'historical_block_experts':historic,'novel_experts':1,
            'prequential_suffix_count':len(ledger)-start,'final_anchor_readout':final,
            'published_anchor_match':True,'brier':{win:{name:sum(loss[a:b])/(b-a) for name,loss in sorted(losses.items())}
                      for win,(a,b) in windows.items()},'key_counts':{str(k):v for k,v in sorted(keys_seen.items())},
            'limitations':['Reconstructed Python arithmetic, not actual NativeEpisodeExperience.restore execution',
                           'All 134 episode outcomes were already consumed in earlier engineering work',
                           'No new held source, independently qualified science, native integration or cost-matched trained control',
                           'Contextual selector uses prior observed outcomes but no current labels; no tuning or preregistered claim']}

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: python archived_native_recall_audit.py LINUX_ZIP WINDOWS_ZIP')
    print(json.dumps(audit(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))
