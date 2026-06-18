# scripts/

Pipeline scripts and supporting utilities. Generic and config-driven
since Tier B.1 (2026-05-15). Gene-family-specific behaviour lives in
`config/<gene_set>.yaml`; project-level genome architecture lives in
`data/genome_config.yaml`. Scripts share a `_config.py` helper that
loads both and derives the chromosome → subgenome / homeolog-pair
mapping at startup.

A new user applying the workflow to a different gene set edits a
copy of `config/template.yaml` rather than the script source.

## Pipeline drivers (canonical)

Run in order to reproduce the worked example, or with
`--config config/<your_gene_set>.yaml` for a new application.

| Script | Stage | What it does |
|---|---|---|
| `check_env.py` | — | Verify Python version (>=3.10) and required packages before running the pipeline; no config, no network. Run first. |
| `download_genome_files.py` | 1 | Download the RefSeq GFF and protein FASTA for each species in `data/genome_config.yaml`, directly from the NCBI file server (one step; see GETTING_STARTED.md) |
| `identify_gene_set.py` | 2 | Parse each GFF for gene-set members per the config's inclusion/exclusion rules; write per-species + combined gene lists |
| `extract_sequences.py` | 2 | Extract the gene-set members' protein sequences from the local protein FASTA (preferred; no network) |
| `download_sequences.py` | 2 | NCBI API fallback for protein sequences when the local FASTA is unavailable |
| `clean_sequences.py` | 2 | Dedup and QC the protein FASTAs |
| `build_gene_inventory.py` | 3c | One row per gene across all species, with annotation-quality and gene-model-quality flags |
| `extract_synteny.py` | 3d | Flanking-gene neighbourhoods around each gene-set member; produces `<gene_set>_synteny_extraction_all_pairs.txt` |
| `build_hierarchy_explorer.py` | 5 | Interactive HTML explorer from curation-data JSON — the project's primary deliverable; its first layer is a chromosome map. See `scripts/templates/CURATION_DATA_SCHEMA.md`. |

## Conditional procedures

Not always run; invoked when the genome architecture requires.

| Script | When to use |
|---|---|
| `build_subgenome_lookup.py` | The goldfish lookup ships pre-built at `config/goldfish_subgenome_lookup.tsv`. Run this only to regenerate it, or to build a lookup for a new tetraploid that lacks A/B labels in its chromosome names. Reads a genome-to-genome alignment configured in `data/genome_config.yaml` and writes to `config/goldfish_subgenome_lookup.tsv`. |

## Shared helper

- **`_config.py`** — shared config loader used by every pipeline
  script. Resolves the gene-set config from the `--config` flag, else
  the `HV_HARNESS_CONFIG` env var; if neither is given it raises a clear
  error pointing at `config/template.yaml` (there is no default gene
  set). Loads the genome config, derives
  the chromosome → (label, subgenome, pair) mapping for each species
  (regex-based for Cgib/Ccar/Drer, lookup-file for Caur), and
  exposes `get_chr_info()` and `iter_species()` helpers. Also provides the
  mechanized progress/hand-off banner (`emit_banner`, `BANNER_STEPS`,
  `CHECKPOINT_GATES`) and the `--unattended` flag that every stage script
  emits at completion, so the banner and the non-suppressible checkpoint
  gates come from the scripts rather than the agent's discretion.

## Templates

- **`templates/hierarchy_explorer.html`** — base HTML for the
  hierarchy explorer, with placeholders for the title, the gene-set
  pair list, and the curation-data JSON.
- **`templates/CURATION_DATA_SCHEMA.md`** — the schema for the JSON
  consumed by `build_hierarchy_explorer.py`.

