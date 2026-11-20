// DWSA-06. Read-only static donor compiler. Never import donor modules or call donor forward.
// Scientific status: SAME_TEMPLATE_DEV_ONLY, no source first use / no Yggdrasil integration.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
export function analyze(model,source){
 const require=(ok,key)=>{if(!ok)throw Error("DWSA06_"+key)};
 const d=[35,24,16,12,10],layers=model.layers;
 require(layers.length===4&&model.metadata.parameters===1598&&model.metadata.seed===20261022&&model.metadata.updates===80000,"SOURCE_SCHEMA");
 for(let i=0;i<4;i++){const z=layers[i];require(z.weights.length===d[i+1]&&z.biases.length===d[i+1]&&z.weights.every(row=>row.length===d[i]&&row.every(Number.isFinite))&&z.biases.every(Number.isFinite),"SOURCE_SHAPE")}
 const start=source.indexOf("export const digitPatterns = ");
 require(start>=0,"TEMPLATES_MISSING");
 const seg=source.slice(start+"export const digitPatterns = ".length);
 const raw=seg.slice(0,seg.indexOf("].map(")+1).replace(/,\s*]/g,"]");
 const patterns=JSON.parse(raw).map(row=>row.join("").split("").map(Number));
 require(patterns.length===10&&patterns.every(x=>x.length===35&&x.every(v=>v===0||v===1)),"TEMPLATE_SCHEMA");
 const mul=(A,X)=>A.map(row=>Array.from({length:X[0].length},(_,j)=>{let v=0;for(let k=0;k<row.length;k++)v+=row[k]*X[k][j];return v}));
 let S=layers[3].weights;for(let k=2;k>=0;k--)S=mul(S,layers[k].weights);
 const proto=S.map((row,c)=>row.map((v,i)=>+(v-S.reduce((a,r,j)=>a+(j===c?0:r[i]),0)/9>0)));
 const rand=(seed)=>()=>{seed|=0;seed=(seed+0x6d2b79f5)|0;let t=Math.imul(seed^(seed>>>15),1|seed);t=(t+Math.imul(t^(t>>>7),61|t))^t;return ((t^(t>>>14))>>>0)/4294967296};
 const fR=rand(492615);
 const fitted=patterns.map(t=>{const totals=Array(35).fill(0);for(let n=0;n<20;n++)for(let i=0;i<35;i++)totals[i]+=fR()<0.07?1-t[i]:t[i];return totals.map(x=>+(x>10))});
 const blindR=rand(774113);const blind=Array.from({length:10},()=>Array.from({length:35},()=>+(blindR()<0.5)));
 const banks={learned_path:proto,shuffled_label:proto.map((_,c)=>proto[(c+1)%10]),blind_random:blind,supervised_same_bytes:fitted,source_symbolic:patterns};
 const stats=Object.fromEntries(Object.keys(banks).map(k=>[k,{correct:0,per_class:Array(10).fill(0)}]));stats.class_zero={correct:0,per_class:[200,0,0,0,0,0,0,0,0,0]};
 const classify=(x,bank)=>{let best=0,dist=1e9;for(let c=0;c<10;c++){let n=0;for(let i=0;i<35;i++)n+=x[i]!==bank[c][i];if(n<dist){dist=n;best=c}}return best};
 const eR=rand(637127);
 for(let cls=0;cls<10;cls++)for(let rep=0;rep<200;rep++){
  const x=patterns[cls].map(v=>eR()<0.07?1-v:v);
  for(const [key,bank] of Object.entries(banks)){const y=classify(x,bank);if(y===cls){stats[key].correct++;stats[key].per_class[cls]++}}
  if(cls===0)stats.class_zero.correct++;
 }
 const n=2000;const acc=Object.fromEntries(Object.entries(stats).map(([k,v])=>[k,{correct:v.correct,accuracy:v.correct/n,per_class:v.per_class}]));
 const t=acc.learned_path.accuracy;
 const signal=t>=0.7&&t-acc.shuffled_label.accuracy>=0.3&&t-acc.blind_random.accuracy>=0.3;
 const bits=proto.flat();require(bits.length===350,"BIT_LENGTH");
 const payload=Array(44).fill(0);bits.forEach((v,i)=>{if(v)payload[i>>3]|=1<<(7-i%8)});
 require(payload.length===44&&(payload[43]&3)===0,"PACKING");
 return {metrics:acc,packed_bytes:payload,prototypes:proto,dev_signal_pass:signal,
         ones_by_class:proto.map(row=>row.reduce((a,b)=>a+b,0)),
         source_model_forward_calls:0,source_original_actions:0};
}
function gitBlobSha(raw){const prefix=Buffer.from("blob "+raw.length+"\\0","utf8");return createHash("sha1").update(prefix).update(raw).digest("hex")}
function insist(ok,s){if(!ok)throw new Error("DWSA06_"+s)}
const modelRaw=readFileSync(process.argv[2]);
const sourceRaw=readFileSync(process.argv[3]);
insist(gitBlobSha(modelRaw)==="16ea8cf939bfa0f5f21e227d159b11d4ff578eca","PINNED_DONOR_BLOB");
insist(gitBlobSha(sourceRaw)==="6f95eea88422ceb01b3118e65cd45b9a4c065bd9","PINNED_TEMPLATE_BLOB");
const result=analyze(JSON.parse(modelRaw.toString("utf8")),sourceRaw.toString("utf8"));
const payload=Buffer.from(result.packed_bytes);
const header=Buffer.from([68,87,80,54,1,0,10,35]);
const beforeHash=Buffer.concat([header,payload]);
const digest=createHash("sha256").update(beforeHash).digest();
const checkpoint=Buffer.concat([beforeHash,digest]);
function restore(raw){
 insist(Buffer.isBuffer(raw)&&raw.length===84,"CHECKPOINT_SIZE");
 insist(raw.subarray(0,8).equals(header),"CHECKPOINT_HEADER");
 insist((raw[51]&3)===0,"CHECKPOINT_PADDING");
 insist(createHash("sha256").update(raw.subarray(0,52)).digest().equals(raw.subarray(52)),"CHECKPOINT_SHA");
 return Array.from({length:350},(_,i)=>((raw[8+(i>>3)]>>(7-(i&7)))&1));
}
insist(checkpoint.length===84,"FIXED_FOOTPRINT");
const first=restore(checkpoint);
insist(first.every((v,i)=>v===result.prototypes.flat()[i]),"COLD_RESTORE");
for(let repeat=0;repeat<3;repeat++)insist(restore(Buffer.from(checkpoint)).every((v,i)=>v===first[i]),"RESTORE_REPEAT");
for(const index of [0,8,36,51,70]){const bad=Buffer.from(checkpoint);bad[index]^=1;let rejected=false;try{restore(bad)}catch{rejected=true}insist(rejected,"TAMPER_REJECTION")}
const answer={schema:"dwsa06.static-path-prototype-dev.v1",prereg_committed_sha:"d379477033cab1d9dd72c8cdb5e69bedf574f339",donor_repo:"MasanneckLab/neural-networks-explained",donor_ref:"149a2838309efe6ee5ec9e8c9689e4a321158b7d",donor_git_blob:"16ea8cf939bfa0f5f21e227d159b11d4ff578eca",template_git_blob:"6f95eea88422ceb01b3118e65cd45b9a4c065bd9",candidate_bytes:84,checkpoint_sha256:createHash("sha256").update(checkpoint).digest("hex"),donor_forward_calls:0,original_source_actions:0,tests:{cold_restores:3,tamper_rejections:5},seeds:{eval:637127,fitted_control:492615,random_control:774113},eval_n:2000,metrics:result.metrics,development_signal:result.dev_signal_pass?"PASS":"NO_GO",scientific:"UNVERIFIED",deployment:"NONE",independent_world_transfer:false};
console.log(JSON.stringify(answer,null,2));
