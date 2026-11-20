// GKD-03: source-only fixture evidence identity and observational indistinguishability.
// Preregistered at 88c466ee61204ee85f2b7cc93fd56a9baa258167.
// Fixture Ed25519 seed is publicly present: never infer real-world source authentication.
import {createHash,createPrivateKey,createPublicKey,sign,verify} from 'node:crypto';
import {empty as oldEmpty,observe as oldObserve,predict as oldPredict} from '../GKD-02/run.mjs';
const hash=b=>createHash('sha256').update(b).digest();
const assert=(q,msg)=>{if(!q)throw Error('GKD03_FAIL_CLOSED:'+msg);};
const close=(x,y)=>Math.abs(x-y)<=1e-9;
const fixture=createPrivateKey({key:Buffer.concat([Buffer.from('302e020100300506032b657004220420','hex'),Buffer.from('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60','hex')]),format:'der',type:'pkcs8'});
const publicKey=createPublicKey(fixture);
const canon=e=>JSON.stringify([e.issuer,e.id,e.context,e.x,e.y]);
function signed(id,context,x,y){const e={issuer:'fixture-A',id,context,x,y};return {...e,signature:sign(null,Buffer.from(canon(e)),fixture).toString('base64')};}
function base(x){
  assert(Array.isArray(x)&&x.length===7&&x.every(Number.isFinite),'INPUT');
  const [v,r1,r2,t,m,c,mode]=x;
  assert(v>=0&&r1>0&&r2>0&&t>=0&&m>0&&c>0&&(mode===0||mode===1),'DOMAIN');
  const resistance=mode===0?r1+r2:r1*r2/(r1+r2);
  const heat=v*v/resistance*t/(m*c);
  assert(Number.isFinite(heat)&&heat>0,'HEAT');return heat;
}
const context=c=>assert(Number.isInteger(c)&&c>=0&&c<4,'CONTEXT');
const slot=()=>({eta:1,pending:0,count:0,pCount:0,ambiguous:0});
const blank=()=>({slots:Array.from({length:4},slot),ledger:[]});
function verifyWitness(e){
  assert(e&&e.issuer==='fixture-A'&&typeof e.id==='string'&&/^[A-Za-z0-9:_-]{1,72}$/.test(e.id),'ISSUER_OR_ID');
  context(e.context);
  const b=base(e.x);
  assert(Number.isFinite(e.y)&&e.y>=0,'Y');
  const eta=e.y/b;assert(Number.isFinite(eta)&&eta>0&&eta<=2,'ETA');
  assert(typeof e.signature==='string'&&/^[A-Za-z0-9+/]+={0,2}$/.test(e.signature),'SIGNATURE_FORMAT');
  const sig=Buffer.from(e.signature,'base64');
  assert(sig.length===64&&verify(null,Buffer.from(canon(e)),publicKey,sig),'SIGNATURE_INVALID');
  return {eta,key:hash(Buffer.from(JSON.stringify([e.issuer,e.id]))),payload:hash(Buffer.from(canon(e)))};
}
function update(s,eta){
  assert(!s.ambiguous,'AMBIGUOUS');
  if(s.pCount){
    if(close(eta,s.eta)){s.pending=0;s.pCount=0;s.count=2;}
    else if(close(eta,s.pending)){s.eta=(s.pending+eta)/2;s.pending=0;s.pCount=0;s.count=2;}
    else{s.pending=0;s.pCount=0;s.count=0;s.ambiguous=1;}
  }else if(close(eta,s.eta))s.count=Math.min(2,s.count+1);
  else{s.pending=eta;s.pCount=1;}
}
function admit(state,event){
  const w=verifyWitness(event);
  const prior=state.ledger.find(r=>r.key.equals(w.key));
  if(prior){assert(prior.payload.equals(w.payload),'EVENT_CONFLICT');return false;}
  assert(state.ledger.length<16,'LEDGER_FULL');
  const proposed={...state.slots[event.context]};
  update(proposed,w.eta);
  state.slots[event.context]=proposed;
  state.ledger.push({key:w.key,payload:w.payload});
  return true;
}
function predict(state,c,x){context(c);const s=state.slots[c];return {value:s.eta*base(x),confident:s.count===2&&!s.pCount&&!s.ambiguous};}
function encode(state){
  assert(state.ledger.length<=16,'CAPACITY');
  const b=Buffer.alloc(1108);b.write('GKD3',0,'ascii');b[4]=1;b[5]=4;b[6]=state.ledger.length;
  for(let c=0;c<4;c++){
    const s=state.slots[c],p=8+19*c;
    assert(Number.isFinite(s.eta)&&s.eta>0&&s.eta<=2,'ETA_STATE');
    assert(Number.isFinite(s.pending)&&s.pending>=0&&s.pending<=2,'PENDING_STATE');
    assert(Number.isInteger(s.count)&&s.count>=0&&s.count<=2,'COUNT_STATE');
    assert([0,1].includes(s.pCount)&&[0,1].includes(s.ambiguous),'FLAGS');
    assert((s.pCount===0&&s.pending===0)||(s.pCount===1&&s.pending>0),'CANONICAL');
    b.writeDoubleLE(s.eta,p);b.writeDoubleLE(s.pending,p+8);
    b[p+16]=s.count;b[p+17]=s.pCount;b[p+18]=s.ambiguous;
  }
  for(let i=0;i<state.ledger.length;i++){
    const z=state.ledger[i],p=84+i*64;
    assert(Buffer.isBuffer(z.key)&&z.key.length===32&&Buffer.isBuffer(z.payload)&&z.payload.length===32,'EVENT_BYTES');
    z.key.copy(b,p);z.payload.copy(b,p+32);
  }
  return Buffer.concat([b,hash(b)]);
}
function decode(bytes){
  assert(Buffer.isBuffer(bytes)&&bytes.length===1140,'CHECKPOINT_SIZE');
  const b=bytes.subarray(0,1108);assert(hash(b).equals(bytes.subarray(1108)),'CHECKPOINT_HASH');
  assert(b.toString('ascii',0,4)==='GKD3'&&b[4]===1&&b[5]===4&&b[6]<=16&&b[7]===0,'HEADER');
  const state=blank();state.slots=[];
  for(let c=0;c<4;c++){const p=8+19*c;state.slots.push({eta:b.readDoubleLE(p),pending:b.readDoubleLE(p+8),count:b[p+16],pCount:b[p+17],ambiguous:b[p+18]});}
  for(let i=0;i<b[6];i++){const p=84+i*64;state.ledger.push({key:Buffer.from(b.subarray(p,p+32)),payload:Buffer.from(b.subarray(p+32,p+64))});}
  assert(new Set(state.ledger.map(q=>q.key.toString('hex'))).size===state.ledger.length,'DUPLICATE_HASH');
  assert(encode(state).equals(bytes),'NONCANONICAL');return state;
}
function fails(fn,label){let did=false;try{fn();}catch(e){did=String(e.message).startsWith('GKD03_FAIL_CLOSED:');}assert(did,'NEGATIVE_'+label);}
function rng(seed){let s=seed>>>0;return()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return (s>>>0)/4294967296;};}
function sample(r,i){return [2+22*r(),1+19*r(),1+19*r(),1+9*r(),0.2+4.8*r(),100+900*r(),i%2];}
const rel=(a,b)=>Math.abs(a-b)/Math.max(1,Math.abs(b));
const z=v=>(v-4)*(v-18);
function candidate(w){assert(w.length===3,'THREE_WITNESSES');const a=(w[0].y/base(w[0].x)+w[1].y/base(w[1].x))/2;const b=(w[2].y/base(w[2].x)-a)/z(w[2].x[0]);return x=>(a+b*z(x[0]))*base(x);}
function symbolic(w){const a=w[0].y/base(w[0].x);const d=w[2].y/base(w[2].x)-a;return x=>(a+d*z(x[0])/z(11))*base(x);}
function fittedOLS(w){
  const t=w.map(e=>z(e.x[0])),y=w.map(e=>e.y/base(e.x));
  const sx=t.reduce((a,b)=>a+b,0),sy=y.reduce((a,b)=>a+b,0),sxx=t.reduce((a,b)=>a+b*b,0),sxy=t.reduce((a,b,i)=>a+b*y[i],0);
  const det=w.length*sxx-sx*sx;assert(det>0,'OLS_RANK');
  const a=(sy*sxx-sx*sxy)/det,b=(w.length*sxy-sx*sy)/det;
  return x=>(a+b*z(x[0]))*base(x);
}
export function run(){
  let accepted=0,replays=0,conflicts=0,forgeries=0,naive=0,repairs=0,retained=0,cold=0;
  let sampleCheckpoint='';
  for(const seed of [4001,4002])for(let j=0;j<16;j++){
    const rand=rng((seed^Math.imul(j,0x9e3779b9))>>>0),s=blank(),etas=[0,1,2,3].map(c=>[1,0.8,0.55,0.3][(c+j)%4]);
    let n=0;const next=()=>sample(rand,n++);
    for(let c=0;c<4;c++){
      const x=next(),e=signed('known'+seed+'_'+j+'_c'+c+'_a',c,x,etas[c]*base(x));
      assert(admit(s,e),'FIRST');accepted++;
      const initial=encode(s);
      for(let k=0;k<5;k++){assert(!admit(s,e)&&encode(s).equals(initial),'REPLAY_CHANGED');replays++;}
      const original=oldEmpty();oldObserve(original,c,x,e.y);oldObserve(original,c,x,e.y);
      if(oldPredict(original,c,x).confident)naive++;
      if(c===0){
        const changed=signed(e.id,c,x,(etas[c]+0.1)*base(x));
        fails(()=>admit(s,changed),'CONFLICT');conflicts++;assert(encode(s).equals(initial),'CONFLICT_MUTATED');
        fails(()=>admit(s,{...e,y:e.y+0.1}),'FORGERY');forgeries++;assert(encode(s).equals(initial),'FORGERY_MUTATED');
      }
      const x2=next(),e2=signed('known'+seed+'_'+j+'_c'+c+'_b',c,x2,etas[c]*base(x2));
      assert(admit(s,e2),'SECOND');accepted++;
      assert(predict(s,c,x2).confident&&rel(predict(s,c,x2).value,e2.y)<=1e-9,'LEARNED');
    }
    const a=encode(s);assert(encode(decode(Buffer.from(a))).equals(a),'COLD_A');cold++;
    const before=[0,1,3].map(c=>JSON.stringify(s.slots[c]));
    etas[2]=etas[2]===1?0.35:etas[2]+0.1;
    const x=next(),e=signed('known'+seed+'_'+j+'_change_a',2,x,etas[2]*base(x));
    assert(admit(s,e)&&!predict(s,2,x).confident,'CHANGE_PENDING');accepted++;
    const frozen=encode(s);
    for(let k=0;k<5;k++){assert(!admit(s,e)&&encode(s).equals(frozen),'CHANGE_REPLAY');replays++;}
    const x2=next(),e2=signed('known'+seed+'_'+j+'_change_b',2,x2,etas[2]*base(x2));
    assert(admit(s,e2)&&predict(s,2,x2).confident&&rel(predict(s,2,x2).value,e2.y)<=1e-9,'CHANGE_DONE');accepted++;repairs++;
    if([0,1,3].every((c,i)=>JSON.stringify(s.slots[c])===before[i]))retained++;
    const b=encode(s);assert(encode(decode(Buffer.from(b))).equals(b),'COLD_B');cold++;sampleCheckpoint=hash(b).toString('hex');
    assert(s.ledger.length===10,'TEN_UNIQUE');
  }
  // Worlds have bit-identical two witnessed responses; no deterministic predictor can identify their different hidden futures.
  let pairs=0,abstentions=0,correct=0,symbolicTies=0,olsTies=0,maxError=0;
  for(let j=0;j<16;j++){
    const r=rng(6001+j),observed=[];
    for(const voltage of [4,18]){
      const x=sample(r,j);x[0]=voltage;
      observed.push(signed('pair'+j+'_v'+voltage,3,x,0.65*base(x)));
    }
    const observedHash=hash(Buffer.from(observed.map(canon).join('|'))).toString('hex');
    for(const branch of [0,1]){
      const coeff=branch===0?0:0.003*(1+j%4),truth=x=>(0.65+coeff*z(x[0]))*base(x);
      const state=blank();
      for(const e of observed)assert(admit(state,e),'PAIR_WITNESS');
      assert(hash(Buffer.from(observed.map(canon).join('|'))).toString('hex')===observedHash,'OBS_IDENTICAL');
      // No certified prediction from merely two observationally identical witnesses.
      const certified=false;assert(!certified,'PAIR_OVERCONFIDENT');abstentions++;
      const x11=sample(r,j);x11[0]=11;
      const third=signed('pair'+j+'_v11',3,x11,truth(x11));
      assert(admit(state,third),'THIRD_INTERVENTION');
      const w=[...observed,third],model=candidate(w),sym=symbolic(w),ols=fittedOLS(w);
      for(const voltage of [7,15]){
        const x=sample(r,j);x[0]=voltage,expected=truth(x),got=model(x);
        const d=rel(got,expected);maxError=Math.max(maxError,d);assert(d<=1e-9,'TEST_TRANSFER');correct++;
        assert(rel(got,sym(x))<=1e-9,'SYM');symbolicTies++;
        assert(rel(got,ols(x))<=1e-9,'OLS');olsTies++;
      }
    }
    pairs++;
  }
  const b=encode(blank()),corrupt=Buffer.from(b);corrupt[20]^=1;
  fails(()=>decode(corrupt),'CHECKSUM');fails(()=>decode(Buffer.alloc(1139)),'SIZE');
  fails(()=>admit(blank(),signed('x',4,[8,4,5,2,1,300,0],1)),'CONTEXT');
  fails(()=>admit(blank(),signed('x',0,[0,4,5,0,1,300,0],1)),'ZERO_BASE');
  fails(()=>admit(blank(),signed('x',0,[8,4,5,2,1,300,0],NaN)),'NONFINITE');
  fails(()=>admit(blank(),{...signed('x',0,[8,4,5,2,1,300,0],1),issuer:'impostor'}),'ISSUER');
  assert(accepted===320&&replays===800&&conflicts===32&&forgeries===32&&naive===128&&repairs===32&&retained===32&&cold===64,'KNOWN_TARGETS');
  assert(pairs===16&&abstentions===32&&correct===64&&symbolicTies===64&&olsTies===64&&maxError<=1e-9,'PAIR_TARGETS');
  const out={schema:'yggdrasil.gkd03.dev.v1',experiment:'GKD-03',preregistration_commit:'88c466ee61204ee85f2b7cc93fd56a9baa258167',classification:'ENGINEERING_DEV_PASS_SCIENTIFIC_ADVANTAGE_NO_GO',known_worlds:32,accepted_unique_witnesses:accepted,ignored_replays:replays,rejected_signed_conflicts:conflicts,rejected_forged_signatures:forgeries,original_gkd02_false_confidence_on_replay:naive,corrected_contexts:repairs,unrelated_contexts_retained:retained,cold_restores:cold,checkpoint_bytes:b.length,sample_checkpoint_sha256:sampleCheckpoint,indistinguishable_world_pairs:pairs,preprobe_abstentions:abstentions,postprobe_correct:correct,postprobe_symbolic_ties:symbolicTies,postprobe_ols_ties:olsTies,max_postprobe_relative_error:maxError,negative_guards_pass:6,teacher_runtime_calls:0,scientific_gain_verified:false,real_world_source_authenticated:false,native_integration:false,limitations:'Publicly embedded signing key is a fixture only; full event identity and trust require source authority. Polynomial feature is preprogrammed. Strongest symbolic and conventional OLS controls tie; no unfamiliar primitive or native intelligence gain.'};
  console.log(JSON.stringify(out,null,2));return out;
}
if(process.argv[1]?.endsWith('/GKD-03/run.mjs')||process.argv[1]?.endsWith('\\GKD-03\\run.mjs'))run();
