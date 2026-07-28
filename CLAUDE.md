# CLAUDE.md — HV_Harness

⚠️ **Read this file and `docs/quick_start.md` in full before doing
anything else** — before running any script, before opening any config
file, before proposing any search terms. `quick_start.md` is the entry
script for a session and tells you how to begin.

---

## What this project is

HV_Harness is a human–AI workflow for exploring any group of genes in
the annotation files of the three cyprinid Cs4R allotetraploid carp
genomes — *Cyprinus carpio* (common carp), *Carassius gibelio*
(Prussian carp), and *Carassius auratus* (goldfish) — with *Danio
rerio* (zebrafish) as the diploid comparator.

The contribution is the harness itself: a structured collaboration
protocol (the playbook) plus supporting generic scripts, in which the
AI handles mechanical operations and the human curator applies domain
judgment at five explicit checkpoints. The caspase gene family is the
worked example that validated the approach; see
`examples/caspase_in_carp/`.

To apply the workflow to your own gene group, you copy
`config/template.yaml`, work through the checkpoints with the AI, and
end up with a curated inventory and an interactive hierarchy explorer.

---

## Starting a session

Read `docs/quick_start.md` and follow it. Do **not** run any pipeline
script, open a config, or propose search terms until the quick_start
conversation has been completed — the scripts are fast; the structured
conversation is the work. The one exception is the read-only
environment check (`python scripts/check_env.py`), which quick_start
tells you to run first.

---

## The two documents that govern all work

1. **`docs/curation_playbook.md`** — the methodological heart.
   Sections 0–9. This is the document a new user reads before applying
   the workflow to their gene group. It contains the governing
   principles, the five conversational checkpoints, the per-pair
   curation procedure, the decision rules, and the visualization build
   procedure. When in doubt about methodology, the playbook is the
   authority.

2. **`docs/workflow.md`** — the pipeline stage overview. Maps each
   stage to its driver script and output location. Use this to
   understand how the mechanical stages feed the interpretive stage
   (the curation).

---

## Terminology — strictly observed

These terms are defined in playbook section 0.5 and must be used
consistently throughout all project documents:

- **Homeolog / homeologous** — the A/B relationship between genes or
  chromosomes derived from the same ancestral locus in the two
  parental species. Use this, not "ohnolog."
- **Ohnolog** — do not use. Replaced by "homeolog" throughout.
- **Allopolyploidization event** — the founding hybridization event
  that created the A and B subgenomes. Do not use "WGD" (whole-genome
  duplication), which implies autopolyploidy.
- **Paralog** — genes related by duplication *within* a subgenome.
  Distinct from homeologs.
- **Homologous** — avoid in this context; ambiguous between meiotic
  homologs (two copies of A22) and the A/B homeolog relationship.

---

## Key principles (from the playbook)

- **Annotation-level evidence only.** Claims must be supportable from
  GFF and protein FASTA inputs. Sequence-level work (tBLASTn, genome
  alignment, phylogenetics) goes on the side-projects list, not in
  the curation document.
- **Synteny over similarity-based naming.** Two genes on the same
  homeologous pair with matching flanking-gene neighbourhoods are
  homeologs, regardless of what NCBI has named them.
- **Candidate loss, not confirmed loss.** A gene absent from the
  annotation at its expected syntenic position is a "candidate loss
  with annotation-level evidence." Never "confirmed loss" without
  sequence-level verification.
- **Five checkpoints.** The workflow pauses for human–AI dialogue at:
  Checkpoint 1 (search-term design, section 3.4), Checkpoint 2
  (inventory review and focal-species choice, section 5.1),
  Checkpoint 3 (empty-slots deep dive, section 6.1), Checkpoint 4
  (pre-visualization curation review, section 6.2), Checkpoint 5
  (interpretive layer design, section 6.3). The AI initiates these if
  the human does not.
- **Carry the baton.** The AI never ends a turn by silently stopping.
  Every output ends with a visible hand-off — what was produced, what
  is next, and whose turn it is — via the progress-and-hand-off banner
  (playbook section 7.3; format in `docs/quick_start.md`). The
  pipeline scripts emit this banner themselves at each stage boundary;
  relay and enrich it, never skip it.
- **Bring clarity, maintain humility.** Visualizations must not
  overstate what the annotation-level inputs support.

---

## Repository structure

```
HV_Harness/
├── CLAUDE.md                  ← you are here (project instructions for the AI)
├── AGENTS.md                  ← entry stub for non-Claude agents → CLAUDE.md
├── README.md                  ← user-facing introduction
├── GETTING_STARTED.md         ← setup + how to fetch the genome inputs
├── requirements.txt           ← core dependencies
├── requirements-full.txt      ← + optional download/regeneration deps
├── species_info.txt           ← genome accessions for the focal species
├── .gitignore
├── docs/
│   ├── curation_playbook.md   ← the methodological authority
│   ├── workflow.md            ← pipeline stage overview
│   ├── quick_start.md         ← session entry script (banner, checkpoints)
│   └── data_provenance.md     ← worked-example provenance record
├── scripts/                   ← generic pipeline scripts
│   ├── MANIFEST.md            ← per-script reference
│   ├── _config.py             ← shared config, chromosome mapping, banner helper
│   ├── check_env.py           ← environment check (run first)
│   ├── download_genome_files.py  ← Stage 1: GFF + protein FASTA per species
│   ├── identify_gene_set.py   ← Stage 2: GFF search
│   ├── extract_sequences.py   ← Stage 2: protein FASTAs (local, preferred)
│   ├── download_sequences.py  ← Stage 2: protein FASTAs (NCBI fallback)
│   ├── clean_sequences.py     ← Stage 2: dedup/QC
│   ├── build_subgenome_lookup.py  ← Stage 3a: conditional
│   ├── build_gene_inventory.py    ← Stage 3c
│   ├── extract_synteny.py         ← Stage 3d
│   ├── build_hierarchy_explorer.py   ← Stage 5
│   └── templates/             ← hierarchy explorer HTML template + schema
├── config/
│   ├── template.yaml          ← start here for a new gene set
│   ├── SCHEMA.md              ← full config field documentation
│   ├── caspase_example.yaml   ← worked example parameters
│   └── goldfish_subgenome_lookup.tsv  ← pre-built goldfish A/B labels (Stage 3a input)
├── data/
│   ├── genome_config.yaml     ← species list + chromosome-mapping rules
│   └── annotations/           ← downloaded GFF + protein FASTA (gitignored)
│                                (extracted protein FASTAs are written to
│                                 data/sequences/ at run time — generated,
│                                 not shipped)
├── examples/
│   ├── caspase_in_carp/       ← the full caspase worked example (3 focal species)
│   └── granulin_in_carp/      ← second, smaller example — proof of generality
├── tests/                     ← dependency-free invariant tests
└── results/<gene_set>/        ← run outputs (generated, namespaced per gene set)
```
