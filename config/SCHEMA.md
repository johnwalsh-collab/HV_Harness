# Gene-set config schema (proposal)

Status: **draft for review, 2026-05-15**. Not yet consumed by any
script. Once approved, this becomes the contract the decaspasified
scripts (Tier B.1 of `docs/FINALIZATION_PLAN.md`) read.

The schema separates two kinds of parameter:

1. **Gene-set parameters** — what changes when you apply the workflow
   to a new gene family (caspases, TLRs, MHC, etc.). Live in
   `config/<gene_set>.yaml`. The user/AI conversation at Checkpoint 1
   of the curation playbook produces this file.
2. **Genome parameters** — properties of the carp polyploid genomes
   themselves (which chromosome accession is A1, which is B7, etc.).
   These do not change between gene-set applications. Live in
   `data/genome_config.yaml`. The user does not normally edit this.

This document covers both, with the gene-set config in the foreground
because that is what a new user touches.

---

## File layout

```
config/
├── SCHEMA.md                  ← this file
├── template.yaml              ← annotated empty template (new users start here)
└── caspase_example.yaml       ← worked-example parameters (reference)

data/
└── genome_config.yaml         ← project-level genome architecture (rarely edited)
```

The user runs each script with `--config config/<their_gene_set>.yaml`
(or sets a `CASPASECHAR_CONFIG` environment variable, TBD). Scripts
also load `data/genome_config.yaml` automatically.

---

## Gene-set config (`config/<gene_set>.yaml`)

Top-level sections:

```yaml
gene_set:                    # 1. Identity
identification:              # 2. Stage 2: how to find members in GFFs
classification:              # 3. Stage 3c: map members to canonical types
inventory:                   # 4. Stage 3c: quality-flag thresholds and rules
visualization:               # 5. Stage 5: colours, labels, missing
```

### 1. `gene_set` — identity

```yaml
gene_set:
  name: caspase              # short identifier; used in output filenames
                             # e.g. "caspase" → caspase_gene_inventory.tsv
  display_name: "Caspase family"   # human-readable; used in figure titles,
                                   # legend headers, report prose
```

### 2. `identification` — Stage 2 search

What goes into `identify_gene_set.py` (renamed from
`identify_caspases.py`). All four lists are user-supplied; **no
defaults**. A new user, in conversation with the AI assistant at
Checkpoint 1 of the playbook, builds these by considering likely
false-positive *and* false-negative risks, both before and after
running the script.

```yaml
identification:
  inclusion:
    # A gene is a candidate if it matches at least one inclusion rule.
    name_patterns:           # regex patterns matched against the gene Name field
      - '^casp[0-9]+[a-z]?(?:\.[0-9]+)?$'    # casp3, casp3a, casp6b.1
      - '^casp[0-9]+l[0-9]+$'                # casp8l1 (caspase-like)
      - '^casp[a-z]+$'                       # caspa, caspb, caspbl
    description_keywords:    # substrings matched in description/product fields
      - caspase              # catches LOC-named genes with "caspase" in product
  exclusion:
    # Even if inclusion matches, exclude if any exclusion rule matches.
    gene_names:              # explicit known-false-positive gene names
      - casp8ap2             # caspase-associated, not a caspase
      - caap1                # caspase-activated, not a caspase
    description_patterns:    # disqualifying substrings in description/product
      - recruitment domain   # CARD-domain genes mention "caspase" in description
      - associated           # caspase-associated proteins
      - interacting          # caspase-interacting proteins
      - paracaspase          # MALT1 etc.
      - inhibitor            # caspase inhibitors
      - caspase-activated    # dffb (caspase-activated DNase) etc.
      - activated by caspase # substrates
```

### 3. `classification` — Stage 3c type assignment

What goes into `build_gene_inventory.py` (currently the hard-coded
`classify_caspase_type` function and `PAIR_EXPECTED_TYPE` /
`*_CONFUSION_PAIRS` dicts).

```yaml
classification:
  # Ordered list of type rules. First match wins. The same rule format
  # is used for all gene sets; the values are family-specific.
  type_rules:
    - type: casp22
      matches: [casp22]                      # any substring
    - type: casp23
      matches: [casp23]
    - type: casp9
      matches: [casp9, "caspase-9", "caspase 9"]
    - type: casp8l1
      matches: [casp8l1, "caspase 8, apoptosis-related cysteine peptidase, like 1"]
    - type: casp8
      matches: [casp8, "caspase-8", "caspase 8"]
    # ... (full list in caspase_example.yaml)
    - type: caspa
      matches: [casp1, "caspase-1", caspa, "caspase a", "caspase-a"]
      # Note: casp1 in carp annotations = caspa in fish nomenclature

  # Expected type at each homeolog pair, per the diploid comparator.
  # Used as the default source for visualization pair labels (figure
  # legends). No longer feeds an inventory column (removed 2026-06-11).
  pair_expected:
    1:  "casp3a/caspb"
    3:  "casp6"
    5:  "casp22"
    6:  "casp8"
    7:  "casp23/caspa"
    9:  "casp10"
    10: "casp3/casp7 (exec cluster)"
    12: "casp7"
    14: "casp3b"
    16: "caspa/casp2"
    21: "casp21"
    23: "casp9"

  # Known confusion patterns surfaced by curation. Used by the
  # annotation-confidence assessment. Each entry's KEY is a free label;
  # the behaviour is driven by `confidence_effect`, not the key name:
  #   low    — force low identity confidence, and block the
  #            high-confidence upgrade for cleanly-named genes at these pairs
  #   medium — cap confidence at medium (does not block the upgrade)
  #   none   — record `reason` only; no confidence change (legitimate divergence)
  # An entry without `confidence_effect` defaults to `none`.
  confusion_pairs:
    executioner:               # pairs where casp3/casp7 are interchanged in NCBI naming
      pairs: [10, 14, 21]
      affected_types: [casp3, casp7, casp3b]
      confidence_effect: low
      reason: "exec caspase confusion locus (casp3/casp7 interchangeable)"
    cross_species:             # pairs where casp8/casp10 differ between species
      pairs: [9]
      affected_types: [casp8, casp10]
      confidence_effect: medium
      reason: "casp8/casp10 cross-species annotation inconsistency"
    subfunctionalization:      # pairs where A and B carry different genes (legitimate)
      pairs: [7]
      affected_types: [casp23, caspa]
      confidence_effect: none
      reason: "pair 7: conserved A=casp23/B=caspa divergence"
```

The three keys above are the caspase example's labels; a different gene
set picks its own. The previous version of `build_gene_inventory.py`
hardcoded the literal key `executioner` to mean "force low confidence,"
which only worked for caspases; `confidence_effect` replaces that so the
behaviour is config-driven for any gene set.

### 4. `inventory` — manual additions

Model-quality flags are read from NCBI's own annotation signals
(`gene_biotype`, `partial`, `exception`, and the protein FASTA's
`LOW QUALITY PROTEIN` prefix), so there are no per-family length
thresholds to set. (The former `length_thresholds` field was removed
2026-06-12.)

```yaml
inventory:
  # Special-case entries that should appear in the inventory even
  # though they don't pass the inclusion filter (typically: known
  # genes the search missed). Pulled from playbook Checkpoint 1's
  # after-pass review.
  manual_additions:
    - species: Carassius_auratus
      gene_id: LOC113053832
      gene_name: LOC113053832
      chromosome: NC_039276.1
      reason: "Goldfish A9 homeolog (in homeolog summary but missed by inclusion patterns)"
```

### 5. `visualization` — Stage 5 explorer parameters

```yaml
visualization:
  colors:                    # 5 categories; same scheme works for any gene set
    confident: "#2E7D32"
    worth_reviewing: "#F9A825"
    annotation_concern: "#D84315"
    assembly_concern: "#1565C0"
    missing: "#C62828"

  pair_labels:               # display labels per homeolog pair
    1:  "casp3a / caspb"
    3:  "casp6"
    # ... etc. (Can mirror pair_expected from classification, or differ
    # if shorter labels are needed in figures.)

  # Post-curation: known missing genes per species. Drawn as red
  # outline diamonds at the expected position. Populated from the
  # empty-slots deep dive (playbook Checkpoint 3 surfaces these).
  known_missing:
    Carassius_gibelio:
      - {subgenome: A, pair: 5,  label: "casp22"}
      - {subgenome: A, pair: 9,  label: "casp10"}
      - {subgenome: A, pair: 16, label: "casp2"}
      - {subgenome: B, pair: 21, label: "casp21"}
    Cyprinus_carpio: []
    Carassius_auratus: []
```

### 6. `chromosome_overrides` — unplaced-scaffold placement (optional)

Most gene sets omit this. Record it only when curation reveals that a
group member sits on an unplaced scaffold whose homeolog-pair
membership cannot be derived from the chromosome naming. Each entry
maps an assembly accession to `[chromosome_label, subgenome,
homeolog_pair]`. These assignments are gene-set-specific — they depend
on where this group's members sit — which is why they live in the
gene-set config rather than `genome_config.yaml`. They are applied on
top of any genome-level overrides, so the gene-set layer wins.

```yaml
chromosome_overrides:
  Cyprinus_carpio:
    NW_024879254.1: ["unplaced", "unplaced", 5]   # casp22
  Carassius_auratus:
    NW_020523286.1: ["unplaced", "B", 23]         # casp9
    NW_020525115.1: ["unplaced", "A", 12]         # casp7
```

---

## Project-level genome config (`data/genome_config.yaml`)

Properties of the carp Cs4R polyploid genomes themselves. Does not
change between gene-set applications.

```yaml
species:                     # supersedes the current species_info.txt
  - short_code: Cgib
    full_name: Carassius_gibelio
    common_name: "Prussian carp"
    assembly: GCF_023724105.1
    ploidy: tetraploid
    role: core
    has_explicit_ab_labels: true
    chromosome_rule: explicit_ab       # A1/B1 read from the annotation
    taxon_id: 101364                   # wrong-folder guard (optional)
  - short_code: Ccar
    full_name: Cyprinus_carpio
    common_name: "Common carp"
    assembly: GCF_018340385.1
    ploidy: tetraploid
    role: core
    has_explicit_ab_labels: true
    chromosome_rule: explicit_ab
    taxon_id: 7962
  - short_code: Caur
    full_name: Carassius_auratus
    common_name: "Goldfish"
    assembly: GCF_003368295.1
    ploidy: tetraploid
    role: core
    has_explicit_ab_labels: false
    chromosome_rule: from_lookup_file  # A/B not in annotation; use the lookup
    taxon_id: 7957
    subgenome_lookup: config/goldfish_subgenome_lookup.tsv
  - short_code: Drer
    full_name: Danio_rerio
    common_name: "Zebrafish"
    assembly: GCF_049306965.1          # GRCz12tu
    ploidy: diploid
    role: primary_comparator
    chromosome_rule: diploid           # each numbered chromosome is its own pair
    taxon_id: 7955
  - short_code: Ptet
    full_name: Puntigrus_tetrazona
    common_name: "Tiger barb"
    assembly: GCF_018831695.1
    ploidy: diploid
    role: secondary_comparator
    chromosome_rule: diploid
    taxon_id: null
  - short_code: Cide
    full_name: Ctenopharyngodon_idella
    common_name: "Grass carp"
    assembly: GCF_019924925.1
    ploidy: diploid
    role: secondary_comparator
    chromosome_rule: diploid
    taxon_id: null

# Chromosome accession → (label, subgenome, homeolog_pair)
# Read from each assembly's own annotation at load time (see the
# chromosome_rule field above); no hard-coded per-species tables. The
# `overrides` block handles unplaced scaffolds with known assignments.
chromosome_mappings:
  overrides: {}                # rare genome-level corrections; usually empty
```

**Field — `chromosome_rule`** (per species, required for any species
whose chromosomes should be mapped). Tells the loader how to read
chromosome identity out of that assembly's annotation:

| Value | Meaning | Used by |
|---|---|---|
| `explicit_ab` | Chromosomes are named `A1..An` / `B1..Bn` in the GFF; the letter is the subgenome, the number the homeolog pair. | Cgib, Ccar |
| `diploid` | Each numbered chromosome is its own homeolog pair (`chr1`, `chr2`, …). | Drer and any added comparator |
| `from_lookup_file` | Annotation carries no A/B labels; map via the `subgenome_lookup` TSV. | Caur (goldfish) |

**Field — `taxon_id`** (per species, optional). If set, the loader
checks it against the `Dbxref=taxon:` in the annotation and refuses a
file whose taxon disagrees — catching a file dropped into the wrong
species folder. Leave `null` to skip the check (e.g. on-demand
comparators not yet downloaded).

**How the mapping is derived.** Every NCBI GFF declares, on each
assembled chromosome's `region` feature, a `chromosome=` attribute
(`chromosome=A1`, `chromosome=12`) under `genome=chromosome`. The loader
(`scripts/_config.py:derive_chromosome_mappings`) reads those and
interprets them per `chromosome_rule`. Because the labels come from the
file, **a new assembly version of any species works with no edit here** —
drop its GFF into `data/annotations/<species>/` and re-run; the scan is
cached next to the GFF and rebuilds when the file changes. Scaffolds
that NCBI merely *assigns* a guessed `chromosome=N` under
`genome=genomic` are excluded, so a scaffold is never mistaken for a
chromosome. An annotation that is present but yields no chromosome
mapping raises a clear error rather than silently labelling every gene
`unknown`.

---

## What scripts read what

| Script | Reads from gene-set config | Reads from genome config |
|---|---|---|
| `identify_gene_set.py` | `identification` | `species` |
| `clean_sequences.py` | `gene_set.name` (for filenames) | `species` |
| `download_sequences.py` | `gene_set.name` | `species` |
| `build_subgenome_lookup.py` | — | `species` (target + reference) |
| `build_gene_inventory.py` | `classification`, `inventory` | `species`, `chromosome_mappings` |
| *(new B.2)* synteny extraction | `gene_set.name`, identification (for matching genes in flanking windows) | `species` |
| *(new B.2)* hierarchy explorer | `visualization`, `classification` | `species` |

---

## Questions for review before any scripts are touched

1. **Does the gene-set / genome split feel right?** The alternative is
   one config file per analysis (everything in one place; friendlier
   for end users but more boilerplate). My preference is the split:
   the genome config is project-level infrastructure that almost no
   user will need to touch, and conflating it with the gene-set config
   blurs the line between *what changes per analysis* and *what the
   tool runs on*.
2. **`manual_additions` — keep or drop?** The current
   `build_gene_inventory.py` manually adds a single entry
   (LOC113053832). The cleaner answer is to fix the inclusion patterns
   so this is no longer needed. The pragmatic answer is to keep a
   manual-additions list because there will always be edge cases. My
   read: keep it, but flag it as the place where Checkpoint 1's
   after-pass review surfaces issues that the search alone can't
   resolve.
3. **`known_missing` lives in `visualization` — is that the right
   place?** It's gene-set-and-curation-specific (you only know what's
   missing after curation). Could equally live under
   `curation.known_missing`. My read: keep under `visualization`
   since the hierarchy explorer's rendering is what consumes it; that
   matches how it's used.
4. **`pair_expected` (in `classification`) vs `visualization.pair_labels`.**
   As of 2026-06-11 the inventory's expected-type column was removed, so
   `classification.pair_expected` now serves only as the default source
   for `visualization.pair_labels` (figure legends). With the labels as
   its only consumer, the two could be consolidated into a single
   `pair_labels` field; kept separate for now.
5. **YAML format vs JSON or TOML?** YAML is the most readable for the
   kinds of nested structure here. The cost is one Python dependency
   (`pyyaml`) added to `requirements.txt`. JSON has no extra
   dependency but is much less pleasant to edit by hand. TOML is
   pleasant but less suited to deeply nested data. My recommendation:
   YAML.

Sign-off on these five questions unblocks writing
`config/caspase_example.yaml` + `config/template.yaml` and then the
script refactors.
