// GKD-02 — GPT-donor contradiction and bounded correction.
// Preregistered FIRST at 2f3482d3f36cd7e0a9d20b0d5c20150bcea0c393.
// Synthetic development only; no source model inference, native learner, or original causal-world action.
import {createHash} from "node:crypto";
const sha=b=>createHash("sha256").update(b).digest();
const need=(ok,msg)=>{if(!ok)throw Error("GKD02_FAIL_CLOSED:"+msg);};
const close=(a,b,t=1e-9)=>Math.abs(a-b)<=t;
const baseline=x=>{
  need(Array.isArray(x)&&x.length===7&&x.every(Number.isFinite),"INPUT");
  const [v,r1,r2,t,m,c,top]=x;
  need(v>=0&&r1>0&&r2>0&&t>=0&&m>0&&c>0&&(top===0||top===1),"DOMAIN");
  const r=top===0?r1+r2:r1*r2/(r1+r2);
  const b=(v*v/r)*t/(m*c);
  need(Number.isFinite(b)&&b>0,"ZERO_OR_NONFINITE_BASE");
  return b;
};
const slot=()=>({eta:1,pending:0,count:0,pCount:0,ambiguous:0});
export const empty=()=>Array.from({length:4},slot);
const context=c=>need(Number.isInteger(c)&&c>=0&&c<4,"CONTEXT");
function observationValue(x,y){
  need(Number.isFinite(y)&&y>=0,"OBSERVATION");
  const e=y/baseline(x);
  need(Number.isFinite(e)&&e>0&&e<=2,"ETA_RANGE");
  return e;
}
export function observe(s,c,x,y){
  context(c);need(Array.isArray(s)&&s.length===4,"STATE");
  const e=observationValue(x,y),v=s[c];
  need(v&&!v.ambiguous,"FROZEN_AMBIGUOUS");
  if(v.pCount){
    if(close(e,v.eta)){v.pending=0;v.pCount=0;v.count=2;}
    else if(close(e,v.pending)){v.eta=(v.pending+e)/2;v.pending=0;v.pCount=0;v.count=2;}
    else{v.pending=0;v.pCount=0;v.count=0;v.ambiguous=1;}
  }else if(close(e,v.eta)){v.count=Math.min(2,v.count+1);}
  else{v.pending=e;v.pCount=1;}
}
export function predict(s,c,x){
  context(c);
  const v=s[c],value=baseline(x)*v.eta;
  return {value,confident:v.count===2&&!v.pCount&&!v.ambiguous};
}
export function encode(s){
  need(Array.isArray(s)&&s.length===4,"STATE");
  const b=Buffer.alloc(84);
  b.write("GKD2",0,"ascii");b[4]=1;b[5]=4;
  for(let c=0;c<4;c++){
    const v=s[c],i=8+c*19;
    need(v&&Number.isFinite(v.eta)&&v.eta>0&&v.eta<=2,"TRUST");
    need(Number.isFinite(v.pending)&&v.pending>=0&&v.pending<=2,"PENDING");
    need(Number.isInteger(v.count)&&v.count>=0&&v.count<=2,"COUNT");
    need((v.pCount===0||v.pCount===1)&&(v.ambiguous===0||v.ambiguous===1),"FLAGS");
    need((v.pCount===0&&v.pending===0)||(v.pCount===1&&v.pending>0),"PENDING_CANONICAL");
    b.writeDoubleLE(v.eta,i);b.writeDoubleLE(v.pending,i+8);
    b[i+16]=v.count;b[i+17]=v.pCount;b[i+18]=v.ambiguous;
  }
  return Buffer.concat([b,sha(b)]);
}
export function decode(raw){
  need(Buffer.isBuffer(raw)&&raw.length===116,"SIZE");
  const b=raw.subarray(0,84);
  need(sha(b).equals(raw.subarray(84)),"DIGEST");
  need(b.toString("ascii",0,4)==="GKD2"&&b[4]===1&&b[5]===4&&b[6]===0&&b[7]===0,"HEADER");
  const out=[];
  for(let c=0;c<4;c++){
    const i=8+c*19;
    out.push({eta:b.readDoubleLE(i),pending:b.readDoubleLE(i+8),count:b[i+16],pCount:b[i+17],ambiguous:b[i+18]});
  }
  need(encode(out).equals(raw),"NONCANONICAL");
  return out;
}
// Independently authored exact symbolic control: separate state representation/logic.
class ExactSymbolic {
  constructor(){this.slots=Array.from({length:4},()=>({gain:1,guess:null,readings:0,unknown:false}));}
  observe(c,x,y){
    context(c);
    const e=observationValue(x,y),v=this.slots[c];
    need(!v.unknown,"SYMBOLIC_FROZEN");
    if(v.guess!==null){
      if(close(e,v.gain)){v.guess=null;v.readings=2;}
      else if(close(e,v.guess)){v.gain=(v.guess+e)/2;v.guess=null;v.readings=2;}
      else{v.guess=null;v.readings=0;v.unknown=true;}
    }else if(close(e,v.gain)){v.readings=Math.min(2,v.readings+1);}
    else v.guess=e;
  }
  predict(c,x){context(c);const s=this.slots[c];return{value:baseline(x)*s.gain,confident:s.readings===2&&s.guess===null&&!s.unknown};}
}
// Conventional fitted OLS, last two consequences/context; fully refit on the same evidence.
class ContextOLS {
  constructor(){this.rows=Array.from({length:4},()=>[]);}
  observe(c,x,y){context(c);const rows=this.rows[c];rows.push([baseline(x),y]);if(rows.length>2)rows.shift();}
  predict(c,x){
    const rows=this.rows[c];
    const numerator=rows.reduce((a,[b,y])=>a+b*y,0),denominator=rows.reduce((a,[b])=>a+b*b,0);
    return baseline(x)*(denominator>0?numerator/denominator:1);
  }
}
const rng=seed=>{let s=seed>>>0;return()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)/4294967296;};};
const specimen=(u,n)=>[2+22*u(),1+19*u(),1+19*u(),1+9*u(),0.2+4.8*u(),100+900*u(),n%2];
const err=(a,b)=>Math.abs(a-b)/Math.max(1,Math.abs(b));
const fail=(f,reason)=>{let caught=false;try{f();}catch(e){caught=String(e.message).startsWith("GKD02_FAIL_CLOSED:");}need(caught,"NEGATIVE_"+reason);};
export function run(){
  const seeds=[1101,1102,1103,1104],effs=[1,0.8,0.55,0.3];
  let scored=0,symbolicTies=0,olsTies=0,maxError=0,donorWrong=0;
  let spuriousAbstain=0,spuriousRecovery=0,isolatedRepair=0,coldRestores=0,offAbstain=0;
  let witnesses=0,checkpointDigest=null;
  for(const seed of seeds)for(let j=0;j<16;j++){
    const u=rng((seed^Math.imul(j,0x9e3779b9))>>>0);
    let n=0;const sample=()=>specimen(u,n++);
    const laws=Array.from({length:4},(_,c)=>effs[(c+j)%4]);
    const native=empty(),sym=new ExactSymbolic(),ols=new ContextOLS();
    const learn=(c,x,e)=>{const y=e*baseline(x);observe(native,c,x,y);sym.observe(c,x,y);ols.observe(c,x,y);witnesses++;};
    const score=()=>{
      for(let c=0;c<4;c++)for(let k=0;k<3;k++){
        const x=sample(),truth=laws[c]*baseline(x);
        const got=predict(native,c,x),ref=sym.predict(c,x),fit=ols.predict(c,x);
        need(got.confident&&ref.confident,"CONFIDENCE");
        const e=err(got.value,truth);
        maxError=Math.max(maxError,e);need(e<=1e-9,"PREDICTION");
        need(err(got.value,ref.value)<=1e-9,"SYMBOLIC");symbolicTies++;
        need(err(got.value,fit)<=1e-9,"OLS");olsTies++;
        if(err(baseline(x),truth)>1e-9)donorWrong++;
        scored++;
      }
    };
    const cold=()=>{
      const bytes=encode(native),restored=decode(Buffer.from(bytes));
      need(bytes.length===116&&encode(restored).equals(bytes),"COLD");
      for(let c=0;c<4;c++)need(JSON.stringify(restored[c])===JSON.stringify(native[c]),"COLD_SLOT");
      checkpointDigest=sha(bytes).toString("hex");coldRestores++;
    };
    for(let c=0;c<4;c++)for(let k=0;k<2;k++)learn(c,sample(),laws[c]);
    score();cold();
    const old=structuredClone(native);
    const bad=sample();learn(0,bad,laws[0]+0.2);
    if(!predict(native,0,bad).confident&&native[0].eta===old[0].eta)spuriousAbstain++;
    const recovery=sample();learn(0,recovery,laws[0]);
    if(predict(native,0,recovery).confident&&native[0].eta===old[0].eta)spuriousRecovery++;
    const oldEta=laws[2];laws[2]=oldEta===1?0.35:oldEta+0.1;
    for(let k=0;k<2;k++)learn(2,sample(),laws[2]);
    if([0,1,3].every(c=>native[c].eta===old[c].eta)&&err(native[2].eta,laws[2])<=1e-9&&predict(native,2,recovery).confident)isolatedRepair++;
    score();cold();
  }
  // OFF law: two distinct voltage readings cannot be explained by one eta coefficient.
  for(let j=0;j<16;j++){
    const u=rng(2201+j),state=empty();
    for(const v of [4,18]){
      const x=specimen(u,j);x[0]=v;
      const y=(0.2+0.02*v)*baseline(x);
      observe(state,3,x,y);
    }
    for(let k=0;k<3;k++){
      const x=specimen(u,k);
      if(!predict(state,3,x).confident)offAbstain++;
    }
  }
  const s=empty(),valid=[8,4,5,2,1,300,0],signed=encode(s);
  const corrupt=Buffer.from(signed);corrupt[9]^=1;
  fail(()=>decode(corrupt),"DIGEST");
  fail(()=>decode(Buffer.alloc(115)),"SIZE");
  fail(()=>predict(s,4,valid),"CONTEXT");
  fail(()=>observe(s,0,[0,4,5,0,1,300,0],1),"ZERO_BASE");
  fail(()=>observe(s,0,valid,NaN),"NONFINITE");
  fail(()=>observe(s,0,valid,-1),"NEGATIVE_OUTCOME");
  need(scored===1536&&symbolicTies===1536&&olsTies===1536&&maxError<=1e-9,"PRIMARY");
  need(witnesses===768&&spuriousAbstain===64&&spuriousRecovery===64&&isolatedRepair===64,"REPAIR");
  need(coldRestores===128&&offAbstain===48,"RETENTION_AND_OFF");
  const result={
    schema:"yggdrasil.gkd02.donor-contradiction-dev.v1",experiment_id:"GKD-02",
    preregistration_sha:"2f3482d3f36cd7e0a9d20b0d5c20150bcea0c393",
    classification:"ENGINEERING_DEV_PASS_SCIENTIFIC_UNVERIFIED",
    worlds:64,seeds,witnesses,heldout:scored,symbolic_ties:symbolicTies,
    fitted_ols_ties:olsTies,max_relative_error:maxError,
    donor_prior_wrong_predictions:donorWrong,spurious_abstentions:spuriousAbstain,
    spurious_recoveries:spuriousRecovery,isolated_repairs:isolatedRepair,
    cold_restores:coldRestores,off_family_abstentions:offAbstain,
    checkpoint_bytes:116,sample_checkpoint_sha256:checkpointDigest,
    invalid_guard_cases_pass:6,teacher_inference_at_recipient_runtime:0,
    scientific_gain_verified:false,native_integration:false,
    limitation:"Same known eta*ideal family; exact symbolic and fully fitted OLS tie; no independent causal law discovery, no new original world and no automatic LLM semantic compiler"
  };
  console.log(JSON.stringify(result,null,2));return result;
}
if(process.argv[1]?.endsWith("/GKD-02/run.mjs")||process.argv[1]?.endsWith("\\GKD-02\\run.mjs"))run();
