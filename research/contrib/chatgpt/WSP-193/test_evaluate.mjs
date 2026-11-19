/** WSP-193 source-free fixture: never scientific evidence. */
import { evaluateWSP193 } from "./evaluate.mjs";
import assert from "node:assert/strict";
function fixture(){
 const old="ACDEFGHIKLMN",new1="PQRST",new2="VWXYZAB";
 let index=0,lines=[",mutant,mutated_sequence,DMS_score_SPG1_STRSG_Olson_2014.csv,DMS_score_SPG1_STRSG_Wu_2016.csv"];
 for(let i=0;i<12;i++)for(let j=i+1;j<12;j++)for(let a=0;a<5;a++)for(let b=0;b<7;b++){
  const mut=old[i]+(i+1)+new1[a]+":"+old[j]+(j+1)+new2[b];
  const y=Math.sin(i*.7+j*.5+a*.3+b*.2)+i*.05+b*.02;
  lines.push((index++)+","+mut+",TESTSEQ,"+y+","+(y*.8+j*.02));
 }
 return lines.join("\n")+"\n";
}
const input=fixture(), result=evaluateWSP193(input);
assert.equal(result.schema,"yggdrasil.wsp193.real-protein-fitness-public-development.v1");
assert.equal(result.prereg_commit,"231e0f0989a6b90f032822e744ff040b9fc56724");
assert.equal(result.source.rows,2310);
assert.equal(result.assays.length,2);
assert.equal(result.assays[0].counts.fit_multi+result.assays[0].counts.valid_multi+result.assays[0].counts.dev_multi,2310);
assert.ok(result.assays.every(a=>a.counts.fit_mutation_sites>=10));
assert.ok(result.assays.every(a=>a.programmed_candidate.pair_gradient_updates===0));
assert.ok(result.assays.every(a=>a.polynomial_pair_controls.length===3));
assert.ok(result.assays.every(a=>Number.isFinite(a.held.gain_over_strongest)));
assert.ok(result.assays.every(a=>a.held.bootstrap_pair_variants===1000));
assert.equal(result.science.scientific_pass,false);
assert.equal(result.science.native_yggdrasil_training,false);
assert.throws(()=>evaluateWSP193(input.replace("mutated_sequence,","mutated_sequence_BAD,")),/SOURCE_HEADER_MISMATCH/);
assert.throws(()=>evaluateWSP193(input.replace("A1P:C2V","A1P/A1Q")),/MUTATION_DUPLICATE_SITE/);
assert.throws(()=>evaluateWSP193(input.replace("A1P:C2V","A1P_C2V")),/MUTATION_FORMAT_UNSUPPORTED/);
assert.throws(()=>evaluateWSP193(input.slice(0,500)),/SOURCE_GENOTYPES_INSUFFICIENT|SOURCE_ROW_WIDTH/);
console.log(JSON.stringify({status:"FOCUSED_FIXTURE_PASS",assertions:15,source:"synthetic-engineering-only",original_experiment_run:false}));
