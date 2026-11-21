"use strict";
// Gate20 frozen developmental source; independently implemented static control.
// Preregistration: c1ff29dbbdbd54444fe339982356a4913a7d0789.
const run = function gate20(){
"use strict";
const check=(ok,msg)=>{if(!ok)throw Error("GATE20_INVARIANT "+msg);};
const pop=m=>{let n=0;for(;m;m>>>=1)n+=m&1;return n;};
const bits=m=>{const out=[];for(let i=0;i<6;i++)if(m&(1<<i))out.push(i);return out;};
const ix=(x,m)=>bits(m).reduce((n,k)=>(n<<1)|((x>>>k)&1),0);
const subsets=Array.from({length:63},(_,i)=>i+1).filter(m=>pop(m)<=3);
const mix=u=>{u=(u^(u>>>16))>>>0;u=Math.imul(u,0x7feb352d)>>>0;u=(u^(u>>>15))>>>0;u=Math.imul(u,0x846ca68b)>>>0;return (u^(u>>>16))>>>0;};
const hash=(seed,ctx,x,domain)=>mix(mix(seed^Math.imul(ctx+1,0x9e3779b1)^Math.imul(domain+1,0x85ebca6b))^Math.imul(x+1,0xc2b2ae35));
const rng=seed=>{let x=seed||0x6d2b79f5;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};};
const shuffle=(a,random)=>{let v=a.slice();for(let i=v.length-1;i>0;i--){let j=random()%(i+1);[v[i],v[j]]=[v[j],v[i]];}return v;};
const clip=p=>Math.max(.05,Math.min(.95,p));
const sq=(p,y)=>(p-y)*(p-y);
const xors=(t,k)=>{for(let i=0;i<k;i++){let affects=false;for(let b=0;b<(1<<k);b++){if(((t>>b)&1)!==((t>>(b^(1<<i)))&1)){affects=true;break;}}if(!affects)return false;}return true;};
function tableFor(family,r){
 if(family==="xor_pair")return 0b0110;
 if(family==="unary")return 0b10;
 if(family==="mux3"){let t=0;for(let v=0;v<8;v++){const y=(v&4)?(v&1):((v>>>1)&1);t|=y<<v;}return t;}
 if(family==="essential3"){let t;do{t=r()&255;}while(!xors(t,3));return t;}
 return 0;
}
function worlds(seed,family){
 const rrA=rng(mix(seed^0x518a4ccd)),rrB=rng(mix(seed^0x7e2139bf)),k=family==="xor_pair"?2:family==="unary"?1:family==="independent_noise"?0:3;
 const orderA=shuffle([0,1,2,3,4,5],rrA).slice(0,k);
 let orderB=[],tries=0;
 if(k){do{orderB=shuffle([0,1,2,3,4,5],rrB).slice(0,k);tries++;check(tries<500,"distinct causal parents");}
 while(orderB.slice().sort().join(",")===orderA.slice().sort().join(","));}
 const table=tableFor(family,rrA);
 return [{order:orderA,table,family},{order:orderB,table,family}];
}
function response(w,seed,context,x,domain){
 if(w.family==="independent_noise")return hash(seed,context,x,domain)&1;
 let bin=0;for(const b of w.order)bin=(bin<<1)|((x>>>b)&1);
 const y=(w.table>>>bin)&1;
 return y^(hash(seed,context,x,domain)%20===0?1:0);
}
function data(seed,family){
 const [A,B]=worlds(seed,family);
 const randomA=rng(mix(seed^0x129fc82d)),randomB=rng(mix(seed^0x98a7b314));
 const xA=shuffle(Array.from({length:64},(_,i)=>i),randomA);
 const xB=shuffle(Array.from({length:64},(_,i)=>i),randomB);
 const fitA=xA.map(x=>[x,response(A,seed,0,x,2001)]),
       fitB=xB.slice(0,32).map(x=>[x,response(B,seed,1,x,2002)]);
 const held=xB.slice(32,48),unused=xB.slice(48);
 check(new Set(xB).size===64&&fitA.length===64&&fitB.length===32&&held.length===16&&unused.length===16,"data splits");
 return {A,B,fitA,fitB,held};
}
function stats(rows,m){
 const N=1<<pop(m),n=new Uint16Array(N),y=new Uint16Array(N);
 for(const [x,v]of rows){const b=ix(x,m);n[b]++;y[b]+=v;}return{n,y};
}
function prediction(rows,m,x){
 const s=stats(rows,m),b=ix(x,m);return clip((s.y[b]+1)/(s.n[b]+2));
}
function dynamicRisk(rows,m){
 const s=stats(rows,m);let v=0;
 for(const [x,y]of rows){const b=ix(x,m);v+=sq(clip((s.y[b]-y+1)/(s.n[b]+1)),y);}
 return v/rows.length+.003*(1<<pop(m));
}
function selectSource(rows){
 let winner=1,risk=Infinity,work=0;
 for(const m of subsets){const v=dynamicRisk(rows,m);work++;if(v<risk-1e-12){risk=v;winner=m;}}
 return{mask:winner,work};
}
function candidates(m){
 const k=pop(m),nbr=new Set();
 for(let i=0;i<6;i++)if(m&(1<<i)){if(k>1)nbr.add(m^(1<<i));for(let j=0;j<6;j++)if(!(m&(1<<j)))nbr.add((m^(1<<i))|(1<<j));}
 else if(k<3)nbr.add(m|(1<<i));
 return [...nbr].filter(v=>pop(v)>=1&&pop(v)<=3).sort((a,b)=>a-b);
}
function begin(A,source){return {A:A.map(r=>r.slice()),B:[],mask:source.mask,origin:source.mask,spawn:0,prune:0,swap:0,work:source.work};}
function update(s,record){
 check(s.B.length<32,"B records overflow");
 s.B.push(record.slice());
 if(s.B.length<8||s.B.length%4!==0)return;
 const now=dynamicRisk(s.B,s.mask);s.work++;
 let winner=s.mask,winnerRisk=now;
 for(const m of candidates(s.mask)){const cost=dynamicRisk(s.B,m);s.work++;if(cost<winnerRisk-1e-12){winner=m;winnerRisk=cost;}}
 if(winner!==s.mask&&now-winnerRisk>=.008){
  const before=pop(s.mask),after=pop(winner);
  if(after>before)s.spawn++;else if(after<before)s.prune++;else s.swap++;
  s.mask=winner;
 }
}
function serialize(s){
 check(s.A.length===64&&s.B.length<=32&&s.mask>=1&&s.mask<64&&s.origin>=1&&s.origin<64&&pop(s.mask)<=3,"packed model shape");
 const b=new Uint8Array(260);
 for(let i=0;i<64;i++){const [x,y]=s.A[i];check(x<64&&y<=1,"source bytes");b[2*i]=x;b[2*i+1]=y;}
 for(let i=0;i<s.B.length;i++){const [x,y]=s.B[i];check(x<64&&y<=1,"target bytes");b[128+2*i]=x;b[129+2*i]=y;}
 b[192]=s.mask;b[193]=s.B.length;b[194]=s.origin;b[195]=s.spawn;b[196]=s.prune;b[197]=s.swap;
 check(s.work<65536,"work counter overflow");b[198]=s.work&255;b[199]=s.work>>>8;
 return b;
}
function restore(raw){
 check(raw instanceof Uint8Array&&raw.length===260,"restore format");
 const A=[],B=[];
 for(let i=0;i<64;i++){check(raw[2*i]<64&&raw[2*i+1]<2,"restore A bytes");A.push([raw[2*i],raw[2*i+1]]);}
 const n=raw[193];check(n<=32&&raw.slice(200).every(x=>x===0),"restore zero padding");
 for(let i=0;i<32;i++){const x=raw[128+2*i],y=raw[129+2*i];if(i<n){check(x<64&&y<2,"restore B bytes");B.push([x,y]);}else check(x===0&&y===0,"restore B padding");}
 const s={A,B,mask:raw[192],origin:raw[194],spawn:raw[195],prune:raw[196],swap:raw[197],work:raw[198]+256*raw[199]};
 check(pop(s.mask)>=1&&pop(s.mask)<=3&&pop(s.origin)>=1&&pop(s.origin)<=3,"restore graph order");
 return s;
}
// An independent static selector. It never invokes the adaptive risk,
// source-graph constructor, neighbor generator, or graph-update path.
function independentFullyFitFixed(rows){
 let best=1,bestRisk=Infinity,comparisons=0;
 for(let m=1;m<64;m++){
  let size=0;for(let b=0;b<6;b++)size+=(m>>>b)&1;
  if(size>3)continue;
  let totals=Array.from({length:1<<size},()=>({n:0,yes:0})),ids=[];
  for(const [x,y]of rows){let bin=0;for(let bit=0;bit<6;bit++)if(m&(1<<bit))bin=(bin<<1)|((x>>>bit)&1);ids.push(bin);totals[bin].n++;totals[bin].yes+=y;}
  let sum=0;
  for(let j=0;j<rows.length;j++){const t=totals[ids[j]],target=rows[j][1],p=Math.max(.05,Math.min(.95,(t.yes-target+1)/(t.n+1)));sum+=(p-target)*(p-target);}
  const risk=sum/rows.length+.003*(1<<size);comparisons++;
  if(risk<bestRisk-1e-12){bestRisk=risk;best=m;}
 }
 return{mask:best,work:comparisons};
}
const fac=[0];for(let i=1;i<=65;i++)fac.push(fac[i-1]+Math.log(i));
function strongBayes(rows){
 const logw=[],st=[];
 for(const m of subsets){
  const z=stats(rows,m);let v=-Math.log(3*subsets.filter(q=>pop(q)===pop(m)).length);
  for(let j=0;j<z.n.length;j++)v+=fac[z.y[j]]+fac[z.n[j]-z.y[j]]-fac[z.n[j]+1];
  st.push({m,z});logw.push(v);
 }
 const top=Math.max(...logw),weights=logw.map(v=>Math.exp(v-top)),denom=weights.reduce((a,b)=>a+b,0);
 return x=>weights.reduce((sum,w,j)=>{const {m,z}=st[j],b=ix(x,m);return sum+w*clip((z.y[b]+1)/(z.n[b]+2));},0)/denom;
}
function paired(a){
 const n=a.length,mean=a.reduce((x,y)=>x+y,0)/n,variance=a.reduce((x,y)=>x+(y-mean)*(y-mean),0)/(n-1);
 const half=1.96*Math.sqrt(variance/n),r=x=>Number(x.toFixed(10));
 return {mean:r(mean),ci95:[r(mean-half),r(mean+half)]};
}
function trial(seed,family){
 const d=data(seed,family),source=selectSource(d.fitA);
 const learner=begin(d.fitA,source);
 for(let i=0;i<16;i++)update(learner,d.fitB[i]);
 const earlyBytes=serialize(learner),coldMid=restore(new Uint8Array(earlyBytes));
 let midExact=Array.from(serialize(coldMid)).every((x,i)=>x===earlyBytes[i]);
 for(let i=16;i<32;i++){update(learner,d.fitB[i]);update(coldMid,d.fitB[i]);}
 const finishBytes=serialize(learner),coldEnd=restore(new Uint8Array(finishBytes));
 const afterMidBytes=serialize(coldMid),afterEndBytes=serialize(coldEnd);
 const same=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
 let coldExact=midExact&&same(Array.from(finishBytes),Array.from(afterMidBytes))&&same(Array.from(finishBytes),Array.from(afterEndBytes));
 const B=learner.B,full=independentFullyFitFixed(B),bayes=strongBayes(B);
 const negativeR=rng(mix(seed^0x71b08d9f)),shuff=shuffle(B.map(r=>r[1]),negativeR),negRows=B.map(([x],i)=>[x,shuff[i]]);
 const neg=independentFullyFitFixed(negRows);
 const score={dynamic:0,fully_fit_fixed:0,frozen_A:0,bayesian:0,shuffled_B:0,null:0};
 const seen=new Set(B.map(([x])=>x)),disjoint=d.held.every(x=>!seen.has(x));
 let retained=JSON.stringify(d.fitA)===JSON.stringify(coldEnd.A);
 for(let x=0;x<64;x++)if(prediction(d.fitA,source.mask,x)!==prediction(coldEnd.A,coldEnd.origin,x))retained=false;
 for(const x of d.held){
  const y=response(d.B,seed,1,x,9877);
  const forecast={dynamic:prediction(B,learner.mask,x),fully_fit_fixed:prediction(B,full.mask,x),
    frozen_A:prediction(B,source.mask,x),bayesian:bayes(x),shuffled_B:prediction(negRows,neg.mask,x),null:.5};
  for(const k of Object.keys(score))score[k]+=sq(forecast[k],y)/16;
  if(forecast.dynamic!==prediction(coldMid.B,coldMid.mask,x)||forecast.dynamic!==prediction(coldEnd.B,coldEnd.mask,x))coldExact=false;
 }
 check(serialize(learner).length===260&&serialize(coldMid).length===260,"byte budget");
 return{score,coldExact,disjoint,retained,mutated:learner.spawn+learner.prune+learner.swap>0,
 changed:learner.origin!==learner.mask,spawn:learner.spawn,prune:learner.prune,swap:learner.swap,
 sourceMask:learner.origin,finalMask:learner.mask,fixedMask:full.mask,work_local:learner.work-source.work,work_static:full.work,work_bayes:subsets.length,
 final_parents_match:learner.mask===d.B.order.reduce((m,b)=>m|(1<<b),0)};
}
const designs=[["xor_pair",91000],["mux3",92000],["essential3",93000],["unary",94000],["independent_noise",95000]];
const all={},joined=[];
for(const [name,first]of designs){
 const rows=Array.from({length:32},(_,i)=>trial(first+i,name));
 if(name!=="independent_noise")joined.push(...rows);
 const keys=["dynamic","fully_fit_fixed","frozen_A","bayesian","shuffled_B","null"],r=v=>Number(v.toFixed(10));
 const means=Object.fromEntries(keys.map(k=>[k,r(rows.reduce((s,t)=>s+t.score[k],0)/32)]));
 all[name]={seed_first:first,seed_last:first+31,seeds:32,means,
  graph_mutated:rows.filter(z=>z.mutated).length,final_graph_changed:rows.filter(z=>z.changed).length,
  spawn:rows.reduce((s,z)=>s+z.spawn,0),prune:rows.reduce((s,z)=>s+z.prune,0),swap:rows.reduce((s,z)=>s+z.swap,0),
  final_true_parent_sets:rows.filter(z=>z.final_parents_match).length,
  cold_continuations_exact:rows.filter(z=>z.coldExact).length,held_disjoint:rows.filter(z=>z.disjoint).length,source_A_retained:rows.filter(z=>z.retained).length,
  total_local_evaluations:rows.reduce((s,z)=>s+z.work_local,0),
  total_fixed_evaluations:rows.reduce((s,z)=>s+z.work_static,0),
  total_bayes_evidences:rows.reduce((s,z)=>s+z.work_bayes,0),
  gain_vs_frozen_A:paired(rows.map(z=>z.score.frozen_A-z.score.dynamic)),
  gain_vs_fully_fit_fixed:paired(rows.map(z=>z.score.fully_fit_fixed-z.score.dynamic)),
  deficit_to_bayes:paired(rows.map(z=>z.score.dynamic-z.score.bayesian))};
}
const related=["xor_pair","mux3","essential3","unary"],noise=all.independent_noise;
const poolFrozen=paired(joined.map(z=>z.score.frozen_A-z.score.dynamic));
const poolFixed=paired(joined.map(z=>z.score.fully_fit_fixed-z.score.dynamic));
const relatedMutation=joined.filter(z=>z.mutated).length/joined.length,
 relatedChanged=joined.filter(z=>z.changed).length/joined.length;
const worstBayes=Math.max(...related.map(k=>all[k].means.dynamic-all[k].means.bayesian));
const allGroups=Object.values(all);
const conditions={
 related_trials_with_mutation_fraction_min:relatedMutation>=.8,
 related_trials_final_graph_changed_fraction_min:relatedChanged>=.5,
 related_macro_gain_vs_frozen_A_min:poolFrozen.mean>=.02,
 related_macro_gain_vs_frozen_A_ci_lower_positive:poolFrozen.ci95[0]>0,
 related_macro_gain_vs_fully_fit_static_min:poolFixed.mean>=.01,
 related_macro_gain_vs_fully_fit_static_ci_lower_positive:poolFixed.ci95[0]>0,
 worst_related_dynamic_deficit_to_bayes_max:worstBayes<=.01,
 independent_noise_regression_vs_fully_fit_static_max:noise.means.dynamic-noise.means.fully_fit_fixed<=.02,
 all_held_disjoint:allGroups.every(x=>x.held_disjoint===32),
 all_cold_continuations_exact:allGroups.every(x=>x.cold_continuations_exact===32),
 all_source_predictions_unchanged:allGroups.every(x=>x.source_A_retained===32),
 all_byte_budget_checks:true
};
const success=Object.values(conditions).every(Boolean);
return{schema:"yggdrasil.gate20.online-topology-rewiring.v1",
 prereg_commit:"c1ff29dbbdbd54444fe339982356a4913a7d0789",
 predecessor_commit:"98b99c959509db614d751962e68f75c454d0ce66",
 protocol:{seed_count:160,fit_A:64,fit_B:32,held_B:16,unused_B:16,bytes:260,graph_max_edges:3},
 groups:all,summary:{related_mutation_fraction:Number(relatedMutation.toFixed(10)),
 related_changed_fraction:Number(relatedChanged.toFixed(10)),related_gain_vs_frozen_A:poolFrozen,
 related_gain_vs_fully_fit_fixed:poolFixed,worst_related_bayes_deficit:Number(worstBayes.toFixed(10)),
 noise_dynamic_minus_fixed:Number((noise.means.dynamic-noise.means.fully_fit_fixed).toFixed(10))},
 conditions,all_scientific_thresholds_pass:success,
 verdict:success?"STRUCTURAL_DEV_GAIN_ONLY":"MIXED_OR_NEGATIVE_DEV",
 exclusions:{independent_process_cold_restore:false,original_yggdrasil_native_first_use:false,
  canonical_learning:false,compute_or_energy_equivalence_proven:false,deployment:false}};
};
if (typeof module!=="undefined" && require.main===module) {
 const fs=require("fs"), result=run();
 if(process.argv.includes("--verify")){
  const idx=process.argv.indexOf("--verify"), sealed=JSON.parse(fs.readFileSync(process.argv[idx+1],"utf8"));
  if(JSON.stringify(result)!==JSON.stringify(sealed))throw Error("GATE20_EXACT_REPLAY_FAIL");
  process.stdout.write("GATE20_EXACT_REPLAY_PASS "+result.verdict+"\n");
 }else process.stdout.write(JSON.stringify(result,null,2)+"\n");
}
