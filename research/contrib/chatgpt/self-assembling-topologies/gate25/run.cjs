"use strict";
// Gate25 frozen before primary score: new 8-observable-sensor, 4-intervention, delayed-consequence world.
// Prereg commit: 5f9cc9abeea1b9b339452e3229cd56fc0139d3cc
const run = function gate25(){
"use strict";
const need=(v,m)=>{if(!v)throw Error("GATE25_INVARIANT_"+m);};
const mix=x=>{x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;return(x^(x>>>16))>>>0;};
const hash=(seed,a,b,c)=>(mix(seed^Math.imul(a+1,0x9e3779b1)^Math.imul(b+1,0x85ebca6b)^Math.imul(c+1,0xc2b2ae35)))>>>0;
const pop=m=>{let k=0;for(;m;m>>>=1)k+=m&1;return k;};
const ix=(feat,mask)=>{let z=0;for(let i=0;i<12;i++)if(mask&(1<<i))z=(z<<1)|((feat>>i)&1);return z;};
const masks=Array.from({length:4095},(_,i)=>i+1).filter(m=>pop(m)<=3);
const clamp=p=>Math.max(.05,Math.min(.95,p)),brier=(p,y)=>(p-y)**2;
function causalWorld(seed,f){
 const immediate=f==="immediate"||f==="stationary",delay=f==="delayed",noise=f==="pure_noise";
 const worlds=[];
 const choose=(stage,j)=>{
  const a=hash(seed,stage*7+j,19,0)%8;
  let b=hash(seed,stage*7+j,31,1)%7;if(b>=a)b++;
  const effect=8+(stage+j)%2+(delay?2:0);
  return{mask:(1<<a)|(1<<b)|(1<<effect),bias:hash(seed,stage,j,81)&1};
 };
 for(let stage=0;stage<2;stage++){
  worlds.push([choose(stage,0),choose(stage,1)]);
 }
 if(f==="stationary")worlds[1]=worlds[0];
 const truth=(feature,phase,t,domain)=>{
  if(noise)return (hash(seed,phase*17+t,domain,44)&3);
  let y=0,ws=phase===1?worlds[1]:worlds[0];
  for(let j=0;j<2;j++){
   const {mask,bias}=ws[j];let v=pop(feature&mask)%2 ^ bias;
   if(hash(seed,phase*257+t,j,domain)%31===0)v^=1;
   y|=v<<j;
  }
  return y;
 };
 return{truth,worlds};
}
function action(seed,t){return (t+(seed&3)+(t>>2))&3;}
function feature(state,a,prev){return state|(a<<8)|(prev<<10);}
function step(seed,w,phase,st,a,prev,t,domain){
 const feat=feature(st,a,prev),y=w.truth(feat,phase,t,domain);
 const other=(((st<<1)|(st>>>7)) ^ (st>>>3) ^ (a*43) ^ (prev*17) ^ ((t*13)&255))&252;
 return {feat,y,state:(other|y)&255};
}
function data(seed,f){
 const w=causalWorld(seed,f),out={A:[],B:[],R:[],BH:[],RH:[],actions:[]};
 let st=hash(seed,3,7,9)&255,prev=0;
 for(let t=0;t<160;t++){
  const a=action(seed,t),phase=t<64?0:t<112?1:2;
  const x=step(seed,w,phase,st,a,prev,t,1101);
  out.actions.push(a);
  (t<64?out.A:t<112?out.B:out.R).push([x.feat,x.y]);
  st=x.state;prev=a;
 }
 for(let phase=1;phase<=2;phase++){
  const train=phase===1?out.B:out.R,known=new Set(train.map(([x])=>x)),rows=[];
  for(let i=0;i<16;i++){
   let attempts=0,feat,y;
   do{
    const state=hash(seed,phase*19+i,attempts,14)&255,a=hash(seed,phase*17+i,attempts,22)&3,prev=hash(seed,phase*13+i,attempts,33)&3;
    feat=feature(state,a,prev);y=w.truth(feat,phase,1000+i,9017);
    attempts++;need(attempts<=128,"holdout_disjoint_exhausted");
   }while(known.has(feat)||rows.some(r=>r[0]===feat));
   rows.push([feat,y]);
  }
  if(phase===1)out.BH=rows;else out.RH=rows;
 }
 need(out.A.length===64&&out.B.length===48&&out.R.length===48&&out.BH.length===16&&out.RH.length===16,"data_dimensions");
 return out;
}
function stats(rows,mask,j){
 const n=new Uint16Array(1<<pop(mask)),yes=new Uint16Array(n.length);
 for(const [feat,out]of rows){const z=ix(feat,mask);n[z]++;yes[z]+=(out>>j)&1;}
 return{n,yes};
}
function predict(rows,mask,feat,j){
 if(!rows.length)return .5;
 const v=stats(rows,mask,j),z=ix(feat,mask);
 return clamp((v.yes[z]+1)/(v.n[z]+2));
}
function loo(rows,mask,j){
 const v=stats(rows,mask,j);let e=0;
 for(const [feat,out]of rows){const y=(out>>j)&1,k=ix(feat,mask),p=clamp((v.yes[k]-y+1)/(v.n[k]+1));e+=brier(p,y);}
 return e/rows.length+.003*(1<<pop(mask));
}
function sourceFit(rows){
 const wins=[],work=[];
 for(let j=0;j<2;j++){let mask=1,min=Infinity,n=0;
  for(const candidate of masks){const v=loo(rows,candidate,j);n++;if(v<min-1e-12){min=v;mask=candidate;}}
  wins.push(mask);work.push(n);
 }
 const risk=wins.reduce((s,m,j)=>s+(loo(rows,m,j)-.003*(1<<pop(m))),0)/2;
 return{wins,work:work.reduce((a,b)=>a+b,0),reliable:risk<=.20,risk};
}
// Independently implemented exhaustive static refit (does not call local risk/neighbor search).
function staticFit(rows){
 let chosen=[],operationCount=0;
 for(let j=0;j<2;j++){
  let win=1,score=Infinity;
  for(let mask=1;mask<4096;mask++){
   let k=0;for(let b=0;b<12;b++)if(mask&(1<<b))k++;
   if(k>3)continue;
   let counts=Array.from({length:1<<k},()=>({n:0,yes:0})),bins=[];
   for(const [feat,y]of rows){let idx2=0;for(let bit=0;bit<12;bit++)if(mask&(1<<bit))idx2=(idx2<<1)|((feat>>bit)&1);
    bins.push(idx2);counts[idx2].n++;counts[idx2].yes+=(y>>j)&1;}
   let lossSum=0;
   for(let i=0;i<rows.length;i++){
    const count=counts[bins[i]],y=(rows[i][1]>>j)&1,p=Math.max(.05,Math.min(.95,(count.yes-y+1)/(count.n+1)));
    lossSum+=(p-y)*(p-y);
   }
   const candidateScore=lossSum/rows.length+.003*(1<<k);operationCount++;
   if(candidateScore<score-1e-12){score=candidateScore;win=mask;}
  }
  chosen.push(win);
 }
 return{masks:chosen,work:operationCount};
}
function neighbors(mask){
 let res=new Set(),k=pop(mask);
 for(let i=0;i<12;i++){
  if(mask&(1<<i)){
   if(k>1)res.add(mask^(1<<i));
   for(let j=0;j<12;j++)if(!(mask&(1<<j)))res.add((mask^(1<<i))|(1<<j));
  }else if(k<3)res.add(mask|(1<<i));
 }
 return [...res].sort((a,b)=>a-b);
}
function makeLearner(A){
 const source=sourceFit(A);
 return{A:A.map(r=>r.slice()),stream:[],source:source.wins,graph:source.wins.slice(),reliable:source.reliable,edits:0,work:source.work,log:[]};
}
function localForecast(t,feat){
 if(!t.reliable)return[.5,.5];
 const pa=t.source.map((m,j)=>predict(t.A,m,feat,j));
 if(t.stream.length<8)return pa;
 const pb=t.graph.map((m,j)=>predict(t.stream.slice(-32),m,feat,j));
 const total=t.log.reduce((s,v)=>s+v,0)/32,w=1/(1+Math.exp(-total));
 return pa.map((p,j)=>clamp((1-w)*p+w*pb[j]));
}
function localObserve(t,row){
 const[feat,y]=row;
 const pa=t.source.map((m,j)=>predict(t.A,m,feat,j));
 const prior=t.stream.slice(-32),pb=t.stream.length>=8?t.graph.map((m,j)=>predict(prior,m,feat,j)):pa;
 let evidence=0;for(let j=0;j<2;j++){const obs=(y>>j)&1;const a=obs?pa[j]:1-pa[j],b=obs?pb[j]:1-pb[j];evidence+=Math.log(b/a);}
 t.log.push(Math.max(-127,Math.min(127,Math.round(evidence*32))));if(t.log.length>16)t.log.shift();
 t.stream.push(row.slice());
 if(!t.reliable||t.stream.length%8!==0)return;
 const recent=t.stream.slice(-32);
 for(let j=0;j<2;j++){
  let old=loo(recent,t.graph[j],j),best=old,mask=t.graph[j];t.work++;
  for(const candidate of neighbors(t.graph[j])){const value=loo(recent,candidate,j);t.work++;if(value<best-1e-12){best=value;mask=candidate;}}
  if(mask!==t.graph[j]&&old-best>=.006){t.graph[j]=mask;t.edits++;}
 }
}
function pack(t){
 need(t.A.length===64&&t.stream.length<=96&&t.log.length<=16&&t.edits<256&&t.work<65536,"pack_bounds");
 const b=new Uint8Array(512);
 const rec=(r,k)=>{const[x,y]=r;need(x>=0&&x<4096&&y>=0&&y<4,"record");b[k]=x&255;b[k+1]=x>>>8;b[k+2]=y;};
 t.A.forEach((r,i)=>rec(r,i*3));t.stream.forEach((r,i)=>rec(r,192+i*3));
 const m=[...t.source,...t.graph];m.forEach((mask,i)=>{need(mask>=1&&mask<4096,"mask");b[480+i*2]=mask&255;b[481+i*2]=mask>>>8;});
 b[488]=t.stream.length;b[489]=t.reliable?1:0;b[490]=t.edits;b[491]=t.work&255;b[492]=t.work>>>8;b[493]=t.log.length;
 t.log.forEach((v,i)=>{b[494+i]=v&255;});return b;
}
function restore(b){
 need(b instanceof Uint8Array&&b.length===512&&b.slice(510).every(v=>!v),"packed_shape");
 const row=k=>{const x=b[k]|(b[k+1]<<8),y=b[k+2];need(x<4096&&y<4,"decoded_record");return[x,y];};
 let A=[],stream=[];need(b[488]<=96&&b[493]<=16,"counts");
 for(let i=0;i<64;i++)A.push(row(i*3));
 for(let i=0;i<96;i++){
  if(i<b[488])stream.push(row(192+i*3));
  else need(!b[192+i*3]&&!b[193+i*3]&&!b[194+i*3],"padding");
 }
 let graph=[];for(let i=0;i<4;i++){const mask=b[480+2*i]|(b[481+2*i]<<8);need(mask>0&&mask<4096&&pop(mask)<=3,"decoded_mask");graph.push(mask);}
 const log=[];for(let i=0;i<16;i++){let x=b[494+i];if(x>127)x-=256;if(i<b[493])log.push(x);else need(x===0,"log_padding");}
 return{A,stream,source:graph.slice(0,2),graph:graph.slice(2),reliable:!!b[489],edits:b[490],work:b[491]+(b[492]<<8),log};
}
function makeControl(A,source){
 return{A:A.map(r=>r.slice()),stream:[],source:source.slice(),recent:source.slice(),growing:source.slice(),weights:[.05,.05],work:0,online:0};
}
function controlPredict(c,feat){
 const pa=c.source.map((m,j)=>predict(c.A,m,feat,j));
 const rr=c.stream.slice(-32);
 const pr=c.stream.length>=8?c.recent.map((m,j)=>predict(rr,m,feat,j)):pa;
 const pg=c.growing.map((m,j)=>predict(c.A.concat(c.stream),m,feat,j));
 const ph=pa.map((v,j)=>clamp((1-c.weights[j])*v+c.weights[j]*pr[j]));
 return{source:pa,rolling:pr,growing:pg,hazard:ph,null:[.5,.5]};
}
function controlObserve(c,row){
 const[feat,out]=row,all=controlPredict(c,feat);
 for(let j=0;j<2;j++){
  const y=(out>>j)&1,src=y?all.source[j]:1-all.source[j],tar=y?all.rolling[j]:1-all.rolling[j];
  const prior=(1/64)+(1-2/64)*c.weights[j],denom=prior*tar+(1-prior)*src;
  c.weights[j]=denom>0?prior*tar/denom:.5;c.online++;
 }
 c.stream.push(row.slice());
 if(c.stream.length%8===0){
  const recent=staticFit(c.stream.slice(-32)),growing=staticFit(c.A.concat(c.stream));
  c.recent=recent.masks;c.growing=growing.masks;c.work+=recent.work+growing.work;
 }
}
const norm=(x)=>Number(x.toFixed(10));
function paired(values){
 const n=values.length,mean=values.reduce((s,x)=>s+x,0)/n,s2=values.reduce((s,x)=>s+(x-mean)*(x-mean),0)/(n-1),ci=1.96*Math.sqrt(s2/n);
 return{mean:norm(mean),ci95:[norm(mean-ci),norm(mean+ci)]};
}
function trial(seed,f){
 const d=data(seed,f),local=makeLearner(d.A),ctrl=makeControl(d.A,local.source);
 const fixedA=JSON.stringify(local.A),sourceMasks=JSON.stringify(local.source);
 const names=["local","source","rolling","growing","hazard","null","no_retention"];
 const pre={B:{},R:{}},held={B:{},R:{}};for(const stage of ["B","R"])for(const name of names){pre[stage][name]=0;held[stage][name]=0;}
 const equal=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
 let cold=true,rep48=null,rep72=null,heldExcluded=true;
 for(let i=0;i<96;i++){
  const row=i<48?d.B[i]:d.R[i-48],stage=i<48?"B":"R",[feat,y]=row;
  const c=controlPredict(ctrl,feat),lp=localForecast(local,feat),
   no=local.stream.length>=8?local.graph.map((m,j)=>predict(local.stream.slice(-32),m,feat,j)):[.5,.5];
  const forecast={local:lp,...c,no_retention:no};
  for(const name of names)for(let j=0;j<2;j++)pre[stage][name]+=brier(forecast[name][j],(y>>j)&1)/96;
  localObserve(local,row);controlObserve(ctrl,row);
  if(rep48&&i>=48){localObserve(rep48,row);cold=cold&&equal(Array.from(pack(rep48)),Array.from(pack(local)));}
  if(rep72&&i>=72){localObserve(rep72,row);cold=cold&&equal(Array.from(pack(rep72)),Array.from(pack(local)));}
  if(i===47){rep48=restore(new Uint8Array(pack(local)));cold=cold&&equal(Array.from(pack(local)),Array.from(pack(rep48)));}
  if(i===71){rep72=restore(new Uint8Array(pack(local)));cold=cold&&equal(Array.from(pack(local)),Array.from(pack(rep72)));}
  if(i===47||i===95){
   const probes=stage==="B"?d.BH:d.RH,train=stage==="B"?d.B:d.R,ids=new Set(train.map(r=>r[0]));
   if(probes.some(r=>ids.has(r[0])))heldExcluded=false;
   for(const [probe,truth]of probes){
    const c2=controlPredict(ctrl,probe),localp=localForecast(local,probe);
    const no2=local.stream.length>=8?local.graph.map((m,j)=>predict(local.stream.slice(-32),m,probe,j)):[.5,.5];
    const all={local:localp,...c2,no_retention:no2};
    for(const name of names)for(let j=0;j<2;j++)held[stage][name]+=brier(all[name][j],(truth>>j)&1)/32;
    if(i===95){if(localp.some((v,j)=>v!==localForecast(rep48,probe)[j]||v!==localForecast(rep72,probe)[j]))cold=false;}
   }
  }
 }
 const rec=restore(new Uint8Array(pack(local)));
 cold=cold&&equal(Array.from(pack(local)),Array.from(pack(rec)));
 for(let feature=0;feature<4096;feature+=97){if(localForecast(local,feature).some((v,j)=>v!==localForecast(rec,feature)[j]))cold=false;}
 const unchanged=fixedA===JSON.stringify(local.A)&&sourceMasks===JSON.stringify(local.source);
 const policy=d.actions.every((a,t)=>a===action(seed,t));
 return{pre,held,edits:local.edits,cold,unchanged,heldExcluded,policy,work:{local:local.work,global:ctrl.work,hazard:ctrl.online},reliable:local.reliable};
}
const plans=[["immediate",201000],["delayed",202000],["stationary",203000],["pure_noise",204000]],groups={},related=[];
for(const [family,first]of plans){
 const rows=Array.from({length:24},(_,i)=>trial(first+i,family));
 if(first<203000)related.push(...rows);
 const names=Object.keys(rows[0].pre.B),avg=fn=>norm(rows.reduce((s,x)=>s+fn(x),0)/24);
 const means=(where,phase)=>Object.fromEntries(names.map(k=>[k,avg(x=>x[where][phase][k])]));
 groups[family]={trials:24,seed_first:first,seed_last:first+23,
 prequential_B:means("pre","B"),prequential_R:means("pre","R"),held_B:means("held","B"),held_R:means("held","R"),
 edited_trials:rows.filter(x=>x.edits>0).length,reliable_source_trials:rows.filter(x=>x.reliable).length,
 cold_exact:rows.filter(x=>x.cold).length,source_immutable:rows.filter(x=>x.unchanged).length,
 held_excluded:rows.filter(x=>x.heldExcluded).length,world_independent_action_policy:rows.filter(x=>x.policy).length,
 avg_work:{local:avg(x=>x.work.local),global:avg(x=>x.work.global),hazard:avg(x=>x.work.hazard)}};
}
const delta=(a,b,phase,metric="pre")=>paired(related.map(x=>x[metric][phase][a]-x[metric][phase][b]));
const Bglob=delta("rolling","local","B"),Bhaz=delta("hazard","local","B"),
 Rglob=delta("rolling","local","R","held"),Rhaz=delta("hazard","local","R","held"),
 Rsrc=delta("source","local","R","held"),Bnr=delta("no_retention","local","B");
const g=groups,noise=g.pure_noise,stationary=g.stationary;
const conditions={
 B_prequential_gain_vs_recent_global_min:Bglob.mean>=.01,
 B_prequential_gain_vs_recent_global_ci_lower_positive:Bglob.ci95[0]>0,
 B_prequential_gain_vs_hazard_min:Bhaz.mean>=.005,
 B_prequential_gain_vs_hazard_ci_lower_positive:Bhaz.ci95[0]>0,
 R_held_gain_vs_recent_global_min:Rglob.mean>=.01,
 R_held_gain_vs_recent_global_ci_lower_positive:Rglob.ci95[0]>0,
 R_held_gain_vs_hazard_min:Rhaz.mean>=.005,
 R_held_gain_vs_hazard_ci_lower_positive:Rhaz.ci95[0]>0,
 R_held_gain_vs_source_only_min:Rsrc.mean>=.005,
 stationary_unnecessary_edit_trial_fraction_max:stationary.edited_trials/24<=.20,
 noise_unnecessary_edit_trial_fraction_max:noise.edited_trials/24<=.20,
 noise_held_Brier_regression_vs_null_max:Math.max(noise.held_B.local-noise.held_B.null,noise.held_R.local-noise.held_R.null)<=.025,
 B_prequential_gain_vs_no_retention_ablation_min:Bnr.mean>=.005,
 all_source_immutable:Object.values(g).every(v=>v.source_immutable===24),
 all_phase_held_outcomes_excluded:Object.values(g).every(v=>v.held_excluded===24),
 all_exact_512byte_cold_replays:Object.values(g).every(v=>v.cold_exact===24),
 all_action_policy_world_independent:Object.values(g).every(v=>v.world_independent_action_policy===24),
 all_comparator_work_counts_finite:Object.values(g).every(v=>Object.values(v.avg_work).every(x=>x>=0&&Number.isFinite(x)))
};
return{schema:"yggdrasil.gate25.temporal-intervention-transfer.v1",parent_commit:"2a42430cecc25d4fea84034cf9a31d0bc1dc0715",prereg_commit:"5f9cc9abeea1b9b339452e3229cd56fc0139d3cc",
 worlds:{cohorts:4,trials:96,related:48,observable_bits:8,interventions:4,target_bits:2,prev_action_history:true,source_transitions:64,B_feedback:48,R_feedback:48,held_per_phase:16,state_budget_bytes:512},
 groups,summary:{B_gain_vs_recent_global:Bglob,B_gain_vs_hazard:Bhaz,R_held_gain_vs_recent_global:Rglob,R_held_gain_vs_hazard:Rhaz,R_held_gain_vs_source_only:Rsrc,B_gain_vs_no_retention:Bnr,
 stationary_edited_trials:stationary.edited_trials,noise_edited_trials:noise.edited_trials},
 conditions,verdict:Object.values(conditions).every(Boolean)?"PROVISIONAL_SYNTHETIC_TRANSFER_SIGNAL":"SCIENTIFIC_NO_GO_TEMPORAL_INTERVENTION",
 limitations:{native_first_use:false,process_exit_cold_retention:false,independent_replication:false,compute_matched:false,unseen_real_world:false,canonical_learner:false,deployment:false}};
};
if(typeof module!=="undefined"&&require.main===module){
 const fs=require("fs"),got=run();
 if(process.argv.includes("--verify")){const p=process.argv.indexOf("--verify"),expected=JSON.parse(fs.readFileSync(process.argv[p+1],"utf8"));if(JSON.stringify(got)!==JSON.stringify(expected))throw Error("GATE25_EXACT_REPLAY_MISMATCH");console.log("GATE25_EXACT_REPLAY_PASS "+got.verdict);}
 else console.log(JSON.stringify(got,null,2));
}
