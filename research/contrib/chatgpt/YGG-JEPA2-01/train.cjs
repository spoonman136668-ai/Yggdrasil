"use strict";
/* YGG-JEPA2-01: two genuinely trained, independent, source-bound native causal
 * specialists. This is an action-conditioned latent JEPA adaptation, NOT Meta's
 * video V-JEPA 2 implementation, not accepted native inference, and not science.
 * Public views and witnessed actions/outcomes only. No hidden simulator labels.
 */
const SOURCE = {
  "101": {sha256:"52452b533495807f45a9f1489e3737ec179de96d8f4d3fdc68e03d80f183e57b",blob:"c4cbbe025db60a70a8fcdd88425d1ab39fdba4ff"},
  "202": {sha256:"9d9bfd406d48f94024c8a033e4f649ef3723957b3db6db8f0cf213cc8e1ccc81",blob:"f6aadc83ae545034abd69ec8f8e864f4442bd591"},
  "303": {sha256:"bcd931564f8cd384ea401ca9a8b7d4e35821cde985638285460b494f80ee8b30",blob:"62d654c48c4089bf5fae6b2f61487494b8c43c70"}
};
const CONFIG = Object.freeze({hidden:8,latent:2,first_epochs:80,
  continuation_epochs:24,jepa_lr:0.30,direct_lr:0.80,initial_count:640,
  final_count:832,sham_shift:320});
function guard(c, m) {if (!c) throw new Error("YGG_JEPA2_"+m);}
function bit(b) {guard(b === 0 || b === 1,"PUBLIC_BIT");return b;}
function sigmoid(v) {return v >= 0 ? 1/(1+Math.exp(-v)) : Math.exp(v)/(1+Math.exp(v));}
function publicFeatures(row, kind) {
  guard(Array.isArray(row)&&row.length===6,"EPISODE_SHAPE");
  const v=row[1];guard(Array.isArray(v)&&v.length===2&&v.every(z=>Array.isArray(z)&&z.length===2),"PUBLIC_VIEWS");
  const x=[bit(v[0][0]),bit(v[0][1]),bit(v[1][0]),bit(v[1][1]),bit(row[2])];
  if(kind==="reward") x.push(bit(row[3]),bit(row[4]));
  else guard(kind==="transition","LEARNER_KIND");
  return x.map(z=>2*z-1);
}
function outcome(row,kind) {return bit(row[kind==="transition"?3:5]);}
function teacher(row,kind) {
  const b=outcome(row,kind);
  return b===1?[1,-1]:[-1,1]; // fixed, noncollapsed, no target-branch gradient
}
function init(kind) {
  const d=kind==="transition"?5:7,salt=kind==="transition"?3:11;
  const encoder=Array.from({length:CONFIG.hidden},(_,j)=>
    Array.from({length:d},(_,i)=>0.09*Math.sin((j+2)*(i+1)*(salt+1))));
  const eb=Array(CONFIG.hidden).fill(0);
  const predictor=Array.from({length:CONFIG.latent},(_,k)=>
    Array.from({length:CONFIG.hidden},(_,j)=>0.11*Math.cos((k+2)*(j+2)*(salt+2))));
  return {kind,encoder,eb,predictor,pb:[0,0],updates:0};
}
function forward(m,x) {
  const h=m.encoder.map((w,j)=>Math.tanh(w.reduce((s,v,i)=>s+v*x[i],m.eb[j])));
  const output=m.predictor.map((w,k)=>w.reduce((s,v,j)=>s+v*h[j],m.pb[k]));
  return {h,output};
}
function probability(m,row) {
  const p=forward(m,publicFeatures(row,m.kind)).output;
  return sigmoid(2*(p[0]-p[1]));
}
function fit(m,rows,epochs,shift=0) {
  guard(rows.length>0&&Number.isInteger(epochs)&&epochs>=1,"FIT_BUDGET");
  guard(shift===0||shift===CONFIG.sham_shift,"PAIR_SHIFT");
  const d=m.encoder[0].length;
  const ys=rows.map(r=>outcome(r,m.kind));
  guard(ys.some(y=>y===0)&&ys.some(y=>y===1),"COLLAPSED_TEACHER");
  for(let epoch=0;epoch<epochs;epoch++) {
    const gE=Array.from({length:CONFIG.hidden},()=>Array(d).fill(0));
    const gEB=Array(CONFIG.hidden).fill(0);
    const gP=Array.from({length:2},()=>Array(CONFIG.hidden).fill(0));
    const gPB=[0,0];
    for(let i=0;i<rows.length;i++){
      const row=rows[i],x=publicFeatures(row,m.kind);
      const t=teacher(rows[(i+shift)%rows.length],m.kind);
      const {h,output}=forward(m,x),e=[output[0]-t[0],output[1]-t[1]];
      for(let k=0;k<2;k++){
        gPB[k]+=e[k];
        for(let j=0;j<CONFIG.hidden;j++)gP[k][j]+=e[k]*h[j];
      }
      for(let j=0;j<CONFIG.hidden;j++){
        const dh=(e[0]*m.predictor[0][j]+e[1]*m.predictor[1][j])*(1-h[j]*h[j]);
        gEB[j]+=dh;
        for(let v=0;v<d;v++)gE[j][v]+=dh*x[v];
      }
    }
    const step=CONFIG.jepa_lr/rows.length;
    for(let j=0;j<CONFIG.hidden;j++){
      m.eb[j]-=step*gEB[j];
      for(let v=0;v<d;v++)m.encoder[j][v]-=step*gE[j][v];
    }
    for(let k=0;k<2;k++){
      m.pb[k]-=step*gPB[k];
      for(let j=0;j<CONFIG.hidden;j++)m.predictor[k][j]-=step*gP[k][j];
    }
    guard(m.encoder.concat(m.predictor).every(w=>w.every(Number.isFinite))&&
      m.eb.concat(m.pb).every(Number.isFinite),"NUMERICS");
    m.updates+=1;
  }
  return m;
}
function initDirect(kind) {
  return {kind,w:Array(kind==="transition"?6:8).fill(0),updates:0};
}
function directP(m,row) {
  const x=[...publicFeatures(row,m.kind),1];
  return sigmoid(x.reduce((s,v,i)=>s+v*m.w[i],0));
}
function fitDirect(m,rows,epochs) {
  for(let epoch=0;epoch<epochs;epoch++){
    const g=m.w.map(()=>0);
    for(const row of rows){
      const x=[...publicFeatures(row,m.kind),1];
      const err=directP(m,row)-outcome(row,m.kind);
      for(let i=0;i<g.length;i++)g[i]+=err*x[i];
    }
    for(let i=0;i<g.length;i++)m.w[i]-=CONFIG.direct_lr*g[i]/rows.length;
    guard(m.w.every(Number.isFinite),"CONTROL_NUMERICS");m.updates++;
  }
  return m;
}
function fitCount(kind,rows) {
  const counts={};
  for(const r of rows){
    const key=publicFeatures(r,kind).join(",");
    if(!counts[key])counts[key]=[0,0];
    counts[key][outcome(r,kind)]++;
  }
  return counts;
}
function countP(counts,kind,row) {
  const n=counts[publicFeatures(row,kind).join(",")]||[0,0];
  return (n[1]+1)/(n[0]+n[1]+2);
}
function score(rows,fnT,fnR) {
  let t=0,r=0;
  for(const row of rows){
    const a=fnT(row),b=fnR(row);
    guard(Number.isFinite(a)&&Number.isFinite(b)&&a>=0&&a<=1&&b>=0&&b<=1,"PROBABILITY");
    t+=(a-outcome(row,"transition"))**2;
    r+=(b-outcome(row,"reward"))**2;
  }
  return {transition:t/rows.length,reward:r/rows.length,pooled:(t+r)/(2*rows.length)};
}
function clone(x) {return JSON.parse(JSON.stringify(x));}
function runSeed(seed, native) {
  const s=SOURCE[String(seed)];guard(!!s,"SEED");
  const original=JSON.stringify(native);
  guard(native && native.accepted_native===false && native.scientific_pass===false,"NATIVE_STATUS");
  guard(native.experience_source==="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef","SOURCE_MODE");
  const experience=JSON.parse(native.experience_ascii);
  guard(experience.schema==="yggdrasil.ckad.native-episode-experience.v4","EPISODE_VERSION");
  const rows=experience.episodes;
  guard(rows.length===CONFIG.final_count,"EXACT_832_EPISODES");
  const ids=new Set();
  for(const r of rows){
    guard(typeof r[0]==="string"&&r[0].length===64&&!ids.has(r[0]),"EVENT_ID");
    ids.add(r[0]);publicFeatures(r,"transition");publicFeatures(r,"reward");outcome(r,"reward");
  }
  const initial=rows.slice(0,CONFIG.initial_count);
  const later=rows.slice(CONFIG.initial_count);
  const jt=fit(init("transition"),initial,CONFIG.first_epochs);
  const jr=fit(init("reward"),initial,CONFIG.first_epochs);
  const dt=fitDirect(initDirect("transition"),initial,CONFIG.first_epochs);
  const dr=fitDirect(initDirect("reward"),initial,CONFIG.first_epochs);
  const ct=fitCount("transition",initial),cr=fitCount("reward",initial);
  const st=fit(init("transition"),initial,CONFIG.first_epochs,CONFIG.sham_shift);
  const sr=fit(init("reward"),initial,CONFIG.first_epochs,CONFIG.sham_shift);
  const pre=score(later,x=>probability(jt,x),x=>probability(jr,x));
  const direct=score(later,x=>directP(dt,x),x=>directP(dr,x));
  const count=score(later,x=>countP(ct,"transition",x),x=>countP(cr,"reward",x));
  const mispaired=score(later,x=>probability(st,x),x=>probability(sr,x));
  const oldBefore=score(initial,x=>probability(jt,x),x=>probability(jr,x));
  const stage1={transition:clone(jt),reward:clone(jr)};
  const resumed=clone(stage1);
  fit(resumed.transition,later,CONFIG.continuation_epochs);
  fit(resumed.reward,later,CONFIG.continuation_epochs);
  const uninterrupted={transition:clone(jt),reward:clone(jr)};
  fit(uninterrupted.transition,later,CONFIG.continuation_epochs);
  fit(uninterrupted.reward,later,CONFIG.continuation_epochs);
  guard(JSON.stringify(resumed)===JSON.stringify(uninterrupted),"COLD_CONTINUATION");
  guard(JSON.stringify(stage1)!==JSON.stringify(resumed),"STAGE2_UNCHANGED");
  const oldAfter=score(initial,x=>probability(resumed.transition,x),x=>probability(resumed.reward,x));
  const laterAfter=score(later,x=>probability(resumed.transition,x),x=>probability(resumed.reward,x));
  guard(JSON.stringify(native)===original,"NATIVE_CHECKPOINT_MUTATED");
  const strong=Math.min(direct.pooled,count.pooled);
  const predicates={
    versus_strong_control: pre.pooled<=strong-.01,
    pairing_sensitive: pre.pooled<=mispaired.pooled-.01,
    old_retention: oldAfter.pooled<=oldBefore.pooled+.03
  };
  return {
    report:{seed,source_checkpoint_sha256:s.sha256,source_git_blob:s.blob,
      initial:CONFIG.initial_count,continued:later.length,
      metrics:{held_before_continuation:pre,held_direct:direct,held_count:count,
        held_mispaired:mispaired,initial_prefix_before:oldBefore,
        initial_prefix_after:oldAfter,continued_prefix_after_in_sample:laterAfter},
      predicates,development_go:Object.values(predicates).every(Boolean),
      science_pass:false,accepted_native:false,
      native_checkpoint_changed:false,cold_resumed_exact:true},
    checkpoint:{seed,source_checkpoint_sha256:s.sha256,config:CONFIG,
      initial_state:stage1,continued_state:resumed,
      conventional_direct:{transition:dt,reward:dr}}
  };
}
if(typeof module!=="undefined") module.exports={SOURCE,CONFIG,runSeed,publicFeatures,fit,init,probability};
if(typeof require!=="undefined"&&typeof module!=="undefined"&&require.main===module){
  const fs=require("fs"),crypto=require("crypto"),path=require("path");
  const out=process.argv[2];
  guard(typeof out==="string" && out.length>0,"OUTPUT_DIR");
  fs.mkdirSync(out,{recursive:true});
  const reports=[];
  for(const seed of [101,202,303]){
    const sourcePath=path.resolve(__dirname,"../CKAD-24/seed-"+seed+"-coverage-native.json");
    const raw=fs.readFileSync(sourcePath),sha=crypto.createHash("sha256").update(raw).digest("hex");
    guard(sha===SOURCE[seed].sha256,"CHECKPOINT_SHA256_"+seed);
    const result=runSeed(seed,JSON.parse(raw.toString("utf8")));
    reports.push(result.report);
    fs.writeFileSync(path.join(out,"seed-"+seed+"-jepa2-checkpoint.json"),JSON.stringify(result.checkpoint,null,2)+"\n");
  }
  const summary={schema:"yggdrasil.jepa2-01-training-result.v1",
    prereg_sha:"8ff651073ea2505232cac6047a45c2133e56c14f",
    source_parent:"a5faea392679756f172b87f3e40399ed88329a06",
    config:CONFIG,replicas:reports,
    development_go:reports.every(x=>x.development_go),science_pass:false,
    training_kind:"actual additional learner fitting from previously retained Yggdrasil native causal episodes; no fresh original-world source",
    note:"Pre-consumed synthetic development trajectories; no sealed or novel-world science; protected original learner and prior checkpoints unchanged."};
  fs.writeFileSync(path.join(out,"result.json"),JSON.stringify(summary,null,2)+"\n");
  process.stdout.write(JSON.stringify({development_go:summary.development_go,
    metrics:reports.map(x=>({seed:x.seed,held:x.metrics.held_before_continuation.pooled,
      direct:x.metrics.held_direct.pooled,count:x.metrics.held_count.pooled,
      mispaired:x.metrics.held_mispaired.pooled,predicates:x.predicates}))})+"\n");
}
