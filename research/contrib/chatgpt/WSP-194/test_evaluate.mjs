/* WSP-194 synthetic fixture engineering checks ONLY. Not a fitness data source. */
import assert from "node:assert/strict";
import { evaluateWSP194 } from "./evaluate.mjs";
const head="mutant,mutated_sequence,DMS_score_RAF,DMS_score_PI3,DMS_score_RAL,DMS_score_SOS,DMS_score_K27,DMS_score_K55";
const aa="PQRST";
function sequence(changes){const a=Array(105).fill("A");for(const [i,z] of changes)a[i]=z;return a.join("");}
function scores(x){return [x,x*.88+.1,x*1.12-.12,x*.75+.05,x*.65-.04,x*.5+.02].join(",");}
function fixture(){
 let single=[head],multi=[head],idx=0;
 for(let p=0;p<30;p++)for(let k=0;k<5;k++) {
  single.push("M"+(idx++)+","+sequence([[p,aa[k]]])+","+scores((p-15)*.04+k*.03));
 }
 let count=0;
 for(let p=0;p<30;p++)for(let q=p+1;q<30;q++)for(let k=0;k<5;k++)for(let b=0;b<5;b++){
  if(count>=4200)break;
  multi.push("M"+(idx++)+","+sequence([[p,aa[k]],[q,aa[b]]])+","+scores((p-15)*.04+(q-15)*.04+.03*(k+b)+.01*Math.sin(p*q)));
  count++;
 }
 return {single:single.join("\n")+"\n",multi:multi.join("\n")+"\n"};
}
const {single,multi}=fixture(),result=evaluateWSP194(single,multi);
assert.equal(result.schema,"yggdrasil.wsp194.kras-native-weight-public-development.v1");
assert.equal(result.prereg_commit,"5ea08782aacd270b69c56f6393532d46d622cc06");
assert.equal(result.source.single_rows,150);
assert.equal(result.source.multi_rows,4200);
assert.equal(result.assays.length,6);
assert.equal(result.admitted_assays,6);
assert.equal(result.classification,"PUBLIC_DEV_NO_GO");
assert.ok(result.assays.every(x=>x.admitted));
assert.ok(result.assays.every(x=>x.converged_pairwise.length===3));
assert.ok(result.assays.every(x=>x.converged_pairwise.every(y=>y.converged)));
assert.ok(result.assays.every(x=>x.held.retention_weight_drift===0));
assert.ok(result.assays.every(x=>x.held.single_held_rmse_before===x.held.single_held_rmse_after));
assert.ok(result.assays.every(x=>x.direct_candidate.non_gradient_pair_updates>0));
assert.equal(result.science.scientific_pass,false);
assert.equal(result.science.native_yggdrasil_training,false);
assert.throws(()=>evaluateWSP194(single.replace("DMS_score_RAF","WRONG_ASSAY"),multi),/SOURCE_HEADER_MISMATCH/);
assert.throws(()=>evaluateWSP194(single,multi.replace("DMS_score_PI3","DMS_score_X")),/SOURCE_HEADER_MISMATCH/);
assert.throws(()=>evaluateWSP194(single.slice(0,300),multi),/SOURCE_ROW_ADMISSION_INSUFFICIENT|CSV_COLUMN_COUNT/);
assert.throws(()=>evaluateWSP194(single.replace("M0,","M0,".replace("M0","M0")).replace("P","*"),multi),/SOURCE_HEADER_MISMATCH|SEQUENCE_STRUCTURE_INVALID/);
console.log(JSON.stringify({fixture:"PASS",checks:19,science:"NOT_RUN",real_source:false}));
