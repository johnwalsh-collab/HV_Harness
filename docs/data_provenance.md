# Data provenance — worked example

This file records the genome data used for the caspase worked example:
which assemblies were used, how subgenome identity was assigned, how
the inputs were obtained, and which curatorial priors were encoded into
the config (so the paper can separate what the harness *derived* from
what it was *given*). It exists so the worked example is reproducible
and so the paper's Methods can cite a single source of truth.

A new user applying the workflow to a different gene group does not
edit this file for their own provenance — they keep their own record.
This file documents the reference run only.

> **Status (2026-06-10):** assembly identities, roles, and subgenome
> methods below are authoritative (from `species_info.txt` and
> `data/genome_config.yaml`).
>
> **Inputs locked 2026-06-15:** the RefSeq annotation releases and the
> obtained dates in "Inputs obtained per species" are now filled, read
> directly from the downloaded GFF headers (`#!annotation-source`) and
> file mtimes in `data/annotations/`. Still *[to confirm]*: the
> per-assembly QC metrics (N50 / BUSCO / sequencing for Ccar, Caur, Drer)
> and the goldfish subgenome alignment service/version + date.
>
> **Final model (pinned 2026-06-11):** the reported worked-example
> re-run uses **Claude Opus 4.8**. The manuscript Methods (which
> currently states Claude Opus 4.6) must be updated to match; the
> manuscript is not in this repository.

---

## Assemblies

All assemblies are NCBI RefSeq. Short codes match
`data/genome_config.yaml`.

| Code | Species | Common name | Assembly accession | Ploidy | Role |
|---|---|---|---|---|---|
| Cgib | *Carassius gibelio* | Prussian carp | GCF_023724105.1 | Allotetraploid | Core — **anchor** |
| Ccar | *Cyprinus carpio* | Common carp | GCF_018340385.1 | Allotetraploid | Core |
| Caur | *Carassius auratus* | Goldfish | GCF_003368295.1 | Allotetraploid | Core |
| Drer | *Danio rerio* | Zebrafish | GCF_049306965.1 (GRCz12tu) | Diploid | Primary comparator (ancestral-state proxy) |
| Ptet | *Puntigrus tetrazona* | Tiger barb | GCF_018831695.1 | Diploid | Secondary comparator (on demand) |
| Cide | *Ctenopharyngodon idella* | Grass carp | GCF_019924925.1 | Diploid | Secondary comparator (on demand) |

The three core allotetraploids share the Cs4R allopolyploidization
event (~10–13 Mya). Zebrafish is the primary diploid comparator: its
25 chromosomes correspond to the 25 ancestral chromosome pairs of the
allotetraploids, and its annotation is the most thoroughly curated
among cyprinids. The two secondary diploids are consulted only when a
zebrafish-specific feature is suspected; for the focal curation only
the four-species set (three core + zebrafish) is required.

## Anchor species

**Cgib (*C. gibelio*, GCF_023724105.1)** is the anchor — the species
whose curation is built first, against which the other carps are
compared. It was selected on assembly quality: contig N50 ~5.1 Mb,
BUSCO ~99.5%, PacBio HiFi (2022), and explicit A/B subgenome labels
in its chromosome names (the strongest form of subgenome evidence).

## Subgenome assignment method (per species)

- **Cgib, Ccar** — subgenome and homeolog pair are read directly from
  the chromosome naming. Each chromosome's `region` feature in the GFF
  carries its label (`chromosome=A1` … `chromosome=B25`); the loader
  reads those per the species' `chromosome_rule: explicit_ab` (see
  `scripts/_config.py:derive_chromosome_mappings` and `config/SCHEMA.md`).
- **Caur** — goldfish chromosomes are numbered 1–50 with no A/B
  labels. Subgenome identity was derived once from **NCBI's
  assembly-to-assembly alignment** of goldfish (GCF_003368295.1) against
  Prussian carp (GCF_023724105.1), consumed as a GFF
  (`data/alignments/genome_to_genome/GCF_003368295.1-GCF_023724105.1.gff`).
  `scripts/build_subgenome_lookup.py` sums aligned bases per chromosome
  pair and assigns each goldfish chromosome to the subgenome of its
  best-matching Cgib chromosome. The resulting lookup
  (`config/goldfish_subgenome_lookup.tsv`) was generated **2026-05-15**.
  *[still to confirm: the exact NCBI alignment release/version — the
  alignment GFF is not retained in the repo, only the derived lookup.]*
- **Drer (and the two diploid comparators)** — each chromosome is its
  own homeolog pair; no subgenome assignment applies.

## Inputs obtained per species

For each species the workflow uses two files from the RefSeq dataset:

- the genome annotation (`*_genomic.gff.gz`)
- the protein FASTA (`*_protein.faa.gz`)

These are not stored in the repository (too large). They are placed
under `data/annotations/<species>/` and read locally by the pipeline.

| Code | RefSeq annotation release (from GFF header) | GFF obtained | Protein FASTA obtained |
|---|---|---|---|
| Cgib | `GCF_023724105.1-RS_2023_02` (annotation 2023-02-25) | 2026-01-13 | 2026-06-04 |
| Ccar | NCBI *Cyprinus carpio* Annotation Release 101 | 2026-01-13 | not downloaded |
| Caur | `GCF_003368295.1-RS_2025_06` (annotation 2025-06-18) | 2026-01-13 | not downloaded |
| Drer | `GCF_049306965.1-RS_2025_04` (annotation 2025-04-11) | 2026-06-16 | 2026-06-16 |

The **RefSeq annotation release** is the authoritative, reproducible
identifier (the `#!annotation-source` line of each `*_genomic.gff.gz`);
re-downloading the same release by accession reproduces the inputs
exactly. **Obtained** dates are the local file modification times in
`data/annotations/` (the three carp GFFs were fetched on 2026-01-13; the
Cgib protein FASTA was added 2026-06-04; the zebrafish GFF + protein
FASTA were replaced on 2026-06-16 when the comparator was updated from
GRCz11 to GRCz12tu — see the note below).

The *C. carpio* and *C. auratus* protein FASTAs were **not** downloaded,
so the model-quality `low_quality` flag (which reads the protein FASTA)
is unavailable for those two species; all GFF-derived columns are
complete for them. The protein FASTAs that were used (Cgib, Drer) are
the `*_protein.faa.gz` for the same accessions.

## Per-assembly QC

Sequencing technology and assembly identity below are sourced from the
assembly publications and the NCBI assembly pages. N50 / BUSCO values
are investigator-supplied from the NCBI assembly records (the carp rows
filled 2026-06-15, the zebrafish/GRCz12tu row 2026-06-17); all rows are
now complete.

BUSCO is against `actinopterygii_odb10` (3640 orthologs) for every row.
N50 column shows contig N50 (scaffold N50 in parentheses).

| Code | Contig N50 (scaffold) | BUSCO | Sequencing | Assembly notes |
|---|---|---|---|---|
| Cgib | ~5.1 Mb | ~99.5% complete | PacBio HiFi (2022) | Chromosome; explicit A/B labels |
| Ccar | 1.6 Mb (29.5 Mb) | C 98.6% (S 36.1% / D 62.4%), F 0.5%, M 0.9% [†] | PacBio + Oxford Nanopore + Illumina HiSeq | Chromosome; explicit A/B labels; ASM1834038v1 |
| Caur | 821 kb (22.8 Mb) | C 99.1% (S 35.6% / D 63.4%), F 0.5%, M 0.4% [†] | PacBio RSII (Canu) | Chromosome; no A/B labels; "Wakin" goldfish (cauAur01), Chen et al. 2019 |
| Drer | 59 Mb (59 Mb) | C 99.0% (S 97.7% / D 1.3%), F 0.5%, M 0.5% | Oxford Nanopore PromethION + PacBio (NHGRI, Tübingen strain) | Diploid comparator; GRCz12tu / GCF_049306965.1, complete-genome assembly, annotation RS_2025_04 (2025-04-11) |

[†] For the two allotetraploid carps the high **duplicated** BUSCO
fraction (Ccar D 62.4%, Caur D 63.4%, both ≫ single-copy) is *expected* —
orthologs retained as two homeologous copies — not an over-assembly
artefact. The diploid comparator (zebrafish) is instead single-copy-
dominant (S 97.7% / D 1.3%), exactly as expected.

> **Note — zebrafish comparator updated GRCz11 → GRCz12tu (2026-06-16).**
> The worked example originally used the GRCz11 RefSeq annotation
> (`GCF_000002035.6`), but NCBI **suppressed** that assembly (checked
> 2026-06-15: *"removed as a result of standard genome annotation
> processing"*), so it is no longer re-downloadable by accession. The
> comparator was therefore moved to the current zebrafish reference,
> **GRCz12tu** (`GCF_049306965.1`, annotation release RS_2025_04), a
> newer T2T-style assembly (Nanopore PromethION + PacBio). This is the
> assembly now pinned in `data/genome_config.yaml` and present in
> `data/annotations/Danio_rerio/`, and — unlike GRCz11 — it is current
> and re-downloadable by accession, so the zebrafish input no longer
> forces the §D deposit decision.

---

## Encoded priors (curator-supplied config knowledge)

Not everything the worked example reports is derived by the agent during
the run. Some of it is curator knowledge encoded into
`config/caspase_example.yaml` *before* the run and then applied
consistently by the harness. For the worked example to be read correctly —
and for the manuscript to separate what the harness *derived* from what it
was *given* — these supplied priors are recorded here.

| Config field | What it encodes | Supplied or derived |
|---|---|---|
| inclusion / search terms | Which gene names and patterns define the family | Supplied (Checkpoint 1) |
| `classification.pair_labels` | Expected ancestral identity per homeolog pair | Supplied |
| `classification.confusion_pairs` | Known naming/identity confusions and their confidence effect | **Supplied prior** — see below |
| `chromosome_overrides` | Unplaced-scaffold placements for specific members | Supplied |
| `manual_additions` | Members missed by the inclusion patterns (currently empty) | Supplied |

The `confusion_pairs` block is the one most easily mistaken for an agent
finding. It encodes confusions learned over prior study of the caspase
family (the Caspase-Char curation) — chiefly the executioner cluster,
where casp3/casp7 naming is effectively interchangeable — and sets the
identity-confidence flag accordingly: `executioner` → `low` on pairs
10/14/21; `cross_species` (casp8/casp10) → `medium` on pair 9;
`subfunctionalization` (casp23/caspa) → `none` on pair 7 (recorded but not
downgraded). When the worked example shows low identity confidence on the
executioner cluster, that is an **applied prior**, not an independent agent
inference.

This is distinct from the *synteny-driven ambiguity flag* at the same
cluster (1:1 A/B pairing unresolved; playbook §5.4.3), which the harness
surfaces from cluster structure alone, on any gene set, with no encoded
knowledge. The two coincide at pair 10 but are different mechanisms: the
ambiguity flag is emergent and reportable as harness behaviour; the
confidence downgrade is curator-supplied. The manuscript should attribute
them accordingly.

A new gene set starts from `template.yaml` with `confusion_pairs: {}` and
receives none of this until its own curator encodes equivalent knowledge.
That ability — accumulated curatorial judgment captured in an inspectable,
reproducible form — is itself a feature of the workflow, not a caspase-only
special case; it just has to be declared (as here) so supplied priors are
never read as run-derived findings.
