# Workflow Guide

Top-level sequencing of the HV_Harness workflow, from raw genome
annotations through curation to visualization. The mechanical stages
are scripts; the interpretive stage is the curation playbook
(`docs/curation_playbook.md`); the final output is a curated
inventory document and a hierarchical visualization.

This guide is the entry point for re-running the workflow on a new
dataset (different species, different gene family) and for following
how the existing caspase outputs were produced.

For the full project description, see the top-level `README.md`.

---

## Stage sequence

The workflow has six stages plus one conditional procedure. Stages
1–3d are mechanical (scripts); Stage 3a runs only when the anchor
assembly lacks A/B subgenome labels; Stage 3e is interpretive (the
playbook); Stage 5 is mostly mechanical; Stage 4 is
preliminary work that lives in `side_projects/` and is not part of
the core deliverable.

The scripts are generic and config-driven; gene-family-specific
behaviour lives in `config/<gene_set>.yaml`. A new application is
started by copying `config/template.yaml`, not by editing script
source. The caspase worked example runs from
`config/caspase_example.yaml`.

| Stage | What it produces | Driver | Output location |
|---|---|---|---|
| 1 — Acquire genome files | Per-species RefSeq GFF + protein FASTA (bulk reference files) | `scripts/download_genome_files.py` | `data/annotations/<species>/<species>_genomic.gff.gz` and `<species>_protein.faa.gz` |
| 2 — Identify gene-set members | Raw gene list per species + protein FASTAs | `scripts/identify_gene_set.py`, then `scripts/extract_sequences.py` (primary) or `scripts/download_sequences.py` (fallback), then `scripts/clean_sequences.py` | `results/identification/<gene_set>_genes_all_species*.tsv`; `data/sequences/<gene_set>_proteins_<species>*.fasta` |
| 3a — Subgenome assignment *(conditional; pre-built for goldfish)* | A/B label per chromosome, when the assembly lacks explicit labels. Ships pre-built in the repo; only run to regenerate it or to build one for a new unlabelled tetraploid. | `scripts/build_subgenome_lookup.py` (uses an NCBI assembly-to-assembly alignment at `data/alignments/genome_to_genome/`) | `config/goldfish_subgenome_lookup.tsv` |
| 3c — Gene-level inventory | One row per gene, all species, with subgenome and homeolog-pair assignment, annotation confidence, gene-model quality, and assembly-artefact flags. **Note:** the TSV has 15 `#`-prefixed comment lines before the column header; pandas users need `comment='#'` when reading it (e.g. `pd.read_csv(..., sep='\t', comment='#')`). | `scripts/build_gene_inventory.py` | `results/identification/<gene_set>_gene_inventory.tsv` |
| 3d — Synteny extraction | Flanking-gene neighbourhoods (~12 genes on each side, configurable) for every gene-set-bearing region | `scripts/extract_synteny.py` | `results/identification/<gene_set>_synteny_extraction_all_pairs.txt` |
| 3e — Per-pair curation | Curation document with one section per homeologous pair; empty A/B slots are flagged only | **`docs/curation_playbook.md` — interpretive, AI-assisted** | `results/identification/<species>_<family>_curation.md` |
| 3f — Empty-slots deep dive (Checkpoint 3) | The flagged empty slots resolved into explicit loss calls via the in-region sweep + cross-species reasoning; updates the curation document and its "Empty slots — assessed" table | **`docs/curation_playbook.md` §6.1 — interpretive, AI-assisted** | updates `results/identification/<species>_<family>_curation.md` |
| 4 — Phylogenetics *(side project; preliminary)* | Gene-tree alignments and IQ-TREE output | `side_projects/phylogenetic_analysis/scripts/*.py` | `side_projects/phylogenetic_analysis/` (flagged preliminary; see its MANIFEST) |
| 5 — Hierarchy explorer | Interactive HTML visualization of the curated inventory, organised by homeolog slots | `scripts/build_hierarchy_explorer.py` (consumes a curation-data JSON; see `scripts/templates/CURATION_DATA_SCHEMA.md`) | `results/explorers/<species_short>_<gene_set>_hierarchy.html` |

**Note on Stage 3b.** An earlier version of this document listed a
separate Stage 3b — a manually-produced cross-species homeolog pair
table. That step is now absorbed into Stage 3c: `build_gene_inventory.py`
assigns `homeolog_pair` and `subgenome` to every gene directly from
`data/genome_config.yaml`. Some curators find it useful to produce a
quick cross-species pair overview from the 3c output before starting
curation (3e), but this is optional and no downstream script requires
it. Stage 3b is therefore not listed as a named stage.

---

## Where the playbook fits

Stage 3e — the per-pair curation — is the interpretive heart of the
workflow. It cannot be reduced to a script because it requires
judgment: synteny vs naming conflicts, candidate-loss assessment,
within-cluster ambiguity, identity calls. The
`docs/curation_playbook.md` document captures that judgment as an
explicit procedure with decision rules and templates, so an AI
assistant working with a careful project lead can reproduce the
quality of the existing Cgib curation on a new gene family.

The playbook consumes the outputs of Stages 1–3d and produces the
curation MD that becomes the input to Stage 5.

---

## Re-running on a different gene set

The workflow's design goal is that a new user, with AI assistance,
can apply it to a different gene set in the same three carp genomes
without editing scripts.

1. **Define the gene set via the playbook's Checkpoint 1
   conversation.** Decide on inclusion patterns (name regexes and
   description keywords), exclusion patterns (false-positive gene
   names and disqualifying description substrings), and any borderline
   cases to flag. Both before and after the initial gene list is
   generated, the human + AI review the candidate set for false
   positives and false negatives, iterating on the config until the
   set is stable. The conversation produces a YAML config in
   `config/<your-gene-set>.yaml` (copied from `config/template.yaml`).
2. **Run the pipeline pointing at the new config:**
   `python scripts/identify_gene_set.py --config config/<your-gene-set>.yaml`
   and similarly for `build_gene_inventory.py`,
   `extract_synteny.py`, and `build_hierarchy_explorer.py`.
3. **Run Stage 3e** by handing the curation playbook plus the new
   inventory to an AI assistant. The playbook prescribes per-pair
   curation regardless of the gene set.
4. **Output is automatic for any chosen anchor carp.** The chromosome
   maps and hierarchy explorer come out of the standard scripts
   using your config's interpretive-layer parameters (functional
   categorisation, colour scheme, etc.).

---

## Re-running on a different species set

If new allopolyploid genomes become available, the workflow extends
naturally:

1. Add the new species to `species_info.txt` with its assembly
   accession.
2. Re-run Stage 1 (`download_genome_files.py`) to fetch the new
   annotation and protein FASTA.
3. If the new species lacks explicit subgenome labels in its
   chromosome names, fetch an assembly-to-assembly alignment between
   it and a labelled reference (NCBI Datasets), and run a Stage 3a
   step adapted from `build_subgenome_lookup.py`.
4. Run Stages 2–3d as before.
5. Apply the playbook (Stage 3e) to produce a curation for the new
   species.

The principles in the playbook are not species-specific; they apply
to any genome that has undergone a recent allopolyploidization event.

---

## Quick-reference paths

The project's standard layout (see top-level `README.md` for full
description):

```
data/annotations/<species>/                 GFF inputs, gzipped (six species)
data/alignments/genome_to_genome/           goldfish↔gibelio alignment for Stage 3a
data/sequences/                             extracted protein FASTAs
scripts/                                    mechanical pipeline (Stages 1–3d, 5)
scripts/archive/                            earlier-stage exploratory scripts
config/                                     gene-set configs
results/identification/                     curated TSVs + curation MD
results/identification/archive/             part2 exploration, etc.
results/synteny/                            synteny tables + plain-language methods
results/explorers/                          hierarchy explorer HTML (primary output)
results/SESSION_STATUS.md                   live hand-off / resume state (scratch, gitignored)
side_projects/phylogenetic_analysis/        preliminary Stage 4 work
docs/                                       this file + the curation playbook + data provenance
docs/archive/                               historical docs
tools/                                      local MAFFT and IQ-TREE binaries (gitignored)
```

Each results subfolder has a `MANIFEST.md` describing what's
canonical vs intermediate.

---

## Tools and dependencies

Python dependencies are split by need. `requirements.txt` is the core
runtime — `pandas` + `pyyaml` — and is all that's required to regenerate
the inventory and synteny outputs. `requirements-full.txt` adds the
optional extras: `biopython` + `requests` (the NCBI download fallback in
`download_sequences.py`).

The two non-Python tools used in the side-project Stage 4 are MAFFT
(for sequence alignment) and IQ-TREE (for tree construction). They
are not required by the core deliverable. The macOS-arm builds are
bundled in `tools/` for convenience but should be reinstalled locally
on other platforms; they are excluded from version control.

For provenance details (assembly versions, download dates, tool
versions used), see `docs/data_provenance.md`.

---

## Minimum viable re-run sequence

For a reader who wants to verify or rerun the caspase worked example
end to end:

```
# Each script accepts --config config/<gene_set>.yaml. There is no
# default config: pass --config, or set HV_HARNESS_CONFIG (start from
# config/template.yaml).
1.  python scripts/download_genome_files.py    # GFF + protein FASTA for each species
2.  python scripts/identify_gene_set.py
3.  python scripts/extract_sequences.py       # preferred: uses local protein FASTAs
    # python scripts/download_sequences.py   # fallback: fetches from NCBI
4.  python scripts/clean_sequences.py
    → preliminary gene-list check with user (false positives / missing members)
5.  python scripts/build_subgenome_lookup.py   # only to regenerate, or for a new species lacking A/B labels (goldfish ships pre-built)
6.  python scripts/build_gene_inventory.py
    → Checkpoint 2: review the built inventory as the baseline; agree a curation plan
7.  python scripts/extract_synteny.py
8.  Curate per-pair using docs/curation_playbook.md
    → produces results/identification/<species>_<family>_curation.md
9.  python scripts/build_hierarchy_explorer.py
```

Side-project Stage 4 (phylogenetics) is independent and can be run
before or after the curation; in this project it ran before and its
output is flagged preliminary.
