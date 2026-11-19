/** WSP-195 engineering checks; synthetic values are NEVER scientific evidence.
 * Full 20^4 synthetic fixture is opt-in: node test_evaluate.mjs --full-fixture.
 */
import { evaluateWSP195 } from "./evaluate.mjs";
import assert from "node:assert/strict";
const header="mut\tHD\tInput\tIGG10\tIGG20\tIGG90\tI10fit\tI20fitRaw\tI90fit\tAOfit\tI20fit";
assert.throws(()=>evaluateWSP195(""),/SOURCE_BYTES_INVALID/);
assert.throws(()=>evaluateWSP195("incorrect "+("z".repeat(200))),/ORIGINAL_11_COLUMN_HEADER_MISMATCH/);
assert.throws(()=>evaluateWSP195(header+"\nNOOO\t0\t20\t1\t1\t1\t1\t1\t1\tNA\t1\n"),/HD_WT_DISAGREEMENT/);
assert.throws(()=>evaluateWSP195(header+"\n?DGV\t0\t20\t1\t1\t1\t1\t1\t1\tNA\t1\n"),/MUTANT_ALPHABET_OR_LENGTH/);
assert.throws(()=>evaluateWSP195(header+"\nVDGV\t0\t20\t1\t1\t1\t1\t-3\t1\tNA\t1\n"),/INVALID_FITNESS_VALUE/);
assert.throws(()=>evaluateWSP195(header+"\nVDGV\t0\t20\t1\t1\t1\t1\t1\t1\tNA\t1\n"),/SOURCE_MEASURED_HD_COHORT_MINIMUM/);
if(process.argv.includes("--full-fixture")) {
 const A="ACDEFGHIKLMNPQRSTVWY",W="VDGV",lines=[header];
 for(let a=0;a<20;a++)for(let b=0;b<20;b++)for(let c=0;c<20;c++)for(let d=0;d<20;d++){
  const id=A[a]+A[b]+A[c]+A[d],hd=[...id].reduce((s,v,i)=>s+(v!==W[i]),0);
  const v=Math.max(0,Math.exp(.15+Math.sin(a*.3)+Math.cos(b*.18)+Math.sin(c*.2+d*.07))-.2).toFixed(6);
  lines.push([id,hd,20,2,3,4,1,v,1,"NA",v].join("\t"));
 }
 const t=Date.now(),report=evaluateWSP195(lines.join("\n")+"\n");
 assert.equal(report.source.measured_count_by_hd.join(","),"1,76,2166,27436,130321");
 assert.equal(report.cohorts.dev,130321);
 assert.equal(report.candidate.gradient_updates,0);
 assert.equal(report.retention.serialized_and_restored,true);
 assert.ok(report.conventional_models.some(x=>x.degree===3&&x.converged));
 assert.equal(report.science.scientific_pass,false);
 assert.ok(Number.isFinite(report.held.relative_gain_vs_strong));
 console.log(JSON.stringify({fixture:"FULL_SIZE_SOURCE_FREE_PASS",elapsed_ms:Date.now()-t,rows:160000,real_data_used:false}));
}
console.log(JSON.stringify({fixture:"NEGATIVE_SOURCE_FREE_PASS",checks:6,real_data_used:false}));
