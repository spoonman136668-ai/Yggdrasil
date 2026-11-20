"use strict";
// Gate22: frozen synthetic causal change detection, prequential / A-B-A retention.
// Preregistration: a4ad408eb9e4032407962ac06e4b14bd3a8e290a
const run = function gate22(){
"use strict";
const need=(a,m)=>{if(!a)throw Error("GATE22_INVARIANT "+m);};
const pop=m=>{let n=0;for(;m;m>>>=1)n+=m&1;return n;};
const masks=Array.from({length:63},(_,i)=>i+1).filter(m=>pop(m)<=3);
const ix=(x,m)=>{let z=0;for(let i=0;i<6;i++)if(m&(1<<i))z=(z<<1)|((x>>i)&1);return z;};
const mix=x=>{x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;return(x^(x>>>16))>>>0;};
const rand=seed=>{let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};};
const shuffled=(a,r)=>{const b=a.slice();for(let i=b.length-1;i>0;i--){let j=r()%(i+1);[b[i],b[j]]=[b[j],b[i]];}return b;};
const h=(seed,context,x,visit,domain)=>mix(mix(seed^Math.imul(context+1,0x9e3779b1)^Math.imul(domain+1,0x85ebca6b))^Math.imul(x+1,0xc2b2ae35)^Math.imul(visit+1,0x27d4eb2f));
const clip=p=>Math.max(.05,Math.min(.95,p)),sq=(p,y)=>(p-y)*(p-y);
const essential=t=>[0,1,2].every(i=>Array.from({length:8},(_,j)=>j).some(j=>((t>>j)&1)!==((t>>(j^(1<<i)))&1)));
function table(f,r){
 if(f==="xor_pair")return 6;if(f==="unary")return 2;
 if(f==="mux3"){let t=0;for(let x=0;x<8;x++){const y=(x&4)?(x&1):((x>>1)&1);t|=y<<x;}return t;}
 let t;do{t=r()&255;}while(!essential(t));return t;
}
function make(seed,family){
 const ra=rand(mix(seed^0x41b9d70e)),rb=rand(mix(seed^0x5ec70d31));
 const stationary=family==="stationary_essential3",independent=family==="independent_noise";
 const k=independent?0:family==="unary"?1:family==="xor_pair"?2:3;
 const orderA=k?shuffled([0,1,2,3,4,5],ra).slice(0,k):[],ta=k?table(family,ra):0;
 let orderB=[],tries=0;if(stationary)orderB=orderA.slice();else if(k)do{orderB=shuffled([0,1,2,3,4,5],rb).slice(0,k);need(++tries<500,"distinct parents");}while(orderB.slice().sort().join()===orderA.slice().sort().join());
 const A={order:orderA,truth:ta},B={order:orderB,truth:ta};
 const source=shuffled(Array.from({length:64},(_,i)=>i),rand(mix(seed^0x137eab65))).map(x=>[x,outcome(A,0,x,0,901)]),
       bOrder=shuffled(Array.from({length:64},(_,i)=>i),rand(mix(seed^0xd28ba1c5))),
       aReturn=shuffled(Array.from({length:64},(_,i)=>i),rand(mix(seed^0xc3f1442a)));
 function outcome(w,ctx,x,visit,domain){
  const z=h(seed,ctx,x,visit,domain);
  if(independent)return z&1;
  let state=0;for(const b of w.order)state=(state<<1)|((x>>b)&1);
  return((w.truth>>state)&1)^(z%20===0?1:0);
 }
 const fitB=bOrder.slice(0,48).map(x=>[x,outcome(B,1,x,0,902)]),
       heldB=bOrder.slice(48).map(x=>[x,outcome(B,1,x,0,907)]),
       fitR=aReturn.slice(0,48).map(x=>[x,outcome(A,2,x,0,903)]),
       heldR=aReturn.slice(48).map(x=>[x,outcome(A,2,x,0,908)]);
 need(source.length===64&&fitB.length===48&&heldB.length===16&&fitR.length===48&&heldR.length===16,"data sizes");
 need(!fitB.some(([x])=>heldB.some(z=>z[0]===x))&&!fitR.some(([x])=>heldR.some(z=>z[0]===x)),"held disjoint");
 return{source,fitB,heldB,fitR,heldR,stationary,independent};
}
function stats(rows,m){const n=new Uint16Array(1<<pop(m)),yes=new Uint16Array(n.length);for(const [x,y]of rows){const j=ix(x,m);n[j]++;yes[j]+=y;}return{n,yes};}
function forecast(rows,m,x){const z=stats(rows,m),j=ix(x,m);return clip((z.yes[j]+1)/(z.n[j]+2));}
function loo(rows,m){
 if(!rows.length)return Infinity;
 const z=stats(rows,m);let loss=0;
 for(const [x,y]of rows){const j=ix(x,m);loss+=sq(clip((z.yes[j]-y+1)/(z.n[j]+1)),y);}
 return loss/rows.length+.003*(1<<pop(m));
}
function maskBest(rows){let best=1,val=Infinity;for(const m of masks){const s=loo(rows,m);if(s<val-1e-12){best=m;val=s;}}return best;}
function neighbors(m){
 const out=new Set(),k=pop(m);
 for(let i=0;i<6;i++)if(m&(1<<i)){
  if(k>1)out.add(m^(1<<i));
  for(let j=0;j<6;j++)if(!(m&(1<<j)))out.add((m^(1<<i))|(1<<j));
 }else if(k<3)out.add(m|(1<<i));
 return [...out].sort((a,b)=>a-b);
}
const lf=[0];for(let i=1;i<=64;i++)lf[i]=lf[i-1]+Math.log(i);
function bayesShort(rows){
 if(!rows.length)return x=>.5;
 const priors=[0,6,15,20],components=[];
 for(const mask of masks){
  const s=stats(rows,mask);let log=-Math.log(3*priors[pop(mask)]);
  for(let j=0;j<s.n.length;j++)log+=lf[s.yes[j]]+lf[s.n[j]-s.yes[j]]-lf[s.n[j]+1];
  components.push({mask,counts:s,log});
 }
 const mx=Math.max(...components.map(z=>z.log));let total=0;
 for(const z of components){z.w=Math.exp(z.log-mx);total+=z.w;}
 return x=>components.reduce((v,z)=>{const j=ix(x,z.mask);return v+z.w*clip((z.counts.yes[j]+1)/(z.counts.n[j]+2));},0)/total;
}
// Separate global fixed-model optimizer: does not call the local neighbor or penalized-LOO selector.
function fitStatic(rows){
 let best=1,score=Infinity,work=0;
 for(let mask=1;mask<64;mask++){
  let k=0;for(let i=0;i<6;i++)k+=(mask>>i)&1;if(k>3)continue;
  const counts=Array.from({length:1<<k},()=>({count:0,yes:0})),bins=[];
  for(const [x,y]of rows){let j=0;for(let bit=0;bit<6;bit++)if(mask&(1<<bit))j=(j<<1)|((x>>bit)&1);bins.push(j);counts[j].count++;counts[j].yes+=y;}
  let loss=0;for(let i=0;i<rows.length;i++){const c=counts[bins[i]],y=rows[i][1],p=Math.max(.05,Math.min(.95,(c.yes-y+1)/(c.count+1)));loss+=(p-y)**2;}
  const val=loss/rows.length+.003*(1<<k);work++;if(val<score-1e-12){score=val;best=mask;}
 }
 return{mask:best,work};
}
function fresh(A,source){return{A:A.map(q=>q.slice()),rows:[],source,mask:source,mode:0,cooldown:0,switches:0,edits:0,work:0,everNew:0,everReturn:0};}
function memory(s){
 need(s.A.length===64&&s.rows.length<=96&&s.work<65536,"packable");
 const bytes=new Uint8Array(384);
 s.A.forEach(([x,y],i)=>{need(x<64&&y<2,"A records");bytes[i*2]=x;bytes[i*2+1]=y;});
 s.rows.forEach(([x,y],i)=>{need(x<64&&y<2,"stream records");bytes[128+i*2]=x;bytes[129+i*2]=y;});
 const values=[s.rows.length,s.source,s.mask,s.mode,s.cooldown,s.switches,s.edits,s.everNew,s.everReturn,s.work&255,s.work>>8];
 for(let i=0;i<values.length;i++){need(values[i]>=0&&values[i]<256,"meta byte");bytes[320+i]=values[i];}
 return bytes;
}
function reload(bytes){
 need(bytes.length===384&&bytes.slice(331).every(v=>v===0),"pack format");
 const A=[],rows=[],n=bytes[320];need(n<=96,"row count");
 for(let i=0;i<64;i++){const x=bytes[i*2],y=bytes[i*2+1];need(x<64&&y<2,"source bytes");A.push([x,y]);}
 for(let i=0;i<96;i++){const x=bytes[128+i*2],y=bytes[129+i*2];if(i<n){need(x<64&&y<2,"stream bytes");rows.push([x,y]);}else need(x===0&&y===0,"padding");}
 const s={A,rows,source:bytes[321],mask:bytes[322],mode:bytes[323],cooldown:bytes[324],switches:bytes[325],edits:bytes[326],everNew:bytes[327],everReturn:bytes[328],work:bytes[329]+256*bytes[330]};
 need(pop(s.source)>=1&&pop(s.source)<=3&&pop(s.mask)>=1&&pop(s.mask)<=3&&s.mode<=1,"restored graph");
 return s;
}
function predictG(s,x){
 return s.mode===0?forecast(s.A,s.source,x):forecast(s.rows.slice(-32),s.mask,x);
}
function gainOn(validation,other,preferred){const z=validation.map(([x,y])=>sq(other(x),y)-sq(preferred(x),y));return z.reduce((a,b)=>a+b,0)/z.length;}
function gatedUpdate(s,ob){
 s.rows.push(ob.slice());const n=s.rows.length;
 if(n<16||n%8!==0)return;
 if(s.cooldown>0){s.cooldown--;return;}
 const last=s.rows.slice(-Math.min(n,32)),fit=last.slice(0,-8),val=last.slice(-8);
 need(fit.length>=8&&val.length===8,"witness split");
 const oldRisk=loo(fit,s.mask);s.work++;
 let winner=s.mask,score=oldRisk;
 for(const m of neighbors(s.mask)){const cost=loo(fit,m);s.work++;if(cost<score-1e-12){score=cost;winner=m;}}
 const source=x=>forecast(s.A,s.source,x),
       active=x=>forecast(fit,s.mask,x),
       alternate=x=>forecast(fit,winner,x);
 const twoHalves=(a,b,threshold)=>gainOn(val.slice(0,4),a,b)>0&&gainOn(val.slice(4),a,b)>0&&gainOn(val,a,b)>=threshold;
 if(s.mode===0){
  if(winner!==s.mask&&oldRisk-score>=.006&&twoHalves(source,alternate,.025)&&gainOn(val,()=>.5,alternate)>=.005){
   s.mask=winner;s.mode=1;s.switches++;s.edits++;s.everNew=1;s.cooldown=1;
  }
 }else {
  if(twoHalves(active,source,.025)){
   s.mode=0;s.mask=s.source;s.switches++;s.everReturn=1;s.cooldown=1;
  }else if(winner!==s.mask&&oldRisk-score>=.006&&twoHalves(active,alternate,.025)){
   s.mask=winner;s.edits++;
  }
 }
}
function greedyUpdate(s,ob){
 s.rows.push(ob.slice());const n=s.rows.length;if(n<8||n%8!==0)return;
 const fit=s.rows.slice(-32);
 let current=loo(fit,s.mask);s.work++,best=s.mask;let risk=current;
 for(const m of neighbors(s.mask)){const v=loo(fit,m);s.work++;if(v<risk-1e-12){risk=v;best=m;}}
 if(best!==s.mask&&current-risk>=.006){s.mask=best;s.edits++;s.mode=1;}
}
function makeControl(A,source){
 return{A,source,rows:[],global:{mask:source,work:0},sliding:{mask:source,work:0},ungated:fresh(A,source),hazardWeight:0.05};
}
function controlForecast(c,x){
 const seen=c.A.concat(c.rows),short=seen.slice(-32),
       pg=forecast(seen,c.global.mask,x),ps=forecast(short,c.sliding.mask,x),
       pu=forecast(c.ungated.rows.length?c.ungated.rows.slice(-32):c.A,c.ungated.mask,x),
       pa=forecast(c.A,c.source,x),pb=bayesShort(short)(x);
 return {frozen:pa,growing:pg,sliding:ps,bayes:(1-c.hazardWeight)*pa+c.hazardWeight*pb,ungated:pu,null:.5};
}
function controlUpdate(c,row,predictBefore){
 const [x,y]=row;
 const prior=forecast(c.A,c.source,x),
       recent=bayesShort(c.A.concat(c.rows).slice(-32))(x);
 // Bayesian hazard mixture weights update from out-of-sample likelihoods only.
 let w=(1/64)+(1-2/64)*c.hazardWeight;
 const likelihoodB=y?recent:1-recent,likelihoodA=y?prior:1-prior;
 const denominator=w*likelihoodB+(1-w)*likelihoodA;
 c.hazardWeight=denominator>0?(w*likelihoodB)/denominator:.5;
 c.rows.push(row.slice());greedyUpdate(c.ungated,row);
 if(c.rows.length%8===0){
  const total=c.A.concat(c.rows),short=total.slice(-32);
  const global=fitStatic(total),slide=fitStatic(short);
  c.global.mask=global.mask;c.global.work+=global.work;
  c.sliding.mask=slide.mask;c.sliding.work+=slide.work;
 }
}
function paired(xs){
 const n=xs.length,mean=xs.reduce((a,b)=>a+b,0)/n,variance=xs.reduce((a,b)=>a+(b-mean)**2,0)/(n-1);
 const ci=1.96*Math.sqrt(variance/n),r=x=>Number(x.toFixed(10));return {mean:r(mean),ci95:[r(mean-ci),r(mean+ci)]};
}
function trial(seed,family){
 const d=make(seed,family),origin=maskBest(d.source),s=fresh(d.source,origin),ctrl=makeControl(d.source,origin);
 const labels=["gated","frozen","growing","sliding","bayes","ungated","null","oracle"],phaseScores={B:{},R:{}},preScores={B:{},R:{}};
 for(const phase of ["B","R"]){for(const k of labels){phaseScores[phase][k]=0;preScores[phase][k]=0;}}
 const same=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
 let sourceRetention=true,heldDisjoint=true,cold=true;
 let replicate48=null,replicate72=null;
 let firstNew=null,firstReturn=null;
 const stream=d.fitB.concat(d.fitR);
 for(let t=0;t<96;t++){
  const [x,y]=stream[t],phase=t<48?"B":"R";
  const control=controlForecast(ctrl,x),own=predictG(s,x);
  const oracle=phase==="R"?forecast(d.source,origin,x):ctrl.rows.length>=8?forecast(d.fitB.slice(0,Math.min(t,48)),maskBest(d.fitB.slice(0,Math.min(t,48))),x):forecast(d.source,origin,x);
  const preds={gated:own,...control,oracle};
  for(const k of labels)preScores[phase][k]+=sq(preds[k],y)/48;
  gatedUpdate(s,[x,y]);controlUpdate(ctrl,[x,y],control);
  if(t>=48&&replicate48){gatedUpdate(replicate48,[x,y]);cold=cold&&same(Array.from(memory(s)),Array.from(memory(replicate48)));}
  if(t>=72&&replicate72){gatedUpdate(replicate72,[x,y]);cold=cold&&same(Array.from(memory(s)),Array.from(memory(replicate72)));}
  if(firstNew===null&&s.everNew)firstNew=t;
  if(firstReturn===null&&s.everReturn)firstReturn=t;
  if(t===47){
   const sourceBytes=memory(s);replicate48=reload(new Uint8Array(sourceBytes));
   cold=cold&&same(Array.from(sourceBytes),Array.from(memory(replicate48)));
  }
  if(t===71){
   const sourceBytes=memory(s);replicate72=reload(new Uint8Array(sourceBytes));
   cold=cold&&same(Array.from(sourceBytes),Array.from(memory(replicate72)));
  }
  if(t===47||t===95){
   const held=phase==="B"?d.heldB:d.heldR;
   const set=new Set((phase==="B"?d.fitB:d.fitR).map(r=>r[0]));
   if(held.some(([act])=>set.has(act)))heldDisjoint=false;
   const oracleRows=phase==="B"?d.fitB:d.source,
         oracleMask=phase==="B"?maskBest(d.fitB):origin;
   for(const [hx,hy]of held){
    const controls=controlForecast(ctrl,hx),me=predictG(s,hx),oracleP=forecast(oracleRows,oracleMask,hx);
    const pp={gated:me,...controls,oracle:oracleP};
    for(const k of labels)phaseScores[phase][k]+=sq(pp[k],hy)/16;
    if(replicate48&&phase==="R"&&predictG(replicate48,hx)!==me)cold=false;
    if(replicate72&&phase==="R"&&predictG(replicate72,hx)!==me)cold=false;
   }
  }
 }
 const end=reload(new Uint8Array(memory(s)));cold=cold&&same(Array.from(memory(s)),Array.from(memory(end)));
 for(let x=0;x<64;x++){
  if(forecast(s.A,s.source,x)!==forecast(d.source,origin,x))sourceRetention=false;
  if(predictG(end,x)!==predictG(s,x))cold=false;
 }
 need(memory(s).length===384,"capacity");
 return{phaseScores,preScores,sourceRetention,heldDisjoint,cold,
 switches:s.switches,edits:s.edits,everNew:s.everNew,everReturn:s.everReturn,finalSource:s.mode===0,
 firstNew,firstReturn,work:{local:s.work,ungated:ctrl.ungated.work,global:ctrl.global.work,sliding:ctrl.sliding.work,bayes:masks.length*96}};
}
const groups={},related=[];
for(const [family,first]of [["xor_pair",121000],["mux3",122000],["essential3",123000],["unary",124000],["stationary_essential3",125000],["independent_noise",126000]]){
 const rows=Array.from({length:32},(_,i)=>trial(first+i,family)),labels=Object.keys(rows[0].phaseScores.B),mean=key=>Number((rows.reduce((s,x)=>s+key(x),0)/32).toFixed(10));
 if(first<125000)related.push(...rows);
 groups[family]={seeds:32,seed_first:first,seed_last:first+31,
  held_B:Object.fromEntries(labels.map(k=>[k,mean(x=>x.phaseScores.B[k])])),
  held_R:Object.fromEntries(labels.map(k=>[k,mean(x=>x.phaseScores.R[k])])),
  prequential_B:Object.fromEntries(labels.map(k=>[k,mean(x=>x.preScores.B[k])])),
  prequential_R:Object.fromEntries(labels.map(k=>[k,mean(x=>x.preScores.R[k])])),
  ever_entered_new:rows.filter(x=>x.everNew).length,
  source_reactivated:rows.filter(x=>x.everNew&&x.everReturn&&x.finalSource).length,
  any_mode_switch:rows.filter(x=>x.switches>0).length,
  cold_exact:rows.filter(x=>x.cold).length,
  source_immutable:rows.filter(x=>x.sourceRetention).length,
  held_disjoint:rows.filter(x=>x.heldDisjoint).length,
  mean_work:Object.fromEntries(Object.keys(rows[0].work).map(k=>[k,mean(x=>x.work[k])])),
  B_gain_vs_frozen:paired(rows.map(x=>x.phaseScores.B.frozen-x.phaseScores.B.gated)),
  B_gated_minus_sliding:paired(rows.map(x=>x.phaseScores.B.gated-x.phaseScores.B.sliding)),
  return_gain_vs_sliding:paired(rows.map(x=>x.phaseScores.R.sliding-x.phaseScores.R.gated)),
  return_gain_vs_bayes:paired(rows.map(x=>x.phaseScores.R.bayes-x.phaseScores.R.gated)),
  new_lag_mean:mean(x=>x.firstNew===null?48:Math.max(0,x.firstNew-47)),
  return_lag_mean:mean(x=>x.firstReturn===null?48:Math.max(0,x.firstReturn-47))
 };
}
const pooledBSource=paired(related.map(x=>x.phaseScores.B.frozen-x.phaseScores.B.gated));
const pooledBSlide=paired(related.map(x=>x.phaseScores.B.gated-x.phaseScores.B.sliding));
const pooledBBayes=paired(related.map(x=>x.phaseScores.B.gated-x.phaseScores.B.bayes));
const pooledRSlide=paired(related.map(x=>x.phaseScores.R.sliding-x.phaseScores.R.gated));
const pooledRBayes=paired(related.map(x=>x.phaseScores.R.bayes-x.phaseScores.R.gated));
const stable=groups.stationary_essential3,noise=groups.independent_noise;
const conditions={
 related_B_gain_vs_frozen_A_min:pooledBSource.mean>=.045,
 related_B_gain_vs_frozen_A_ci_lower_positive:pooledBSource.ci95[0]>0,
 related_B_regression_vs_sliding_max:pooledBSlide.mean<=.02,
 related_B_regression_vs_hazard_bayes_max:pooledBBayes.mean<=.025,
 related_return_gain_vs_sliding_min:pooledRSlide.mean>=.012,
 related_return_gain_vs_sliding_ci_lower_positive:pooledRSlide.ci95[0]>0,
 related_return_gain_vs_hazard_bayes_min:pooledRBayes.mean>=.005,
 related_return_gain_vs_hazard_bayes_ci_lower_positive:pooledRBayes.ci95[0]>0,
 related_return_source_reactivated_fraction_min:related.filter(x=>x.everNew&&x.everReturn&&x.finalSource).length/128>=.75,
 stationary_false_mode_switch_trials_max_fraction:stable.any_mode_switch/32<=.20,
 noise_false_mode_switch_trials_max_fraction:noise.any_mode_switch/32<=.20,
 stationary_holdout_Brier_regression_vs_sliding_max:Math.max(stable.held_B.gated-stable.held_B.sliding,stable.held_R.gated-stable.held_R.sliding)<=.02,
 noise_holdout_Brier_regression_vs_null_max:Math.max(noise.held_B.gated-noise.held_B.null,noise.held_R.gated-noise.held_R.null)<=.025,
 all_held_disjoint:Object.values(groups).every(g=>g.held_disjoint===32),
 all_A_source_immutable:Object.values(groups).every(g=>g.source_immutable===32),
 all_384byte_replay_exact:Object.values(groups).every(g=>g.cold_exact===32)
};
const pass=Object.values(conditions).every(Boolean);
return{schema:"yggdrasil.gate22.causedrift-cold-reactivation.v1",
 prereg_commit:"a4ad408eb9e4032407962ac06e4b14bd3a8e290a",parent_commit:"eb44df75612be0aaa6ee388a08f308eb8fc8dc39",
 design:{seeds:192,source_A:64,phase_B_training:48,return_A_training:48,held_each_phase:16,saved_state_bytes:384,hidden_phase_change:true,oracle_info_advantaged:true},
 groups,summary:{related_B_gain_vs_frozen_A:pooledBSource,related_B_gated_minus_sliding:pooledBSlide,related_B_gated_minus_bayes:pooledBBayes,
 related_R_gain_vs_sliding:pooledRSlide,related_R_gain_vs_bayes:pooledRBayes,
 source_reactivated_related:related.filter(x=>x.everNew&&x.everReturn&&x.finalSource).length,
 stationary_false_switch_trials:stable.any_mode_switch,noise_false_switch_trials:noise.any_mode_switch},
 conditions,verdict:pass?"SYNTHETIC_CHANGEPOINT_DEV_SIGNAL_ONLY":"CHANGEPOINT_MIXED_OR_NEGATIVE_DEV",
 exclusions:{native_first_use:false,training_checkpoint_promotion:false,independent_replication:false,process_exit_restore:false,compute_matched:false,accepted_intelligence_gain:false,deployment:false}};
};
if(typeof module!=="undefined" && require.main===module){
 const fs=require("fs"), result=run();
 if(process.argv.includes("--verify")){
  const i=process.argv.indexOf("--verify");if(i+1>=process.argv.length)throw Error("missing sealed result");
  const want=JSON.parse(fs.readFileSync(process.argv[i+1],"utf8"));
  if(JSON.stringify(want)!==JSON.stringify(result))throw Error("GATE22_EXACT_REPLAY_MISMATCH");
  process.stdout.write("GATE22_EXACT_REPLAY_PASS "+result.verdict+"\n");
 }else process.stdout.write(JSON.stringify(result,null,2)+"\n");
}
