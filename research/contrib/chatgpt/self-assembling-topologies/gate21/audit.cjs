"use strict";
// Gate21 receipt/threshold/source-separation audit: does not independently reimplement the learner.
const a=require("assert").strict,fs=require("fs"),join=require("path").join;
const p=JSON.parse(fs.readFileSync(join(__dirname,"prereg.json"),"utf8"));
const r=JSON.parse(fs.readFileSync(join(__dirname,"result.json"),"utf8"));
const src=fs.readFileSync(join(__dirname,"run.cjs"),"utf8");
a.equal(p.id,"GATE21-REPEAT-EVIDENCE-GATED-REWIRING-20261120");
a.equal(r.prereg_commit,"834c26e40562e52581997b040d6a39d3f947d337");
a.equal(r.parent_commit,"90515a68cc0ffb00a6063600e9a7c2500c92702b");
a.equal(r.design.seed_trials,192);
a.deepEqual([r.design.A_fit,r.design.B_fit,r.design.B_sentinel_rows,r.design.B_held,r.design.max_persistent_bytes],[64,96,24,16,384]);
const families={xor_pair:101000,mux3:102000,essential3:103000,unary:104000,unrelated3:105000,independent_noise:106000};
for(const [name,seed]of Object.entries(families)){
 const z=r.groups[name];a.deepEqual([z.seed_first,z.seed_last,z.seeds],[seed,seed+31,32]);
 a.equal(z.cold_replay,32);a.equal(z.source_A_retained,32);a.equal(z.held_disjoint,32);a.equal(z.fit96_and_24_sentinel,32);a.equal(z.bytes384,32);
 for(const v of Object.values(z.means))a(v>=0&&v<=1);
 for(const k of ["gated_ever_edited","ungated_ever_edited","gated_final_changed","ungated_final_changed"])a(z[k]>=0&&z[k]<=32);
 const close=(x,y)=>a(Math.abs(x-y)<2e-9,"group arithmetic mismatch");
 close(z.means.fixed-z.means.gated,z.gain_vs_fixed.mean);
 close(z.means.gated-z.means.ungated,z.cost_vs_ungated.mean);
 close(z.means.gated-z.means.bayes,z.deficit_to_bayes.mean);
}
a.equal(r.groups.independent_noise.gated_final_changed,13);
a.equal(r.groups.independent_noise.ungated_final_changed,30);
a(r.summary.related_gated_cost_vs_ungated.mean>.01);
a(r.summary.related_gated_gain_vs_static.mean<-.03);
a(r.summary.related_gated_gain_vs_static.ci95[1]<0);
a(r.summary.worst_related_deficit_to_bayesian>.015);
a.equal(r.verdict,"GATED_REWIRING_MIXED_OR_NEGATIVE_DEV");
a.deepEqual(Object.keys(r.conditions).filter(k=>!r.conditions[k]).sort(),[
 "noise_gated_change_fraction_max","related_gated_gain_vs_fully_fit_fixed_ci_lower_positive",
 "related_gated_gain_vs_fully_fit_fixed_min","related_gated_vs_ungated_Brier_cost_max",
 "related_gated_vs_ungated_paired_ci_upper_max","unrelated_gated_Brier_regression_vs_fully_fit_fixed_max",
 "worst_related_gated_deficit_to_bayesian_max"].sort());
const staticSource=src.split("function staticFit(rows){")[1]?.split("const lf=")[0];
a(staticSource&&staticSource.includes("for(let m=1;m<64;m++)"),"static exhaustive selector missing");
a(!staticSource.includes("cost(")&&!staticSource.includes("nearby(")&&!staticSource.includes("receive("),"static calls adaptive selection");
a(src.includes("val=s.B.filter(r=>r[2])")&&src.includes("fit=s.B.filter(r=>!r[2])"),"witness split source check");
a.equal(p.frozen_thresholds.noise_gated_change_fraction_max,.20);
a.equal(p.frozen_thresholds.related_gated_gain_vs_fully_fit_fixed_min,.01);
a.equal(p.frozen_thresholds.related_gated_vs_ungated_Brier_cost_max,.01);
process.stdout.write("GATE21_INDEPENDENT_RECEIPT_AUDIT_PASS SCIENTIFIC_NO_GO_NOISE_REWIRE_REMAINS\n");
