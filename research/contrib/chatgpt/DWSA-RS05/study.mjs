// RS05 source-free, preregistered, paired synthetic single-intervention test.
// It tests conditional causal disambiguation, NOT a trained donor or native Yggdrasil.
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const N=2048, ACTIONS=8, CAP=.10;
const model0=Array(ACTIONS).fill(.5),model1=Array(ACTIONS).fill(.5);
model0[7]=.2; model1[7]=.8;
const all=Array.from({length:ACTIONS},(_,i)=>i);
const H=p=>p===0||p===1?0:-p*Math.log2(p)-(1-p)*Math.log2(1-p);
function chooseProbe(m0,m1){
  if(!Array.isArray(m0)||!Array.isArray(m1)||m0.length!==ACTIONS||m1.length!==ACTIONS)throw Error('BAD_MODEL');
  if([...m0,...m1].some(p=>typeof p!=='number'||!Number.isFinite(p)||p<0||p>1))throw Error('BAD_PROB');
  const scores=all.map(a=>H((m0[a]+m1[a])/2)-(H(m0[a])+H(m1[a]))/2);
  return scores.indexOf(Math.max(...scores));
}
function uniformAction(i){return (Math.floor(i/2)*5+(i%2)*3+1)%ACTIONS;}
function outcome(tag,i,a,p){
  const digest=createHash('sha256').update('rs05:'+tag+':'+i+':'+a).digest('hex');
  return parseInt(digest.slice(0,8),16)/2**32<p?1:0;
}
function posterior(a,y){
  if(y!==0&&y!==1)throw Error('BAD_OBSERVATION');
  const p0=y?model0[a]:1-model0[a],p1=y?model1[a]:1-model1[a];
  return p1/(p0+p1);
}
function forecast(a,y,heldAction,cap=true){
  if(heldAction!==7||a!==7)return .5;
  const post=posterior(a,y);
  const q=model0[heldAction]*(1-post)+model1[heldAction]*post;
  return cap?Math.max(.5-CAP,Math.min(.5+CAP,q)):q;
}
function expectedBrier(p,q){return p*(1-q)**2+(1-p)*q*q;}
function probe(tag,i,a,p){return {action:a,observation:outcome(tag,i,a,p)};}
function chooseSafe(){return chooseProbe(model0,model1);}
function score(){
  const k=chooseSafe(),sum={raw:0,active:0,uniform:0,symbolic:0,fullBayes:0,sham:0,inverted:0,nullRaw:0,nullActive:0,oldRaw:0,oldActive:0};
  const counts={active:0,uniform:0,symbolic:0,fullBayes:0,inverted:0,nullActive:0};
  for(let i=0;i<N;i++){
    const world=i%2,actual=world?model1:model0,p=actual[7];
    const a=probe('aligned',i,k,actual[k]);counts.active++;
    const uAction=uniformAction(i),u=probe('aligned',i,uAction,actual[uAction]);counts.uniform++;
    const s=probe('aligned',i,7,actual[7]);counts.symbolic++;
    const full=probe('aligned',i,7,actual[7]);counts.fullBayes++;
    counts.inverted++;
    const predict=forecast(a.action,a.observation,7);
    sum.raw+=expectedBrier(p,.5);
    sum.active+=expectedBrier(p,predict);
    sum.uniform+=expectedBrier(p,forecast(u.action,u.observation,7));
    sum.symbolic+=expectedBrier(p,forecast(s.action,s.observation,7));
    sum.fullBayes+=expectedBrier(p,forecast(full.action,full.observation,7,false));
    sum.sham+=expectedBrier(p,.6);
    sum.inverted+=expectedBrier(p,forecast(a.action,1-a.observation,7));
    sum.oldRaw+=expectedBrier(.5,.5);
    sum.oldActive+=expectedBrier(.5,forecast(a.action,a.observation,0));
    const n=probe('null',i,k,.5);counts.nullActive++;
    sum.nullRaw+=expectedBrier(.5,.5);
    sum.nullActive+=expectedBrier(.5,forecast(n.action,n.observation,7));
  }
  return {schema:'dwsa-rs05.source-free.synthetic.v1',parent_sha:'3387637118f8b088a4f5d2a43ed20cf91d1715c3',
    episodes:N,probeSelected:k,simulated_actions:counts,brier:Object.fromEntries(Object.entries(sum).map(([key,value])=>[key,value/N])),
    protected_source_actions:0,trained_donor_verified:false,native_yggdrasil_used:false,scientific_gain_verified:false};
}
assert.equal(chooseSafe(),7,'informative action must be 7');
assert.equal(forecast(0,1,7),.5,'noninformative action must not change prediction');
assert.equal(forecast(7,1,0),.5,'old context must not change');
assert.throws(()=>chooseProbe([.5],[.5]),/BAD_MODEL/);
assert.throws(()=>posterior(7,3),/BAD_OBSERVATION/);
const out=score(),b=out.brier;
for(const v of Object.values(out.simulated_actions))assert.equal(v,N,'same simulated query budget');
assert.ok(Math.abs(b.active-b.symbolic)<1e-12,'cannot beat perfectly informed bounded symbolic');
assert.ok(Math.abs(b.oldRaw-b.oldActive)<1e-12,'old contexts retained');
assert.ok(Math.abs(b.raw-.25)<1e-12&&Math.abs(b.nullRaw-.25)<1e-12,'unmodified raw reference');
const gainRaw=b.raw-b.active,gainUniform=b.uniform-b.active;
let classification;
if(gainRaw>=.015&&gainUniform>=.010&&b.nullActive>b.nullRaw){
  classification='MIXED_DEV_ONLY';
}else if(gainRaw>=.015&&gainUniform>=.010&&b.nullActive<=b.nullRaw){
  classification='ENGINEERING_SUPPORTED_DEV_ONLY';
}else{
  classification='NEGATIVE_DEV_ONLY';
}
console.log(JSON.stringify({...out,compared:{active_vs_raw_brier_gain:gainRaw,active_vs_uniform_brier_gain:gainUniform,active_vs_bounded_symbolic_gain:b.symbolic-b.active,null_drift:b.nullActive-b.nullRaw,old_drift:b.oldActive-b.oldRaw},classification},null,2));
