# Caspase family — curation in *Carassius auratus* (goldfish)

Focal species: **Carassius auratus** (goldfish, GCF_003368295.1). Goldfish
chromosomes are numbered 1–50 with no native A/B labels; subgenome
assignments come from the pre-built `config/goldfish_subgenome_lookup.tsv`
(Stage 3a, alignment to *C. gibelio*). Curated against the zebrafish
reference framework; other carps consulted as supporting evidence.

Status: **reviewed and signed off** (2026-06-30). Standard-of-evidence
and synteny-over-naming conventions as in the *C. gibelio* document.
Zebrafish is the only diploid comparator (losses hedged accordingly).

### Revision history

1. **Initial per-pair draft** (unattended mode) — 12 framework pairs +
   6 unplaced-scaffold caspases.
2. **Checkpoint 3 — empty-slots deep dive** — in-region sweeps run on the
   subgenome-lookup-mapped empty chromosomes; **four candidate losses**
   (casp22/A5, casp21/B21, casp3b/A14, caspb/B1, all negative sweeps),
   **one candidate non-functional locus** (casp10/A9, pseudogene-biotype
   remnant LOC113053832), and caspbl absent on both subgenomes.
3. **Checkpoint 4 — review, signed off by curator** (2026-06-30) — all
   five empty/degraded slots confirmed as drafted; the **pair-7 casp23
   relabel confirmed**; [NEEDS REVIEW] items (B14 near-identical casp3b
   pair, casp2/A16 LOW QUALITY PROTEIN, the 6 unplaced caspases) confirmed
   as logged to side projects. CP5 grouping agreed; explorer built at
   `../example_explorers/Caur_caspase_hierarchy.html`.

## Headline

Goldfish shows the **most reduction** of the three carps. It shares the
gibelio losses (casp22/A5, casp21/B21) and adds a casp3b/A14 loss and a
caspb/B1 loss, and at casp10/A9 it carries a **pseudogene** rather than a
clean absence — a *candidate non-functional locus*. caspbl is absent
entirely. Six caspases sit on **unplaced scaffolds** (subgenome
unresolvable).

31 placed caspase models across 12 framework pairs + 6 unplaced.

---

## CP3 — empty / degraded slots (assessed)

| Missing/degraded | Chr (goldfish) | Outcome | Block | Sweep | Shared with other carps? |
|---|---|---|---|---|---|
| casp22 | A5 (NC_039247.1) | candidate loss (annotation-level) | clear | negative (0 caspase features) | yes — also lost on A5 in gibelio |
| casp21 | B21 (NC_039263.1) | candidate loss (annotation-level) | clear | negative | yes — also lost on B21 in gibelio |
| casp3b | A14 (NC_039281.1) | candidate loss (annotation-level) | clear | negative; B14 retains 2 copies | no — gibelio retains both |
| caspb | B1 (NC_039268.1) | candidate loss (annotation-level) | clear | negative (only casp3a, a separate gene) | no — gibelio retains both |
| casp10 | A9 (NC_039276.1) | **candidate non-functional locus** | clear | **pseudogene biotype** (LOC113053832, "caspase-8-like") | gibelio = clean loss; goldfish = pseudogene remnant |
| caspbl | A1 + B1 | candidate loss both sides (hedged) | — | no caspbl annotated in goldfish | gibelio/Ccar retain degraded remnants |

The casp10/A9 finding is the methodologically interesting one: a
`gene_biotype=pseudogene` feature sits at the A9 syntenic position, so the
locus is *present but non-functional* (third outcome label) rather than
absent — a stronger annotation-level signal than gibelio's clean A9 loss.

---

## Per-pair summary

**Pair 1 (casp3a/caspb/caspbl):** casp3a clean pair (A1 LOC113105596 320 /
B1 `casp3a` 282). caspb on A1 only (LOC113115174, 384) — **B1 caspb
candidate loss**. caspbl absent on both subgenomes (candidate loss, hedged
— caspbl is degraded even where retained in the other carps).

**Pair 3 (casp6):** clean A/B pair (297 / 298, QACRG, 8 exons).

**Pair 5 (casp22):** B5 `casp22` (376) retained; **A5 candidate loss**
(shared with gibelio).

**Pair 6 (casp8/casp8l1/casp20):** casp8 clean (A6 LOC113050793 474 / B6
LOC113093418 476, QACQG). casp20 clean (A6 345 / B6 352). casp8l1 on B6
only (A-side uncertain — asymmetric).

**Pair 7 (casp23):** synteny override again — B7 LOC113105593 (NCBI
"caspase a-like") is a casp23 homeolog by position; A7 `casp23` carries
the QSCRG variant. **Relabel B7 → casp23 — CONFIRMED by curator (CP4,
2026-06-30);** original NCBI name preserved above.

**Pair 9 (casp10):** B9 `casp10` (520) clean. **A9 = candidate
non-functional locus** — LOC113053832 is a `pseudogene`-biotype remnant
at the A9 position (NCBI "caspase-8-like").

**Pair 10 (executioner cluster):** A10 ×3 (326, 304, 240), B10 ×2 (318,
274) — ambiguous tandem cluster; within-cluster identity → phylogeny.

**Pair 12 (casp7):** A12 LOC113076928 (312, on an unplaced scaffold,
override→A12) / B12 LOC113111581 (276). Both present.

**Pair 14 (casp3b):** B14 retains two near-identical copies (LOC113113788,
LOC113113799, both 275 aa / 6 exons — a tandem pair, possible recent
duplication or assembly duplicate [NEEDS REVIEW]). **A14 candidate loss.**

**Pair 16 (caspa/casp2):** both bilateral. casp2 A16 LOC113060139 (435,
**RefSeq LOW QUALITY PROTEIN** [NEEDS REVIEW]) / B16 `casp2` (435). caspa
A16 LOC113059546 (394) / B16 LOC113115897 (393).

**Pair 21 (casp21):** A21 `casp21` (266) retained; **B21 candidate loss**
(shared with gibelio).

**Pair 23 (casp9):** A23 LOC113065546 (421) / B23 `casp9` (436, on an
unplaced scaffold, override→B23). Both present, QACGG site.

**Unplaced scaffolds (6 caspases, subgenome unresolvable):** LOC113074243
(385), LOC113082415 (381), LOC113074954 (282), LOC113102528 (240),
LOC113074955 (125, fragment), LOC113102983 (pseudogene). These carry
caspase models but sit on unplaced scaffolds, so neither pair nor
subgenome can be assigned. Several may be additional executioner-cluster
or casp3b copies. Logged to side projects (scaffold placement / identity).

---

## Summary

### Gene count
31 placed framework models + 6 unplaced, across 12 pairs:

- ~26 functional placed genes
- 1 pseudogene at a framework position (casp10/A9 non-functional locus)
- 0 placed assembly artefacts (B14 near-identical pair flagged, not excluded)
- 6 unplaced-scaffold caspases (2 of them fragment/pseudogene)

### Candidate losses / non-functional (5)
casp22/A5, casp21/B21, casp3b/A14, caspb/B1 (candidate losses);
casp10/A9 (candidate non-functional locus, pseudogene). caspbl absent
both subgenomes. **Most reduced of the three carps.**

### Cross-species synthesis (the point of curating all three)
| Locus | C. gibelio | C. carpio | C. auratus |
|---|---|---|---|
| casp22 / A5 | candidate loss | present (unplaced) | candidate loss |
| casp10 / A9 | candidate loss | present (bilateral) | **pseudogene (non-functional)** |
| casp21 / B21 | candidate loss | present (bilateral) | candidate loss |
| casp2 / A16 | candidate loss | present (bilateral, LOC) | present (bilateral) |
| casp3b | A+B | A + B×3 (expansion) | **A loss**, B×2 |
| caspb / B1 | present | present | candidate loss |

Common carp is the most complete; goldfish the most reduced; gibelio
intermediate. The casp10/A9 outcome differs in *kind* across species
(loss vs pseudogene vs retention) — a clean illustration of why each
focal species is curated independently rather than merged.

### Side projects
1. Six unplaced-scaffold caspases — placement & identity (scaffold
   anchoring / phylogeny).
2. B14 near-identical casp3b pair — recent duplication vs assembly
   artefact (cross-assembly).
3. casp2/A16 LOW QUALITY PROTEIN model — structural check.
4. Executioner-cluster within-cluster identities — phylogeny.
5. tBLASTn confirmation of all candidate losses; sequence-level dating of
   the casp10/A9 pseudogene.
