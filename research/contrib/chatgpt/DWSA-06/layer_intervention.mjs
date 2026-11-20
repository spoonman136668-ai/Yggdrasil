// DWSA-06-M: static pretrained-vs-original-init layer interventions.
// Pre-scoring prereg commit 416429f6ea77d189876289b098718d5e44438775.
// No donor network inference, no donor training, no original-world actions.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";

const REF="149a2838309efe6ee5ec9e8c9689e4a321158b7d";
const BLOBS=[
  "16ea8cf939bfa0f5f21e227d159b11d4ff578eca",
  "6f95eea88422ceb01b3118e65cd45b9a4c065bd9",
  "1776478a312781e0866f16e1ef237fcbc1092d1a",
];
const D=[35,24,16,12,10], MASKS=16, INPUTS=2000;
function requireCondition(condition,code){
  if(!condition)throw new Error("DWSA06M_REJECT_"+code);
}
function gitBlob(raw){
  return createHash("sha1")
    .update(Buffer.from("blob "+raw.length+"\0","utf8"))
    .update(raw).digest("hex");
}
function seededRandom(seed){
  return ()=>{
    seed|=0;
    seed=(seed+0x6d2b79f5)|0;
    let t=Math.imul(seed^(seed>>>15),1|seed);
    t=(t+Math.imul(t^(t>>>7),61|t))^t;
    return ((t^(t>>>14))>>>0)/4294967296;
  };
}
function originalInitialization(){
  const r=seededRandom(20261022);
  return {layers:D.slice(1).map((size,i)=>({
    weights:Array.from({length:size},()=>
      Array.from({length:D[i]},()=> (r()-0.5)*Math.sqrt(24/D[i]))),
    biases:Array(size).fill(i===3?0:0.1)
  }))};
}
function checkShape(model){
  requireCondition(model&&Array.isArray(model.layers)&&model.layers.length===4,"LAYER_COUNT");
  for(let i=0;i<4;i++){
    const layer=model.layers[i];
    requireCondition(Array.isArray(layer.weights)&&layer.weights.length===D[i+1]&&
      layer.weights.every(row=>Array.isArray(row)&&row.length===D[i]&&
        row.every(v=>typeof v==="number"&&Number.isFinite(v)))&&
      Array.isArray(layer.biases)&&layer.biases.length===D[i+1]&&
        layer.biases.every(v=>typeof v==="number"&&Number.isFinite(v)),
      "LAYER_SHAPE_"+i);
  }
}
function multiply(A,B){
  requireCondition(A[0].length===B.length,"MULTIPLY_DIMENSIONS");
  return A.map(row=>Array.from({length:B[0].length},(_,column)=>{
    let total=0;
    for(let i=0;i<row.length;i++)total+=row[i]*B[i][column];
    return total;
  }));
}
function extract(trained,initial,mask){
  const matrices=D.slice(1).map((_,i)=>
    ((mask&(1<<i))!==0?trained:initial).layers[i].weights);
  let route=matrices[3];
  for(let i=2;i>=0;i--)route=multiply(route,matrices[i]);
  return route.map((row,label)=>row.map((v,i)=>{
    const background=route.reduce((total,r,c)=>total+(c===label?0:r[i]),0)/9;
    return +(v-background>0);
  }));
}
function sealPrototype(proto){
  requireCondition(proto.length===10&&proto.every(r=>r.length===35&&
    r.every(v=>v===0||v===1)),"PROTOTYPE_BITS");
  const flat=proto.flat(),payload=Buffer.alloc(44);
  flat.forEach((v,i)=>{if(v)payload[i>>3]|=1<<(7-(i&7))});
  requireCondition((payload[43]&3)===0,"PROTOTYPE_PADDING");
  const body=Buffer.concat([Buffer.from([68,87,80,54,1,0,10,35]),payload]);
  const checkpoint=Buffer.concat([body,createHash("sha256").update(body).digest()]);
  requireCondition(checkpoint.length===84,"CHECKPOINT_LENGTH");
  return checkpoint;
}
function restore(raw){
  const hdr=Buffer.from([68,87,80,54,1,0,10,35]);
  requireCondition(Buffer.isBuffer(raw)&&raw.length===84&&
    raw.subarray(0,8).equals(hdr)&&
    (raw[51]&3)===0&&
    createHash("sha256").update(raw.subarray(0,52)).digest().equals(raw.subarray(52)),
    "CHECKPOINT_INTEGRITY");
  return Array.from({length:10},(_,c)=>
    Array.from({length:35},(_,i)=>{
      const j=c*35+i;
      return (raw[8+(j>>3)]>>(7-(j&7)))&1;
    }));
}
function sourceTemplates(source){
  const marker="export const digitPatterns = ";
  const pos=source.indexOf(marker);
  requireCondition(pos>=0,"SOURCE_TEMPLATE_MARKER");
  const suffix=source.slice(pos+marker.length),end=suffix.indexOf("].map(");
  requireCondition(end>0,"SOURCE_TEMPLATE_DELIMITER");
  const patterns=JSON.parse(suffix.slice(0,end+1).replace(/,\s*]/g,"]"))
    .map(rows=>rows.join("").split("").map(Number));
  requireCondition(patterns.length===10&&patterns.every(row=>row.length===35&&
    row.every(v=>v===0||v===1)),"SOURCE_TEMPLATE_DIMENSIONS");
  return patterns;
}
function run(model,source,trainingSource){
  requireCondition(model.metadata?.seed===20261022&&
    model.metadata?.parameters===1598&&
    model.metadata?.updates===80000&&
    JSON.stringify(model.metadata?.architecture)===JSON.stringify(D),
    "DONOR_METADATA");
  requireCondition(trainingSource.includes("seededRandom(20261022)")&&
    trainingSource.includes("Math.sqrt(24 / architecture[l])")&&
    trainingSource.includes("const steps = 80000;"),"INITIALIZATION_CONTRACT");
  const init=originalInitialization();
  checkShape(model);checkShape(init);
  const templates=sourceTemplates(source),g=seededRandom(637127),events=[];
  for(let label=0;label<10;label++)
    for(let n=0;n<200;n++)
      events.push({label,x:templates[label].map(bit=>g()<0.07?1-bit:bit)});
  requireCondition(events.length===INPUTS,"EVALUATION_CASES");
  const measurements=[],checksums=[];
  for(let mask=0;mask<MASKS;mask++){
    const proto=extract(model,init,mask);
    const checkpoint=sealPrototype(proto);
    const decoded=restore(checkpoint);
    const packedAgain=sealPrototype(decoded);
    requireCondition(checkpoint.equals(packedAgain),"CHECKPOINT_ROUNDTRIP_"+mask);
    for(let rep=0;rep<3;rep++)
      requireCondition(sealPrototype(restore(Buffer.from(checkpoint))).equals(checkpoint),
        "COLD_RESTORE_"+mask);
    if(mask===15){
      for(const bit of [0,8,51,70]){
        const modified=Buffer.from(checkpoint);modified[bit]^=1;
        let rejected=false;
        try{restore(modified)}catch{rejected=true}
        requireCondition(rejected,"TAMPER_REJECT_"+bit);
      }
    }
    const perClass=Array(10).fill(0);
    for(const {label,x} of events){
      let best=0,min=36;
      for(let c=0;c<10;c++){
        let distance=0;
        for(let k=0;k<35;k++)distance+=(decoded[c][k]!==x[k]);
        if(distance<min){best=c;min=distance}
      }
      if(best===label)perClass[label]++;
    }
    const correct=perClass.reduce((a,b)=>a+b,0);
    measurements.push({
      mask,trained_layer_indices:[0,1,2,3].filter(i=>(mask&(1<<i))!==0),
      correct,accuracy:correct/INPUTS,per_class:perClass,
    });
    checksums.push(createHash("sha256").update(checkpoint).digest("hex"));
  }
  requireCondition(measurements[0].correct===230,"ORIGINAL_INITIAL_SCORE_PARITY");
  requireCondition(measurements[15].correct===1615,"ORIGINAL_TRAINED_SCORE_PARITY");
  const bestMixed=measurements.slice(1,15).reduce((a,b)=>b.correct>a.correct?b:a);
  const margin=measurements[15].accuracy-bestMixed.accuracy;
  const interaction=measurements[15].accuracy-measurements[0].accuracy-
    [1,2,4,8].reduce((a,mask)=>a+measurements[mask].accuracy-
      measurements[0].accuracy,0);
  return {
    schema:"dwsa06.frozen-layer-intervention-dev.v1",
    protocol_commit:"416429f6ea77d189876289b098718d5e44438775",
    donor_ref:REF,
    donors_executed:0,teacher_outputs_used:0,source_world_actions:0,
    registered_masks:16,examples_per_mask:INPUTS,
    same_template_world:true,unfamiliar_causal_world:false,
    checkpoint_bytes:84,cold_restores_per_mask:3,tamper_rejections:4,
    checkpoint_sha256:checksums,
    measurements,
    best_mixed_mask:bestMixed.mask,
    best_mixed_accuracy:bestMixed.accuracy,
    trained_minus_best_mixed:margin,
    leave_one_out_masks:[14,13,11,7].map(i=>({
      mask:i,accuracy:measurements[i].accuracy,correct:measurements[i].correct,
    })),
    exploratory_additive_interaction:interaction,
    criterion:(measurements[15].accuracy>=0.7&&margin>=0.10)?
      "INTERLAYER_DEPENDENCE_DEV_SIGNAL":"INTERLAYER_DEPENDENCE_DEV_NO_GO",
    strongest_preexisting_same_capacity_supervised_accuracy:0.9925,
    scientific:"UNVERIFIED",deployment:"NONE",
  };
}
requireCondition(process.argv.length===5,"CLI_PINNED_SOURCE_ARGS");
const input=process.argv.slice(2).map(p=>readFileSync(p));
input.forEach((buffer,i)=>requireCondition(gitBlob(buffer)===BLOBS[i],
  "ORIGINAL_GIT_BLOB_"+i));
const result=run(JSON.parse(input[0].toString("utf8")),
  input[1].toString("utf8"),input[2].toString("utf8"));
console.log(JSON.stringify(result,null,2));
