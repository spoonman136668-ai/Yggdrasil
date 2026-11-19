/* WSP-196 source-free engineering controls. Never biological training. */
import assert from "node:assert/strict";
import { evaluateWSP196 } from "./evaluate.mjs";
const header="mut\tHD\tInput\tIGG10\tIGG20\tIGG90\tI10fit\tI20fitRaw\tI90fit\tAOfit\tI20fit";
const pad="FR_R\t0\t20\t1\t1\t1\t1\tNA\t1\tNA\tNA";
const wt="VDGV\t0\t20\t1\t1\t1\t1\t1\t1\tNA\t1";
const invalidAA="VDG?\t0\t20\t1\t1\t1\t1\t1\t1\tNA\t1";
const source=(count,tail=wt)=>header+"\n"+Array(count).fill(pad).join("\n")+"\n"+tail+"\n";
assert.throws(()=>evaluateWSP196(""),/SOURCE_BYTES_INVALID/);
assert.throws(()=>evaluateWSP196("wrong "+("x".repeat(200))),/ORIGINAL_11_COLUMN_HEADER_MISMATCH/);
assert.throws(()=>evaluateWSP196(source(32586)),/ORIGINAL_PLACEHOLDER_ROSTER_DRIFT/);
assert.throws(()=>evaluateWSP196(source(32587)),/SOURCE_MEASURED_HD_COHORT_MINIMUM/);
assert.throws(()=>evaluateWSP196(source(32587,invalidAA)),/MUTANT_ALPHABET_OR_LENGTH/);
const s=source(32587,wt)+"VDGV\t0\t20\t1\t1\t1\t1\t1\t1\tNA\t1\n";
assert.throws(()=>evaluateWSP196(s),/DUPLICATE_GB1_GENOTYPE/);
console.log(JSON.stringify({checks:6,status:"SOURCE_FREE_PASS",original_numeric_values_used:false}));
