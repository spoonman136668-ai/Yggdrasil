// DWSA-BR01: MIT-licensed upstream source used by immutable Git blob, no donor inference.
// Node >=18, run: node run.mjs donor-digit-model.json pinned-src-models.js
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
function experiment(model,source) {
  const shape=[35,24,16,12,10], layers=model.layers;
  if(model.metadata.parameters!==1598||model.metadata.seed!==20261022||model.metadata.updates!==80000||layers.length!==4)throw Error("BAD_DONOR");
  for(let k=0;k<4;k++)if(layers[k].weights.length!==shape[k+1]||layers[k].weights.some(row=>row.length!==shape[k]||row.some(x=>!Number.isFinite(x))))throw Error("BAD_SHAPE");
  const mark="export const digitPatterns = ", i=source.indexOf(mark); if(i<0)throw Error("MISSING_GENERATOR");
  const raw=source.slice(i+mark.length).split("].map(")[0]+"]";
  const patterns=JSON.parse(raw.replace(/,\s*]/g,"]")).map(row=>row.join("").split("").map(Number));
  if(patterns.length!==10||patterns.some(row=>row.length!==35||row.some(x=>x!==0&&x!==1)))throw Error("BAD_PATTERNS");
  const mul=(A,X)=>A.map(row=>Array.from({length:X[0].length},(_,j)=>row.reduce((sum,v,k)=>sum+v*X[k][j],0)));
  let S=layers[3].weights;
  for(let k=2;k>=0;k--)S=mul(S,layers[k].weights);
  const donor=S.map((row,c)=>row.map((v,bit)=>+(v-S.reduce((sum,r,j)=>sum+(j===c?0:r[bit]),0)/9>0)));
  const rng=(seed)=>()=>{seed|=0;seed=(seed+0x6d2b79f5)|0;let t=Math.imul(seed^(seed>>>15),1|seed);t=(t+Math.imul(t^(t>>>7),61|t))^t;return ((t^(t>>>14))>>>0)/4294967296;};
  const sample=(seed,p,count)=>{const random=rng(seed), a=[];for(let c=0;c<10;c++)for(let rep=0;rep<count;rep++)a.push({label:c,x:patterns[c].map(bit=>random()<p?1-bit:bit)});return a;};
  const train=sample(504827,0.07,20);
  const predict=(bank,x)=>{let best=0,dmin=36;for(let c=0;c<10;c++){let dist=0;for(let bit=0;bit<35;bit++)dist+=+(bank[c][bit]!==x[bit]);if(dist<dmin){dmin=dist;best=c;}}return best;};
  const tally=(bank,data)=>{const counts=Array(10).fill(0);for(const e of data)if(predict(bank,e.x)===e.label)counts[e.label]++;return counts;};
  const majorities=Array.from({length:10},()=>Array(35).fill(0));
  for(const e of train)for(let bit=0;bit<35;bit++)majorities[e.label][bit]+=e.x[bit];
  const fitted=majorities.map(row=>row.map(n=>+(n>10)));
  const attempted={};
  function repair(initial){
    const bank=initial.map(row=>row.slice()), countByClass=Array(10).fill(0);
    const proposals=[];
    for(let c=0;c<10;c++)for(let bit=0;bit<35;bit++){const n=majorities[c][bit], target=+(n>=16);
      if((n>=16||n<=4)&&bank[c][bit]!==target)proposals.push({c,bit,target,confidence:Math.abs(n-10)});
    }
    proposals.sort((a,b)=>b.confidence-a.confidence||a.c-b.c||a.bit-b.bit);
    let accepted=0,rejected=0,oldCounts=tally(bank,train);
    for(const p of proposals){
      if(accepted>=48||countByClass[p.c]>=12){rejected++;continue;}
      const previous=bank[p.c][p.bit];bank[p.c][p.bit]=p.target;
      const counts=tally(bank,train);
      const improves=counts.reduce((a,b)=>a+b,0)>oldCounts.reduce((a,b)=>a+b,0);
      if(improves&&counts.every((v,i)=>v>=oldCounts[i])){accepted++;countByClass[p.c]++;oldCounts=counts;}
      else{bank[p.c][p.bit]=previous;rejected++;}
    }
    return {bank, proposals:proposals.length,accepted,rejected,accepted_by_class:countByClass,train_correct:oldCounts.reduce((a,b)=>a+b,0),train_per_class:oldCounts};
  }
  const corrected=repair(donor);
  const zero=repair(Array.from({length:10},()=>Array(35).fill(0)));
  const copiedFitted=fitted.map(row=>row.slice());
  const models={donor_only:donor,donor_bounded:corrected.bank,zero_bounded:zero.bank,fitted_same_labels:fitted,source_template_upper_bound:patterns,donor_unbounded_replaced:copiedFitted};
  const evaluated={};
  for(const [key,seed,p] of [["familiar_7pct",781223,0.07],["shifted_12pct",781229,0.12]]){
    const data=sample(seed,p,200);evaluated[key]={seed,noise:p,n:data.length,models:{}};
    for(const [name,bank] of Object.entries(models)){const per=tally(bank,data),n=per.reduce((a,b)=>a+b,0);evaluated[key].models[name]={correct:n,accuracy:n/data.length,per_class:per};}
  }
  function pack(bank){const b=Array(44).fill(0);bank.flat().forEach((v,i)=>{if(v)b[i>>>3]|=1<<(7-(i&7));});return b;}
  function unpack(bytes){if(bytes.length!==44||(bytes[43]&3)!==0)throw Error("PACK_CORRUPT");return Array.from({length:10},(_,c)=>Array.from({length:35},(_,i)=>(bytes[(c*35+i)>>>3]>>>(7-((c*35+i)&7)))&1));}
  const packed=pack(corrected.bank);let restores=0;for(let k=0;k<3;k++){const q=unpack(packed.slice());if(JSON.stringify(q)!==JSON.stringify(corrected.bank))throw Error("COLD_ROUNDTRIP");restores++;}
  let tamperRejected=false;try{const bad=packed.slice();bad[43]|=3;unpack(bad)}catch{tamperRejected=true;}
  if(!tamperRejected)throw Error("TAMPER_FAILURE");
  const f=evaluated.familiar_7pct.models,v=evaluated.shifted_12pct.models;
  const margin7=f.donor_bounded.accuracy-f.donor_only.accuracy;
  const margin12=v.donor_bounded.accuracy-v.donor_only.accuracy;
  const screen=margin7>=0.05-1e-12 && margin12>=-0.02-1e-12 && restores===3;
  return {schema:"dwsa-br01.dev-screen.v1",donor_blob:"16ea8cf939bfa0f5f21e227d159b11d4ff578eca",generator_blob:"6f95eea88422ceb01b3118e65cd45b9a4c065bd9",seeds:{calibration:504827,familiar:781223,shifted:781229},pinned_prereg_commit:"510f06ede757e33900fadc63735842c2e75fd87b",total_labeled_calibration:train.length,donor_forward_calls:0,donor_runtime_invocations:0,protected_world_actions:0,checkpoint_bits:350,checkpoint_payload_bytes:44,initial_train_correct:tally(donor,train).reduce((a,b)=>a+b,0),bounded_repair:{proposals:corrected.proposals,accepted:corrected.accepted,rejected:corrected.rejected,accepted_by_class:corrected.accepted_by_class,train_correct:corrected.train_correct},zero_control:{proposals:zero.proposals,accepted:zero.accepted,rejected:zero.rejected,train_correct:zero.train_correct},restores,tamperRejected,metrics:evaluated,delta_familiar:margin7,delta_shifted:margin12,dev_screen:screen?"PASS":"NO_GO",science:"NOT_VERIFIED",deployment:"NONE"};
}
function gitBlobSha(buffer){return createHash("sha1").update(Buffer.from("blob "+buffer.length+"\0","utf8")).update(buffer).digest("hex");}
if(process.argv.length!==4)throw Error("USAGE: node run.mjs donor.json models.js");
const m=readFileSync(process.argv[2]),s=readFileSync(process.argv[3]);
if(gitBlobSha(m)!=="16ea8cf939bfa0f5f21e227d159b11d4ff578eca"||gitBlobSha(s)!=="6f95eea88422ceb01b3118e65cd45b9a4c065bd9")throw Error("SOURCE_BLOB_DRIFT");
console.log(JSON.stringify(experiment(JSON.parse(m.toString("utf8")),s.toString("utf8")),null,2));
