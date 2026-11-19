/** WSP-192 offline reproducibility runner. No network, no file writes, no original-world actions. */
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { evaluateWSP192 } from "./evaluate.mjs";
const ROOT=dirname(fileURLToPath(import.meta.url));
if(process.argv.length!==3)throw Error("USAGE: node reproduce.mjs /absolute/path/to/processed_fitnesses.csv");
const path=resolve(process.argv[2]),buf=readFileSync(path);
const hash=createHash("sha1").update(Buffer.from("blob "+buf.length+"\0")).update(buf).digest("hex");
const SOURCE_BLOB="c3609fe77b10e8b18d61bde816743528e42a0533";
if(hash!==SOURCE_BLOB)throw Error("WSP192_SOURCE_GIT_BLOB_MISMATCH expected="+SOURCE_BLOB+" actual="+hash);
const candidate=evaluateWSP192(buf.toString("utf8"));
const sealed=JSON.parse(readFileSync(resolve(ROOT,"result.json"),"utf8"));
function eq(a,b,label) { if(!Number.isFinite(a)||Math.abs(a-b)>1e-12*Math.max(1,Math.abs(a),Math.abs(b)))throw Error("WSP192_NONREPRODUCIBLE_"+label+" "+a+" vs "+b); }
eq(candidate.programmed_candidate.dev_rmse,sealed.programmed_candidate.dev_rmse,"CANDIDATE");
eq(candidate.selected_strong_control.dev_rmse,sealed.selected_strong_control.dev_rmse,"STRONG_CONTROL");
eq(candidate.held_comparison.gain_vs_selected_strong_control,sealed.held_comparison.gain_vs_selected_strong_control,"GAIN");
eq(candidate.held_comparison.bootstrap_95_lower,sealed.held_comparison.bootstrap_95_lower,"LOW_CI");
eq(candidate.held_comparison.bootstrap_95_upper,sealed.held_comparison.bootstrap_95_upper,"HIGH_CI");
if(candidate.conclusions.development!==sealed.conclusions.development)throw Error("WSP192_NONREPRODUCIBLE_CLASS");
process.stdout.write(JSON.stringify({reproduction:"PASS",source_blob:hash,primary_commit:"caef27604605491cc459eb4a99165963ac383078",development:sealed.conclusions.development,scientific_pass:false,tool_runtime_ms:candidate.runtime.internal_milliseconds})+"\n");
