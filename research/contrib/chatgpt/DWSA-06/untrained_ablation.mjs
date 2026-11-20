// DWSA-06-L: zero-teacher trained-vs-untrained weight-path ablation.
// Frozen prereg: 56341888b193d98e8aa168ed61fe8f23dc030d98.
// Invocation: node untrained_ablation.mjs ORIGINAL_model.json ORIGINAL_models.js ORIGINAL_train.mjs
// No donor inference / no network / no original-world actions / no Yggdrasil integration.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";

const SOURCE_BLOBS = [
  "16ea8cf939bfa0f5f21e227d159b11d4ff578eca",
  "6f95eea88422ceb01b3118e65cd45b9a4c065bd9",
  "1776478a312781e0866f16e1ef237fcbc1092d1a",
];
const REF = "149a2838309efe6ee5ec9e8c9689e4a321158b7d";
const SEEDS = [20261022,101,202,303,404,505,606,707,808,909,1001,2002,3003,4004,5005,6006];
const DIMS = [35,24,16,12,10];
const INSPECTIONS = 2000;
function need(cond, key) {if (!cond) throw Error("DWSA06L_REJECT_"+key)}
function gitblob(raw) {
  const prefix = Buffer.from("blob "+raw.length+"\0","utf8");
  return createHash("sha1").update(prefix).update(raw).digest("hex");
}
function random(seed) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function initialize(seed) {
  const draw = random(seed);
  return {layers: DIMS.slice(1).map((units,l) => ({
    weights: Array.from({length:units},() =>
      Array.from({length:DIMS[l]},() =>
        (draw()-0.5)*Math.sqrt(24/DIMS[l]))),
    biases: Array(units).fill(l===3?0:0.1),
  }))};
}
function product(A,B) {
  need(A[0].length === B.length, "MATRIX_PRODUCT_SHAPE");
  return A.map(row => Array.from({length:B[0].length},(_,j) => {
    let acc=0;
    for(let k=0;k<row.length;k++) acc += row[k]*B[k][j];
    return acc;
  }));
}
function compile(model) {
  need(model && Array.isArray(model.layers) && model.layers.length===4, "MODEL_LAYERS");
  for(let i=0;i<4;i++){
    const layer=model.layers[i];
    need(Array.isArray(layer.weights) && layer.weights.length===DIMS[i+1] &&
      layer.weights.every(row => Array.isArray(row) && row.length===DIMS[i] &&
      row.every(v => typeof v==="number" && Number.isFinite(v))),"MODEL_MATRIX_"+i);
  }
  let W=model.layers[3].weights;
  for(let i=2;i>=0;i--)W=product(W,model.layers[i].weights);
  return W.map((row,c)=>row.map((value,i)=>
    +(value-W.reduce((sum,r,j)=>sum+(j===c?0:r[i]),0)/9 > 0)));
}
function score(proto, samples) {
  need(proto.length===10 && proto.every(row=>row.length===35), "PROTOTYPE_SHAPE");
  let correct=0;
  const per_class=Array(10).fill(0);
  for(const {label,x} of samples) {
    let chosen=0, min=36;
    for(let c=0;c<10;c++){
      let distance=0;
      for(let i=0;i<35;i++)distance += x[i]!==proto[c][i];
      if(distance<min){min=distance;chosen=c}
    }
    if(chosen===label){correct++;per_class[label]++}
  }
  return {correct,accuracy:correct/samples.length,per_class};
}
function patternsFromSource(src) {
  const marker="export const digitPatterns = ";
  const first=src.indexOf(marker);
  need(first>=0,"TEMPLATES_MISSING");
  const rest=src.slice(first+marker.length),end=rest.indexOf("].map(");
  need(end>0,"TEMPLATES_PARSE");
  const templates=JSON.parse(rest.slice(0,end+1).replace(/,\s*]/g,"]"))
    .map(rows=>rows.join("").split("").map(Number));
  need(templates.length===10 && templates.every(v=>v.length===35 &&
    v.every(bit=>bit===0||bit===1)),"TEMPLATES_SHAPE");
  return templates;
}
function evaluate(model,src,train) {
  need(model.metadata?.seed===20261022 &&
    model.metadata?.updates===80000 &&
    model.metadata?.parameters===1598 &&
    JSON.stringify(model.metadata?.architecture)===JSON.stringify(DIMS),
    "DONOR_METADATA");
  need(train.includes("seededRandom(20261022)") &&
    train.includes("Math.sqrt(24 / architecture[l])") &&
    train.includes("const steps = 80000;"),"INITIALIZER_SPEC");
  const patterns=patternsFromSource(src);
  const draw=random(637127),samples=[];
  for(let c=0;c<10;c++)for(let repeat=0;repeat<200;repeat++)
    samples.push({label:c,x:patterns[c].map(v=>draw()<0.07?1-v:v)});
  need(samples.length===INSPECTIONS,"SAMPLES");
  const trained=score(compile(model),samples);
  need(trained.correct===1615,"DWSA06_ORIGINAL_REPRODUCTION");
  const untrained=SEEDS.map(seed=>({seed,...score(compile(initialize(seed)),samples)}));
  const maximum=Math.max(...untrained.map(v=>v.accuracy));
  const minimum=Math.min(...untrained.map(v=>v.accuracy));
  const mean=untrained.reduce((sum,v)=>sum+v.accuracy,0)/untrained.length;
  const seed_matched=untrained[0].accuracy;
  const margin_to_strongest=trained.accuracy-maximum;
  const margin_to_original_init=trained.accuracy-seed_matched;
  return {
    schema:"dwsa06.learning-specific-weight-path-dev.v1",
    prereg_commit:"56341888b193d98e8aa168ed61fe8f23dc030d98",
    original_ref:REF,
    donor_forward_calls:0,
    new_source_actions:0,
    scientific:"UNVERIFIED",
    deployment:"NONE",
    evaluation:{n:INSPECTIONS,seed:637127,source_family:"same_ten_synthetic_digit_templates",
                independently_unfamiliar_world:false},
    trained,
    untrained,
    untrained_accuracy:{minimum,mean,maximum,original_training_seed:seed_matched},
    trained_advantage:{over_max_untrained:margin_to_strongest,
                       over_exact_training_seed_init:margin_to_original_init},
    frozen_dev_decision:(trained.accuracy>=0.70 && margin_to_strongest>=0.15 &&
      margin_to_original_init>=0.15)?"LEARNING_SPECIFIC_DEV_SIGNAL":"LEARNING_SPECIFIC_DEV_NO_GO",
    comparison_note:"Strong same-footprint supervised 99.25% and symbolic 99.25% controls still win",
  };
}
need(process.argv.length===5,"USAGE_EXPECT_THREE_PINNED_SOURCE_FILES");
const originals=process.argv.slice(2).map(s=>readFileSync(s));
originals.forEach((buffer,i)=>need(gitblob(buffer)===SOURCE_BLOBS[i],"ORIGINAL_BLOB_"+i));
const report=evaluate(JSON.parse(originals[0].toString("utf8")),
                      originals[1].toString("utf8"),originals[2].toString("utf8"));
console.log(JSON.stringify(report,null,2));
