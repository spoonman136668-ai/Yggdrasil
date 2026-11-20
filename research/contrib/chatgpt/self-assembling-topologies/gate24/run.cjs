"use strict";
// Gate24 source frozen before primary scoring. Prereg committed in e966549d2e689842ea0dafcf4ebd03bce2d778eb.
const run = function gate24(){
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

// Gate24 local-versus-global soft causal evidence bridge, seeded separately.
function softStart(A,kind){
 const src=sourceFit(A);
 return{A:A.map(r=>r.slice()),stream:[],source:src.mask,mask:src.mask,reliable:src.risk<=.20,kind,
 evidence:[],edits:0,work:0};
}
function softForecast(t,x){
 if(!t.reliable)return .5;
 const pa=predict(t.A,t.source,x);
 if(t.stream.length<8)return pa;
 const pb=predict(t.stream.slice(-32),t.mask,x);
 const score=t.evidence.reduce((a,b)=>a+b,0)/32;
 const w=1/(1+Math.exp(-score));
 return clip((1-w)*pa+w*pb);
}
function softNeighbors(mask){
 const neighbors=new Set(),k=pop(mask);
 for(let i=0;i<6;i++){
  if(mask&(1<<i)){
   if(k>1)neighbors.add(mask^(1<<i));
   for(let j=0;j<6;j++)if(!(mask&(1<<j)))neighbors.add((mask^(1<<i))|(1<<j));
  }else if(k<3)neighbors.add(mask|(1<<i));
 }
 return [...neighbors].sort((a,b)=>a-b);
}
function softObserve(t,row){
 const [x,y]=row,pa=predict(t.A,t.source,x);
 const recent=t.stream.slice(-32);
 const pb=t.stream.length>=8?predict(recent,t.mask,x):pa;
 const p0=y?pa:1-pa,p1=y?pb:1-pb;
 const val=Math.max(-127,Math.min(127,Math.round(32*Math.log(p1/p0))));
 t.evidence.push(val);
 if(t.evidence.length>16)t.evidence.shift();
 t.stream.push(row.slice());
 if(t.stream.length%8!==0||!t.reliable)return;
 const fit=t.stream.slice(-32);
 if(t.kind==="global"){
  const next=fittedStatic(fit);t.work+=next.work;
  if(next.mask!==t.mask){t.edits++;t.mask=next.mask;}
 }else{
  const objective=m=>loo(fit,m)+.003*(1<<pop(m));
  const before=objective(t.mask);t.work++;let best=t.mask,cost=before;
  for(const m of softNeighbors(t.mask)){const c=objective(m);t.work++;if(c<cost-1e-12){best=m;cost=c;}}
  if(best!==t.mask&&before-cost>=.006){t.mask=best;t.edits++;}
 }
}
function softPack(t){
 must(t.A.length===64&&t.stream.length<=96&&t.work<65536&&t.evidence.length<=16&&t.edits<256,"soft_capacity");
 const out=new Uint8Array(384);
 t.A.forEach(([x,y],i)=>{must(x<64&&y<2,"softA");out[2*i]=x;out[2*i+1]=y;});
 t.stream.forEach(([x,y],i)=>{must(x<64&&y<2,"softStream");out[128+2*i]=x;out[129+2*i]=y;});
 const meta=[t.stream.length,t.source,t.mask,t.reliable?1:0,t.work&255,t.work>>8,t.edits,t.kind==="global"?2:1,t.evidence.length];
 for(let i=0;i<meta.length;i++){must(meta[i]>=0&&meta[i]<256,"softMeta");out[320+i]=meta[i];}
 t.evidence.forEach((x,i)=>{must(x>=-127&&x<=127,"softEvidence");out[329+i]=x&255;});
 return out;
}
function softRestore(v){
 must(v instanceof Uint8Array&&v.length===384&&v.slice(345).every(x=>x===0),"softFormat");
 const n=v[320],k=v[328],A=[],stream=[],evidence=[];
 must(n<=96&&k<=16&&[1,2].includes(v[327]),"softSizes");
 for(let i=0;i<64;i++){const x=v[2*i],y=v[2*i+1];must(x<64&&y<2,"softSourceRecord");A.push([x,y]);}
 for(let i=0;i<96;i++){const x=v[128+2*i],y=v[129+2*i];if(i<n){must(x<64&&y<2,"softStreamRecord");stream.push([x,y]);}else must(!x&&!y,"softPadding");}
 for(let i=0;i<16;i++){let x=v[329+i];if(x>127)x-=256;if(i<k)evidence.push(x);else must(x===0,"softEvidencePadding");}
 const t={A,stream,source:v[321],mask:v[322],reliable:!!v[323],work:v[324]+(v[325]<<8),edits:v[326],kind:v[327]===2?"global":"local",evidence};
 must(t.source>0&&t.mask>0&&pop(t.source)<=3&&pop(t.mask)<=3,"softMask");
 return t;
}
function trial(seed,f){
 const d=world(seed,f),t=init(d.A),c=comparator(d.A);
 const local=softStart(d.A,"local"),global=softStart(d.A,"global");
 const arms=["detector","local_soft","global_soft","frozen","rolling","growing","bayesian","null"];
 const held={B:Object.fromEntries(arms.map(k=>[k,0])),R:Object.fromEntries(arms.map(k=>[k,0]))},
       pre={B:Object.fromEntries(arms.map(k=>[k,0])),R:Object.fromEntries(arms.map(k=>[k,0]))};
 const same=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
 let replica48=null,replica72=null,cold=true,sourceImmutable=true,heldClean=true;
 let local48=null,local72=null,global48=null,global72=null,softCold=true;
 for(let j=0;j<96;j++){
  const [x,y]=(j<48?d.B[j]:d.R[j-48]),phase=j<48?"B":"R";
  const preds={detector:model(t,x),local_soft:softForecast(local,x),global_soft:softForecast(global,x),...controls(c,x)};
  for(const name of arms)pre[phase][name]+=loss(preds[name],y)/48;
  observe(t,[x,y]);controlUpdate(c,[x,y]);softObserve(local,[x,y]);softObserve(global,[x,y]);
  if(replica48&&j>=48){observe(replica48,[x,y]);cold=cold&&same(Array.from(stored(t)),Array.from(stored(replica48)));}
  if(replica72&&j>=72){observe(replica72,[x,y]);cold=cold&&same(Array.from(stored(t)),Array.from(stored(replica72)));}
  for(const [copy,main]of [[local48,local],[global48,global],[local72,local],[global72,global]]){
   if(copy&&j>=copy.stream.length){softObserve(copy,[x,y]);softCold=softCold&&same(Array.from(softPack(main)),Array.from(softPack(copy)));}
  }
  if(j===47){
   let b=stored(t);replica48=recover(new Uint8Array(b));cold=cold&&same(Array.from(b),Array.from(stored(replica48)));
   let a=softPack(local),g=softPack(global);local48=softRestore(new Uint8Array(a));global48=softRestore(new Uint8Array(g));
   softCold=softCold&&same(Array.from(a),Array.from(softPack(local48)))&&same(Array.from(g),Array.from(softPack(global48)));
  }
  if(j===71){
   let b=stored(t);replica72=recover(new Uint8Array(b));cold=cold&&same(Array.from(b),Array.from(stored(replica72)));
   let a=softPack(local),g=softPack(global);local72=softRestore(new Uint8Array(a));global72=softRestore(new Uint8Array(g));
   softCold=softCold&&same(Array.from(a),Array.from(softPack(local72)))&&same(Array.from(g),Array.from(softPack(global72)));
  }
  if(j===47||j===95){
   const evalRows=phase==="B"?d.BH:d.RH,train=phase==="B"?d.B:d.R;
   const trainIds=new Set(train.map(z=>z[0]));if(evalRows.some(([id])=>trainIds.has(id)))heldClean=false;
   for(const [id,yHeld]of evalRows){
    const pp={detector:model(t,id),local_soft:softForecast(local,id),global_soft:softForecast(global,id),...controls(c,id)};
    for(const name of arms)held[phase][name]+=loss(pp[name],yHeld)/16;
    if(j===95&&replica48&&model(replica48,id)!==pp.detector)cold=false;
    if(j===95&&replica72&&model(replica72,id)!==pp.detector)cold=false;
    if(j===95)for(const [copy,target]of [[local48,pp.local_soft],[local72,pp.local_soft],[global48,pp.global_soft],[global72,pp.global_soft]]){
     if(!copy||softForecast(copy,id)!==target)softCold=false;
    }
   }
  }
 }
 const final=recover(new Uint8Array(stored(t))),softLocal=softRestore(new Uint8Array(softPack(local))),softGlobal=softRestore(new Uint8Array(softPack(global)));
 cold=cold&&same(Array.from(stored(t)),Array.from(stored(final)));
 softCold=softCold&&same(Array.from(softPack(local)),Array.from(softPack(softLocal)))&&same(Array.from(softPack(global)),Array.from(softPack(softGlobal)));
 for(let x=0;x<64;x++){
  if(predict(t.A,t.source,x)!==predict(d.A,t.source,x)||predict(local.A,local.source,x)!==predict(d.A,local.source,x)||predict(global.A,global.source,x)!==predict(d.A,global.source,x))sourceImmutable=false;
  if(model(final,x)!==model(t,x))cold=false;
  if(softForecast(softLocal,x)!==softForecast(local,x)||softForecast(softGlobal,x)!==softForecast(global,x))softCold=false;
 }
 return{held,pre,entered:t.everAlt,returned:t.everAlt&&t.everReturn&&t.mode===0,switches:t.switches,sourceReliable:t.reliable,
 localEdited:local.edits>0,globalEdited:global.edits>0,cold,softCold,sourceImmutable,heldClean,
 work:{detector:t.work,rolling:c.rollingWork,growing:c.growingWork,bayesianMasks:41*96,evidenceOps:96,
 softLocal:local.work,softGlobal:global.work,softEvidenceOps:192}};
}
const designs=[["pair_xor",161000],["mux3",162000],["essential3",163000],["unary",164000],["stationary3",165000],["noise_fair",166000]],groups={},related=[];
for(const [name,seed]of designs){
 const runs=Array.from({length:32},(_,i)=>trial(seed+i,name));if(seed<165000)related.push(...runs);
 const keys=Object.keys(runs[0].held.B),r=v=>Number(v.toFixed(10));
 const mean=path=>r(runs.reduce((s,x)=>s+path(x),0)/32);
 const means=(section,phase)=>Object.fromEntries(keys.map(k=>[k,mean(x=>x[section][phase][k])]));
 groups[name]={seeds:32,seed_first:seed,seed_last:seed+31,
 held_B:means("held","B"),held_R:means("held","R"),prequential_B:means("pre","B"),prequential_R:means("pre","R"),
 legacy_hard_switch_trials:runs.filter(x=>x.switches>0).length,source_reliable:runs.filter(x=>x.sourceReliable).length,
 soft_local_edited_trials:runs.filter(x=>x.localEdited).length,soft_global_refit_changed_trials:runs.filter(x=>x.globalEdited).length,
 legacy_returned_to_source:runs.filter(x=>x.returned).length,
 cold_exact:runs.filter(x=>x.cold).length,soft_cold_exact:runs.filter(x=>x.softCold).length,
 source_immutable:runs.filter(x=>x.sourceImmutable).length,held_disjoint:runs.filter(x=>x.heldClean).length,
 mean_work:Object.fromEntries(Object.keys(runs[0].work).map(k=>[k,mean(x=>x.work[k])]))};
}
const delta=(a,b,phase,section="held")=>ci(related.map(t=>t[section][phase][a]-t[section][phase][b]));
const BHard=delta("detector","local_soft","B","pre"),
 BRoll=delta("local_soft","rolling","B","pre"),
 BBayes=delta("local_soft","bayesian","B","pre"),
 BGlobal=delta("local_soft","global_soft","B","pre"),
 RRoll=delta("rolling","local_soft","R"),
 RBayes=delta("bayesian","local_soft","R"),
 RGlobal=delta("global_soft","local_soft","R");
const g=groups,noise=g.noise_fair,stationary=g.stationary3;
const conditions={
 related_B_prequential_gain_vs_G23_hard_min:BHard.mean>=.02,
 related_B_prequential_gain_vs_G23_hard_CI_lower_positive:BHard.ci95[0]>0,
 related_B_prequential_regression_vs_rolling_max:BRoll.mean<=.015,
 related_B_prequential_regression_vs_Bayes_max:BBayes.mean<=.015,
 related_R_held_gain_vs_rolling_min:RRoll.mean>=.01,
 related_R_held_gain_vs_rolling_CI_lower_positive:RRoll.ci95[0]>0,
 related_R_held_gain_vs_Bayes_min:RBayes.mean>=.005,
 related_R_held_gain_vs_Bayes_CI_lower_positive:RBayes.ci95[0]>0,
 related_R_held_gain_vs_global_soft_min:RGlobal.mean>=.005,
 related_R_held_gain_vs_global_soft_CI_lower_positive:RGlobal.ci95[0]>0,
 related_B_prequential_regression_vs_global_soft_max:BGlobal.mean<=.01,
 noise_false_local_graph_edit_trials_max_fraction:noise.soft_local_edited_trials/32<=.2,
 stationary_false_local_graph_edit_trials_max_fraction:stationary.soft_local_edited_trials/32<=.2,
 noise_B_or_R_held_regression_vs_null_max:Math.max(noise.held_B.local_soft-noise.held_B.null,noise.held_R.local_soft-noise.held_R.null)<=.025,
 source_retained_immutable_all:Object.values(g).every(z=>z.source_immutable===32),
 phase_held_disjoint_all:Object.values(g).every(z=>z.held_disjoint===32),
 cold_both_384byte_replays_exact_all:Object.values(g).every(z=>z.soft_cold_exact===32&&z.cold_exact===32),
 comparator_work_counts_finite_all:Object.values(g).every(z=>Object.values(z.mean_work).every(v=>Number.isFinite(v)&&v>=0)&&z.mean_work.bayesianMasks===3936)
};
const pass=Object.values(conditions).every(Boolean);
return{schema:"yggdrasil.gate24.local-soft-bridge.v1",prereg_commit:"e966549d2e689842ea0dafcf4ebd03bce2d778eb",parent_commit:"eb825ad1fb3b0722da398e9b92794c4ea0f28d7d",
 design:{trials:192,A64:64,B48:48,R48:48,held_B:16,held_R:16,soft_state_bytes:384,hard_state_bytes:384},
 groups,summary:{B_gain_vs_hard:BHard,B_loss_vs_rolling:BRoll,B_loss_vs_bayes:BBayes,B_loss_vs_global_soft:BGlobal,
 R_gain_vs_rolling:RRoll,R_gain_vs_bayes:RBayes,R_gain_vs_global_soft:RGlobal,
 noise_local_edited:noise.soft_local_edited_trials,stationary_local_edited:stationary.soft_local_edited_trials,
 return_count_legacy:related.filter(z=>z.returned).length},
 conditions,verdict:pass?"SYNTHETIC_STRUCTURAL_DEVELOPMENT_SIGNAL_ONLY":"LOCAL_SOFT_BRIDGE_SCIENTIFIC_NO_GO",
 exclusions:{native_original_first_use:false,qualified_independent_replication:false,process_exit_checkpoint:false,compute_equalized:false,accepted_cumulative_learner:false,deployment:false}};

};
if(typeof module !== "undefined" && require.main===module){
 const fs=require("fs"),actual=run();
 if(process.argv.includes("--verify")){
  const at=process.argv.indexOf("--verify"),expected=JSON.parse(fs.readFileSync(process.argv[at+1],"utf8"));
  if(JSON.stringify(expected)!==JSON.stringify(actual))throw Error("GATE24_EXACT_REPLAY_MISMATCH");
  console.log("GATE24_EXACT_REPLAY_PASS "+actual.verdict);
 }else console.log(JSON.stringify(actual,null,2));
}
