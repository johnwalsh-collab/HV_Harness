# HV_Harness

A human-AI workflow for exploring gene annotation files in allopolyploid genomes.

## What this is

HV_Harness is a structured collaboration protocol — a playbook plus supporting scripts — that lets a biology-literate researcher work with an AI assistant to produce a synteny-grounded inventory and visualization of any group of genes in the cyprinid Cs4R allopolyploid genomes (common carp, Prussian carp, goldfish), using only publicly available annotation files.

The researcher supplies domain expertise at specific decision points. The AI handles the mechanical operations: parsing GFF annotation files, extracting flanking-gene neighbourhoods, matching protein motifs, and generating outputs. The result is a per-pair curation document and an interactive hierarchy explorer that organizes the gene inventory by homeologous slot.

The workflow was developed and validated on the caspase gene family. The full worked example — curation documents, gene inventory, synteny evidence, and interactive explorers for all three focal carp species — ships in this repo under `examples/caspase_in_carp/`.

## What you will produce

An **interactive hierarchy explorer** organizing the curated inventory by homeologous slot. Its first layer is a chromosome map showing all annotated members of your gene group across all four species; deeper layers add per-pair calls and per-gene detail, with confidence and quality annotation throughout.

## Where to start

New here? Use `GETTING_STARTED.md` first — it covers installing the tools and fetching the genome inputs. For the methodology, read `docs/curation_playbook.md`: the procedure, the governing principles, and the five conversational checkpoints where the researcher's expertise guides the analysis. When you begin a working session, your AI assistant follows `docs/quick_start.md`, the session entry script.

In short: this README is orientation, `GETTING_STARTED.md` is the practical setup-and-first-run guide, the playbook is the methodology, and `quick_start.md` is what the assistant runs each session.

## Repository structure

```
HV_Harness/
├── CLAUDE.md                       ← read this first — project instructions for an AI assistant
├── AGENTS.md                       ← entry stub for non-Claude agents → CLAUDE.md
├── GETTING_STARTED.md              ← setup + how to fetch the genome inputs
├── docs/
│   ├── curation_playbook.md        ← start here (the methodology)
│   ├── workflow.md                 ← pipeline stage overview
│   ├── quick_start.md              ← user-session entry script
│   └── data_provenance.md          ← worked-example provenance
├── scripts/                        ← generic pipeline scripts
│   ├── MANIFEST.md                 ← per-script reference
│   ├── templates/                  ← hierarchy-explorer HTML template + curation-data schema
│   ├── _config.py                  ← shared config + chromosome-mapping loader
│   ├── check_env.py                ← environment check (run first)
│   ├── download_genome_files.py    ← Stage 1: GFF + protein FASTA per species
│   ├── identify_gene_set.py        ← Stage 2: extract genes from GFF
│   ├── extract_sequences.py        ← Stage 2: protein FASTAs (local, preferred)
│   ├── download_sequences.py       ← Stage 2: protein FASTAs (NCBI fallback)
│   ├── clean_sequences.py          ← Stage 2: dedup / QC
│   ├── build_subgenome_lookup.py   ← conditional: assign A/B by alignment
│   ├── build_gene_inventory.py     ← Stage 3c: one-row-per-gene inventory
│   ├── extract_synteny.py          ← Stage 3d: flanking-gene neighbourhoods
│   └── build_hierarchy_explorer.py  ← Stage 5: interactive HTML explorer
├── config/
│   ├── template.yaml               ← annotated template for a new gene set
│   ├── SCHEMA.md                   ← full config field documentation
│   ├── caspase_example.yaml        ← the config used for the worked example
│   └── goldfish_subgenome_lookup.tsv  ← pre-built goldfish A/B labels
├── data/
│   ├── genome_config.yaml          ← species list + chromosome-mapping rules
│   └── annotations/                ← downloaded GFF + protein FASTA (gitignored)
├── examples/
│   ├── caspase_in_carp/            ← the full, signed-off caspase worked example (all 3 focal species)
│   └── granulin_in_carp/           ← second, smaller example (common carp only) — proof of generality
├── tests/                          ← fixture tests for pipeline invariants
├── species_info.txt                ← genome accessions for the four focal species
├── requirements.txt                ← core dependencies (pandas, pyyaml)
└── requirements-full.txt           ← + optional extras (NCBI-download fallback)
```

Each run's output lands in `results/<gene_set>/` (gitignored — regenerated
per run, not shipped).

## Applying this to a new gene group

First-time setup (once): with **Python 3.10+**, run `pip install -r requirements.txt`, then `python scripts/check_env.py` to confirm the environment. See `GETTING_STARTED.md` for details. Then:

1. Read `docs/curation_playbook.md` section 0 to understand the procedure and its scope.
2. Copy `config/template.yaml` to `config/<your_gene_set>.yaml` and fill it in (Checkpoint 1 in the playbook walks you through this with an AI assistant).
3. Run the pipeline stages described in `docs/workflow.md`, using your config.
4. Follow the playbook's per-pair curation procedure with an AI assistant.
5. Generate the outputs using `build_hierarchy_explorer.py`.

## Scope

This workflow is designed for:
- Allopolyploid (Cs4R) cyprinid genomes with chromosome-level assemblies
- Publicly available NCBI-style annotations (GFF + protein FASTA)
- Any group of genes a researcher wants to organize and visualize — formal gene families, functional categories, or custom lists

It is not designed for diploid genomes, scaffold-only assemblies, or automated classification without human curation.

## Worked examples

The caspase gene family, curated independently in all three focal carp species (*Cyprinus carpio*, *Carassius gibelio*, *Carassius auratus*), is the primary validation case. The full curation record — per-pair curation documents, curation-data JSON, gene inventory, synteny evidence, and interactive hierarchy explorers — ships in this repo under `examples/caspase_in_carp/`. See `examples/caspase_in_carp/README.md` for a guide to those files.

A second, smaller example — the granulin gene family in common carp only — ships under `examples/granulin_in_carp/`. It exists to demonstrate that the harness generalizes beyond caspases, including a run with a different AI agent; it's a deliberately narrower, partial-coverage curation rather than a second comprehensive worked example. See `examples/granulin_in_carp/README.md`.

## What the workflow does and does not claim

Every inference here is **annotation-level**: each claim is supportable from the GFF and protein-FASTA inputs alone. No sequence-level analysis (tBLASTn against unannotated regions, whole-genome alignment, phylogenetic reconstruction) is performed. The practical consequence is that an absent gene is reported as a **candidate loss with annotation-level evidence**, never a confirmed loss — the workflow can say where a slot is and that nothing is annotated in it, not what occupies it. Questions needing sequence-level evidence are logged to a side-projects list rather than answered.

The output is not a definitive gene list. It is a disambiguated starting representation, with confidence and ambiguity recorded per call, from which downstream work can proceed.

## Citing this work

If you use HV_Harness, please cite both the software and the paper describing it. `CITATION.cff` in this repository carries both records, and GitHub renders a "Cite this repository" button from it.

**Software.** Archived on Zenodo. Cite the concept DOI — it always resolves to the latest release:

> Walsh, J.G. HV_Harness: a human–AI workflow for synteny-grounded gene-family curation in allotetraploid carp genomes. https://doi.org/10.5281/zenodo.21654547

To pin the exact snapshot behind a published result, cite the version DOI instead: v1.0.1 is [10.5281/zenodo.21654548](https://doi.org/10.5281/zenodo.21654548).

**Paper.** Walsh, J.G. (2026) *Synteny over similarity: human–AI curation of the caspase family in allopolyploid carp genomes.* bioRxiv. <!-- DOI pending — fill on posting -->

The manuscript's worked example is the caspase curation under `examples/caspase_in_carp/`, including the interactive hierarchy explorers that Figures 2 and 3 are rendered from.

## License

MIT — see `LICENSE`. The genome annotations the workflow consumes are public NCBI RefSeq data and are not redistributed here; `GETTING_STARTED.md` explains how to fetch them, and `docs/data_provenance.md` records the accessions used for the worked example.
