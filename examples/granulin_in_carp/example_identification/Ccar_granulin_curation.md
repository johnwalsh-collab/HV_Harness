# Granulin family — curation in *Cyprinus carpio* (common carp)

Focal species: **Cyprinus carpio** (common carp, GCF_018340385.1), A and
B subgenomes curated against the *Danio rerio* (zebrafish) reference
framework. Other carp genomes are consulted as supporting evidence only.

Status: **collaborative draft in progress**. Per-pair curation is drafted
for pairs 3, 19, and 24. Checkpoint 3 has assessed the one empty slot
flagged during per-pair work: common-carp B3 at the `grna` /
progranulin locus.

## Standard of evidence — what "loss" and "absent" mean in this file

This curation operates on annotated inputs (RefSeq GFF and protein
FASTAs) and makes annotation-level claims. The strongest loss claim it
commits to is **candidate loss with annotation-level evidence**: the gene
is present at the syntenic locus in zebrafish, the gene is present on the
homeologous chromosome in the same carp assembly, a search of the
annotation in the syntenic region returns no candidate member or
family-adjacent feature, and the syntenic block on the empty chromosome is
recognisable enough to support the absence claim.

That is supportive evidence for a real evolutionary loss. It is not
confirmation. Confirmed loss claims require sequence-level work (tBLASTn
against the unannotated genomic region, synteny alignment) and are out of
scope for this curation. Sequence-level follow-up questions are logged to
the project's side-projects list.

Slots with no specific search are labelled **absent — no specific search
done**. This is the honest default. Slots are upgraded to *candidate loss*
only when the procedure in playbook section 5.4.2 has been worked through.

## Annotation principle for homeolog labelling

This curation treats **conserved syntenic position** as the primary
evidence for homeolog identity in the carp polyploid genomes. When NCBI
labels the A and B copies at the same syntenic locus with different
gene-family names, the divergent label is most likely a
sequence-similarity-based mis-call; synteny-derived identity overrides
automated naming by default.

The default is not absolute. Local tandem duplication with differential
within-cluster loss, gene conversion, chromosomal rearrangement, assembly
collapse, and lineage-specific change in the zebrafish reference are
situations where the synteny rule needs supplementation. The exception
cases are flagged inline where they apply.

For every relabelled gene, the original NCBI annotation appears in the
per-pair Genes table and the Proposed-curation table's "Current NCBI
name" column. A reader can always map the curation's calls back to the
public annotation.

## Pair 3 — grna / progranulin locus (zebrafish chr3)

**Chromosomes:** A3 = `NC_056574.1`; B3 = `NC_056599.1` by common-carp
chromosome convention. No B3 granulin-family gene was recovered in the
Stage 2 inventory.

### Genes

| Chr | Gene ID | NCBI name | Protein | Length | Outgroup ref | Motif / domain feature | CDS exons (repr. isoform) | Status |
|---|---|---|---|---:|---|---|---:|---|
| A3 | LOC109064429 | LOC109064429; progranulin-like | XP_042581193.1 | 783 aa | 1053 aa (`grna`) | cysteine-rich granulin-repeat architecture present by sequence pattern; automated domain parsing not run | 15 | ok |
| B3 | — | — | — | — | 1053 aa (`grna`) | not assessed | — | candidate loss (annotation-level, partial block) |

### Protein assessment

Common-carp A3 carries `LOC109064429`, annotated as
`progranulin-like, transcript variant X2`. The representative protein
used by the harness is 783 aa, shorter than zebrafish `grna`
(`XP_005164023.2`, 1053 aa) but still a large multi-repeat progranulin
model rather than a small single-granulin peptide. The inventory records
15 representative CDS exons and four coding transcript variants. No NCBI
model-quality flag is present.

No common-carp B3 granulin-family gene was recovered by the Stage 2
search. During the Checkpoint 3 empty-slot deep dive, B3
(`NC_056599.1`) was searched chromosome-wide for granulin-family terms
(`granulin`, `progranulin`, `epithelin`, `acrogranin`, `grn`): no hits
were found. A syntenic-marker search found a partial pair-3 block around
23.75-24.08 Mb, including `ccndx`, `fgf21`, `rpl27`, and `slc25a39`.
The in-region sweep of that interval found no granulin-family
description, no pseudogene-biotyped feature, and no interval protein
with a `LOW QUALITY PROTEIN` header. The B3 slot is therefore upgraded
from `absent — no specific search done` to **candidate loss
(annotation-level)**, hedged because the syntenic block is partially
preserved rather than cleanly present.

Supporting cross-species context: Prussian carp and goldfish both show
pair-3 A/B granulin-family loci in the inventory, with the B-side copy
named `grna` in both species. That pattern makes the common-carp B3
absence worth a careful CP3 search rather than dismissing it as a search
artefact.

### Synteny

```text
Zebrafish chr3:
  apol - cacng2a - rpl3 - slc25a39 - rpl27 - rundc1 - GRNA - ifi35 - bcat2 - hsd17b14 - kcna7 - fgf21 - ppfia3 - nucb1 - ccndx - tbc1d17

Common carp A3:
  tbc1d17 - ccnd-like - nucb-like - ppfia3-like - slc1a-like - fgf21-like - kcna7-like - bcat2-like - ifi35-like - LOC109064429 - rundc1-like - rpl27 - slc25a39-like - rpl3 - cacng2-like - apol - sult3st1 - eif3d

Common carp B3:
  partial syntenic block only: ccndx - fgf21 - rpl27 - slc25a39; no granulin-family feature in CP3 sweep
```

The common-carp A3 block is a strong match to the zebrafish chr3 `grna`
locus, with many of the same flanking genes around the central granulin
model. Relative order is broadly reversed around the focal gene compared
with zebrafish, consistent with an inversion or orientation difference,
but the neighborhood identity is clear. This supports `LOC109064429` as
the common-carp A3 homeolog at the `grna` / progranulin locus.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Confidence (L/I/M) | Notes |
|---|---|---|---|---|
| LOC109064429 | LOC109064429; progranulin-like | **grna / progranulin-like** (A3 homeolog) | H/H/M | Strong syntenic placement at zebrafish chr3 `grna` locus; model appears structurally credible but is shorter than zebrafish `grna`, so model confidence is medium pending deeper protein/domain review. |
| — | — | **grna / progranulin-like** (B3 candidate loss, annotation-level) | H/H/— | CP3 sweep negative for granulin-family feature or degraded model; syntenic block partially preserved, so the loss call is annotation-level and hedged. |

### Checkpoint 3 empty-slot assessment

| Missing gene | Chromosome | Outcome label | Syntenic-block quality | Interval sweep result | Shared with other species? |
|---|---|---|---|---|---|
| `grna` / progranulin-like B homeolog | B3 (`NC_056599.1`) | candidate loss (annotation-level) | partial | negative | no; Prussian carp and goldfish retain B3-side pair-3 granulin-family loci |

### Deferred questions

- Side project: domain-level/protein-architecture comparison of the
  multi-repeat progranulin models, especially the shorter common-carp A3
  model relative to zebrafish `grna`.
- Side project: sequence-level check of the common-carp B3 interval to
  test whether an unannotated granulin-family remnant exists despite the
  negative annotation-level sweep.

## Pair 19 — grna.1 / grna.2 small-granulin tandem locus (zebrafish chr19)

**Chromosomes:** A19 = `NC_056590.1`; B19 = `NC_056615.1`.

### Genes

| Chr | Gene ID | NCBI name | Protein | Length | Outgroup ref | Motif / domain feature | CDS exons (repr. isoform) | Status |
|---|---|---|---|---:|---|---|---:|---|
| A19 | LOC109060267 | LOC109060267; progranulin-like | XP_042632893.1 | 188 aa | 147 aa (`grna.1` / `grna.2`) | short cysteine-rich granulin-like peptide; automated domain parsing not run | 5 | ok |
| A19 | LOC109112498 | LOC109112498; progranulin-like | XP_042632894.1 | 188 aa | 147 aa (`grna.1` / `grna.2`) | short cysteine-rich granulin-like peptide; automated domain parsing not run | 5 | ok |
| B19 | LOC109051021 | LOC109051021; progranulin-like | XP_042600696.1 | 147 aa | 147 aa (`grna.1` / `grna.2`) | short cysteine-rich granulin-like peptide; automated domain parsing not run | 4 | ok |
| B19 | LOC109068459 | LOC109068459; progranulin-like | XP_042600695.1 | 154 aa | 147 aa (`grna.1` / `grna.2`) | short cysteine-rich granulin-like peptide; automated domain parsing not run | 4 | ok |

### Protein assessment

Common carp has two short granulin-family genes on A19 and two on B19.
All four are LOC-named `progranulin-like` annotations, but their protein
lengths (147-188 aa) place them with the zebrafish chr19 small-granulin
tandem duplicates rather than the large multi-repeat `grna` model on
chr3. The A19 copies are modestly longer and have one more representative
CDS exon than the B19 copies, but none carries an NCBI model-quality flag.

The zebrafish reference at this locus is itself a tandem pair:
`grna.1` and `grna.2`, both 147 aa. Because the focal species carries a
two-copy cluster on both A19 and B19 in the same local block, synteny
supports a pair-19 small-granulin tandem slot. It does not, by itself,
settle which A19 copy should be matched 1:1 to which B19 copy, or which
carp copy is closest to zebrafish `grna.1` versus `grna.2`.

Supporting cross-species context: Prussian carp shows an A19 two-copy
cluster near the same local context and a B19 two-copy cluster; goldfish
shows one A19-like small-granulin gene and two B19-like small-granulin
genes. This supports the interpretation that pair 19 is a genuine
small-granulin tandem locus with lineage- or annotation-level copy-count
variation, not an isolated common-carp artefact.

### Synteny

```text
Zebrafish chr19:
  sfpq - zmym4.1 - zmym4.2 - rbm48 - clxn - GRNA.1 - GRNA.2 - cdk6 - fam133b - hepacam2 - vps50 - calcr - tfpi2 - gngt1 - bet1

Common carp A19:
  sfpq-like - zmym4-like - zmym4-like - rbm48-like - LOC109060267 - LOC109112498 - cdk6-like - fam133b - hepacam2-like - vps50 - calcr-like - tfpi2-like - gngt1 - bet1 - col1a2 - casd1 - sgce

Common carp B19:
  sfpq - zmym4.1 - zmym4-like - rbm48-like - efcab1 - LOC109051021 - LOC109068459 - cdk6 - hepacam2-like - syndetin-like - calcr-like - tfpi2-like - gngt1 - bet1 - col1a2-like
```

The A19 and B19 regions share the same core neighborhood as zebrafish
chr19: `sfpq`, `zmym4`, `rbm48`, the small-granulin cluster, `cdk6`,
`hepacam2`, `calcr`, `tfpi2`, `gngt1`, and `bet1`. The focal granulin
copies sit in the expected position between `rbm48`/nearby calcium-related
features and `cdk6`. The B19 interval carries an extra local `efcab1`
between `rbm48` and the first granulin-family gene; this does not
undermine the block-level match.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Confidence (L/I/M) | Notes |
|---|---|---|---|---|
| LOC109060267 | LOC109060267; progranulin-like | **pair-19 small-granulin cluster** (A19 copy 1) | H/L/H | Strong locus placement and credible model; specific within-cluster identity relative to `grna.1`/`grna.2` not resolved by synteny alone. |
| LOC109112498 | LOC109112498; progranulin-like | **pair-19 small-granulin cluster** (A19 copy 2) | H/L/H | Strong locus placement and credible model; specific within-cluster identity relative to `grna.1`/`grna.2` not resolved by synteny alone. |
| LOC109051021 | LOC109051021; progranulin-like | **pair-19 small-granulin cluster** (B19 copy 1) | H/L/H | Strong locus placement and credible model; specific within-cluster identity relative to `grna.1`/`grna.2` not resolved by synteny alone. |
| LOC109068459 | LOC109068459; progranulin-like | **pair-19 small-granulin cluster** (B19 copy 2) | H/L/H | Strong locus placement and credible model; specific within-cluster identity relative to `grna.1`/`grna.2` not resolved by synteny alone. |

### Deferred questions

- Side project: curated protein-domain and/or phylogenetic analysis to
  resolve whether the four common-carp pair-19 copies correspond to
  zebrafish `grna.1` and `grna.2` in a recoverable 1:1 pattern.
- CP4: decide whether the final visualization should display pair 19 as a
  single ambiguous tandem cluster or split the two local positions with an
  explicit low-identity-confidence flag.

## Pair 24 — grnb locus (zebrafish chr24)

**Chromosomes:** A24 = `NC_056595.1`; B24 = `NC_056620.1`.

### Genes

| Chr | Gene ID | NCBI name | Protein | Length | Outgroup ref | Motif / domain feature | CDS exons (repr. isoform) | Status |
|---|---|---|---|---:|---|---|---:|---|
| A24 | grnb | grnb; granulin b, transcript variant X1 | XP_042570624.1 | 737 aa | 729 aa (`grnb`) | multi-repeat progranulin / granulin b architecture by sequence pattern; automated domain parsing not run | 15 | ok |
| B24 | LOC109075413 | LOC109075413; progranulin-like | XP_042608155.1 | 516 aa | 729 aa (`grnb`) | multi-repeat progranulin-like architecture by sequence pattern; automated domain parsing not run | 11 | partial |

### Protein assessment

Common-carp A24 carries the named `grnb` gene. Its representative protein
is 737 aa, very close to zebrafish `grnb` at 729 aa, with 15 CDS exons
and no NCBI model-quality concern. This is the cleanest common-carp
granulin-family model in the focal species.

Common-carp B24 carries `LOC109075413`, annotated `progranulin-like`. Its
representative protein is 516 aa, substantially shorter than zebrafish
`grnb` and common-carp A24 `grnb`, and the inventory records
`partial=true` from NCBI. The model nevertheless sits at the expected
syntenic locus and retains a multi-repeat granulin/progranulin-like
sequence architecture at annotation level. I therefore treat it as a
retained B24 `grnb`-locus copy with low model confidence, not as an empty
slot or candidate loss.

Supporting cross-species context: Prussian carp has a clean A24/B24 pair
at this locus (`LOC127945929` and `grnb`), and goldfish has a mapped
chr24 `granulins-like` locus. This supports pair 24 as a conserved
granulin-family locus across the carp annotations, while also suggesting
that the common-carp B24 model deserves follow-up because it is shorter
and partial. Goldfish currently lacks the mapped A24 counterpart in the
inventory, but goldfish is not the focal species for this curation.

### Synteny

```text
Zebrafish chr24:
  gnal2 - tmem14cb - pak1ip1 - esco1 - rbbp8 - tmem241 - riok3 - coasy - naglu - pus3 - GRNB - map3k14b - arf2b - grb7 - srcin1b - fmnl1b - ccr10 - c1ql1l - dcakd

Common carp A24:
  gnal-like - pak1ip1-like - esco1-like - tmem241 - riok3 - mlck-like - coasy-like - pus3-like - THAP-domain protein - GRNB - arf1-like - grb7 - srcin1-like - fmnl1-like - kv channel - ccr7-like - ramp3-like - ugt2a2-like - c1q-related factor

Common carp B24:
  pak1ip1 - esco1 - rbbp8 - riok3-like - mlck-like - coasy-like - naglu - pus3 - LOC109075413 - map3k14-like - arf2b - grb7-like - srcin1-like - ccr7-like - ramp3-like - c1q-related factor
```

The A24 and B24 regions both match the zebrafish chr24 `grnb`
neighborhood. The central ordering around `pus3` / `grnb` /
`map3k14` / `arf` / `grb7` / `srcin1` is especially informative. A24
and B24 are not identical in local gene content, and some distal
flanking genes differ in annotation or identity, but the conserved block
is clear enough to support an A/B homeologous relationship at the `grnb`
locus.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Confidence (L/I/M) | Notes |
|---|---|---|---|---|
| grnb | grnb | **grnb** (A24 homeolog) | H/H/H | Named gene, full-length relative to zebrafish `grnb`, and strongly placed in the chr24 syntenic block. |
| LOC109075413 | LOC109075413; progranulin-like | **grnb** (B24 homeolog) | H/H/L | Strong syntenic placement at the `grnb` locus, but NCBI `partial=true` and shorter protein length lower model confidence. Original LOC/progranulin-like annotation retained. |

### Deferred questions

- Side project: inspect the common-carp B24 `LOC109075413` gene model and
  genomic region to determine whether the shorter partial model reflects a
  real truncated copy, an annotation boundary problem, or assembly
  incompleteness.

## Summary

### Gene count

Seven annotated granulin-family gene models across three homeolog-pair
framework loci in common carp:

- 1 pair-3 A-side multi-repeat progranulin-like model (`LOC109064429`)
- 4 pair-19 short small-granulin models in an ambiguous tandem cluster
- 2 pair-24 `grnb`-locus models, one named and full-length, one partial
- 1 empty slot assessed at Checkpoint 3: B3 `grna` / progranulin-like
  candidate loss (annotation-level, partial syntenic block)

### Empty slots — assessed

| Missing gene | Chromosome | Outcome label | Syntenic-block quality | Interval sweep result | Shared with other species? |
|---|---|---|---|---|---|
| `grna` / progranulin-like B homeolog | B3 (`NC_056599.1`) | candidate loss (annotation-level) | partial | negative | no; Prussian carp and goldfish retain B3-side pair-3 granulin-family loci |

### Confidence summary

| Locus / Identity / Model triple | Count | Pairs |
|---|---:|---|
| H/H/H | 1 | Pair 24 A24 `grnb` |
| H/H/M | 1 | Pair 3 A3 `LOC109064429` |
| H/L/H | 4 | Pair 19 A19/B19 small-granulin cluster |
| H/H/L | 1 | Pair 24 B24 `LOC109075413` |
| Candidate loss | 1 slot | Pair 3 B3 |

### Side-project list

- Domain-level/protein-architecture comparison of the multi-repeat
  progranulin models, especially common-carp A3 `LOC109064429` relative
  to zebrafish `grna`.
- Sequence-level check of the common-carp B3 interval to test whether an
  unannotated granulin-family remnant exists despite the negative
  annotation-level sweep.
- Curated protein-domain and/or phylogenetic analysis for the pair-19
  small-granulin tandem cluster.
- Gene-model/genomic-region inspection for common-carp B24
  `LOC109075413`, which is partial and shorter than the A24 and zebrafish
  `grnb` proteins.
