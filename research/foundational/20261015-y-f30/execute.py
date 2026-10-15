"""Y-F30: can learned second-sensor choice use the first for source regime?
A source-identifiability diagnostic, not a new general-purpose information-value
theorem. Source0 is a noisy latent-mode measurement unrelated to target truth.
Source1 or Source2 predicts target truth conditional on the mode; a static pair
cannot always succeed. One unseen regime reverses the first source polarity.
All tasks are DEVELOPMENT-only; 576B native state plus external labeled anchor
bank. Source truth and unseen regime names are never given to candidate policy.
"""
from __future__ import annotations
import importlib.util,json,math,random,sys,hashlib
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("yf28_sensor_custody",str(HERE.parent/"20261015-y-f28"/"sensor_custody.py"))
custody=importlib.util.module_from_spec(sp);sys.modules[sp.name]=custody;sp.loader.exec_module(custody)
torch.set_num_threads(1);torch.manual_seed(3030)
TRAIN_SEEDS=range(174000,174120)
TEST_SEEDS=range(175500,175524)
TRAIN_REGIMES=(0,1,2)
TEST_REGIMES=(3,4)
FAMILIES=(108,109,110,111)
ARMS=("learned","conditional_empirical","simple_marker","static_calibrated","fixed_expert1","privileged_oracle")
CALIBRATION=40;NATIVE_BYTES=576;EXTERNAL_CALIBRATION_BYTES=40*(4+1)*8
def stream(seed,episode,regime):
 return random.Random(seed*1000003+episode*7117+regime*331)
def source(seed,episode,regime):
 r=stream(seed,episode,regime)
 bit=r.randrange(2);mode=r.randrange(2)
 # For regimes 0..3 mode0 => low mode sensor value. Unseen test regime4
 # inverts the meaning of that first reading, without changing its marginal.
 reversal=(regime==4)
 cue=(.23 if mode==0 else .77)
 if reversal:cue=1-cue
 first=max(0.,min(1.,cue+r.gauss(0,.045 if regime%2==0 else .065)))
 effect=1 if bit else -1
 strong=.32 if regime%2==0 else .28
 weak=.01 if regime%2==0 else -.025
 s1=max(0.,min(1.,.5+(strong if mode==0 else weak)*effect+r.gauss(0,.095)))
 s2=max(0.,min(1.,.5+(strong if mode==1 else weak)*effect+r.gauss(0,.095)))
 s3=max(0.,min(1.,.5+.10*effect+r.gauss(0,.13)))
 return bit,(first,s1,s2,s3)
def calibrate(seed,regime):
 # Public anchor truth is known; its index/source cohort is separate.
 bank=[source(seed+95000+i*19,200+i,regime) for i in range(CALIBRATION)]
 corr=[];miss=[]
 for j in range(4):
  corr.append(sum((2*v[j]-1)*(2*truth-1) for truth,v in bank)/len(bank))
  miss.append(sum(v[j]==.5 for _,v in bank)/len(bank))
 return custody.PublicSensorInfo(tuple(corr),tuple(miss)),bank
def first(pub):return 0
def read_probability(second):
 return 1/(1+math.exp(-max(-20,min(20,7*(2*second.value-1)))))
def second(mode,pub,read,bank,weights):
 opts=(1,2)
 if mode=="learned":
  z=weights[0]+weights[1]*(2*read.value-1)
  return 2 if z>=0 else 1
 if mode=="simple_marker":return 1 if read.value<.5 else 2
 if mode=="static_calibrated":
  return max(opts,key=lambda j:(abs(pub.reliability[j]),-j))
 if mode=="fixed_expert1":return 1
 if mode=="conditional_empirical":
  # Strong cheap fair control: public labeled calibration outcomes, weighted
  # by similarity of its first observation to the purchased first reading.
  def risk(j):
   total=mass=0.
   for truth,values in bank:
    w=math.exp(-((values[0]-read.value)/.12)**2)
    pred=read_probability(custody.PurchasedReading(j,values[j]))
    total+=w*(pred-truth)**2;mass+=w
   return total/max(mass,1e-10)
  return min(opts,key=lambda j:(risk(j),j))
 raise ValueError(mode)
def fit():
 x=[];p1=[];p2=[];y=[]
 for seed in TRAIN_SEEDS:
  for regime in TRAIN_REGIMES:
   for role in range(3):
    truth,vals=source(seed,role+10,regime)
    x.append([1.,2*vals[0]-1])
    p1.append(read_probability(custody.PurchasedReading(1,vals[1])))
    p2.append(read_probability(custody.PurchasedReading(2,vals[2])))
    y.append(float(truth))
 X=torch.tensor(x,dtype=torch.float32)
 P1=torch.tensor(p1,dtype=torch.float32)
 P2=torch.tensor(p2,dtype=torch.float32)
 Y=torch.tensor(y,dtype=torch.float32)
 W=torch.nn.Parameter(torch.zeros(2))
 optimizer=torch.optim.Adam([W],lr=.07)
 for step in range(260):
  optimizer.zero_grad()
  gate=torch.sigmoid(X@W)
  prob=(gate*P2+(1-gate)*P1).clamp(1e-5,1-1e-5)
  loss=torch.nn.functional.binary_cross_entropy(prob,Y)
  loss.backward();optimizer.step()
 return [float(w) for w in W.detach()],float(loss.detach()),len(y)
def relation(bits,fam):
 if fam%2==0:return bool(bits[0]^bits[1]^bits[2])
 return sum(int(v) for v in bits)>=2
def evaluate():
 custody.validate_disjoint(
   {"seeds":set(TRAIN_SEEDS),"entities":{v+10000 for v in TRAIN_SEEDS},"families":{120,121}},
   {"seeds":set(TEST_SEEDS),"entities":{v+50000 for v in TEST_SEEDS},"families":set(FAMILIES)})
 weights,loss,ntrain=fit();rows=[]
 for seed in TEST_SEEDS:
  for fam in FAMILIES:
   for regime in TEST_REGIMES:
    info,bank=calibrate(seed,regime)
    bits=[];observations=[]
    for role in range(3):
     truth,vals=source(seed,role+300,regime)
     bits.append(truth);observations.append(vals)
    truth=relation(bits,fam)
    predictions={"privileged_oracle":truth};traces={}
    for arm in ARMS[:-1]:
     predicted=[];cost=[];trace=[]
     for vals in observations:
      receipt=custody.evaluate_policy(vals,info,first,
        lambda pub,read,a=arm:second(a,pub,read,bank,weights),
        NATIVE_BYTES,EXTERNAL_CALIBRATION_BYTES)
      if receipt.physical_reads!=2:raise AssertionError("not two actual reads")
      p1,p2=receipt.trace
      if p1.sensor!=0 or p2.sensor not in (1,2):raise AssertionError("illegal source action")
      predicted.append(read_probability(p2)>=.5)
      cost.append(receipt.physical_reads)
      trace.append([[k.sensor,round(k.value,7)] for k in receipt.trace])
     predictions[arm]=relation(predicted,fam)
     traces[arm]=trace
    rows.append(dict(seed=seed,family=fam,regime=regime,truth=truth,
      predictions=predictions,receipts=traces,
      public_reliabilities=info.reliability,
      anchor_count=len(bank)))
 def score(name,rs):
  n=len(rs);good=sum(r["predictions"][name]==r["truth"] for r in rs)
  fp=sum(r["predictions"][name] and not r["truth"] for r in rs)
  fn=sum(not r["predictions"][name] and r["truth"] for r in rs)
  return dict(total=n,correct=good,accuracy=good/n,false_positives=fp,false_negatives=fn)
 scores={m:score(m,rows) for m in ARMS}
 by={str(regime):{m:score(m,[r for r in rows if r["regime"]==regime]) for m in ARMS} for regime in TEST_REGIMES}
 # Counterfactual first-value test with identical public anchor bank.
 switches=0
 for seed in TEST_SEEDS:
  for regime in TEST_REGIMES:
   pub,bank=calibrate(seed,regime)
   lo=custody.PurchasedReading(0,.2);hi=custody.PurchasedReading(0,.8)
   switches+=second("learned",pub,lo,bank,weights)!=second("learned",pub,hi,bank,weights)
 best=max(scores[m]["accuracy"] for m in ARMS[1:-1])
 passed=(scores["learned"]["accuracy"]>=.9 and
  scores["learned"]["accuracy"]-best>=.02 and
  all(by[str(r)]["learned"]["accuracy"]>=.85 for r in TEST_REGIMES)
  and switches>=len(TEST_SEEDS))
 return dict(schema="yggdrasil.f30.identified-conditional-sensing.dev.v1",
   stage="DEVELOPMENT_ONLY",parent="21ebe0696474638048123f15f7799cd76d11be3c",
   training_seed_range=[174000,174120],test_seed_range=[175500,175524],
   training_regimes=list(TRAIN_REGIMES),unseen_test_regimes=list(TEST_REGIMES),
   test_family_ids=list(FAMILIES),learned_policy_weights=weights,
   train_only_examples=ntrain,train_only_loss=loss,questions=len(rows),
   first_source_is_mode_probe_not_truth_sensor=True,
   first_probe_mode_cue_polarity_reverses_in_test_regime4=True,
   source_mode_not_given_to_learned_policy=True,
   hidden_truth_not_given_to_learned_policy=True,
   learned_conditional_switch_count=switches,possible_switch_count=48,
   actual_two_purchased_readings_per_role=True,
   native_state_bytes=NATIVE_BYTES,calibration_external_bytes=EXTERNAL_CALIBRATION_BYTES,
   known_anchor_count=CALIBRATION,rows=rows,scores=scores,by_test_regime=by,
   verdict="DEVELOPMENT_CONDITIONAL_VOI_LEARNED_GAIN" if passed else "DEVELOPMENT_CONDITIONAL_VOI_NO_QUALIFIED_GAIN",
   source_born_independently=False,sealed_first_use=False,accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
