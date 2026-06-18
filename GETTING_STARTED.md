# Getting started with HV_Harness

HV_Harness is a human-AI workflow for exploring gene groups in the
annotated allotetraploid carp genomes. You work alongside an AI
assistant — it handles the mechanical steps while you apply domain
judgment at structured decision points.

For what the project is and what you'll produce, see `README.md`. This
guide is the hands-on part: setting up the tools, fetching the genome
inputs, and starting your first session.

---

## What you need before starting

- An AI assistant connected to this folder (e.g. Claude in Cowork,
  Claude Code, or a compatible agent)
- A gene group you want to explore (a gene family, pathway, or any
  custom list)
- Roughly 1–3 hours for a first run, depending on how many homeolog
  pairs your gene group spans

You do **not** need bioinformatic experience. You do need enough
domain knowledge to recognise your gene group and judge whether the
AI's identity calls look right.

---

## Set up your environment (once)

The scripts are plain Python and depend on a few packages. You need
**Python 3.10 or newer**. From inside the HV_Harness folder:

```bash
# optional but recommended — keeps these packages isolated:
python -m venv .venv && source .venv/bin/activate

# install the dependencies (core = pandas + pyyaml):
pip install -r requirements.txt
# (optional — only if you use the NCBI download fallback rather than
#  local protein FASTAs:  pip install -r requirements-full.txt)

# confirm Python and the packages are ready:
python scripts/check_env.py
```

`check_env.py` is read-only and needs no internet. It reports whether
your Python version and the required packages are in place and prints
the exact command to fix anything missing. Run it once before your
first session — it removes the usual guesswork about Python versions
and virtual environments.

---

## Genome data files (do this once before your first session)

The workflow needs two genome files per species — the annotation
(GFF) and the protein sequence file (FASTA). These are too large to
ship in the repository, so you download them once before starting.
You only need files for the species you plan to use; a good starting
point is one carp species plus zebrafish.

### The one-step way (recommended)

From inside the HV_Harness folder:

```bash
# all four focal species (three carps + zebrafish):
python scripts/download_genome_files.py

# or just the ones you need:
python scripts/download_genome_files.py --species Carassius_gibelio Danio_rerio
```

This fetches both files for each species directly from the NCBI file
server (not the rate-limited Entrez API), verifies each download, and
skips anything already present. If a file fails, it prints the exact
manual command to run. Each file downloads in 1–2 minutes.

### The manual way (fallback)

If you would rather download by hand — or a script download failed —
run the commands below from inside the HV_Harness folder, placing
each file in `data/annotations/<species>/`. (These are the same URLs
the script uses; you can also print them with
`python scripts/download_genome_files.py --print-commands`.)

**GFF annotation files:**

| Species | Assembly | GFF curl command |
|---|---|---|
| *Carassius gibelio* | GCF_023724105.1 | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/023/724/105/GCF_023724105.1_carGib1.2-hapl.c/GCF_023724105.1_carGib1.2-hapl.c_genomic.gff.gz" -o "data/annotations/Carassius_gibelio/Carassius_gibelio_genomic.gff.gz"` |
| *Cyprinus carpio* | GCF_018340385.1 | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/018/340/385/GCF_018340385.1_ASM1834038v1/GCF_018340385.1_ASM1834038v1_genomic.gff.gz" -o "data/annotations/Cyprinus_carpio/Cyprinus_carpio_genomic.gff.gz"` |
| *Carassius auratus* | GCF_003368295.1 | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/003/368/295/GCF_003368295.1_ASM336829v1/GCF_003368295.1_ASM336829v1_genomic.gff.gz" -o "data/annotations/Carassius_auratus/Carassius_auratus_genomic.gff.gz"` |
| *Danio rerio* | GCF_049306965.1 (GRCz12tu) | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/049/306/965/GCF_049306965.1_GRCz12tu/GCF_049306965.1_GRCz12tu_genomic.gff.gz" -o "data/annotations/Danio_rerio/Danio_rerio_genomic.gff.gz"` |

**Protein FASTA files** (placed alongside the GFF — the workflow
extracts the gene-set sequences from these local files rather than
making unreliable NCBI API calls):

| Species | Protein FASTA curl command |
|---|---|
| *Carassius gibelio* | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/023/724/105/GCF_023724105.1_carGib1.2-hapl.c/GCF_023724105.1_carGib1.2-hapl.c_protein.faa.gz" -o "data/annotations/Carassius_gibelio/Carassius_gibelio_protein.faa.gz"` |
| *Cyprinus carpio* | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/018/340/385/GCF_018340385.1_ASM1834038v1/GCF_018340385.1_ASM1834038v1_protein.faa.gz" -o "data/annotations/Cyprinus_carpio/Cyprinus_carpio_protein.faa.gz"` |
| *Carassius auratus* | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/003/368/295/GCF_003368295.1_ASM336829v1/GCF_003368295.1_ASM336829v1_protein.faa.gz" -o "data/annotations/Carassius_auratus/Carassius_auratus_protein.faa.gz"` |
| *Danio rerio* | `curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/049/306/965/GCF_049306965.1_GRCz12tu/GCF_049306965.1_GRCz12tu_protein.faa.gz" -o "data/annotations/Danio_rerio/Danio_rerio_protein.faa.gz"` |

Whichever way you choose, the files for your chosen species must be
in place before you start a session.

The `-o` targets above rename each file to a canonical
`<species>_genomic.gff.gz` / `<species>_protein.faa.gz`, but this is no
longer required: the workflow also recognises files left under their
native RefSeq names (e.g. `GCF_049306965.1_GRCz12tu_genomic.gff.gz`) as
long as they sit in the right `data/annotations/<species>/` folder.
Chromosome labels are read from each annotation itself, so a newer
assembly **version** of any species can be dropped in and run without
editing `data/genome_config.yaml`.

---

## How to start a session

Open the AI assistant, connect it to this folder, and send this
opening message:

> "I want to explore a gene group in the carp polyploid genomes.
> Please read CLAUDE.md before we begin."

That's it. The AI will read the project instructions and guide you
through the rest — asking what gene group you want, which species to
start with, and how you'd like to work through the curation.

**Do not give the AI a detailed task upfront.** Let it ask you the
questions. The structured conversation is the first and most
important part of the workflow.

---

## What to expect

The workflow has six stages:

1. **Gene group and species** — you tell the AI what you're looking
   for and where to start. Recommended: one carp species plus
   zebrafish to begin.

2. **Search term design** — the AI works with you to define what
   to search for in the annotation files. This is Checkpoint 1.

3. **Gene list review** — the AI searches the annotations and shows
   you the results. You check for false positives and missing genes.
   This is Checkpoint 2.

4. **Per-pair curation** — the AI works through each homeologous
   chromosome pair, identifying genes, checking synteny, and flagging
   uncertain cases (including empty A/B slots). You can do this
   collaboratively (pair by pair) or leave the AI to produce a draft
   you review afterwards.

5. **Empty-slots deep dive** — the AI takes a closer look at the empty
   slots flagged during curation, searching the syntenic region for an
   explanation and resolving each into an explicit "candidate loss" or
   other call with you. This is Checkpoint 3.

6. **Visualization** — the AI builds an interactive HTML explorer
   showing your gene group across the carp genomes. You review the
   design before it is built (Checkpoints 4 and 5).

---

## If something goes wrong

If the AI starts running scripts without asking you questions first,
it has not read the project instructions. Stop it and say:

> "Please stop. Read CLAUDE.md and docs/quick_start.md before doing
> anything else."

If `download_genome_files.py` reports a failure, it prints the exact
`curl` command for the file that failed — run that directly, or paste
it to the AI. The same commands are in the genome-data-files section
above.

---

## Where outputs go

All outputs from a session land in `results/` inside this folder:

- `results/identification/` — gene lists, inventory, synteny files,
  curation document
- `results/explorers/` — interactive HTML visualization

---

## Further reading

- `docs/curation_playbook.md` — the full methodology, including
  decision rules and the reasoning behind every step
- `docs/workflow.md` — the pipeline stage overview
- `README.md` — project description and scope
