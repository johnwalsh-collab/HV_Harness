# Caspase family — curation in *Carassius gibelio* (Prussian carp)

Focal species: **Carassius gibelio** (Prussian carp, GCF_023724105.1),
A and B subgenomes curated against the *Danio rerio* (zebrafish)
reference framework. Other carp genomes (common carp, goldfish) are
consulted only as supporting evidence, not curated here.

Status: **reviewed and signed off** (2026-06-30). Uncertain calls are
marked **[NEEDS REVIEW]**; empty slots that were initially flagged
**[EMPTY-SLOT → CP3]** have been resolved.

### Revision history

1. **Initial per-pair draft** (unattended mode) — all 12 pairs drafted
   in one pass; empty slots left at the honest default `absent — no
   specific search`; uncertain calls flagged.
2. **Checkpoint 3 — empty-slots deep dive** (signed off by curator) —
   in-region annotation sweeps run for every flagged empty slot;
   distractor genes (card9, cflar, nlrc3l1) ruled out against the
   retaining homeolog; four slots resolved to *candidate loss
   (annotation-level)*. See the "Empty slots — assessed" table.
3. **Checkpoint 4 — whole-curation review** (completed) — cross-pair
   consistency checked: the executioner-confusion prior is applied
   uniformly (pairs 10, 14), the synteny-over-naming rule is applied
   consistently (pairs 1, 7, 16), and hedging language is uniform. The
   **pair-7 casp23 relabel was confirmed by the curator** (no longer a
   proposal). No cross-pair inconsistencies were found. Open [NEEDS
   REVIEW] items (B12 casp7 motif, casp8l1/casp20 split, A16 casp2 hedge)
   are logged to side projects, not unresolved contradictions.

---

## Standard of evidence — what "loss" and "absent" mean in this file

This curation operates on annotated inputs (RefSeq GFF and protein
FASTAs) and makes annotation-level claims only. The strongest loss claim
it commits to is **candidate loss with annotation-level evidence**: the
gene is present at the syntenic locus in zebrafish, the gene is present
on the homeologous chromosome in the same carp assembly, a search of the
annotation in the syntenic region returns no candidate member or
family-adjacent feature, and the syntenic block on the empty chromosome
is recognisable enough to support the absence claim.

That is supportive evidence for a real evolutionary loss. It is **not**
confirmation. Confirmed-loss claims require sequence-level work (tBLASTn
against the unannotated genomic region, synteny alignment) and are out
of scope. Sequence-level follow-ups are logged to the side-projects
list.

Slots with no specific search are labelled **absent — no specific search
done** — the honest default. They are upgraded to *candidate loss* only
after the Checkpoint 3 procedure (playbook §5.4.2) has been worked
through.

## Annotation principle for homeolog labelling

This curation treats **conserved syntenic position** as the primary
evidence for homeolog identity. When NCBI labels the A and B copies at
the same syntenic locus with different caspase names, the divergent
label is most likely a sequence-similarity-based mis-call; synteny-
derived identity overrides automated naming by default. The default is
not absolute — tandem duplication with differential within-cluster loss,
gene conversion, rearrangement, assembly collapse, and zebrafish-
lineage-specific change are the documented exceptions, flagged inline
where they apply.

For every relabelled gene, the original NCBI annotation is preserved in
the Genes table and the "Current NCBI name" column, so a reader can map
every call back to the public annotation.

**A note on the comparator.** Tiger barb and grass carp annotations are
not present in this repository, so zebrafish is the **only** diploid
comparator available. Where a locus shows a possibly zebrafish-specific
pattern (e.g. a zebrafish tandem expansion not mirrored in carp), the
section 4.2 secondary cross-check cannot be run; the standing caveat —
*a zebrafish-specific pattern cannot be excluded* — is recorded as a
hedge rather than resolved.

---

## Zebrafish reference framework

The ancestral-state reference: caspase members in *Danio rerio*, by
chromosome (= carp homeolog pair number), with protein lengths.

| Pair / zf chr | Zebrafish caspase(s) | Length (aa) |
|---|---|---|
| 1 | casp3a; caspb; caspbl | 282; 404; 395 |
| 3 | casp6a; casp6b.1; casp6b.2 | 297; 279; 283 |
| 5 | casp22 | 376 |
| 6 | casp8; casp8l1; casp20; LOC795066 | 476; 330; 347; 346 |
| 7 | casp23 | 446 |
| 9 | casp10 | 520 |
| 10 | casp17; LOC798445 | 276; 289 |
| 12 | casp7 | 381 |
| 14 | casp3b | 224 |
| 16 | casp2; caspa | 435; 383 |
| 21 | casp21 | 266 |
| 23 | casp9 | 436 |

Catalytic pentapeptide reference: the canonical caspase active site is
**QACxG**. Scans below report the observed pentapeptide; variants
(QSCRG, QACQG, QACGG) are noted as features of interest and do **not**
by themselves lower confidence when a valid motif is present (playbook
§5.4.6).

---

## Pair 1 — casp3a / caspb / caspbl (zebrafish chr1)

**Chromosomes:** A1 = NC_068371-series, B1 = NC_068396-series

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A1 | casp3a | casp3a | 282 aa | 282 aa (casp3a) | QACRG | 6 | ok |
| A1 | LOC128029032 | caspase b | 384 aa | 404 aa (caspb) | QACRG | 7 | ok |
| A1 | LOC127935548 | (caspase b) | 143 aa | 395 aa (caspbl) | NONE | 2 | candidate_nonfunctional |
| B1 | LOC127949347 | caspase-3 | 276 aa | 282 aa (casp3a) | QACRG | 6 | ok |
| B1 | LOC127949502 | (caspase b) | 381 aa | 404 aa (caspb) | QACRG | 7 | ok |
| B1 | LOC127949561 | (caspase b-like) | 93 aa | 395 aa (caspbl) | NONE | 2 | candidate_nonfunctional |

### Protein assessment

Three slots resolve at this pair. **casp3a:** A1 `casp3a` (282 aa, QACRG,
6 exons) and B1 `LOC127949347` (276 aa, NCBI "caspase-3", QACRG, 6 exons)
are a clean homeolog pair — matched length, motif, and exon count.
**caspb:** A1 `LOC128029032` (384 aa) and B1 `LOC127949502` (381 aa),
both QACRG / 7 exons, against the 404 aa zebrafish caspb — a clean
homeolog pair.

**caspbl — pseudogene call (both homeologs).** A1 `LOC127935548` (143 aa)
and B1 `LOC127949561` (93 aa) are both truncated to roughly a third to a
half of the 395 aa zebrafish caspbl, both lack the catalytic motif, and
both have only 2 CDS exons against the family-typical 5–7. Multiple
independent lines of structural disruption on both copies support a
**strong pseudogene call** on each (playbook §5.4.5). The two
truncations are different lengths (143 vs 93 aa), which is consistent
with independent post-hybridization degradation rather than a shared
ancestral pseudogene. Recorded as `candidate_nonfunctional` for the
explorer (truncated, motif-less, but not formally NCBI-pseudogene-
biotyped).

### Synteny

A1 and B1 share the casp3a flanking neighbourhood (`pcm1`,
`mtap`/microtubule-associated tumour suppressor homolog, `fat1a`/
protocadherin Fat 1, long-chain-fatty-acid-CoA ligase 1), matching the
zebrafish chr1 casp3a locus. The caspb/caspbl copies sit in a second
chr1 block (CMRF35-like / polymeric-Ig-receptor neighbourhood) shared by
A1 and B1.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| casp3a | casp3a | **casp3a** (A homeolog) | H/H/H | clean |
| LOC127949347 | caspase-3 | **casp3a** (B homeolog) | H/H/H | NCBI "caspase-3"; synteny → casp3a |
| LOC128029032 | caspase b | **caspb** (A homeolog) | H/H/H | |
| LOC127949502 | caspase b | **caspb** (B homeolog) | H/H/H | |
| LOC127935548 | caspase b | **caspbl pseudogene** (A) | H/H/L | 143 aa, no motif, 2 exons |
| LOC127949561 | caspase b-like | **caspbl pseudogene** (B) | H/H/L | 93 aa, no motif, 2 exons |

---

## Pair 3 — casp6 (zebrafish chr3)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A3 | LOC127950387 | caspase-6 | 297 aa | 297 aa (casp6a) | QACRG | 8 | ok |
| B3 | LOC127952414 | caspase-6 | 298 aa | 297 aa (casp6a) | QACRG | 8 | ok |

### Protein assessment

A clean single homeolog pair: A3 (297 aa) and B3 (298 aa), both QACRG,
both 8 exons, matched to the 297 aa zebrafish casp6a.

**[NEEDS REVIEW] — zebrafish casp6 expansion.** Zebrafish chr3 carries
**three** casp6 paralogues (casp6a, casp6b.1, casp6b.2), whereas
*C. gibelio* retains a single casp6 homeolog per subgenome. This is most
parsimoniously a zebrafish-lineage-specific tandem expansion, but with
no secondary diploid comparator in the repository the section 4.2
cross-check cannot confirm that. Carried as a hedge: the carp casp6
homeologs are well-supported; the ancestral casp6 copy-number is left
open.

### Synteny

A3 and B3 share the casp6 flanking block and match the zebrafish chr3
casp6a locus. Single clean slot.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| LOC127950387 | caspase-6 | **casp6** (A homeolog) | H/M/H | zf casp6 expansion → identity M |
| LOC127952414 | caspase-6 | **casp6** (B homeolog) | H/M/H | |

---

## Pair 5 — casp22 (zebrafish chr5)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A5 | — | — | — | 376 aa (casp22) | — | — | **[EMPTY-SLOT → CP3]** |
| B5 | casp22 | casp22 | 376 aa | 376 aa (casp22) | QACRG | 7 | ok |

### Protein assessment

B5 `casp22` (376 aa, QACRG, 7 exons) is a clean, full-length casp22
homeolog matched 1:1 to the zebrafish reference. A5 carries no caspase.

**A5 empty — flagged for Checkpoint 3.** Recorded as `absent — no
specific search`. The in-region sweep, syntenic-block-quality call, and
cross-species check are performed at the empty-slots deep dive, not
here.

### Synteny

B5 casp22 sits in its expected flanking block. A5's syntenic block to be
assessed at CP3.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| casp22 | casp22 | **casp22** (B homeolog) | H/H/H | clean |
| — | — | **casp22** (A5 absent) | — | flagged → CP3 |

---

## Pair 6 — casp8 / casp8l1 / casp20 (zebrafish chr6)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A6 | LOC128015385 | (caspase-8) | 474 aa | 476 aa (casp8) | QACQG | 9 | ok |
| A6 | LOC128015387 | (caspase-8-like) | 345 aa | 347 aa (casp20) | QACRG | 4 | ok |
| B6 | casp8 | casp8 | 476 aa | 476 aa (casp8) | QACQG | 9 | ok |
| B6 | casp8l1 | casp8l1 | 330 aa | 330 aa (casp8l1) | QACQG | 5 | ok |
| B6 | LOC127959693 | (caspase-8-like) | 352 aa | 347 aa (casp20) | QACRG | 4 | ok |

### Protein assessment

**casp8 (clean slot).** A6 `LOC128015385` (474 aa, QACQG, 9 exons) and B6
`casp8` (476 aa, QACQG, 9 exons) are an unambiguous homeolog pair —
matched length, the distinctive QACQG variant, and 9 exons on both.

**casp8l1 / casp20 sub-cluster — [NEEDS REVIEW].** The smaller copies are
harder to assign 1:1. B6 carries a named `casp8l1` (330 aa, QACQG, 5
exons). The two ~345–352 aa / 4-exon copies — A6 `LOC128015387` (345 aa)
and B6 `LOC127959693` (352 aa) — match the zebrafish casp20 length
(347 aa) and most likely form a casp20 homeolog pair, leaving casp8l1
with a B copy but an **uncertain A copy** (no clean ~330 aa / 5-exon A6
gene was found). Annotation-level evidence cannot firmly separate
casp8l1 from casp20 among the short copies; the casp8l1-vs-casp20
assignment and the possibility of a casp8l1 A-side absence are flagged
for curator review and, if needed, phylogenetic follow-up.

### Synteny

A6 and B6 share the casp8 neighbourhood, matching zebrafish chr6. The
casp8/casp8l1/casp20 copies are clustered, consistent with a local
caspase-8 subfamily array.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| LOC128015385 | caspase-8 | **casp8** (A homeolog) | H/H/H | QACQG, 9 exons |
| casp8 | casp8 | **casp8** (B homeolog) | H/H/H | |
| casp8l1 | casp8l1 | **casp8l1** (B) | H/M/H | A-side copy uncertain — review |
| LOC128015387 | caspase-8-like | **casp20** (A homeolog) | H/L/H | casp8l1/casp20 split — review |
| LOC127959693 | caspase-8-like | **casp20** (B homeolog) | H/L/H | casp8l1/casp20 split — review |

---

## Pair 7 — casp23 (zebrafish chr7) — synteny-vs-naming override

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A7 | casp23 | casp23 | 446 aa | 446 aa (casp23) | **QSCRG** | 11 | ok |
| B7 | LOC127961949 | **caspase a** | 452 aa | 446 aa (casp23) | QACRG | 11 | ok |

### Protein assessment

A textbook synteny-over-naming case. NCBI labels A7 `casp23` and B7
`LOC127961949` as **"caspase a" (caspa)**. But zebrafish chr7 carries
`casp23` only — `caspa` proper sits on zebrafish chr16 (pair 16). Both
A7 (446 aa, 11 exons) and B7 (452 aa, 11 exons) match the zebrafish
casp23 length and exon count.

**A7 motif variant.** A7 carries an unusual **QSCRG** active site (Ser at
position 2) against the standard QACRG on B7. Per §5.4.6 this is noted as
a feature of interest and does not lower confidence — a valid catalytic
pentapeptide is present and the rest of the evidence supports casp23.

### Synteny

Decisive. A7 `casp23` and B7 `LOC127961949` sit in the **same** flanking
neighbourhood — `oxa1l`, `slc7a7`, `ccnb1ip1`, `ttc5`, `man2b2`, `cd68`,
`mus81`, `ovol1a`, `znf638`, `trim39` — and that neighbourhood matches
the zebrafish chr7 casp23 locus exactly. B7 is therefore a casp23
homeolog by syntenic position; the NCBI "caspase a" label is a
similarity-based mis-call.

```
Zebrafish chr7:  ...mus81 ovol1a tkfc znf638 slc7a7 oxa1l [CASP23] ccnb1ip1 ttc5 man2b2 cd68...
Cgib A7:         ...mus81 ovol1a tkfc znf638 ...oxa1l [CASP23] slc7a7 ccnb1ip1 ttc5 cd68...
Cgib B7:         ...trim39 znf638 ...[LOC127961949=casp23] oxa1l slc7a7 ccnb1ip1 ttc5 man2b2 cd68...
```

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| casp23 | casp23 | **casp23** (A homeolog) | H/H/H | QSCRG variant (noted) |
| LOC127961949 | caspase a | **casp23** (B homeolog) | H/H/H | **NCBI override**: synteny → casp23, not caspa |

> **Curator decision — CONFIRMED (CP4, 2026-06-30):** B7 `LOC127961949`
> is relabelled from NCBI "caspase a" to **casp23 (B homeolog)**. The
> original NCBI annotation is preserved in the table above per §5.4.1.

---

## Pair 9 — casp10 (zebrafish chr9)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A9 | — | — | — | 520 aa (casp10) | — | — | **[EMPTY-SLOT → CP3]** |
| B9 | casp10 | casp10 | 520 aa | 520 aa (casp10) | QACRG | 8 | ok |

### Protein assessment

B9 `casp10` (520 aa, QACRG, 8 exons) is a clean full-length casp10
homeolog. A9 carries no caspase — flagged `absent — no specific search`
for Checkpoint 3.

### Synteny

B9 casp10 sits in its expected block; A9 to be assessed at CP3.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| casp10 | casp10 | **casp10** (B homeolog) | H/H/H | clean |
| — | — | **casp10** (A9 absent) | — | flagged → CP3 |

---

## Pair 10 — executioner tandem cluster (zebrafish chr10) — ambiguous slot

### Genes

| Chr | Gene ID | NCBI name | Length | Motif | CDS exons | Position | Status |
|-----|---------|-----------|--------|-------|-----------|----------|--------|
| A10 | LOC128020717 | (casp3/7-like) | 266 aa | QACRG | 5 | 0.81 Mb | ok |
| A10 | LOC128020716 | (casp3/7-like) | 267 aa | QACRG | 5 | 0.81 Mb | ok |
| A10 | LOC128020855 | (casp3/7-like) | 240 aa | QACRG | 4 | 3.57 Mb | ok |
| B10 | LOC127966004 | (casp3/7-like) | 274 aa | QACRG | 4 | 21.09 Mb | ok |
| B10 | LOC127966003 | (casp3/7-like) | 318 aa | QACRG | 4 | 21.10 Mb | ok |
| B10 | LOC127966001 | (casp3/7-like) | 273 aa | QACRG | 4 | 0.03 Mb | **artefact** |

### Protein assessment

This is the **executioner caspase confusion locus** (casp3/casp7
interchangeable in NCBI naming; encoded prior in the config sets
identity confidence to **low** here). It is a **tandem-cluster slot**:
synteny confirms the locus but cannot settle 1:1 within-cluster
paralogue identity, so the cluster is marked **ambiguous** and the A and
B members are listed as groups rather than paired (§5.4.3).

- A10 retains a near-identical tandem pair `LOC128020717` / `LOC128020716`
  (84% k-mer similarity, adjacent at ~0.81 Mb) plus a divergent third
  copy `LOC128020855` at 3.57 Mb (26% similarity — a separate paralogue).
- B10 retains a tandem pair `LOC127966004` / `LOC127966003` (~21.1 Mb).

**Asymmetric retention**, not a loss: A and B each retain multiple
paralogues; the procedure cannot say *which* paralogue is absent on
either side, so no within-cluster loss is claimed.

### Assembly artefact assessment for LOC127966001

`LOC127966001` matches the strong-artefact pattern (§5.4.4):
**subtelomeric** (27 kb from the B10 chromosome start), ~82% k-mer
similarity to `LOC127966003` which sits mid-chromosome at 21.10 Mb,
and **anomalous transcript variants** (3 isoforms vs 1 for its
neighbours). It is treated as a likely subtelomeric duplicate of
`LOC127966003` and marked **excluded** (status `artefact`). Because the
slot is present and ambiguous (not an empty side), the exclusion does
not generate a loss label. *Recent-tandem-duplication vs haplotig
cannot be separated at the annotation level → cross-assembly check
logged to side projects.*

### Synteny

A10 and B10 share the executioner-cluster flanking block; the cluster is
present on both subgenomes. Within-cluster order/identity is not
resolvable by synteny alone.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| LOC128020717 | casp3/7-like | **executioner cluster** (A) | H/L/H | ambiguous; identity awaits phylogeny |
| LOC128020716 | casp3/7-like | **executioner cluster** (A) | H/L/H | tandem dup of 717 |
| LOC128020855 | casp3/7-like | **executioner cluster** (A) | H/L/M | divergent 3rd copy, 240 aa |
| LOC127966004 | casp3/7-like | **executioner cluster** (B) | H/L/H | |
| LOC127966003 | casp3/7-like | **executioner cluster** (B) | H/L/H | |
| LOC127966001 | casp3/7-like | **assembly artefact** | — | subtelomeric dup of 966003 → excluded |

> Within-cluster casp3 vs casp7 identity → side projects (curated
> phylogeny).

---

## Pair 12 — casp7 (zebrafish chr12)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A12 | LOC128025366 | (caspase-7) | 312 aa | 381 aa (casp7) | QACRG | 6 | ok |
| B12 | casp7 | casp7 | 381 aa | 381 aa (casp7) | **NONE** | 7 | ok |

### Protein assessment

A12 `LOC128025366` (312 aa, QACRG, 6 exons) and B12 `casp7` (381 aa, 7
exons) sit at the casp7 locus on both subgenomes.

**[NEEDS REVIEW] — B12 casp7 active site not detected.** The named B12
`casp7` (full length, 381 aa, matching zebrafish casp7) returned **no
QACxG pentapeptide** in the motif scan, whereas its shorter A12 partner
carries a clean QACRG. This is the reverse of the usual pattern (the
named, full-length copy lacking the canonical motif). Possible
explanations: a non-canonical catalytic pentapeptide in this lineage, a
gene-model/isoform issue at the active-site exon, or a real catalytic
divergence. Annotation-level evidence cannot decide; flagged for the
curator and logged to side projects for sequence-level inspection of the
active-site region. Identity as casp7 (by synteny and length) is not in
doubt; the **model/functional** status of B12 is what needs review.

### Synteny

A12 and B12 share the casp7 flanking block, matching zebrafish chr12.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| LOC128025366 | caspase-7 | **casp7** (A homeolog) | H/H/M | 312 aa (shorter); QACRG |
| casp7 | casp7 | **casp7** (B homeolog) | H/H/M | **motif not detected — review** |

---

## Pair 14 — casp3b (zebrafish chr14)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A14 | LOC128027693 | (casp3-like) | 282 aa | 224 aa (casp3b) | QACRG | 6 | ok |
| B14 | LOC127970959 | (casp3-like) | 275 aa | 224 aa (casp3b) | QACRG | 6 | ok |

### Protein assessment

A14 (282 aa) and B14 (275 aa), both QACRG / 6 exons, form a clean
homeolog pair at the casp3b locus. Identity confidence is set **low** by
the encoded executioner-confusion prior (casp3b shares the casp3/casp7
naming ambiguity). Both copies are longer than the rather short
zebrafish casp3b reference (224 aa); structurally credible (intact motif,
group-typical exon count).

### Synteny

A14 and B14 share the casp3b flanking block (matching zebrafish chr14).
Note: the common-carp pilot found a syntenic-position-loss at its A14
(§5.4.2); in *C. gibelio* the block is present on both subgenomes, so
that sub-case does **not** apply here.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| LOC128027693 | casp3-like | **casp3b** (A homeolog) | H/L/H | exec-confusion prior → identity L |
| LOC127970959 | casp3-like | **casp3b** (B homeolog) | H/L/H | |

---

## Pair 16 — caspa / casp2 (zebrafish chr16)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A16 | LOC128030415 | (caspase a) | 394 aa | 383 aa (caspa) | QACRG | 7 | ok |
| A16 | — | — | — | 435 aa (casp2) | — | — | **[EMPTY-SLOT → CP3]** |
| B16 | LOC127975488 | (caspase a) | 393 aa | 383 aa (caspa) | QACRG | 7 | ok |
| B16 | casp2 | casp2 | 435 aa | 435 aa (casp2) | QACRG | 10 | ok |

### Protein assessment

Zebrafish chr16 carries two separate caspase loci, `caspa` (383 aa) and
`casp2` (435 aa). In *C. gibelio*:

- **caspa slot:** A16 `LOC128030415` (394 aa, 7 exons) and B16
  `LOC127975488` (393 aa, 7 exons) form a clean caspa homeolog pair
  (matched length and exon count to the 383 aa zebrafish caspa).
- **casp2 slot:** B16 `casp2` (435 aa, 10 exons) is a clean casp2
  homeolog. **A16 appears to lack a casp2 homeolog** — only the caspa-
  like copy is present on A16.

**[NEEDS REVIEW] / [EMPTY-SLOT → CP3] — possible casp2 candidate loss on
A16.** This is an additional empty slot beyond the three obvious ones
(A5, A9, B21). It is flagged `absent — no specific search`; the
Checkpoint 3 sweep will determine whether the A16 casp2 syntenic block is
present-but-empty (candidate loss) or whether a casp2 A-copy was missed
by the Stage 2 search (→ inventory addition before any loss claim). Note
this slot was **not** in the worked-example's known-missing list, so it
warrants explicit curator attention.

### Synteny

B16 carries two distinct blocks (caspa at ~25.95 Mb, casp2 at
~12.28 Mb); zebrafish likewise carries two separate chr16 blocks. A16
carries the caspa block; the casp2 block on A16 to be assessed at CP3.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| LOC128030415 | caspase a | **caspa** (A homeolog) | H/H/H | |
| LOC127975488 | caspase a | **caspa** (B homeolog) | H/H/H | |
| casp2 | casp2 | **casp2** (B homeolog) | H/H/H | |
| — | — | **casp2** (A16 absent?) | — | flagged → CP3 (review: loss vs missed gene) |

---

## Pair 21 — casp21 (zebrafish chr21)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A21 | casp21 | casp21 | 266 aa | 266 aa (casp21) | QACRG | 6 | ok |
| B21 | — | — | — | 266 aa (casp21) | — | — | **[EMPTY-SLOT → CP3]** |

### Protein assessment

A21 `casp21` (266 aa, QACRG, 6 exons) is a clean full-length casp21
homeolog matched 1:1 to zebrafish. B21 carries no caspase — flagged
`absent — no specific search` for Checkpoint 3.

### Synteny

A21 casp21 sits in its expected block; B21 to be assessed at CP3.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| casp21 | casp21 | **casp21** (A homeolog) | H/H/H | clean |
| — | — | **casp21** (B21 absent) | — | flagged → CP3 |

---

## Pair 23 — casp9 (zebrafish chr23)

### Genes

| Chr | Gene ID | NCBI name | Length | Outgroup ref | Motif | CDS exons | Status |
|-----|---------|-----------|--------|--------------|-------|-----------|--------|
| A23 | LOC127944670 | (caspase-9) | 421 aa | 436 aa (casp9) | QACGG | 10 | ok |
| B23 | casp9 | casp9 | 436 aa | 436 aa (casp9) | QACGG | 10 | ok |

### Protein assessment

A clean homeolog pair: A23 `LOC127944670` (421 aa) and B23 `casp9`
(436 aa), both with the **QACGG** variant (Gly at position 4, the
casp9-typical active site) and both 10 exons. Matched to the 436 aa
zebrafish casp9.

### Synteny

A23 and B23 share the casp9 flanking block, matching zebrafish chr23.

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Conf (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------|-------|
| LOC127944670 | caspase-9 | **casp9** (A homeolog) | H/H/H | QACGG |
| casp9 | casp9 | **casp9** (B homeolog) | H/H/H | QACGG |

---

## Summary

### Gene count

33 *C. gibelio* caspase gene models across 12 homeolog pairs:

- **27** functional full-length genes
- **2** pseudogenes / non-functional remnants (caspbl A1, caspbl B1)
- **1** assembly artefact, excluded (LOC127966001, B10 subtelomeric)
- **3** ambiguous executioner-cluster copies counted as functional but
  with unresolved within-cluster identity (pair 10)

### Empty slots — assessed at Checkpoint 3

CP3 in-region sweep performed for each flagged slot on the empty
chromosome: outgroup retention (zebrafish) ✓, homeolog retention (other
subgenome) ✓, syntenic-block quality, and the biotype→description→
protein-FASTA sweep. All four return **candidate loss (annotation-
level)** — pending curator sign-off.

| Missing gene | Chromosome | Outcome | Syntenic-block quality | In-region sweep result | Shared with other carps? |
|---|---|---|---|---|---|
| casp22 | A5 (NC_068375.1) | candidate loss (annotation-level) | clear | negative — `card9` (CARD9) is a **separate gene present on both A5 and B5**, not casp22 | likely (single casp22 copy in each carp) |
| casp10 | A9 (NC_068379.1) | candidate loss (annotation-level) | clear | negative — `cflar` is a **separate gene forming its own A9/B9 homeolog pair and coexisting with casp10 on B9**, not a casp10 | needs check |
| casp21 | B21 (NC_068416.1) | candidate loss (annotation-level) | clear | negative — `nlrc3l1` / NLR-CARD genes present on **both A21 and B21**, not casp21 | needs check |
| casp2 | A16 (NC_068386.1) | candidate loss (annotation-level) **[hedged]** | **partial** | negative — **no casp2 feature anywhere on A16**; only `caspa` (inventoried) + ASC | single-copy casp2 in each carp; **common carp has no named casp2 at all** |

**Distractor-gene verification (CP3).** For each candidate loss the
caspase-adjacent feature that the in-region sweep returned was checked
against the *retaining* homeolog and is confirmed to be a genuinely
distinct gene, not a mislabeled copy of the missing caspase:

- **A5 / card9:** CARD9 (the canonical caspase false-positive) sits on
  B5 (~25.6 Mb) and a card9 ortholog is also present in the A5 region —
  a separate CARD-domain gene on both subgenomes, not casp22.
- **A9 / cflar:** B9 carries **both** casp10 (4.84 Mb) **and** cflar
  (5.50 Mb) as two distinct genes; A9 carries cflar (6.81 Mb) but not
  casp10. cflar is the catalytically-dead DED-domain paralogue in the
  casp8/casp10 death-fold cluster (excluded at CP1). Zebrafish likewise
  carries casp10 and, separately, cflara/cflarb. So the A9 cflar is the
  cflar homeolog, **not** a casp10 — casp10 is genuinely absent at its
  A9 syntenic position.
- **B21 / nlrc3l1:** NLR-CARD genes are present on both A21 and B21 —
  separate genes, not casp21.

**A16 casp2 — hedged.** No casp2 feature exists anywhere on A16; the
casp2 immediate-flanking block is only *partially* recovered on A16
(near the chromosome start), so the loss claim is hedged relative to the
three clean cases. Supporting cross-species signal: casp2 is single-copy
in each carp and **common carp carries no named casp2 at all**, hinting
at broader casp2 sparseness worth a sequence-level check.

Each candidate-loss slot carries `A_loss`/`B_loss = "searched"` in the
curation JSON so the explorer renders it as *candidate loss · annotation-
level*. None reached a pseudogene/`LOW QUALITY PROTEIN` finding, so none
takes the non-functional-locus label. Sequence-level confirmation
(tBLASTn) for every candidate loss is logged to side projects.

### Motif / functional-feature variants

- **QSCRG** (Ser at pos 2): A7 casp23 — a notable variant; B7 casp23 is
  standard QACRG.
- **QACQG** (Gln at pos 4): the casp8 group (A6/B6 casp8, casp8l1).
- **QACGG** (Gly at pos 4): casp9 (A23/B23) — the casp9-typical site.
- **NONE detected**: B12 casp7 (full length, motif not found — **[NEEDS
  REVIEW]**); both caspbl remnants (expected — pseudogenes).

### Synteny quality

Cleanest single-slot pairs (best starting points for any downstream
phylogenetic work): **7 (casp23), 23 (casp9), 1 (casp3a), 3 (casp6)** —
flanking blocks fully conserved A/B and against zebrafish. The
executioner cluster (pair 10) has conserved flanking blocks but
unresolved internal order. Pair 7 is the strongest synteny story and the
clearest NCBI-naming override.

### Confidence summary (functional genes)

| L/I/M triple | Count | Pairs |
|---|---|---|
| H/H/H | 11 | 1 (casp3a×2, caspb×2), 5, 6 (casp8×2), 7 (casp23×2), 9, 16 (caspa×2, casp2), 21, 23×2 |
| H/M/H | 2 | 3 (casp6 ×2) |
| H/M (mixed) | 2 | 6 casp8l1; (casp7 model M ×2) |
| H/L/H | 5–7 | 6 (casp20×2), 10 (cluster), 14 (casp3b×2) |
| Pseudogene | 2 | 1 (caspbl A1, B1) |
| Artefact (excluded) | 1 | 10 (LOC127966001) |

### Side-projects list (annotation-level evidence insufficient)

1. **Within-cluster identity at pair 10** (casp3 vs casp7 vs casp17 for
   each executioner copy) → curated phylogeny.
2. **B10 LOC127966001**: recent tandem duplication vs assembly haplotig
   → cross-assembly comparison.
3. **B12 casp7 active site**: motif not detected in the full-length
   named copy → sequence-level inspection of the active-site exon.
4. **A16 casp2**: confirm candidate loss vs missed annotation →
   resolved at CP3; sequence-level confirmation of any loss → tBLASTn.
5. **casp6 ancestral copy number** (zebrafish 3-paralogue expansion vs
   carp single copy) → secondary diploid comparator when available.
6. **All candidate losses (A5, A9, B21, ±A16)**: annotation-level
   candidate loss → tBLASTn confirmation at the unannotated locus.

---

*End of curation. Checkpoint 3 (empty-slots deep dive) and Checkpoint 4
(curation sign-off) are complete; Checkpoint 5 (interpretive layer:
Executioner / Initiator / Inflammatory) was agreed and the hierarchy
explorer was built at `results/explorers/Cgib_caspase_hierarchy.html`.
The four candidate losses below were assessed and signed off at CP3 — see
the "Empty slots — assessed" table above. The `[NEEDS REVIEW]` flags and
the `[EMPTY-SLOT → CP3]` markers in the per-pair sections are retained as
provenance of the initial draft state; the resolved outcomes supersede
them and are recorded in the summary and the curation JSON
(`Carassius_gibelio_caspase_curation_data.json`).*
