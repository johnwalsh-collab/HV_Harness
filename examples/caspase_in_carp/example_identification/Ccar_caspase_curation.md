# Caspase family — curation in *Cyprinus carpio* (common carp)

Focal species: **Cyprinus carpio** (common carp, GCF_018340385.1), A and
B subgenomes curated against the *Danio rerio* (zebrafish) reference
framework. Other carp genomes consulted as supporting evidence only.

Status: **reviewed and signed off** (2026-06-30). This is a sibling
curation to the *C. gibelio* document; the standard-of-evidence and
annotation-principle openers there apply verbatim and are summarised
below. Uncertain calls remain marked **[NEEDS REVIEW]** and are logged to
side projects.

### Revision history

1. **Initial per-pair draft** (unattended mode) — all 12 framework pairs
   + the off-framework B22 gene drafted in one pass.
2. **Checkpoint 3 — empty-slots deep dive** — **two candidate losses**:
   casp22 (single-copy; one homeolog lost, subgenome indeterminate as the
   survivor is unplaced) and caspbl/A1 (whole-slot absence on A1, hedged —
   degraded slot). `casp8l1/A6` is genuine asymmetric retention within the
   casp8 cluster (present on both subgenomes), recorded as `na`.
   (Corrected post-review: caspbl/A1 and casp22 were initially mislabelled
   as no-loss.)
3. **Checkpoint 4 — review, signed off by curator** (2026-06-30) — the
   **pair-7 casp23 relabel was confirmed**; the [NEEDS REVIEW] items (A6
   834-aa casp8 model, B12 casp7 motif, A1 caspb LOW QUALITY PROTEIN,
   off-framework B22 casp23-like gene) are confirmed as logged to side
   projects, not unresolved contradictions. CP5 grouping (Executioner /
   Initiator / Inflammatory) agreed; explorer built at
   `../example_explorers/Ccar_caspase_hierarchy.html`.

## Standard of evidence (summary)

Annotation-level claims only. Strongest loss claim = **candidate loss
with annotation-level evidence** (outgroup retains it, homeolog retains
it, in-region sweep negative, syntenic block recognisable). "Confirmed
loss" requires out-of-scope sequence-level work. Conserved **syntenic
position overrides similarity-based NCBI naming**; original NCBI names
are preserved in every table. Zebrafish is the **only** diploid
comparator in this repository (no tiger barb / grass carp), so possible
zebrafish-specific patterns are hedged, not cross-checked.

## Headline — common carp vs *C. gibelio*

Common carp retains the caspase complement **more completely** than
Prussian carp. The four candidate losses seen in *C. gibelio* (casp22/A5,
casp10/A9, casp21/B21, casp2/A16) are **not** losses in common carp —
casp10, casp21, and casp2 are present on both subgenomes here, and casp22
is present (on an unplaced scaffold). Common carp also shows two
expansions/extras gibelio lacks: a 3-copy casp3b tandem array on B14 and
an off-framework casp23-like gene on chromosome B22.

40 caspase gene models across 12 framework pairs (+1 off-framework).

---

## Pair 1 — casp3a / caspb / caspbl (zf chr1)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A1 | LOC109096543 | caspase-3-like | 276 | QACRG | 6 | ok |
| B1 | casp3a | casp3a | 282 | QACRG | 6 | ok |
| A1 | LOC109062408 | caspase b-like | 383 | QACRG | 8 | ok (LOW QUALITY PROTEIN) |
| B1 | LOC109062412 | caspase b-like | 382 | NONE | 7 | ok |
| B1 | LOC122136065 | caspase b-like | 116 | NONE | 2 | candidate_nonfunctional |
| B1 | LOC122135952 | caspase b-like | 93 | NONE | 2 | candidate_nonfunctional |

**casp3a:** A1 LOC109096543 (276) / B1 `casp3a` (282) — clean homeolog
pair. **caspb:** A1 LOC109062408 (383, flagged LOW QUALITY PROTEIN by
RefSeq) / B1 LOC109062412 (382) — homeolog pair; the A copy carries a
model-quality flag. **caspbl:** both truncated remnants (116, 93 aa, no
motif, 2 exons) sit on **B1**; A1 has no caspbl copy. The caspbl slot is
its own ancestral locus (as in gibelio/goldfish), so the empty A1 side is
a **candidate loss (annotation-level, hedged)** — hedged because caspbl is
a degraded pseudogene wherever it is retained, so the "loss" is of an
already-non-functional element. (This corrects an earlier draft that
mislabelled it "asymmetric retention"; that term is reserved for
copy-count differences *within a cluster present on both subgenomes* — it
does not apply to a whole-slot absence on one side.)

**[NEEDS REVIEW]** A1 caspb (LOC109062408) is RefSeq LOW QUALITY PROTEIN
— model credible but worth a structural check.

## Pair 3 — casp6 (zf chr3)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A3 | LOC109062420 | caspase-6 | 292 | QACRG | 8 | ok |
| B3 | LOC122136604 | caspase-6 | 269 | QACRG | 5 | ok |

Clean casp6 homeolog pair. B3 is shorter with fewer exons (269 aa / 5
exons vs 292 / 8) — a slightly degraded but valid model. Identity high,
model medium on B3.

## Pair 5 — casp22 (zf chr5) — single-copy; one homeolog a candidate loss

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| unplaced | casp22 | casp22 | 376 | QACRG | 7 | ok |
| (other homeolog) | — | — | — | — | — | **candidate loss** |

casp22 is present and full-length, but as a **single copy** on unplaced
scaffold NW_024879254.1 (chromosome_override places it at pair 5). In a
tetraploid, two casp22 homeologs (A5 + B5) are expected, so the single
copy means **one homeolog is a candidate loss (annotation-level)** — the
same single-copy reduction seen in both *Carassius* species. Because the
surviving copy is unplaced, the annotation **cannot determine which
subgenome (A5 or B5) was lost**; the loss is recorded as
subgenome-indeterminate. (In gibelio and goldfish the survivor is on B5,
so A5 is the lost side; whether common carp lost the same A5 copy cannot
be confirmed from annotation alone.) Scaffold placement → side projects.

## Pair 6 — casp8 / casp8l1 / casp20 (zf chr6)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A6 | LOC109056418 | caspase-8-like | 834 | QACQG | 16 | ok **[anomalous]** |
| B6 | casp8 | casp8 | 476 | QACQG | 9 | ok |
| A6 | LOC109053966 | caspase-8-like | 353 | QACRG | 4 | ok |
| B6 | LOC109047269 | caspase-8-like | 352 | QACRG | 4 | ok |
| B6 | casp8l1 | casp8l1 | 330 | QACQG | 5 | ok |

**casp8:** B6 `casp8` (476, 9 exons) is clean. Its A-side partner
LOC109056418 is **834 aa / 16 exons — roughly double the expected casp8
size [NEEDS REVIEW]**: most likely an assembly/gene-model artefact (a
fused or tandem-duplicated model) rather than a genuine 834-aa caspase.
Retained but flagged; cross-assembly check → side projects. **casp20:**
A6 LOC109053966 (353) / B6 LOC109047269 (352) — clean homeolog pair.
**casp8l1:** present on B6 only; A-side copy uncertain (same pattern as
gibelio) — asymmetric, no loss claim.

## Pair 7 — casp23 (zf chr7) — synteny-vs-naming override

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A7 | casp23 | casp23 | 446 | QSCRG | 11 | ok |
| B7 | LOC109093960 | caspase a-like | 455 | QACRG | 11 | ok |

Same textbook override as in gibelio: B7 LOC109093960 is NCBI "caspase
a-like" but is a **casp23 homeolog by syntenic position** (zebrafish chr7
carries casp23 only; caspa proper is chr16). A7 again carries the QSCRG
active-site variant. **Relabel B7 → casp23 (B homeolog) — CONFIRMED by
curator (CP4, 2026-06-30);** original NCBI name preserved above.

## Pair 9 — casp10 (zf chr9) — retained on both (contrast with gibelio)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A9 | LOC109064153 | caspase-10 | 509 | QACRG | 10 | ok |
| B9 | LOC109097220 | caspase-10 | 515 | QACRG | 10 | ok |
| B9 | LOC122138425 | caspase-10-like | 273 | QACRG | 3 | ok |

casp10 is a **clean A/B homeolog pair** in common carp (509 / 515 aa) —
unlike gibelio, where A9 casp10 is a candidate loss. B9 also carries a
short extra copy (273 aa, 3 exons) — likely a partial/truncated
duplicate; noted, low model confidence.

## Pair 10 — executioner tandem cluster (zf chr10) — ambiguous

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A10 | LOC109065583 | casp3/7-like | 278 | QACRG | 4 | ok |
| A10 | LOC109050440 | casp3/7-like | 266 | QACRG | 4 | ok |
| A10 | LOC122146508 | casp3/7-like | 158 | QACRG | 2 | candidate_nonfunctional |
| B10 | LOC109061445 | casp3/7-like | 274 | QACRG | 4 | ok |
| B10 | LOC122138630 | casp3/7-like | 247 | NONE | 5 | candidate_nonfunctional |

Ambiguous executioner cluster (casp3/casp7 interchangeable; low identity
confidence by the encoded prior). Within-cluster identity → phylogeny
(side projects). Two short/atypical copies flagged non-functional:
A10 LOC122146508 (158 aa, partial, 2 exons) and B10 LOC122138630 (247 aa,
no catalytic motif). Asymmetric retention, not loss.

## Pair 12 — casp7 (zf chr12)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A12 | LOC109099719 | caspase-7 | 338 | QACRG | 7 | ok |
| B12 | casp7 | casp7 | 381 | NONE | 7 | ok |
| A12 | LOC122147023 | caspase-7-like | 143 | NONE | 2 | candidate_nonfunctional |

casp7 homeolog pair: A12 LOC109099719 (338, QACRG) / B12 `casp7` (381).
**[NEEDS REVIEW]** — B12 `casp7` again returns **no QACxG motif**, the
same anomaly seen in gibelio B12. Consistent across both species, which
argues for a real lineage feature (non-canonical active site) rather than
a one-off model error → sequence-level check (side projects). A12 also
carries a 143-aa fragment (no motif, 2 exons) — non-functional remnant.

## Pair 14 — casp3b (zf chr14) — B-side tandem expansion

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A14 | LOC109089113 | caspase-3-like | 275 | QACRG | 7 | ok |
| B14 | LOC109071296 | caspase-3-like | 276 | QACRG | 6 | ok |
| B14 | LOC109071297 | caspase-3-like | 282 | QACRG | 6 | ok |
| B14 | LOC109068105 | caspase-3-like | 230 | QACRG | 5 | ok |

casp3b is present on A14 (LOC109089113, flanked by `irf2` and `cenpu` —
casp3b-block markers, so syntenically anchored) and **expanded to three
tandem copies on B14**. This is **asymmetric retention / B-side
expansion**, not a loss. (Note: an older worked-example claim of an A14
syntenic-position-loss is **not** supported by this assembly's
annotation, where the A14 block markers are present.) Identity low by the
executioner-confusion prior; within-B14 paralogue identities → phylogeny.

## Pair 16 — caspa / casp2 (zf chr16) — both retained (contrast with gibelio)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A16 | LOC109105725 | caspase-2-like | 440 | QACRG | 10 | ok |
| B16 | LOC109085235 | caspase-2-like | 436 | QACRG | 10 | ok |
| A16 | caspa | caspa | 383 | QACRG | 7 | ok |
| B16 | LOC109079016 | caspase a-like | 400 | QACRG | 7 | ok |

Both slots are **bilateral** in common carp. **casp2:** A16 LOC109105725
(440) / B16 LOC109085235 (436) — a clean casp2 homeolog pair, **LOC-named
rather than symbol-named** (which is why a symbol search reports "no
casp2 in common carp" — it is present, just not symbol-named). This
directly answers the gibelio-side question: casp2 exists in common carp.
**caspa:** A16 `caspa` (383, named) / B16 LOC109079016 (400) — clean
pair. No casp2 candidate loss here (contrast gibelio A16).

## Pair 21 — casp21 (zf chr21) — retained on both (contrast with gibelio)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A21 | LOC109064749 | caspase-21-like | 279 | QSCRG | 6 | ok |
| B21 | LOC109076849 | caspase-21-like | 263 | QACRG | 6 | ok |

casp21 is a **clean A/B homeolog pair** in common carp — unlike gibelio,
where B21 is a candidate loss. A21 carries a QSCRG active-site variant.

## Pair 23 — casp9 (zf chr23)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| A23 | LOC109103852 | caspase-9 | 424 | QACGG | 10 | ok |
| B23 | LOC109048790 | caspase-9 | 436 | QACGG | 10 | ok |

Clean casp9 homeolog pair, both with the casp9-typical QACGG active site.

## Off-framework — chromosome B22 (LOC109088469)

| Chr | Gene ID | NCBI name | Length | Motif | Exons | Status |
|---|---|---|---|---|---|---|
| B22 | LOC109088469 | caspase a-like | 452 | QSCRG | 11 | ok |

A casp23-like gene (452 aa / 11 exons / QSCRG — matching casp23's
signature) sits on chromosome **B22**, a position with **no caspase in
the zebrafish framework**. Its flanking neighbourhood (RhoA, SDH, USP8,
E3-ARI…) is **not** the casp23/chr7 block, so synteny does not place it
at a known caspase locus. Treated as a **group-related gene at an
anomalous chromosomal position, identity unresolved** → side projects
(possible translocated/duplicated casp23 paralogue; needs phylogeny or
flanking re-annotation). Not assigned to a framework pair.

---

## Summary

### Gene count
40 framework caspase models + 1 off-framework, across 12 pairs:

- ~31 functional full-length genes
- 5 pseudogenes / non-functional remnants (caspbl B1 ×2; exec-cluster
  fragments A10/B10; casp7 fragment A12)
- 0 assembly artefacts excluded (the 834-aa A6 casp8 model is *flagged*,
  not excluded)
- 1 off-framework group-related gene (B22)

### Candidate losses (2)
- **casp22** — single-copy (one homeolog a candidate loss; surviving copy
  unplaced, so the lost subgenome is indeterminate). The same single-copy
  reduction seen in both *Carassius* species.
- **caspbl / A1** — whole-slot absence on A1 (candidate loss, hedged: a
  degraded pseudogene slot; B1 retains two pseudogenized copies).

`casp8l1/A6` is **not** a candidate loss — it is genuine asymmetric
retention of a paralogue *within* the casp8 cluster, which is present on
both subgenomes (casp8 and casp20 bilateral).

Common carp still has the **fewest** losses of the three carps and the
most complete *functional* complement (both candidate losses are of
degraded/single-copy elements; no functional bilateral gene is lost).

### Notable features
- **casp23 override** (B7) — same as gibelio.
- **casp10, casp21, casp2 all bilateral** — retained where gibelio lost
  one homeolog. (casp21 bilateral here is the clean *Carassius*-shared-loss
  contrast; casp22, by contrast, is single-copy in all three carps.)
- **B14 casp3b tandem expansion** (3 copies).
- **Off-framework casp23-like gene on B22.**
- **834-aa casp8 model on A6** — likely model artefact, flagged.
- **B12 casp7 motif absence** — reproduced from gibelio; cross-species
  consistency argues for a real feature.
- **casp22 single-copy / unplaced** — one homeolog candidate loss,
  subgenome indeterminate.

### Side projects
1. B22 off-framework casp23-like gene — identity/origin (phylogeny).
2. A6 834-aa casp8 model — artefact vs real (cross-assembly).
3. B12 casp7 active-site motif absence (shared with gibelio) — sequence
   level.
4. casp22 unplaced-scaffold subgenome placement.
5. Executioner-cluster (pair 10) and B14 within-cluster identities —
   phylogeny.

### Confidence summary (functional genes)
| L/I/M triple | Pairs |
|---|---|
| H/H/H | 7 (casp23), 9 (casp10 ×2), 16 (casp2 ×2, caspa ×2), 23 (casp9 ×2) |
| H/M/H | 1 (casp3a, caspb), 3 (casp6) |
| H/L/H | 6 (casp20), 10 (exec cluster), 14 (casp3b ×4), 21 (casp21 ×2) |
| Non-functional | 1 (caspbl ×2), 10 (fragments), 12 (A12 fragment) |
| Flagged model | 6 (A6 834-aa casp8) |
| Off-framework | B22 |
