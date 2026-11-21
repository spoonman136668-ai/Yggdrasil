"use strict";
const fs=require("fs"),path=require("path"),a=require("assert").strict;
const p=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
const r=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const source=fs.readFileSync(path.join(__dirname,"run.cjs"),"utf8");
a.equal(p.id,"GATE20-BOUNDED-ONLINE-TOPOLOGY-REWIRING-20261120");
a.equal(r.prereg_commit,"c1ff29dbbdbd54444fe339982356a4913a7d0789");
a.deepEqual([r.protocol.seed_count,r.protocol.fit_A,r.protocol.fit_B,r.protocol.held_B,r.protocol.bytes],[160,64,32,16,260]);
a.equal(r.verdict,"MIXED_OR_NEGATIVE_DEV");
a.equal(r.all_scientific_thresholds_pass,false);
const cohorts={xor_pair:91000,mux3:92000,essential3:93000,unary:94000,independent_noise:95000};
const arms=["dynamic","fully_fit_fixed","frozen_A","bayesian","shuffled_B","null"];
for(const [name,start]of Object.entries(cohorts)){
 const c=r.groups[name];
 a.deepEqual([c.seeds,c.seed_first,c.seed_last],[32,start,start+31]);
 a.equal(c.cold_continuations_exact,32);a.equal(c.held_disjoint,32);a.equal(c.source_A_retained,32);
 a(c.graph_mutated<=32&&c.final_graph_changed<=32);
 a(c.spawn+c.prune+c.swap>=c.graph_mutated);
 for(const k of arms)a(c.means[k]>=0&&c.means[k]<=1);
 const close=(v,w)=>a(Math.abs(v-w)<2e-9,"paired arithmetic mismatch");
 close(c.means.frozen_A-c.means.dynamic,c.gain_vs_frozen_A.mean);
 close(c.means.fully_fit_fixed-c.means.dynamic,c.gain_vs_fully_fit_fixed.mean);
 close(c.means.dynamic-c.means.bayesian,c.deficit_to_bayes.mean);
}
const failures=Object.entries(r.conditions).filter(([,v])=>!v).map(([k])=>k).sort();
a.deepEqual(failures,["related_macro_gain_vs_fully_fit_static_ci_lower_positive","related_macro_gain_vs_fully_fit_static_min","worst_related_dynamic_deficit_to_bayes_max"].sort());
a(r.summary.related_gain_vs_frozen_A.mean>.14&&r.summary.related_gain_vs_frozen_A.ci95[0]>0);
a(r.summary.related_gain_vs_fully_fit_fixed.mean<0&&r.summary.related_gain_vs_fully_fit_fixed.ci95[1]<0);
a(r.summary.worst_related_bayes_deficit>.01);
a.equal(r.groups.independent_noise.graph_mutated,31);
const selector=source.split("function independentFullyFitFixed(rows){")[1]?.split("const fac=")[0];
a(selector&&selector.includes("for(let m=1;m<64;m++)"),"independent static implementation missing");
a(!selector.includes("dynamicRisk(")&&!selector.includes("selectSource(")&&!selector.includes("candidates(")&&!selector.includes("update("),
  "fixed selector must not call adaptive selector");
a.equal(p.frozen_accept.related_macro_gain_vs_fully_fit_static_min,.01);
a.equal(p.frozen_accept.worst_related_dynamic_deficit_to_bayes_max,.01);
process.stdout.write("GATE20_INDEPENDENT_RECEIPT_AUDIT_PASS SCIENTIFIC_NO_GO_FIXED_AND_BAYES_WIN\n");
