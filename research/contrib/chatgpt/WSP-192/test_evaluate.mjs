/** WSP-192 source-free engineering tests. Not scientific data or fitness training. */
import { evaluateWSP192 } from "./evaluate.mjs";
import assert from "node:assert/strict";

function fixture() {
  const g=Array.from({length:80},(_,i)=>"G"+String(i).padStart(3,"0"));
  const out=["gene,"+g.join(",")];
  for(let i=0;i<g.length;i++) {
    const values=[];
    for(let j=0;j<g.length;j++) values.push(i===j?"":String((i%7)*0.12+(j%7)*0.12+Math.sin(i+j)*.05));
    out.push(g[i]+","+values.join(","));
  }
  return out.join("\n")+"\n";
}
const sample=fixture(), result=evaluateWSP192(sample);
assert.equal(result.schema,"yggdrasil.wsp192.published-original-gene-fitness-dev.v1");
assert.equal(result.conditions.gene_intersection,80);
assert.equal(result.conditions.observed_unordered_pairs,3160);
assert.equal(result.conditions.split_counts.FIT+result.conditions.split_counts.VALID+result.conditions.split_counts.DEV,3160);
assert.equal(result.prereg_commit,"86f45714b623ac1f755497432aadf3bd7e63daa3");
assert.equal(result.programmed_candidate.gradient_updates,0);
assert.equal(result.bilinear_controls.length,6);
assert.equal(result.design.train_uses_dev,false);
assert.equal(result.conclusions.scientific_pass,false);
assert.equal(result.conclusions.actual_yggdrasil_training,false);
assert.equal(result.held_comparison.bootstrap_replicates,2000);
assert.ok(result.bilinear_controls.every(x=>Number.isFinite(x.fit_rmse) && Number.isFinite(x.validation_rmse)));
assert.throws(()=>evaluateWSP192("gene,A,B\nA,1,2\nB,2,1\n"),/AUTHOR_MATRIX_HEADER_MISMATCH/);
assert.throws(()=>evaluateWSP192(sample.replace("gene,G000,","gene,G000,G000,")),/DUPLICATE_COLUMN|ROW_WIDTH_MISMATCH/);
assert.throws(()=>evaluateWSP192(sample.replace("G000,G001","G000,G001_NONEXISTENT")),/INSUFFICIENT_GENES|ROW_WIDTH_MISMATCH/);
console.log(JSON.stringify({engineering_fixture:"PASS",tests:15,scientific_training:false,genes:80,source:"synthetic engineering-only fixture"}));
