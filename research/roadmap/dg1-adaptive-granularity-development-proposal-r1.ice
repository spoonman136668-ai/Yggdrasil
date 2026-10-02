{
  "schema": "yggdrasil.research-proposal.v1",
  "proposal_id": "DG1-ADAPTIVE-GRANULARITY-DEVELOPMENT-PROPOSAL-R1",
  "date": "2026-10-02",
  "status": "proposed-test-candidate",
  "priority": "high",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "objective": "Test whether the existing Yggdrasil developmental substrate can grow, specialize, consolidate, hibernate, reactivate, and regenerate representational structures at different byte-span granularities while raw bytes remain the external input.",
  "substrate_preservation": "This proposal extends the existing DG-1 developmental/cellular substrate. It does not authorize replacing Yggdrasil with a conventional transformer, static tokenizer, or external-model wrapper.",
  "research_claim_to_test": "Representational granularity can itself be developmental: local raw-byte processing can give rise to reusable higher-span structures whose activation and persistence are controlled by utility and resource pressure.",
  "developmental_interpretation": {
    "raw_bytes": "environmental observations",
    "motif_cells_or_modules": "specialized structures responsive to reusable byte patterns",
    "higher_span_structures": "developmentally consolidated representations over recurring lower-level motifs",
    "hibernation": "remove expensive active structure while retaining bounded wake information",
    "regeneration": "reconstruct useful representational phenotype from persistent developmental information after pruning or lesion"
  },
  "proposed_test_ladder": [
    {
      "stage": "DGR-1",
      "name": "developmental motif specialization",
      "question": "Do repeated byte motifs cause reproducible functional specialization rather than generic frequency tracking?",
      "design": "Use frozen byte streams containing compositional motifs plus frequency-matched shuffled controls. Permit only existing bounded developmental operations.",
      "primary_metrics": [
        "motif-selective specialization",
        "causal ablation effect",
        "specialization reproducibility across seeds",
        "false-specialization rate on shuffled controls",
        "prediction gain"
      ],
      "gate": "Specialization requires intervention evidence; visual clustering alone is insufficient."
    },
    {
      "stage": "DGR-2",
      "name": "resource-pressure granularity consolidation",
      "question": "Under a fixed resource ceiling, does the system consolidate repeated local byte structure into cheaper higher-span representations while preserving capability?",
      "design": "Compare developmental granularity against fixed-byte and static-chunk controls under identical active-parameter, resident-byte, communication, and update budgets.",
      "primary_metrics": [
        "active_parameter_growth_per_capability",
        "resident_byte_growth_per_capability",
        "active_compute_per_input_byte",
        "effective represented span per active structure",
        "held-out predictive quality",
        "communication cost"
      ],
      "gate": "Compression must improve at least one preregistered resource ratio without violating the held-out capability floor."
    },
    {
      "stage": "DGR-3",
      "name": "granularity hibernate and wake",
      "question": "Can expensive motif structures hibernate and later reactivate faster than cold relearning?",
      "design": "Train reusable multi-byte structures, remove them from active execution under a frozen pressure schedule, then reintroduce relevant byte streams.",
      "primary_metrics": [
        "wake cost",
        "wake latency",
        "post-wake predictive recovery",
        "persistent bytes retained",
        "cold-retraining cost",
        "unrelated-capability preservation"
      ],
      "gate": "Wake must recover function materially cheaper than cold retraining under equal evaluation."
    },
    {
      "stage": "DGR-4",
      "name": "granularity lesion and regeneration",
      "question": "Can a specialized multi-byte representational phenotype be destroyed and regenerated from bounded persistent developmental information?",
      "design": "Apply a sealed lesion to qualified motif structures and compare regeneration against intact, erased, shuffled, and cold controls.",
      "primary_metrics": [
        "functional recovery",
        "regeneration cost",
        "regeneration latency",
        "persistent-state bytes",
        "collateral capability loss",
        "structure/function correspondence"
      ],
      "gate": "Regeneration must restore function, not merely recreate structural counts or topology."
    },
    {
      "stage": "DGR-5",
      "name": "cross-domain granularity reorganization",
      "question": "Can the same developmental substrate reuse low-level byte structures while differentiating higher-level structures for prose-like, code-like, structured-data, and binary-like domains?",
      "design": "Use disjoint domains under a shared resource ceiling and measure reuse, specialization, interference, hibernation, and reactivation.",
      "primary_metrics": [
        "shared motif reuse",
        "domain-specific specialization",
        "adaptation cost new domain",
        "resident-state growth",
        "retained capability after sequence",
        "reactivation cost",
        "catastrophic interference"
      ],
      "gate": "Claimed reusable granularity must survive sealed-domain transfer and intervention tests."
    }
  ],
  "required_controls": [
    "fixed byte-processing developmental graph",
    "static hand-specified chunk boundaries",
    "frequency-matched shuffled motifs",
    "random-boundary aggregation",
    "no-hibernation control",
    "cold retraining control",
    "fixed tokenizer/subword architecture only as an external scientific comparator"
  ],
  "north_star_ratios_to_track": [
    "active_parameter_growth / capability_growth",
    "resident_byte_growth / capability_growth",
    "adaptation_cost_new_task / adaptation_cost_first_task",
    "regeneration_cost / cold_retraining_cost",
    "retained_capability_after_sequence / total_tasks_learned",
    "active_compute_per_task / total_persistent_capacity"
  ],
  "additional_granularity_metrics": [
    "active compute per raw byte",
    "effective represented byte span per active structure",
    "motif reuse frequency",
    "motif causal-ablation effect",
    "granularity consolidation rate",
    "wake latency",
    "regeneration fidelity"
  ],
  "success_definition": "A developmental granularity advantage requires causal specialization plus a preregistered resource, transfer, hibernation, or regeneration benefit over fixed-granularity controls. Pattern appearance without causal or resource evidence is not success.",
  "failure_definition": "The hypothesis is weakened if useful byte processing requires effectively static global segmentation, higher-span structures do not improve resource ratios, hibernation loses capability, regeneration costs approach cold retraining, or fixed controls match all benefits at lower complexity.",
  "sequencing_rule": "Do not interrupt or reinterpret currently frozen DG-1 experiments. Promote one stage at a time to a separate preregistration only after prior gates are satisfied. Freeze seeds, splits, pressure schedules, resource ceilings, controls, metrics, thresholds, and stop rules before implementation.",
  "authority": "proposal only; synthetic computational research only; no wetware, production, scheduler, queue-consumer, accepted-ref, deployment, runtime, broker, or external-model inference authority"
}
