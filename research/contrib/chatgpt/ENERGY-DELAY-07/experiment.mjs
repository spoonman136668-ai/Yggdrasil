export function energyDelay(phase="smoke"){
 const seeds=phase==="smoke"?[94199]:phase==="primary"?[94211,94219,94229,94237,94243,94253,94261,94273,94283,94291,94307,94319]:null;
 if(!seeds)throw Error("unknown phase");
 const SCENARIOS=["CONTRADICT","DELAY_SHIFT","NULL"];
 const ARMS=["flux_delayed","intervention_beta","intervention_z_beta","all_z_beta","actionblind_z_beta","immediate_only_beta","temporal_source_bayes","privileged_truth_oracle"];
 function rand(seed,mode,context,step,index){
   const key=`ENERGY-DELAY-07|${seed}|${mode}|${context}|${step}|${index}`;
   let s=2166136261;for(let i=0;i<key.length;i++)s=Math.imul(s^key.charCodeAt(i),16777619)>>>0;
   if(!s)s=0xa1b2c3d4;
   return ()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return (s>>>0)/4294967296};
 }
 function truth(mode,ctx){
   if(ctx==="OLD")return {lag:1,best:1};
   if(mode==="CONTRADICT")return {lag:1,best:0};
   if(mode==="DELAY_SHIFT")return {lag:2,best:1};
   return {lag:-1,best:null};
 }
 function episode(seed,scenario,ctx,step,index){
   const r=rand(seed,scenario,ctx,step,index),u=r()<.5?0:1,z=r()<.9?u:1-u;
   let a;if(step==="observational")a=r()<.9?u:1-u;
   else if(step==="held")a=index%2;
   else a=r()<.5?0:1;
   const law=truth(scenario,ctx);
   const ys=Array.from({length:3},(_,lag)=>{
     const p=lag===law.lag?(a===law.best?.85:.15):(u?.8:.2);
     return r()<p?1:0
   });
   return {a,z,y:ys,assignment:step,u};
 }
 const beta=(on,total)=> (on+.5)/(total+1);
 const zero=()=>Array.from({length:3},()=>({all:Array.from({length:2},()=>[0,0]),
   z:Array.from({length:2},()=>Array.from({length:2},()=>[0,0])),
   zb:Array.from({length:2},()=>[0,0])}));
 function count(rows){const x=zero();for(const row of rows)for(let lag=0;lag<3;lag++){
   const y=row.y[lag],s=x[lag];
   s.all[row.a][0]+=y;s.all[row.a][1]++;
   s.z[row.z][row.a][0]+=y;s.z[row.z][row.a][1]++;
   s.zb[row.z][0]+=y;s.zb[row.z][1]++;
 }return x}
 function fit(rows){
   const intRows=rows.filter(x=>x.assignment==="intervention");
   if(intRows.length!==24||rows.length!==48)throw Error("train size wrong");
   const a=count(intRows),b=count(rows);
   const effects=Array.from({length:3},(_,lag)=>beta(a[lag].all[1][0],a[lag].all[1][1])-beta(a[lag].all[0][0],a[lag].all[0][1]));
   const rank=effects.map((d,i)=>({lag:i,abs:Math.abs(d),d})).sort((x,y)=>y.abs-x.abs||x.lag-y.lag);
   const signal=rank[0].abs>=.30?{lag:rank[0].lag,best:rank[0].d>0?1:0,amplitude:rank[0].abs}:null;
   const pz=z=>z?.74:.26;
   let logposts=[];
   const hyps=[null,...Array.from({length:3},(_,lag)=>[{lag,best:0},{lag,best:1}]).flat()];
   for(const h of hyps){
     let lp=-Math.log(hyps.length);
     for(const row of intRows)for(let lag=0;lag<3;lag++){
       const py=h?.lag===lag?(row.a===h.best?.85:.15):pz(row.z);
       lp+=Math.log(row.y[lag]?py:(1-py));
     }
     logposts.push(lp);
   }
   const max=Math.max(...logposts),w=logposts.map(x=>Math.exp(x-max)),d=w.reduce((x,y)=>x+y,0);
   const posterior=w.map(x=>x/d);
   const trained={signal,effects,counts:{intervention:a,public:b},hypotheses:hyps,posterior};
   if(!trained.posterior.every(v=>Number.isFinite(v)))throw Error("bad temporal posterior");
   return trained;
 }
 function predict(m,arm,act,z,u,law){
   const c=m.counts.intervention,all=m.counts.public,pz=z?.74:.26;
   const b=(x)=>beta(x[0],x[1]),p=[];
   for(let lag=0;lag<3;lag++){
     const ci=c[lag],cp=all[lag];
     const ab=b(cp.zb[z]),pi=b(ci.all[act]),pzact=b(ci.z[z][act]),allz=b(cp.z[z][act]);
     let q;
     if(arm==="flux_delayed")q=m.signal?.lag===lag?(act===m.signal.best?.8:.2):ab;
     else if(arm==="intervention_beta")q=pi;
     else if(arm==="intervention_z_beta")q=pzact;
     else if(arm==="all_z_beta")q=allz;
     else if(arm==="actionblind_z_beta")q=ab;
     else if(arm==="immediate_only_beta")q=lag===0?pi:ab;
     else if(arm==="temporal_source_bayes")q=m.hypotheses.reduce((sum,h,i)=>sum+m.posterior[i]*(h?.lag===lag?(act===h.best?.85:.15):pz),0);
     else if(arm==="privileged_truth_oracle")q=lag===law.lag?(act===law.best?.85:.15):(u?.8:.2);
     else throw Error("unknown arm: "+arm);
     if(!(q>0&&q<1))throw Error("invalid probability");
     p.push(q);
   }
   return p;
 }
 const brier=(p,y)=>(p-y)**2;
 function world(seed,scenario){
   let old=[...Array.from({length:24},(_,i)=>episode(seed,scenario,"OLD","observational",i)),
            ...Array.from({length:24},(_,i)=>episode(seed,scenario,"OLD","intervention",i))];
   let oldModel=fit(old);
   const oldPred=Array.from({length:2},(_,a)=>Array.from({length:2},(_,z)=>
     predict(oldModel,"flux_delayed",a,z,0,truth(scenario,"OLD"))));
   let newRows=[...Array.from({length:24},(_,i)=>episode(seed,scenario,"NEW","observational",i)),
             ...Array.from({length:24},(_,i)=>episode(seed,scenario,"NEW","intervention",i))];
   const models={OLD:oldModel,NEW:fit(newRows)};
   const saved=JSON.stringify(models),restored=JSON.parse(saved);
   if(JSON.stringify(restored)!==saved)throw Error("checkpoint JSON mismatch");
   const recheck=Array.from({length:2},(_,a)=>Array.from({length:2},(_,z)=>
     predict(restored.OLD,"flux_delayed",a,z,0,truth(scenario,"OLD"))));
   if(JSON.stringify(recheck)!==JSON.stringify(oldPred))throw Error("historical prediction drift");
   const totals=Object.fromEntries(ARMS.map(arm=>[arm,{old:0,new:0,old_n:0,new_n:0}]));
   for(const ctx of ["OLD","NEW"]){
     const law=truth(scenario,ctx);
     for(let i=0;i<256;i++){
       const ep=episode(seed,scenario,ctx,"held",i);
       for(const arm of ARMS){
         const p=predict(restored[ctx],arm,ep.a,ep.z,ep.u,law);
         const loss=ep.y.reduce((sum,y,lag)=>sum+brier(p[lag],y),0);
         totals[arm][ctx==="OLD"?"old":"new"]+=loss;
         totals[arm][ctx==="OLD"?"old_n":"new_n"]+=3;
       }
     }
   }
   const scored={};
   for(const arm of ARMS){
     const r=totals[arm];scored[arm]={old:r.old/r.old_n,new:r.new/r.new_n,overall:(r.old+r.new)/(r.old_n+r.new_n)};
   }
   const newSig=restored.NEW.signal, expected=truth(scenario,"NEW");
   return {seed,scenario,old_n:768,new_n:768,score:scored,
     old_retained:true,old_effect:restored.OLD.signal,
     new_effect:newSig,
     true_new_effect:expected,
     new_correct:expected.lag<0?newSig===null:!!newSig&&newSig.lag===expected.lag&&newSig.best===expected.best,
     false_null:expected.lag<0&&newSig!==null,
     new_action_policy_gain:expected.lag<0?(newSig===null?0:-1):(newSig&&newSig.lag===expected.lag&&newSig.best===expected.best?1:(newSig? -1:0)),
     source_true_u_only_for_oracle:true};
 }
 const worlds=seeds.flatMap(seed=>SCENARIOS.map(scenario=>world(seed,scenario)));
 const means={};for(const arm of ARMS){
   means[arm]={};for(const field of ["old","new","overall"])
     means[arm][field]=worlds.reduce((v,w)=>v+w.score[arm][field],0)/worlds.length;
 }
 const families={};
 for(const scenario of SCENARIOS){
   const rows=worlds.filter(w=>w.scenario===scenario);
   families[scenario]={
     count:rows.length,correct:rows.filter(w=>w.new_correct).length,
     false_null:rows.filter(w=>w.false_null).length,
     policy_gain_mean:rows.reduce((v,w)=>v+w.new_action_policy_gain,0)/rows.length,
     scores:Object.fromEntries(ARMS.map(arm=>[arm,rows.reduce((v,w)=>v+w.score[arm].new,0)/rows.length]))
   }
 }
 const nonOracle=ARMS.filter(a=>!["flux_delayed","temporal_source_bayes","privileged_truth_oracle"].includes(a));
 const best=nonOracle.reduce((b,a)=>means[a].overall<means[b].overall?a:b);
 const gain=means[best].overall-means.flux_delayed.overall;
 const guard=families.NULL.false_null===0&&families.CONTRADICT.correct>=10&&families.DELAY_SHIFT.correct>=10&&worlds.every(w=>w.old_retained);
 const pass=guard&&gain>=.01;
 const mixed=(families.CONTRADICT.correct>=8&&families.DELAY_SHIFT.correct>=8 &&
   means.flux_delayed.overall<means.actionblind_z_beta.overall);
 const verdict=pass?"SOURCE_FREE_DEV_SUPPORTED":mixed?"MIXED_NO_GO":"NEGATIVE_NO_GO";
 return {experiment:"ENERGY-DELAY-07",phase,model_type:"energy-inspired delayed intervention flux",seeds,
   data_counts:{worlds:worlds.length,train_episodes:worlds.length*96,held_episodes:worlds.length*512,held_outcomes:worlds.length*1536},
   summary:{means,families,best_non_oracle:best,brier_gain_vs_best_non_oracle:gain,null_false_effects:families.NULL.false_null,
     old_snapshot_retention:worlds.filter(w=>w.old_retained).length,
     verdict,guard_pass:guard,correct_model_source_family_bayes:"reference_not_a_competition_target",
     native_scientific_gain:false},
   worlds,
   limitations:["Observation episodes are confounded by hidden nuisance U; randomized episodes identify interventions in this synthetic task","Context labels OLD/NEW explicitly supplied; no hidden context discovery","The causal lag is an outcome timestamp in an independent episode, not a multi-step dynamical trajectory","Held outcome U is only available to privileged oracle, not other predictors","JSON roundtrip is in-process, not native fresh-process checkpoint","No complete whole-process cost comparison or native scientific first use"]};
}
