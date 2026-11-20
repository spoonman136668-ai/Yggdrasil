"use strict";
// Gate16: preregistered third-order interaction synthesis (synthetic contributor only).
// Frozen protocol: 860487bed0498cc22dc26f93b4b7ed157c799163.
// No native learner/checkpoint, first-use, runner, scheduler or controller touched.
const ok=(v,msg)=>{if(!v)throw Error("G16 "+msg);};
function pc(x){let n=0;for(;x;x>>>=1)n+=x&1;return n;}
const M={unary:[],pair:[],triple:[]};
for(let x=1;x<32;x++){const n=pc(x);if(n===1)M.unary.push(x);if(n===2)M.pair.push(x);if(n===3)M.triple.push(x);}
const LOW=M.unary.concat(M.pair).sort((a,b)=>a-b),ALL=LOW.concat(M.triple).sort((a,b)=>a-b);
const COMPOSE=[...new Set(M.unary.flatMap(u=>M.pair.filter(p=>(u&p)===0).map(p=>u|p)))].sort((a,b)=>a-b);
ok(LOW.length===15&&ALL.length===25&&COMPOSE.length===10&&COMPOSE.every((v,i)=>v===M.triple[i]),"Walsh feature basis");
const rng=seed=>{let a=seed>>>0;return()=>{a^=a<<13;a^=a>>>17;a^=a<<5;return a>>>0;}};
function mix(x){x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;return (x^(x>>>16))>>>0;}
function eventHash(seed,c,x,v,d){
 let z=mix(seed^Math.imul(c+1,0x9e3779b1)^Math.imul(d+1,0x85ebca6b));
 z=mix(z^Math.imul(x+1,0xc2b2ae35));return mix(z^Math.imul(v+1,0x27d4eb2f));
}
const phi=(x,m)=>pc(x&m)%2?-1:1,clamp=p=>Math.max(.05,Math.min(.95,p)),sq=(p,y)=>(p-y)**2;
function correlation(obs,m){let z=0;for(const [x,y]of obs)z+=(2*y-1)*phi(x,m);return z/obs.length;}
function nullProbability(obs){let z=1;for(const [,y]of obs)z+=y;return clamp(z/(obs.length+2));}
const predictFeature=(rho,x,m)=>clamp(.5+.5*rho*phi(x,m));
function select(obs,arm){
 ok(obs.length===96,"fit length");
 if(arm==="flat"||arm==="null")return {route:0,negative:0,work:0,expanded:false};
 const f=obs.slice(0,64),val=obs.slice(64),initial=arm==="fixed_full"?ALL:LOW;
 let winner=0,coef=0,best=0,work=0;
 for(const mask of initial){const r=correlation(f,mask);work+=64;if(Math.abs(r)>best+1e-12){winner=mask;coef=r;best=Math.abs(r);}}
 const expanded=arm==="expanded_dynamic"&&best<.70;
 if(expanded)for(const mask of COMPOSE){const r=correlation(f,mask);work+=64;if(Math.abs(r)>best+1e-12){winner=mask;coef=r;best=Math.abs(r);}}
 let installed=false;
 if(winner!==0&&best>=.70){
  const n=nullProbability(f);let loss0=0,loss1=0;
  for(const [x,y]of val){loss0+=sq(n,y);loss1+=sq(predictFeature(coef,x,winner),y);}
  loss0/=32;loss1/=32;work+=64;
  installed=loss0-loss1>=.10&&loss1<=.15;
 }
 return {route:installed?winner:0,negative:installed&&coef<0?1:0,work,expanded};
}
class Compact{
 constructor(arm){this.arm=arm;this.c=[0,1].map(()=>({obs:[],route:0,negative:0,work:0,expanded:false,ready:false}));}
 train(ctx,obs){ok(!this.c[ctx].ready&&obs.length===96,"train once");
  const c=this.c[ctx];c.obs=obs.map(([x,y])=>{ok(x>=0&&x<32&&(y===0||y===1),"fit data");return [x,y]});
  const s=select(c.obs,this.arm);c.route=s.route;c.negative=s.negative;c.work=s.work;c.expanded=s.expanded;c.ready=true;
 }
 predict(ctx,x){
  const c=this.c[ctx];ok(c.ready&&x>=0&&x<32,"held prediction");
  if(this.arm==="null"||(c.route===0&&this.arm!=="flat"))return nullProbability(c.obs);
  if(this.arm==="flat"){let yes=1,n=2;for(const [xx,y]of c.obs)if(xx===x){yes+=y;n++;}return clamp(yes/n);}
  return predictFeature(correlation(c.obs,c.route),x,c.route);
 }
 pack(){
  const b=new Uint8Array(388);
  for(let k=0;k<2;k++){const c=this.c[k],off=k*194;ok(c.ready&&c.obs.length===96,"complete state");
   for(let i=0;i<96;i++){b[off+i*2]=c.obs[i][0];b[off+i*2+1]=c.obs[i][1];}
   b[off+192]=c.route;b[off+193]=c.negative;
  }return b;
 }
 static fromBytes(b,arm){
  ok(b instanceof Uint8Array&&b.length===388,"packed bytes");
  const a=new Compact(arm);
  for(let k=0;k<2;k++){const c=a.c[k],off=k*194;
   for(let i=0;i<96;i++){const x=b[off+2*i],y=b[off+2*i+1];ok(x<32&&y<=1,"packed example");c.obs.push([x,y]);}
   c.route=b[off+192];c.negative=b[off+193];c.ready=true;
   ok(c.route===0||ALL.includes(c.route),"packed route");ok(c.negative<=1,"packed sign");
   if(arm==="truncated")ok(c.route===0||LOW.includes(c.route),"truncated mask");
  }return a;
 }
}
class Bayes{
 constructor(){
  this.h=[{mask:0,sign:0,p:.5,prior:.5}];
  for(const mask of ALL)for(let sign=0;sign<2;sign++)this.h.push({mask,sign,prior:.01});
  ok(this.h.length===51,"reference candidates");
  this.z=[0,1].map(()=>Float64Array.from(this.h,h=>Math.log(h.prior)));
 }
 likelihood(h,x){if(!h.mask)return .5;return (pc(x&h.mask)%2)===h.sign?.05:.95;}
 train(ctx,obs){for(const [x,y]of obs)for(let i=0;i<51;i++){const p=this.likelihood(this.h[i],x);this.z[ctx][i]+=Math.log(y?p:1-p);}}
 predict(ctx,x){const z=this.z[ctx],peak=Math.max(...z);let mass=0,sum=0;
  for(let i=0;i<51;i++){const w=Math.exp(z[i]-peak);mass+=w;sum+=w*this.likelihood(this.h[i],x);}
  ok(mass>0&&Number.isFinite(mass),"Bayes stable");return sum/mass;
 }
}
function sourceWorld(seed,ctx,family){
 const r=rng(mix(seed^Math.imul(ctx+1,309781))),inv=r()&1;
 const options=family==="triple_parity"||family==="majority3"?M.triple:family==="pair_parity"?M.pair:family==="unary"?M.unary:[0];
 return {family,mask:options[r()%options.length],inv};
}
function observe(w,seed,ctx,x,visit,domain){
 const h=eventHash(seed,ctx,x,visit,domain);
 if(w.family==="independent_random")return h&1;
 const raw=w.family==="majority3"?(pc(x&w.mask)>=2?1:0):(pc(x&w.mask)%2);
 return (raw^w.inv)^(h%20===0?1:0);
}
const ARMS=["expanded_dynamic","fixed_full","truncated","flat","null"];
function trial(seed,family){
 const worlds=[sourceWorld(seed,0,family),sourceWorld(seed,1,family)];
 const arms=ARMS.map(x=>new Compact(x)),bayes=new Bayes();
 for(let k=0;k<2;k++){
  const r=rng(mix(seed^Math.imul(k+1,582941))),visits=new Uint8Array(32),obs=[];
  for(let n=0;n<96;n++){const x=r()&31,y=observe(worlds[k],seed,k,x,visits[x]++,10101);obs.push([x,y]);}
  for(const a of arms)a.train(k,obs);
  bayes.train(k,obs);
 }
 const copies=arms.map(a=>Compact.fromBytes(a.pack(),a.arm));
 let restore=true,exactTriple=0,falseInstalled=0,expanded=0;
 const work=Object.fromEntries(ARMS.map((name,i)=>[name,arms[i].c.reduce((a,c)=>a+c.work,0)]));
 for(let k=0;k<2;k++){const c=arms[0].c[k],mask=c.route;
  if(family==="triple_parity"&&mask===worlds[k].mask)exactTriple++;
  if(["independent_random","majority3"].includes(family)&&mask!==0)falseInstalled++;
  if(c.expanded)expanded++;
 }
 const scores=Object.fromEntries([...ARMS,"bayes"].map(x=>[x,0]));
 for(let k=0;k<2;k++)for(let x=0;x<32;x++){
  const y=observe(worlds[k],seed,k,x,0,30303);
  for(let i=0;i<arms.length;i++){
   const p=arms[i].predict(k,x);scores[ARMS[i]]+=sq(p,y);
   if(p!==copies[i].predict(k,x))restore=false;
  }scores.bayes+=sq(bayes.predict(k,x),y);
 }
 for(const key of Object.keys(scores))scores[key]/=64;
 return {scores,restore,exactTriple,falseInstalled,expanded,work,exactFixedTie:scores.expanded_dynamic===scores.fixed_full};
}
const round=v=>Number(v.toFixed(10));
function ci(xs){const n=xs.length,m=xs.reduce((a,x)=>a+x,0)/n,variance=xs.reduce((a,x)=>a+(x-m)**2,0)/(n-1),h=1.96*Math.sqrt(variance/n);
 return {mean:round(m),ci95:[round(m-h),round(m+h)]};}
function cohort(family,seed,n){
 const a=Array.from({length:n},(_,i)=>trial(seed+i,family));
 const score=Object.fromEntries([...ARMS,"bayes"].map(k=>[k,round(a.reduce((s,x)=>s+x.scores[k],0)/n)]));
 return {family,first_seed:seed,last_seed:seed+n-1,seeds:n,worlds:n*2,scores:score,
  triple_parent_recovered:a.reduce((s,x)=>s+x.exactTriple,0),
  false_parity_routes:a.reduce((s,x)=>s+x.falseInstalled,0),
  high_order_candidate_expansions:a.reduce((s,x)=>s+x.expanded,0),
  cold_prediction_passes:a.filter(x=>x.restore).length,
  exact_fixed_tie_seeds:a.filter(x=>x.exactFixedTie).length,
  gain_over_truncated:ci(a.map(x=>x.scores.truncated-x.scores.expanded_dynamic)),
  gain_over_fixed:ci(a.map(x=>x.scores.fixed_full-x.scores.expanded_dynamic)),
  feature_fit_comparisons:Object.fromEntries(ARMS.map(k=>[k,a.reduce((s,x)=>s+x.work[k],0)]))};
}
function run(){
 const triple=cohort("triple_parity",51000,64),pair=cohort("pair_parity",52000,32),
  unary=cohort("unary",53000,32),random=cohort("independent_random",54000,32),
  majority=cohort("majority3",55000,32);
 const families={triple,pair,unary,random,majority},groups=Object.values(families);
 const gates={
  triple_recovery_min_116:triple.triple_parent_recovered>=116,
  triple_brier_gain_vs_truncated_min_0_10:triple.gain_over_truncated.mean>=.10,
  triple_gain_CI_lower_positive:triple.gain_over_truncated.ci95[0]>0,
  structural_gain_vs_fixed_min_0_015:triple.gain_over_fixed.mean>=.015,
  structural_gain_fixed_CI_lower_positive:triple.gain_over_fixed.ci95[0]>0,
  structural_work_no_greater_than_fixed:triple.feature_fit_comparisons.expanded_dynamic<=triple.feature_fit_comparisons.fixed_full,
  pair_regression_max_0_015:pair.scores.expanded_dynamic-pair.scores.truncated<=.015,
  unary_regression_max_0_015:unary.scores.expanded_dynamic-unary.scores.truncated<=.015,
  random_brier_max_0_270:random.scores.expanded_dynamic<=.270,
  random_false_routes_max_6:random.false_parity_routes<=6,
  majority_brier_max_0_270:majority.scores.expanded_dynamic<=.270,
  majority_false_routes_max_6:majority.false_parity_routes<=6,
  cold_388_byte_all:groups.every(x=>x.cold_prediction_passes===x.seeds),
  fixed_exact_tie:groups.every(x=>x.exact_fixed_tie_seeds===x.seeds)
 };
 const safe=gates.pair_regression_max_0_015&&gates.unary_regression_max_0_015&&gates.random_brier_max_0_270&&gates.random_false_routes_max_6&&gates.majority_brier_max_0_270&&gates.majority_false_routes_max_6&&gates.cold_388_byte_all;
 const expressive=gates.triple_recovery_min_116&&gates.triple_brier_gain_vs_truncated_min_0_10&&gates.triple_gain_CI_lower_positive&&safe;
 const structural=expressive&&gates.structural_gain_vs_fixed_min_0_015&&gates.structural_gain_fixed_CI_lower_positive&&gates.structural_work_no_greater_than_fixed;
 return {schema:"yggdrasil.gate16.synthetic-walsh-interaction-results.v1",prereg_commit:"860487bed0498cc22dc26f93b4b7ed157c799163",
  predecessor_sha:"2271e6d641da350b3b10729fd52c49a9af0118a7",
  design:{binary_controls:5,training_per_world:96,held_per_world:32,contexts_per_seed:2,
   small_packed_bytes:388,unmatched_bayes_posterior_bytes:816,
   hypothesis_class:"1/2/3-bit XOR/Walsh characters ONLY"},
  families,gates,expressivity_development_signal:expressive,structural_superiority:structural,
  verdict:structural?"STRUCTURAL_DEV_SIGNAL_ONLY":expressive?"REPRESENTATIONAL_GAIN_ONLY_NOT_STRUCTURAL":"SCIENTIFIC_NEGATIVE_OR_MIXED_DEV",
  exclusions:{native_first_use:false,native_checkpoint_test:false,scientific_qualification:false,real_runtime_memory_cost:false}};
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 const fs=require("fs"),v=run();
 if(process.argv.includes("--verify")){const path=process.argv[process.argv.indexOf("--verify")+1];ok(path,"missing --verify target");
  const sealed=JSON.parse(fs.readFileSync(path,"utf8"));ok(JSON.stringify(sealed)===JSON.stringify(v),"exact result mismatch");
  process.stdout.write("GATE16_EXACT_REPLAY_PASS "+v.verdict+"\n");
 }else process.stdout.write(JSON.stringify(v,null,2)+"\n");
}
