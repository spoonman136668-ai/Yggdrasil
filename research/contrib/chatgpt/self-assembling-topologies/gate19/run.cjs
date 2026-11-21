"use strict";
// Gate19: frozen research experiment; synthetic A->B hidden-parent remapping.
// Exact prereg: 73e3e3ab872fe3a91f6d999ecbd3bb0146f77ba6.
// Not native Yggdrasil checkpoint, first-use, acceptance, or architecture promotion.
const check=(x,m)=>{if(!x)throw Error("GATE19_INVARIANT "+m);};
const pop=x=>{let n=0;for(;x;x>>>=1)n+=x&1;return n;};
const masks=Array.from({length:31},(_,i)=>i+1),TRIPLES=masks.filter(m=>pop(m)===3);
const bits=m=>Array.from({length:5},(_,i)=>i).filter(i=>(m>>i)&1);
const bin=(x,positions)=>positions.reduce((a,i)=>(a<<1)|((x>>i)&1),0);
const clip=p=>Math.max(.05,Math.min(.95,p)),sqr=(p,y)=>(p-y)**2;
const rng=seed=>{let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};};
function mix(x){x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;return(x^(x>>>16))>>>0;}
function hash(seed,ctx,x,visit,domain){let q=mix(seed^Math.imul(ctx+1,0x9e3779b1)^Math.imul(domain+1,0x85ebca6b));q=mix(q^Math.imul(x+1,0xc2b2ae35));return mix(q^Math.imul(visit+1,0x27d4eb2f));}
function shuffle(a,r){const x=a.slice();for(let i=x.length-1;i>0;i--){const j=r()%(i+1);[x[i],x[j]]=[x[j],x[i]];}return x;}
function essential(t){return [0,1,2].every(k=>Array.from({length:8},(_,x)=>x).some(x=>((t>>x)&1)!==((t>>(x^(1<<k)))&1)));}
const all3Permutations=(()=>{const arr=[];for(let a=0;a<5;a++)for(let b=0;b<5;b++)for(let c=0;c<5;c++)if(a!==b&&a!==c&&b!==c)arr.push([a,b,c]);return arr;})();
check(all3Permutations.length===60&&TRIPLES.length===10,"mapping universe");
function tableFor(family,r){
 if(family==="shared_majority")return 0b11101000;
 if(family==="shared_mux")return Array.from({length:8},(_,x)=>(x&4)?(x&1):((x>>1)&1)).reduce((t,y,x)=>t|(y<<x),0);
 if(family==="shared_parity")return Array.from({length:8},(_,x)=>pop(x)%2).reduce((t,y,x)=>t|(y<<x),0);
 let t;do{t=r()&255;}while(!essential(t));return t;
}
function mapTable(table,perm){
 let next=0;
 for(let x=0;x<8;x++){
  let mapped=0;for(let k=0;k<3;k++)mapped=(mapped<<1)|((x>>(2-perm[k]))&1);
  next|=(((table>>mapped)&1)<<x);
 }
 return next;
}
const PERM6=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
function relatedTable(a,b){return PERM6.some(v=>mapTable(a,v)===b||mapTable(a,v)===(b^255));}
function worlds(seed,family){
 const rA=rng(mix(seed^0x93e94a61)),rB=rng(mix(seed^0x5a1e53cf));
 const maskA=TRIPLES[rA()%10],orderA=bits(maskA),tableA=tableFor(family,rA),flipA=rA()&1;
 const other=TRIPLES.filter(m=>m!==maskA),maskB=other[rB()%other.length],orderB=shuffle(bits(maskB),rB);
 let tableB=tableA,flipB=flipA;
 if(family==="unrelated_essential_boolean"){
  let x=0;
  do{tableB=tableFor(family,rB);x++;check(x<100000,"unrelated-sample candidate");}while(relatedTable(tableA,tableB));
  flipB=rB()&1;
 }
 return [{order:orderA,table:tableA,flip:flipA},{order:orderB,table:tableB,flip:flipB}];
}
function consequence(w,seed,ctx,x,visit,domain){
 const pattern=bin(x,w.order),y=((w.table>>pattern)&1)^w.flip,noise=hash(seed,ctx,x,visit,domain)%20===0?1:0;
 return y^noise;
}
function makeData(seed,family){
 const [A,B]=worlds(seed,family),rngA=rng(mix(seed^0x51a9b6d3)),rngB=rng(mix(seed^0x02b672ad));
 const fitA=[],seenA=new Uint8Array(32);
 for(let round=0;round<3;round++)for(const x of shuffle(Array.from({length:32},(_,i)=>i),rngA))
  fitA.push([x,consequence(A,seed,0,x,seenA[x]++,21201)]);
 const partitionB=shuffle(Array.from({length:32},(_,i)=>i),rngB),allowed=partitionB.slice(0,24),held=partitionB.slice(24);
 const fitB=allowed.map(x=>[x,consequence(B,seed,1,x,0,21202)]);
 check(fitA.length===96&&fitB.length===24&&held.length===8&&new Set([...allowed,...held]).size===32,"data custody");
 return {A,B,fitA,fitB,held};
}
function counts(rows,order){
 const size=1<<order.length,n=new Uint16Array(size),yes=new Uint16Array(size);
 for(const [x,y]of rows){const i=bin(x,order);n[i]++;yes[i]+=y;}return{n,yes};
}
function probability(st,idx){return clip((st.yes[idx]+1)/(st.n[idx]+2));}
function predict(rows,order,x){const st=counts(rows,order);return probability(st,bin(x,order));}
function loo(rows,order){
 const s=counts(rows,order);let loss=0;
 for(const [x,y]of rows){const i=bin(x,order);const p=clip((s.yes[i]-y+1)/(s.n[i]+1));loss+=sqr(p,y);}
 return loss/rows.length;
}
function selectModel(rows,withHigh=true){
 let best={order:[],cost:Infinity};
 for(const mask of masks){
  const k=pop(mask);if(k>3||(!withHigh&&k===3))continue;
  const order=bits(mask),cost=loo(rows,order)+.003*(1<<k);
  if(cost<best.cost-1e-12)best={order,cost};
 }
 return best;
}
function learnedA(rows){
 // Gate17-like source-only selection: first64 LOO and last32 validation.
 const train=rows.slice(0,64),val=rows.slice(64);
 const candidate=selectModel(train,true),baseline=counts(train,[]);
 const srcStats=counts(train,candidate.order);
 const avg=(c)=>val.reduce((sum,[x,y])=>sum+sqr(probability(c,bin(x,c===baseline?[]:candidate.order)),y),0)/val.length;
 let order=candidate.order;
 if(avg(baseline)-avg(srcStats)<.015)order=[];
 return{order,rows,table:counts(rows,order)};
}
function candidateMaps(k){if(k===0)return[[]];if(k===3)return all3Permutations;
 const out=[];function build(prefix){
  if(prefix.length===k){out.push(prefix);return;}
  for(let i=0;i<5;i++)if(!prefix.includes(i))build(prefix.concat(i));
 }build([]);return out;
}
function bestMap(A,firstB){
 const maps=candidateMaps(A.order.length),posterior=A.table;
 let best=null,bestLoss=Infinity;
 for(const map of maps){
  let nll=0;
  for(const [x,y]of firstB){const p=probability(posterior,bin(x,map));nll-=Math.log(y?p:1-p);}
  if(nll<bestLoss-1e-12){bestLoss=nll;best=map;}
 }
 return {map:best,work:maps.length*firstB.length,order_candidates:maps.length};
}
function scratch(rows){return{order:selectModel(rows,true).order,rows};}
function predScratch(model,x){return predict(model.rows,model.order,x);}
function chooseTransfer(rowsA,rowsB,fullScan){
 const A=learnedA(rowsA),first=rowsB.slice(0,16),valid=rowsB.slice(16),B0=scratch(first);
 const map=bestMap(A,first);
 const lossMap=valid.reduce((v,[x,y])=>v+sqr(probability(A.table,bin(x,map.map)),y),0)/8;
 const lossScratch=valid.reduce((v,[x,y])=>v+sqr(predScratch(B0,x),y),0)/8;
 const accepted=lossScratch-lossMap>=.015&&A.order.length>0;
 return {A,B:scratch(rowsB),map:map.map,accepted,work:map.work,work_full:fullScan?60*first.length:map.work,
  validation_gain:lossScratch-lossMap};
}
function transferForecast(m,x){return m.accepted?probability(m.A.table,bin(x,m.map)):predScratch(m.B,x);}
function shuffledA(rows,seed){
 const g=rng(mix(seed^0xa3c59e71)),labels=shuffle(rows.map(r=>r[1]),g);
 return rows.map(([x],i)=>[x,labels[i]]);
}
const ORDERGROUPS={0:[0],1:masks.filter(x=>pop(x)===1),2:masks.filter(x=>pop(x)===2),3:TRIPLES};
const ALLSUBSETS=[0,...masks.filter(x=>pop(x)<=3)];
const LOGFAC=[0];for(let n=1;n<=97;n++)LOGFAC[n]=LOGFAC[n-1]+Math.log(n);
function betaEvidence(rows,order){
 const s=counts(rows,order);let v=0;
 for(let i=0;i<s.n.length;i++)v+=LOGFAC[s.yes[i]]+LOGFAC[s.n[i]-s.yes[i]]-LOGFAC[s.n[i]+1];
 return v;
}
function bayesB(rows){
 const log=[],orders=[];
 for(const mask of ALLSUBSETS){const order=bits(mask);orders.push(order);
  log.push(betaEvidence(rows,order)+Math.log(.25/ORDERGROUPS[order.length].length));}
 const top=Math.max(...log),ww=log.map(v=>Math.exp(v-top)),z=ww.reduce((a,b)=>a+b,0);
 return x=>ww.reduce((sum,w,i)=>sum+w*predict(rows,orders[i],x),0)/z;
}
function bayesShared(rowsA,rowsB){
 const A=learnedA(rowsA),maps=candidateMaps(A.order.length);
 const logShared=maps.map(map=>{
  let value=-Math.log(maps.length);
  for(const [x,y]of rowsB){const p=probability(A.table,bin(x,map));value+=Math.log(y?p:1-p);}
  return value;
 });
 const eIndependent=ALLSUBSETS.map(mask=>betaEvidence(rowsB,bits(mask))+Math.log(.25/ORDERGROUPS[pop(mask)].length));
 const topB=Math.max(...eIndependent),massB=eIndependent.reduce((s,v)=>s+Math.exp(v-topB),0),logIndependent=topB+Math.log(massB);
 const top=Math.max(...logShared,logIndependent);
 const sw=logShared.map(v=>Math.exp(v-top)),iw=Math.exp(logIndependent-top),total=iw+sw.reduce((a,b)=>a+b,0);
 const scratchForecast=bayesB(rowsB);
 return x=>(iw*scratchForecast(x)+sw.reduce((sum,w,i)=>sum+w*probability(A.table,bin(x,maps[i])),0))/total;
}
function packRecords(rowsA,rowsB){
 check(rowsA.length===96&&rowsB.length===24,"packed rows");
 const out=new Uint8Array(388);
 rowsA.forEach(([x,y],i)=>{out[i*2]=x;out[i*2+1]=y;});
 rowsB.forEach(([x,y],i)=>{out[192+i*2]=x;out[193+i*2]=y;});
 return out;
}
function unpackRecords(b){
 check(b instanceof Uint8Array&&b.length===388,"serialized length");
 const a=[],bb=[];
 for(let i=0;i<96;i++){const x=b[i*2],y=b[i*2+1];check(x<32&&y<=1,"A bytes");a.push([x,y]);}
 for(let i=0;i<24;i++){const x=b[192+i*2],y=b[193+i*2];check(x<32&&y<=1,"B bytes");bb.push([x,y]);}
 check(b.slice(240).every(x=>x===0),"zero padding");
 return{A:a,B:bb};
}
function round(x){return Number(x.toFixed(10));}
function trial(seed,family){
 const d=makeData(seed,family),p=packRecords(d.fitA,d.fitB);
 const A=learnedA(d.fitA),transfer=chooseTransfer(d.fitA,d.fitB,false),
 fixed=chooseTransfer(d.fitA,d.fitB,true),scr=scratch(d.fitB),
 shuffled=chooseTransfer(shuffledA(d.fitA,seed),d.fitB,false),
 bayesBOnly=bayesB(d.fitB),bayesT=bayesShared(d.fitA,d.fitB);
 const saved=Array.from(p),loaded1=unpackRecords(new Uint8Array(p)),loaded2=unpackRecords(new Uint8Array(p));
 const restored1=chooseTransfer(loaded1.A,loaded1.B,false),restored2=chooseTransfer(loaded2.A,loaded2.B,false);
 const Aafter=learnedA(loaded1.A);
 let exact=true,retained=true,disjoint=true;
 const beforeBytes=JSON.stringify(d.fitA),afterBytes=JSON.stringify(loaded1.A);
 if(beforeBytes!==afterBytes||A.order.join(",")!==Aafter.order.join(","))retained=false;
 for(let x=0;x<32;x++){
  const prior=predict(A.rows,A.order,x),after=predict(Aafter.rows,Aafter.order,x);
  if(prior!==after)retained=false;
 }
 const scores={transfer:0,fixed:0,scratch:0,shuffled_A:0,bayes_B:0,bayes_shared:0,oracle:0,flat:0,null:0};
 const bOrder=d.B.order,oracleTable=counts(d.fitA,d.A.order),oracleMap=bOrder;
 for(const x of d.held){
  if(d.fitB.some(([action])=>action===x))disjoint=false;
  const y=consequence(d.B,seed,1,x,0,47517);
  const pred={
   transfer:transferForecast(transfer,x),fixed:transferForecast(fixed,x),
   scratch:predScratch(scr,x),shuffled_A:transferForecast(shuffled,x),
   bayes_B:bayesBOnly(x),bayes_shared:bayesT(x),
   oracle:probability(oracleTable,bin(x,oracleMap)),
   flat:.5,null:.5
  };
  for(const [k,v]of Object.entries(pred))scores[k]+=sqr(v,y);
  if(pred.transfer!==transferForecast(restored1,x)||pred.transfer!==transferForecast(restored2,x)||pred.fixed!==pred.transfer)exact=false;
 }
 if(saved.length!==388||!saved.every((v,i)=>v===loaded2.A.concat(loaded2.B).flat()[i]??v)){} // no-op avoided in scoring; parity checked below
 if(JSON.stringify(loaded2.A)!==beforeBytes||JSON.stringify(loaded2.B)!==JSON.stringify(d.fitB))exact=false;
 for(const k of Object.keys(scores))scores[k]/=8;
 return {scores,accepted:transfer.accepted,negative_acceptance:shuffled.accepted,
  exact,retained,disjoint,A_order:A.order.length,
  fitted_mapping_candidates:candidateMaps(A.order.length).length,
  compared_map_labels:transfer.work,full_map_labels:fixed.work_full};
}
function paired(xs){
 const n=xs.length,m=xs.reduce((a,x)=>a+x,0)/n,v=xs.reduce((a,x)=>a+(x-m)**2,0)/(n-1),half=1.96*Math.sqrt(v/n);
 return {mean:round(m),ci95:[round(m-half),round(m+half)]};
}
const ARMS=["transfer","fixed","scratch","shuffled_A","bayes_B","bayes_shared","oracle","flat","null"];
function cohort(family,first,n){
 const rows=Array.from({length:n},(_,i)=>trial(first+i,family));
 const means=Object.fromEntries(ARMS.map(k=>[k,round(rows.reduce((s,r)=>s+r.scores[k],0)/n)]));
 return {family,seed_first:first,seed_last:first+n-1,seeds:n,means,
  transfer_accepted:rows.filter(x=>x.accepted).length,
  shuffled_A_accepted:rows.filter(x=>x.negative_acceptance).length,
  exact_cold_restores:rows.filter(x=>x.exact).length,
  A_retention_exact:rows.filter(x=>x.retained).length,
  B_held_disjoint:rows.filter(x=>x.disjoint).length,
  A_subsets_order3:rows.filter(x=>x.A_order===3).length,
  candidate_map_likelihoods:rows.reduce((s,x)=>s+x.compared_map_labels,0),
  full_mapping_reference_work:rows.reduce((s,x)=>s+x.full_map_labels,0),
  gain_vs_scratch:paired(rows.map(x=>x.scores.scratch-x.scores.transfer)),
  gain_vs_shuffled_A:paired(rows.map(x=>x.scores.shuffled_A-x.scores.transfer)),
  gain_vs_fixed:paired(rows.map(x=>x.scores.fixed-x.scores.transfer)),
  deficit_to_bayes_shared:paired(rows.map(x=>x.scores.transfer-x.scores.bayes_shared))};
}
function run(){
 const majority=cohort("shared_majority",81000,48),mux=cohort("shared_mux",82000,48),
  essential=cohort("shared_essential_boolean",83000,48),
  parity=cohort("shared_parity",84000,48),
  unrelated=cohort("unrelated_essential_boolean",85000,48);
 const groups={majority,mux,essential,parity,unrelated};
 const related=[majority,mux,essential,parity],all=Object.values(groups);
 const overallScratchGain=related.reduce((s,z)=>s+z.gain_vs_scratch.mean,0)/4;
 const overallShuffleGain=related.reduce((s,z)=>s+z.gain_vs_shuffled_A.mean,0)/4;
 const unrelatedRate=unrelated.transfer_accepted/48;
 const bayesDeficit=Math.max(...related.map(z=>z.means.transfer-z.means.bayes_shared));
 const gates={
  majority_gain_vs_scratch_0_025:majority.gain_vs_scratch.mean>=.025,
  mux_gain_vs_scratch_0_025:mux.gain_vs_scratch.mean>=.025,
  essential_gain_vs_scratch_0_025:essential.gain_vs_scratch.mean>=.025,
  parity_gain_vs_scratch_0_025:parity.gain_vs_scratch.mean>=.025,
  pooled_shared_gain_vs_scratch_ci_positive:related.reduce((s,z)=>s+z.gain_vs_scratch.ci95[0],0)>0,
  shared_gain_vs_shuffled_source_min_0_025:overallShuffleGain>=.025,
  shared_mechanism_Brier_max_0_19:related.every(z=>z.means.transfer<=.19),
  unrelated_regression_max_0_025:unrelated.means.transfer-unrelated.means.scratch<=.025,
  unrelated_false_share_fraction_max_0_2:unrelatedRate<=.2,
  worst_bayes_shared_deficit_max_0_02:bayesDeficit<=.02,
  fixed_superiority_min_0_015:majority.gain_vs_fixed.mean>=.015,
  fixed_superiority_ci_positive:majority.gain_vs_fixed.ci95[0]>0,
  all_B_action_holdouts_disjoint:all.every(x=>x.B_held_disjoint===x.seeds),
  all_cold_B_prediction_restores_exact:all.every(x=>x.exact_cold_restores===x.seeds),
  all_A_retained_exact_after_B:all.every(x=>x.A_retention_exact===x.seeds)
 };
 const transferGates=Object.keys(gates).filter(k=>!k.startsWith("fixed_superiority"));
 const qualified=transferGates.every(k=>gates[k]),structural=qualified&&gates.fixed_superiority_min_0_015&&gates.fixed_superiority_ci_positive;
 return {schema:"yggdrasil.gate19.parent-remap-cold-retention.v1",
  prereg_commit:"73e3e3ab872fe3a91f6d999ecbd3bb0146f77ba6",
  parent_sha:"fb772d811ba3b7758c2bca13b52982fcfed6e297",
  design:{A_fit:96,B_fit:24,B_fit_mapping_select:16,B_fit_validation:8,B_held_actions:8,
   saved_bytes:388,hidden_source_mapping:true,matching_B_actions_have_no_training_labels:true,
   model_family:"Finite Boolean conditional subsets, not open-ended intelligence"},
  groups,gates,
  summary:{mean_related_gain_vs_scratch:round(overallScratchGain),mean_related_gain_vs_shuffled_A:round(overallShuffleGain),
   unrelated_transfer_accepted_fraction:round(unrelatedRate),worst_shared_bayes_deficit:round(bayesDeficit)},
  matched_transfer_signal:qualified,structural_superiority:structural,
  verdict:structural?"STRUCTURAL_DEV_GAIN_ONLY":qualified?"A_TO_B_TRANSFER_DEV_GAIN_ONLY":"A_TO_B_TRANSFER_MIXED_NO_GO",
  exclusions:{native_first_use:false,real_cross_process_checkpoint:false,native_cumulative_retention:false,
   standalone_learning_claim:false,process_or_energy_gain_measured:false}};
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 const fs=require("fs"),r=run();
 if(process.argv.includes("--verify")){const path=process.argv[process.argv.indexOf("--verify")+1];check(path,"missing result path");
  const sealed=JSON.parse(fs.readFileSync(path,"utf8"));check(JSON.stringify(sealed)===JSON.stringify(r),"frozen result mismatch");
  process.stdout.write("GATE19_EXACT_REPLAY_PASS "+r.verdict+"\n");
 }else process.stdout.write(JSON.stringify(r,null,2)+"\n");
}
