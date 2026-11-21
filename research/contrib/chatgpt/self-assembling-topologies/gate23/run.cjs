"use strict";
// Gate23 prospective synthetic falsification. Prereg committed 61e43959294aa9122f64cfcb595f09dbf2e6225f.
const run = function gate23(){
"use strict";
const must=(v,msg)=>{if(!v)throw Error("G23_INVARIANT_"+msg);};
const pop=m=>{let n=0;for(;m;m>>>=1)n+=m&1;return n;};
const ix=(x,m)=>{let n=0;for(let b=0;b<6;b++)if(m&(1<<b))n=(n<<1)|((x>>b)&1);return n;};
const masks=Array.from({length:63},(_,i)=>i+1).filter(m=>pop(m)<=3);
const mix=x=>{x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;return(x^(x>>>16))>>>0;};
const rand=seed=>{let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};};
const shuffle=(a,r)=>{let v=a.slice();for(let i=v.length-1;i>0;i--){let j=r()%(i+1);[v[i],v[j]]=[v[j],v[i]];}return v;};
const hash=(seed,ctx,x,visit,dom)=>mix(mix(seed^Math.imul(ctx+1,0x9e3779b1)^Math.imul(dom+1,0x85ebca6b))^Math.imul(x+1,0xc2b2ae35)^Math.imul(visit+1,0x27d4eb2f));
const clip=x=>Math.max(.05,Math.min(.95,x)),loss=(p,y)=>(p-y)*(p-y);
const essential=t=>[0,1,2].every(j=>Array.from({length:8},(_,i)=>i).some(i=>((t>>>i)&1)!==((t>>>(i^(1<<j)))&1)));
function truth(f,r){
 if(f==="pair_xor")return 0b0110;
 if(f==="unary")return 0b10;
 if(f==="mux3"){let out=0;for(let v=0;v<8;v++)out|=((v&4?(v&1):((v>>>1)&1))<<v);return out;}
 let t;do{t=r()&255;}while(!essential(t));return t;
}
function world(seed,family){
 const rA=rand(mix(seed^0x1b37e950)),rB=rand(mix(seed^0x5621ca79)),k=family==="noise_fair"?0:family==="unary"?1:family==="pair_xor"?2:3;
 const parentsA=k?shuffle([0,1,2,3,4,5],rA).slice(0,k):[],table=k?truth(family,rA):0;
 let parentsB=[],count=0;
 if(family==="stationary3")parentsB=parentsA.slice();else if(k)do{parentsB=shuffle([0,1,2,3,4,5],rB).slice(0,k);must(++count<256,"distinct_parent_remap");}
 while(parentsB.slice().sort().join(",")===parentsA.slice().sort().join(","));
 const a={parents:parentsA,table},b={parents:parentsB,table};
 function label(w,phase,x,dom){const z=hash(seed,phase,x,0,dom);if(!k)return z&1;let t=0;for(const bit of w.parents)t=(t<<1)|((x>>>bit)&1);return ((w.table>>>t)&1)^(z%20===0?1:0);}
 const ids=Array.from({length:64},(_,i)=>i);
 const A=shuffle(ids,rand(mix(seed^0x95ddc184))).map(x=>[x,label(a,0,x,1901)]),
  bs=shuffle(ids,rand(mix(seed^0xa06b3fa7))),rs=shuffle(ids,rand(mix(seed^0x4bd159ee)));
 const B=bs.slice(0,48).map(x=>[x,label(b,1,x,1902)]),R=rs.slice(0,48).map(x=>[x,label(a,2,x,1903)]);
 const BH=bs.slice(48).map(x=>[x,label(b,1,x,1908)]),RH=rs.slice(48).map(x=>[x,label(a,2,x,1909)]);
 must(A.length===64&&B.length===48&&R.length===48&&BH.length===16&&RH.length===16,"sizes");
 must(new Set(bs).size===64&&new Set(rs).size===64,"unique_split");
 return{A,B,R,BH,RH};
}
function count(rows,m){const n=new Uint16Array(1<<pop(m)),one=new Uint16Array(n.length);for(const [x,y]of rows){const j=ix(x,m);n[j]++;one[j]+=y;}return{n,one};}
function predict(rows,m,x){
 if(!rows.length)return .5;
 const c=count(rows,m),i=ix(x,m);return clip((c.one[i]+1)/(c.n[i]+2));
}
function loo(rows,m){
 if(!rows.length)return Infinity;
 const c=count(rows,m);let s=0;for(const [x,y]of rows){const i=ix(x,m);s+=loss(clip((c.one[i]-y+1)/(c.n[i]+1)),y);}return s/rows.length;
}
function sourceFit(rows){
 let mask=1,best=Infinity,work=0;
 for(let m of masks){const risk=loo(rows,m)+.003*(1<<pop(m));work++;if(risk<best-1e-12){best=risk;mask=m;}}
 return{mask,risk:loo(rows,mask),work};
}
// Comparator's exhaustive selector is independently coded, not an adaptive function call.
function fittedStatic(rows){
 if(!rows.length)return {mask:1,work:0};
 let selected=1,score=Infinity,work=0;
 for(let m=1;m<64;m++){
  let k=0;for(let j=0;j<6;j++)k+=(m>>>j)&1;if(k>3)continue;
  const bins=Array.from({length:1<<k},()=>({n:0,y:0})),keys=[];
  for(const [x,y]of rows){let z=0;for(let j=0;j<6;j++)if(m&(1<<j))z=(z<<1)|((x>>>j)&1);keys.push(z);bins[z].n++;bins[z].y+=y;}
  let sum=0;for(let i=0;i<rows.length;i++){const b=bins[keys[i]],y=rows[i][1],p=Math.max(.05,Math.min(.95,(b.y-y+1)/(b.n+1)));sum+=(p-y)**2;}
  const fit=sum/rows.length+.003*(1<<k);work++;if(fit<score-1e-12){score=fit;selected=m;}
 }
 return{mask:selected,work};
}
const lf=[0];for(let i=1;i<=160;i++)lf[i]=lf[i-1]+Math.log(i);
function bayes(rows){
 if(!rows.length)return x=>.5;
 const opts=[],number={1:6,2:15,3:20};
 for(const m of masks){const c=count(rows,m);let log=-Math.log(3*number[pop(m)]);
  for(let i=0;i<c.n.length;i++)log+=lf[c.one[i]]+lf[c.n[i]-c.one[i]]-lf[c.n[i]+1];
  opts.push({mask:m,c,log});}
 const mx=Math.max(...opts.map(z=>z.log));let denom=0;
 for(const z of opts){z.w=Math.exp(z.log-mx);denom+=z.w;}
 return x=>opts.reduce((s,z)=>{const i=ix(x,z.mask);return s+z.w*clip((z.c.one[i]+1)/(z.c.n[i]+2));},0)/denom;
}
function init(A){
 const src=sourceFit(A),t={A:A.map(r=>r.slice()),stream:[],source:src.mask,alt:src.mask,
  reliable:src.risk<=.20,mode:0,cooldown:0,switches:0,everAlt:0,everReturn:0,evidence:[],work:src.work};
 return t;
}
function stored(t){
 must(t.A.length===64&&t.stream.length<=96&&t.work<65536,"persist_dimensions");
 const bytes=new Uint8Array(384);
 t.A.forEach(([x,y],i)=>{must(x<64&&y<2,"A");bytes[2*i]=x;bytes[2*i+1]=y;});
 t.stream.forEach(([x,y],i)=>{must(x<64&&y<2,"stream");bytes[128+2*i]=x;bytes[129+2*i]=y;});
 const meta=[t.stream.length,t.source,t.alt,t.reliable?1:0,t.mode,t.cooldown,t.switches,t.everAlt,t.everReturn,t.evidence.length,t.work&255,t.work>>>8];
 meta.forEach((x,i)=>{must(x>=0&&x<=255,"meta");bytes[320+i]=x;});
 t.evidence.forEach((n,i)=>{must(n>=-32768&&n<=32767,"evidence");bytes[332+i*2]=n&255;bytes[333+i*2]=(n>>8)&255;});
 return bytes;
}
function recover(bytes){
 must(bytes instanceof Uint8Array&&bytes.length===384&&bytes.slice(364).every(x=>x===0),"packed_length");
 const n=bytes[320],A=[],stream=[],evlen=bytes[329];must(n<=96&&evlen<=16,"counts");
 for(let i=0;i<64;i++){const x=bytes[2*i],y=bytes[2*i+1];must(x<64&&y<=1,"A_decode");A.push([x,y]);}
 for(let i=0;i<96;i++){const x=bytes[128+2*i],y=bytes[129+2*i];if(i<n){must(x<64&&y<=1,"stream_decode");stream.push([x,y]);}else must(!x&&!y,"padding");}
 const evidence=[];for(let i=0;i<16;i++){let n=bytes[332+i*2]|(bytes[333+i*2]<<8);if(n&32768)n-=65536;if(i<evlen)evidence.push(n);else must(n===0,"evidence_padding");}
 const t={A,stream,source:bytes[321],alt:bytes[322],reliable:!!bytes[323],mode:bytes[324],cooldown:bytes[325],
 switches:bytes[326],everAlt:bytes[327],everReturn:bytes[328],evidence,work:bytes[330]+bytes[331]*256};
 must(t.mode<=1&&t.source>0&&pop(t.source)<=3&&t.alt>0&&pop(t.alt)<=3,"decoded_topology");
 return t;
}
function model(t,x){
 if(!t.reliable)return .5;
 return t.mode===0?predict(t.A,t.source,x):predict(t.stream.slice(-32),t.alt,x);
}
function observe(t,row){
 const [x,y]=row,n=t.stream.length,src=predict(t.A,t.source,x),past=t.stream.slice(-32),alt=n>=8?predict(past,t.alt,x):src;
 // Quantized prequential log-likelihood evidence, deterministic before this label enters training.
 const ps=y?src:1-src,pb=y?alt:1-alt;
 const delta=Math.round(Math.log(pb/ps)*256);
 t.evidence.push(delta);if(t.evidence.length>16)t.evidence.shift();
 t.stream.push(row.slice());
 if(t.stream.length%8===0){
  const fit=fittedStatic(t.stream.slice(-32));t.alt=fit.mask;t.work+=fit.work;
  if(t.cooldown>0)t.cooldown--;
  else if(t.reliable&&t.stream.length>=16){
   const total=t.evidence.reduce((a,b)=>a+b,0);
   if(t.mode===0&&total>=768){t.mode=1;t.switches++;t.cooldown=1;t.everAlt=1;}
   else if(t.mode===1&&total<=-768){t.mode=0;t.switches++;t.cooldown=1;t.everReturn=1;}
  }
 }
}
function comparator(A){
 const start=sourceFit(A);
 return{A:A.map(x=>x.slice()),stream:[],source:start.mask,rolling:start.mask,growing:start.mask,
  bayesWeight:.05,rollingWork:0,growingWork:0,likelihoods:0};
}
function controls(c,x){
 const recent=c.stream.slice(-32),all=c.A.concat(c.stream),source=predict(c.A,c.source,x);
 const sliding=c.stream.length>=8?predict(recent,c.rolling,x):source,
 growing=predict(all,c.growing,x),shortBayes=bayes(recent)(x);
 return{frozen:source,rolling:sliding,growing,bayesian:(1-c.bayesWeight)*source+c.bayesWeight*shortBayes,null:.5};
}
function controlUpdate(c,row){
 const [x,y]=row,ref=controls(c,x),recent=bayes(c.stream.slice(-32))(x),prior=ref.frozen;
 const w=1/64+(1-2/64)*c.bayesWeight,lk1=y?recent:1-recent,lk0=y?prior:1-prior;
 const denom=w*lk1+(1-w)*lk0;c.bayesWeight=denom>0?w*lk1/denom:.5;c.likelihoods++;
 c.stream.push(row.slice());
 if(c.stream.length%8===0){
  const rs=fittedStatic(c.stream.slice(-32)),gs=fittedStatic(c.A.concat(c.stream));
  c.rolling=rs.mask;c.growing=gs.mask;c.rollingWork+=rs.work;c.growingWork+=gs.work;
 }
}
function ci(vals){const n=vals.length,mean=vals.reduce((a,b)=>a+b,0)/n,variance=vals.reduce((a,b)=>a+(b-mean)**2,0)/(n-1),w=1.96*Math.sqrt(variance/n),r=x=>Number(x.toFixed(10));return{mean:r(mean),ci95:[r(mean-w),r(mean+w)]};}
function trial(seed,f){
 const d=world(seed,f),t=init(d.A),c=comparator(d.A);
 const arms=["detector","frozen","rolling","growing","bayesian","null"];
 const held={B:Object.fromEntries(arms.map(k=>[k,0])),R:Object.fromEntries(arms.map(k=>[k,0]))},
       pre={B:Object.fromEntries(arms.map(k=>[k,0])),R:Object.fromEntries(arms.map(k=>[k,0]))};
 const same=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
 let replica48=null,replica72=null,cold=true,sourceImmutable=true,heldClean=true;
 for(let j=0;j<96;j++){
  const [x,y]=(j<48?d.B[j]:d.R[j-48]),phase=j<48?"B":"R";
  const preds={detector:model(t,x),...controls(c,x)};
  for(const name of arms)pre[phase][name]+=loss(preds[name],y)/48;
  observe(t,[x,y]);controlUpdate(c,[x,y]);
  if(replica48&&j>=48){observe(replica48,[x,y]);cold=cold&&same(Array.from(stored(t)),Array.from(stored(replica48)));}
  if(replica72&&j>=72){observe(replica72,[x,y]);cold=cold&&same(Array.from(stored(t)),Array.from(stored(replica72)));}
  if(j===47){const bytes=stored(t);replica48=recover(new Uint8Array(bytes));cold=cold&&same(Array.from(bytes),Array.from(stored(replica48)));}
  if(j===71){const bytes=stored(t);replica72=recover(new Uint8Array(bytes));cold=cold&&same(Array.from(bytes),Array.from(stored(replica72)));}
  if(j===47||j===95){
   const evalRows=phase==="B"?d.BH:d.RH,train=phase==="B"?d.B:d.R;
   const trainIds=new Set(train.map(z=>z[0]));if(evalRows.some(([id])=>trainIds.has(id)))heldClean=false;
   for(const [id,yHeld]of evalRows){
    const pp={detector:model(t,id),...controls(c,id)};
    for(const name of arms)held[phase][name]+=loss(pp[name],yHeld)/16;
    if(j===95&&replica48&&model(replica48,id)!==pp.detector)cold=false;
    if(j===95&&replica72&&model(replica72,id)!==pp.detector)cold=false;
   }
  }
 }
 const final=recover(new Uint8Array(stored(t)));cold=cold&&same(Array.from(stored(t)),Array.from(stored(final)));
 for(let x=0;x<64;x++){if(predict(t.A,t.source,x)!==predict(d.A,t.source,x))sourceImmutable=false;if(model(final,x)!==model(t,x))cold=false;}
 return{held,pre,entered:t.everAlt,returned:t.everAlt&&t.everReturn&&t.mode===0,switches:t.switches,sourceReliable:t.reliable,
 cold,sourceImmutable,heldClean,work:{detector:t.work,rolling:c.rollingWork,growing:c.growingWork,bayesianMasks:41*96,evidenceOps:96}};
}
const designs=[["pair_xor",141000],["mux3",142000],["essential3",143000],["unary",144000],["stationary3",145000],["noise_fair",146000]],groups={},related=[];
for(const [name,seed]of designs){
 const runs=Array.from({length:32},(_,i)=>trial(seed+i,name));if(seed<145000)related.push(...runs);
 const keys=Object.keys(runs[0].held.B),r=v=>Number(v.toFixed(10));
 const mean=path=>r(runs.reduce((s,x)=>s+path(x),0)/32);
 const means=(section,phase)=>Object.fromEntries(keys.map(k=>[k,mean(x=>x[section][phase][k])]));
 groups[name]={seeds:32,seed_first:seed,seed_last:seed+31,held_B:means("held","B"),held_R:means("held","R"),prequential_B:means("pre","B"),prequential_R:means("pre","R"),
  false_switch_trials:runs.filter(x=>x.switches>0).length,
  source_reliable:runs.filter(x=>x.sourceReliable).length,
  returned_to_source:runs.filter(x=>x.returned).length,
  entered_alternate:runs.filter(x=>x.entered).length,
  cold_exact:runs.filter(x=>x.cold).length,
  source_immutable:runs.filter(x=>x.sourceImmutable).length,
  held_disjoint:runs.filter(x=>x.heldClean).length,
  mean_work:Object.fromEntries(Object.keys(runs[0].work).map(k=>[k,mean(x=>x.work[k])]))};
}
const delta=(a,b,phase,section="held")=>ci(related.map(t=>t[section][phase][a]-t[section][phase][b]));
const B_Roll=delta("detector","rolling","B"),B_Bayes=delta("detector","bayesian","B"),
 RB=delta("rolling","detector","R"),RBayes=delta("bayesian","detector","R"),
 preB=delta("detector","rolling","B","pre");
const g=groups,stationary=g.stationary3,noise=g.noise_fair;
const conditions={
 noise_false_switch_trial_fraction_max:noise.false_switch_trials/32<=.2,
 stationary_false_switch_trial_fraction_max:stationary.false_switch_trials/32<=.2,
 related_B_mean_regression_vs_rolling_max:B_Roll.mean<=.025,
 related_B_mean_regression_vs_bayes_max:B_Bayes.mean<=.03,
 related_R_gain_vs_rolling_min:RB.mean>=.01,
 related_R_gain_vs_rolling_ci_lower_positive:RB.ci95[0]>0,
 related_R_gain_vs_bayes_min:RBayes.mean>=.005,
 related_R_gain_vs_bayes_ci_lower_positive:RBayes.ci95[0]>0,
 related_return_reactivation_fraction_min:related.filter(t=>t.returned).length/128>=.75,
 related_prequential_B_regression_vs_rolling_max:preB.mean<=.035,
 noise_held_Brier_regression_vs_null_max:Math.max(noise.held_B.detector-noise.held_B.null,noise.held_R.detector-noise.held_R.null)<=.025,
 stationary_held_Brier_regression_vs_rolling_max:Math.max(stationary.held_B.detector-stationary.held_B.rolling,stationary.held_R.detector-stationary.held_R.rolling)<=.025,
 all_held_phase_disjoint:Object.values(g).every(t=>t.held_disjoint===32),
 all_source_A_immutable:Object.values(g).every(t=>t.source_immutable===32),
 all_384byte_continuations_exact:Object.values(g).every(t=>t.cold_exact===32),
 eligible_comparator_work_accounted:Object.values(g).every(t=>t.mean_work.detector>0&&t.mean_work.rolling>0&&t.mean_work.growing>0&&t.mean_work.bayesianMasks===3936)
};
const yes=Object.values(conditions).every(Boolean);
return{schema:"yggdrasil.gate23.source-reliability-sequential-20261120.v1",prereg_commit:"61e43959294aa9122f64cfcb595f09dbf2e6225f",parent_commit:"7f177f61508d8eeb37458c5c38f117cadf1e4271",
 design:{trials:192,source_A:64,B_train:48,R_train:48,B_held:16,R_held:16,state_bytes:384,first_use:"source_committed_before_primary_score"},
 groups,summary:{B_loss_vs_rolling:B_Roll,B_loss_vs_bayesian:B_Bayes,R_gain_vs_rolling:RB,R_gain_vs_bayesian:RBayes,prequential_B_loss_vs_rolling:preB,
 related_returned_to_source:related.filter(t=>t.returned).length,noise_false_switch:noise.false_switch_trials,stationary_false_switch:stationary.false_switch_trials},
 conditions,verdict:yes?"SYNTHETIC_DEVELOPMENT_SIGNAL_ONLY":"SOURCE_RELIABILITY_CHANGEPOINT_SCIENTIFIC_NO_GO",
 exclusions:{native_first_use:false,actual_causal_generalization:false,independent_replication:false,process_exit_retention:false,compute_equalized:false,canonical_learner:false,accepted_science:false}};
};
if(typeof module !== "undefined" && require.main===module){
 const fs=require("fs"),actual=run();
 if(process.argv.includes("--verify")){
  const at=process.argv.indexOf("--verify"),expected=JSON.parse(fs.readFileSync(process.argv[at+1],"utf8"));
  if(JSON.stringify(expected)!==JSON.stringify(actual))throw Error("GATE23_EXACT_REPLAY_MISMATCH");
  console.log("GATE23_EXACT_REPLAY_PASS "+actual.verdict);
 }else console.log(JSON.stringify(actual,null,2));
}
