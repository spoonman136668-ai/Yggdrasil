"use strict";
// Gate21 synthetic experiment, frozen before first score; prereg 834c26e40562e52581997b040d6a39d3f947d337.
const run = function gate21(){
"use strict";
const ok=(v,m)=>{if(!v)throw Error("G21_"+m);};
const pop=x=>{let n=0;for(;x;x>>>=1)n+=x&1;return n;};
const bits=m=>[0,1,2,3,4,5].filter(i=>m&(1<<i));
const idx=(x,m)=>bits(m).reduce((a,i)=>(a<<1)|((x>>i)&1),0);
const masks=Array.from({length:63},(_,i)=>i+1).filter(m=>pop(m)<=3);
const mix=x=>{x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;return(x^(x>>>16))>>>0;};
const rand=s=>{let x=s>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};};
const shuffle=(a,r)=>{let v=a.slice();for(let i=v.length-1;i>0;i--){let j=r()%(i+1);[v[i],v[j]]=[v[j],v[i]];}return v;};
const h=(seed,ctx,x,v,domain)=>mix(mix(seed^Math.imul(ctx+1,0x9e3779b1)^Math.imul(domain+1,0x85ebca6b))^Math.imul(x+1,0xc2b2ae35)^Math.imul(v+1,0x27d4eb2f));
const clamp=p=>Math.max(.05,Math.min(.95,p)),brier=(p,y)=>(p-y)**2;
const essential=t=>[0,1,2].every(k=>Array.from({length:8},(_,i)=>i).some(i=>((t>>i)&1)!==((t>>(i^(1<<k)))&1)));
const perms=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
function equivalent(a,b){
 return perms.some(p=>{let t=0;for(let x=0;x<8;x++){let q=0;for(let k=0;k<3;k++)q=(q<<1)|((x>>(2-p[k]))&1);t|=((a>>q)&1)<<x;}return t===b||t===(b^255);});
}
function table(f,r){
 if(f==="xor_pair")return 6;if(f==="unary")return 2;
 if(f==="mux3"){let t=0;for(let x=0;x<8;x++)t|=((x&4?(x&1):((x>>1)&1))<<x);return t;}
 let t;do{t=r()&255;}while(!essential(t));return t;
}
function data(seed,f){
 const ra=rand(mix(seed^0x0d21b17e)),rb=rand(mix(seed^0x5eb51cba));
 const k=f==="unary"?1:f==="xor_pair"?2:f==="independent_noise"?0:3;
 const a=k?shuffle([0,1,2,3,4,5],ra).slice(0,k):[],ta=k?table(f,ra):0;
 let b=[],n=0;if(k)do{b=shuffle([0,1,2,3,4,5],rb).slice(0,k);ok(++n<256,"parent_remap");}
 while(b.slice().sort().join()===a.slice().sort().join());
 let tb=ta;
 if(f==="unrelated3"){let j=0;do{tb=table(f,rb);ok(++j<10000,"unrelated_table");}while(equivalent(ta,tb));}
 const source={order:a,table:ta,f},target={order:b,table:tb,f};
 const outcome=(world,ctx,x,visit,dom)=>{const q=h(seed,ctx,x,visit,dom);if(f==="independent_noise")return q&1;let j=0;for(let i of world.order)j=(j<<1)|((x>>i)&1);return ((world.table>>j)&1)^(q%20===0?1:0);};
 const ar=shuffle(Array.from({length:64},(_,i)=>i),rand(mix(seed^0x2decb13a)));
 const br=shuffle(Array.from({length:64},(_,i)=>i),rand(mix(seed^0x89c5129f)));
 const A=ar.map(x=>[x,outcome(source,0,x,0,2100)]),act=br.slice(0,32),sent=new Set(act.slice(0,8)),B=[];
 for(let visit=0;visit<3;visit++)for(let x of shuffle(act,rand(mix(seed^Math.imul(visit+1,0x7a3b46c5)))))B.push([x,outcome(target,1,x,visit,2200),sent.has(x)?1:0]);
 const held=br.slice(32,48);
 ok(B.filter(x=>x[2]).length===24&&B.length===96&&A.length===64&&new Set(br).size===64,"split");
 return{A,B,held,hold:x=>outcome(target,1,x,0,9100)};
}
function counts(rows,m){
 const n=new Uint16Array(1<<pop(m)),yes=new Uint16Array(n.length);
 for(let [x,y]of rows){let j=idx(x,m);n[j]++;yes[j]+=y;}return{n,yes};
}
function predict(rows,m,x){const s=counts(rows,m),j=idx(x,m);return clamp((s.yes[j]+1)/(s.n[j]+2));}
function cost(rows,m){const s=counts(rows,m);let v=0;for(let [x,y]of rows){const j=idx(x,m);v+=brier(clamp((s.yes[j]-y+1)/(s.n[j]+1)),y);}return v/rows.length+.003*(1<<pop(m));}
function selectSource(rows){let best=1,loss=Infinity;for(let m of masks){let v=cost(rows,m);if(v<loss-1e-12){best=m;loss=v;}}return best;}
function nearby(m){const n=new Set(),k=pop(m);for(let a=0;a<6;a++)if(m&(1<<a)){if(k>1)n.add(m^(1<<a));for(let b=0;b<6;b++)if(!(m&(1<<b)))n.add((m^(1<<a))|(1<<b));}else if(k<3)n.add(m|(1<<a));return[...n].sort((a,b)=>a-b);}
function start(A,m){return{A:A.map(v=>v.slice()),B:[],mask:m,origin:m,edits:0,work:0};}
function receive(s,row,gated){
 s.B.push(row.slice());if(s.B.length%32)return;
 let fit=s.B.filter(r=>!r[2]),val=s.B.filter(r=>r[2]),old=cost(fit,s.mask),min=old,next=s.mask;s.work++;
 for(let m of nearby(s.mask)){let c=cost(fit,m);s.work++;if(c<min-1e-12){min=c;next=m;}}
 if(next===s.mask||old-min<.008)return;
 if(gated){
  ok(val.length>=8,"sentinel_length");
  const improvement=rows=>rows.reduce((v,[x,y])=>v+brier(predict(fit,s.mask,x),y)-brier(predict(fit,next,x),y),0)/rows.length;
  if(improvement(val)<.012||improvement(val.filter((_,i)=>i%2===0))<=0||improvement(val.filter((_,i)=>i%2===1))<=0)return;
 }
 s.mask=next;s.edits++;
}
function pack(s){
 ok(s.A.length===64&&s.B.length<=96&&pop(s.mask)<=3&&s.mask>0&&s.work<65536,"pack_state");
 const b=new Uint8Array(384);
 s.A.forEach(([x,y],i)=>{b[i*2]=x;b[i*2+1]=y;});
 s.B.forEach(([x,y,v],i)=>{b[128+i*2]=x;b[129+i*2]=y|(v<<1);});
 b[320]=s.mask;b[321]=s.origin;b[322]=s.B.length;b[323]=s.edits;b[324]=s.work&255;b[325]=s.work>>8;return b;
}
function restore(b){
 ok(b.length===384&&b.slice(326).every(x=>x===0),"restore_size");let A=[],B=[],n=b[322];ok(n<=96,"restore_count");
 for(let i=0;i<64;i++){ok(b[i*2]<64&&b[i*2+1]<2,"A_record");A.push([b[i*2],b[i*2+1]]);}
 for(let i=0;i<96;i++){const x=b[128+i*2],v=b[129+i*2];if(i<n){ok(x<64&&v<4,"B_record");B.push([x,v&1,v>>1]);}else ok(x===0&&v===0,"B_padding");}
 return{A,B,mask:b[320],origin:b[321],edits:b[323],work:b[324]+256*b[325]};
}
// Independent global static selector: does not invoke cost(), nearby(), or receive().
function staticFit(rows){
 let best=1,loss=Infinity,ops=0;
 for(let m=1;m<64;m++){
  let k=0;for(let i=0;i<6;i++)k+=(m>>i)&1;if(k>3)continue;
  const st=Array.from({length:1<<k},()=>({n:0,yes:0})),index=[];
  for(let [x,y]of rows){let j=0;for(let i=0;i<6;i++)if(m&(1<<i))j=(j<<1)|((x>>i)&1);index.push(j);st[j].n++;st[j].yes+=y;}
  let sum=0;for(let i=0;i<rows.length;i++){let t=st[index[i]],y=rows[i][1],p=Math.max(.05,Math.min(.95,(t.yes-y+1)/(t.n+1)));sum+=(p-y)**2;}
  let v=sum/rows.length+.003*(1<<k);ops++;if(v<loss-1e-12){loss=v;best=m;}
 }
 return{mask:best,ops};
}
const lf=[0];for(let i=1;i<=97;i++)lf[i]=lf[i-1]+Math.log(i);
const countsByOrder=[0,6,15,20];
function bayes(rows){
 let log=[],ss=[];for(let m of masks){let s=counts(rows,m),z=-Math.log(3*countsByOrder[pop(m)]);
 for(let i=0;i<s.n.length;i++)z+=lf[s.yes[i]]+lf[s.n[i]-s.yes[i]]-lf[s.n[i]+1];log.push(z);ss.push({m,s});}
 const top=Math.max(...log),w=log.map(z=>Math.exp(z-top)),sum=w.reduce((a,b)=>a+b,0);
 return x=>w.reduce((t,v,i)=>{let s=ss[i],j=idx(x,s.m);return t+v*clamp((s.s.yes[j]+1)/(s.s.n[j]+2));},0)/sum;
}
function paired(vals){const n=vals.length,mean=vals.reduce((a,b)=>a+b,0)/n,v=vals.reduce((a,b)=>a+(b-mean)**2,0)/(n-1),ci=1.96*Math.sqrt(v/n),r=x=>Number(x.toFixed(10));return{mean:r(mean),ci95:[r(mean-ci),r(mean+ci)]};}
function trial(seed,f){
 let d=data(seed,f),initial=selectSource(d.A),g=start(d.A,initial),u=start(d.A,initial);
 for(let i=0;i<64;i++){receive(g,d.B[i],true);receive(u,d.B[i],false);}
 const at64=pack(g),cold=restore(new Uint8Array(at64)),same=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
 let equal=same(Array.from(at64),Array.from(pack(cold)));
 for(let i=64;i<96;i++){receive(g,d.B[i],true);receive(u,d.B[i],false);receive(cold,d.B[i],true);}
 const final=pack(g),end=restore(new Uint8Array(final));
 equal=equal&&same(Array.from(final),Array.from(pack(cold)))&&same(Array.from(final),Array.from(pack(end)));
 const all=d.B.map(x=>x.slice(0,2)),fixed=staticFit(all),posterior=bayes(all),
 negLabels=shuffle(all.map(x=>x[1]),rand(mix(seed^0x718f3ba1))),negRows=all.map(([x],i)=>[x,negLabels[i]]),neg=staticFit(negRows);
 let scores={gated:0,ungated:0,fixed:0,bayes:0,frozen_A:0,shuffled_B:0,null:0};
 const actions=new Set(all.map(x=>x[0])),disjoint=d.held.every(x=>!actions.has(x));
 let retained=JSON.stringify(d.A)===JSON.stringify(end.A);
 for(let x=0;x<64;x++)if(predict(d.A,initial,x)!==predict(end.A,end.origin,x))retained=false;
 for(let x of d.held){let y=d.hold(x),values={gated:predict(all,g.mask,x),ungated:predict(all,u.mask,x),fixed:predict(all,fixed.mask,x),bayes:posterior(x),frozen_A:predict(all,initial,x),shuffled_B:predict(negRows,neg.mask,x),null:.5};
  for(let k of Object.keys(scores))scores[k]+=brier(values[k],y)/16;
  if(values.gated!==predict(cold.B,cold.mask,x)||values.gated!==predict(end.B,end.mask,x))equal=false;
 }
 return{scores,gEdits:g.edits,uEdits:u.edits,gChanged:g.mask!==initial,uChanged:u.mask!==initial,matchedStatic:g.mask===fixed.mask,
 restore:equal,retained,disjoint,fitRows:all.length,witness:d.B.filter(x=>x[2]).length,bytes:final.length,work:[g.work,u.work,fixed.ops,masks.length]};
}
const families=[["xor_pair",101000],["mux3",102000],["essential3",103000],["unary",104000],["unrelated3",105000],["independent_noise",106000]],groups={},related=[];
for(let [family,start] of families){
 const trials=Array.from({length:32},(_,i)=>trial(start+i,family));if(start<105000)related.push(...trials);
 const r=x=>Number(x.toFixed(10)),keys=Object.keys(trials[0].scores),means=Object.fromEntries(keys.map(k=>[k,r(trials.reduce((s,v)=>s+v.scores[k],0)/32)]));
 groups[family]={seeds:32,seed_first:start,seed_last:start+31,means,
  gated_ever_edited:trials.filter(x=>x.gEdits>0).length,ungated_ever_edited:trials.filter(x=>x.uEdits>0).length,
  gated_final_changed:trials.filter(x=>x.gChanged).length,ungated_final_changed:trials.filter(x=>x.uChanged).length,
  gated_matches_fit_fixed:trials.filter(x=>x.matchedStatic).length,
  cold_replay:trials.filter(x=>x.restore).length,source_A_retained:trials.filter(x=>x.retained).length,
  held_disjoint:trials.filter(x=>x.disjoint).length,fit96_and_24_sentinel:trials.filter(x=>x.fitRows===96&&x.witness===24).length,
  bytes384:trials.filter(x=>x.bytes===384).length,
  work:{gated:trials.reduce((s,x)=>s+x.work[0],0),ungated:trials.reduce((s,x)=>s+x.work[1],0),fixed:trials.reduce((s,x)=>s+x.work[2],0),bayes:trials.reduce((s,x)=>s+x.work[3],0)},
  gain_vs_fixed:paired(trials.map(x=>x.scores.fixed-x.scores.gated)),
  cost_vs_ungated:paired(trials.map(x=>x.scores.gated-x.scores.ungated)),
  deficit_to_bayes:paired(trials.map(x=>x.scores.gated-x.scores.bayes))};
}
const pooledCost=paired(related.map(x=>x.scores.gated-x.scores.ungated)),pooledFixed=paired(related.map(x=>x.scores.fixed-x.scores.gated)),pooledA=paired(related.map(x=>x.scores.frozen_A-x.scores.gated));
const noiseGroup=groups.independent_noise,unrelatedGroup=groups.unrelated3;
const worst=Math.max(...["xor_pair","mux3","essential3","unary"].map(k=>groups[k].means.gated-groups[k].means.bayes));
const conditions={
 related_gated_vs_ungated_Brier_cost_max:pooledCost.mean<=.01,
 related_gated_vs_ungated_paired_ci_upper_max:pooledCost.ci95[1]<=.02,
 noise_gated_change_fraction_max:noiseGroup.gated_final_changed/32<=.2,
 noise_ungated_change_fraction_min:noiseGroup.ungated_final_changed/32>=.5,
 noise_gated_Brier_regression_vs_fully_fit_fixed_max:noiseGroup.means.gated-noiseGroup.means.fixed<=.015,
 unrelated_gated_Brier_regression_vs_fully_fit_fixed_max:unrelatedGroup.means.gated-unrelatedGroup.means.fixed<=.02,
 related_gated_gain_vs_fully_fit_fixed_min:pooledFixed.mean>=.01,
 related_gated_gain_vs_fully_fit_fixed_ci_lower_positive:pooledFixed.ci95[0]>0,
 worst_related_gated_deficit_to_bayesian_max:worst<=.015,
 related_gated_gain_vs_frozen_A_min:pooledA.mean>=.025,
 related_gated_retention_source_all:Object.values(groups).every(g=>g.source_A_retained===32),
 cold_checkpoint_replay_all:Object.values(groups).every(g=>g.cold_replay===32),
 all_B_held_disjoint:Object.values(groups).every(g=>g.held_disjoint===32),
 all_saved_state_under_384_bytes:Object.values(groups).every(g=>g.bytes384===32&&g.fit96_and_24_sentinel===32)
};
return{schema:"yggdrasil.gate21.repeat-evidence-gated-local-graph.v1",
prereg_commit:"834c26e40562e52581997b040d6a39d3f947d337",parent_commit:"90515a68cc0ffb00a6063600e9a7c2500c92702b",
design:{seed_trials:192,families:6,A_fit:64,B_fit:96,B_fit_unique:32,B_sentinel_unique:8,B_sentinel_rows:24,B_held:16,B_unused:16,max_persistent_bytes:384},
groups,summary:{related_gated_cost_vs_ungated:pooledCost,related_gated_gain_vs_static:pooledFixed,related_gated_gain_vs_frozen_A:pooledA,
noise_gated_changed:noiseGroup.gated_final_changed,noise_ungated_changed:noiseGroup.ungated_final_changed,worst_related_deficit_to_bayesian:Number(worst.toFixed(10))},
conditions,verdict:Object.values(conditions).every(Boolean)?"STRUCTURAL_DEV_GAIN_ONLY":"GATED_REWIRING_MIXED_OR_NEGATIVE_DEV",
exclusions:{native_original_first_use:false,independent_scientific_reproduction:false,cross_process_checkpoint:false,computation_equalized:false,accepted_cumulative_learner:false,deployment:false}};
};
if(typeof module!=="undefined"&&require.main===module){
 const fs=require("fs"),got=run();
 if(process.argv.includes("--verify")){
  const i=process.argv.indexOf("--verify"),want=JSON.parse(fs.readFileSync(process.argv[i+1],"utf8"));
  if(JSON.stringify(want)!==JSON.stringify(got))throw Error("GATE21_EXACT_REPLAY_MISMATCH");
  process.stdout.write("GATE21_EXACT_REPLAY_PASS "+got.verdict+"\n");
 }else process.stdout.write(JSON.stringify(got,null,2)+"\n");
}
