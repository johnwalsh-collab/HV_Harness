# Methods — Annotation-level curation of a gene family across three allotetraploid carp genomes

*Draft Methods section for the companion paper. Written from the HV_Harness
workflow as applied to the caspase gene family; the procedure is gene-set-
agnostic and is driven entirely by a per-gene-set configuration file.*

## Genomes and reference data

Analyses were performed on the publicly available NCBI RefSeq structural
annotations (genomic GFF3 and protein FASTA) of the three cyprinid Cs4R
allotetraploid carps: *Cyprinus carpio* (common carp, GCF_018340385.1),
*Carassius gibelio* (Prussian carp, GCF_023724105.1), and *Carassius
auratus* (goldfish, GCF_003368295.1). *Danio rerio* (zebrafish) was used
as the diploid outgroup that approximates the pre-hybridization ancestral
state at each locus; because zebrafish diverged from the carp lineage
before the Cs4R allopolyploidization, a zebrafish chromosome carries a
single ancestral copy of each locus rather than the paired A/B subgenome
copies present in the carps, and zebrafish chromosome numbers correspond
directly to the carp homeolog-pair numbers. Two further diploid cyprinids
(*Puntigrus tetrazona*, *Ctenopharyngodon idella*) are supported as
optional secondary comparators for cross-checking putatively
zebrafish-lineage-specific patterns but were not used here, as their
annotations were not included in the working dataset; the single-comparator
caveat (a zebrafish-specific pattern cannot be formally excluded) was
therefore retained as a standing hedge on loss claims.

All inferences are **annotation-level**: every claim is supportable from
the GFF and protein-FASTA inputs alone. No sequence-level analyses
(tBLASTn against unannotated regions, whole-genome alignment, phylogenetic
reconstruction) were performed; questions requiring such evidence were
logged to an explicit side-projects list rather than answered.

## Workflow and human–AI division of labour

The curation followed a structured human–AI collaboration protocol (the
"harness") in which an AI assistant executed all mechanical operations —
GFF parsing, sequence extraction, motif scanning, flanking-gene
retrieval, table and figure generation — while a human curator supplied
domain judgement at five explicit conversational checkpoints: (1)
search-term design, (2) inventory review and focal-species choice, (3)
the empty-slots/loss deep-dive, (4) whole-curation review, and (5)
interpretive-layer design. The AI was constrained to surface conflicts
and evidence rather than to make unsupported identity, loss, or
confidence calls on its own authority; relabelling, loss decisions, and
confidence assignments were confirmed by the curator. Each focal species
was curated independently and taken through to its own outputs rather
than merged into a single cross-species document, so that locus-level
states that differ in kind between genomes are preserved rather than
flattened.

## Gene-set identification

The gene set was defined in a version-controlled YAML configuration
(`config/<gene_set>.yaml`) specifying inclusion terms (regular
expressions matched against the gene `Name` field, plus case-insensitive
keyword substrings matched against the `description`/product field to
recover members carrying generic `LOC` identifiers) and exclusion terms
(named false positives and disqualifying description substrings). For
caspases, inclusion matched `casp` name patterns and the description
keyword "caspase"; exclusion removed CARD-domain proteins (e.g. CARD9),
caspase-associated/interacting/activated proteins, paracaspases, and
inhibitors. Candidate members were extracted per species from each GFF.
The candidate list was reviewed with the curator for false positives and
false negatives, and the configuration iterated until stable
(Checkpoint 1).

## Protein sequences and subgenome assignment

Protein sequences for the identified members were extracted directly from
the local per-species protein FASTAs and deduplicated. Subgenome (A/B)
assignment was read natively from the chromosome names for common carp
and Prussian carp, whose assemblies carry explicit A1–A25/B1–B25 labels.
For goldfish, whose chromosomes are numbered 1–50 without subgenome
labels, assignments were taken from a pre-computed lookup table generated
once by aligning the goldfish assembly to the labelled *C. gibelio*
assembly and assigning each goldfish chromosome to the subgenome of its
best-matching Prussian-carp chromosome (all 50 chromosomes assigned at
79–98% best-hit agreement; 25 to A, 25 to B). Members on unplaced
scaffolds, which cannot be assigned a subgenome by either route, were
flagged as such.

## Inventory and synteny substrate

A gene inventory was built with one row per member per species, recording
chromosome, subgenome, tentative homeolog-pair number (from chromosome
naming), coordinates, representative-isoform CDS exon count, transcript
count, and model-quality flags derived from NCBI's own signals
(`gene_biotype`, partial/exception flags, and the RefSeq `LOW QUALITY
PROTEIN` tag). The inventory was reviewed with the curator as the agreed
baseline and the focal species chosen (Checkpoint 2). Flanking-gene
neighbourhoods (12 genes per side; tandem members within 500 kb merged
into one block) were then extracted for every region occupied by a member
in every species to provide the synteny substrate.

## Per-pair curation

Each homeologous chromosome pair carrying members was curated against the
zebrafish reference locus. For each pair the procedure (i) established the
zebrafish reference gene(s) and their protein lengths; (ii) defined the
slot structure, where a *slot* is a syntenically bounded ancestral gene
position (single-gene, tandem-cluster, or excluded-artefact), explicitly
distinguished from a modern gene so that tandem clusters were treated as a
single slot; (iii) recorded per-gene evidence (protein length versus the
zebrafish orthologue, presence of the caspase catalytic pentapeptide
QAC**x**G detected by the regular expression `Q[A-Z]C[A-Z]G`,
representative-isoform exon count, model-quality flag); and (iv) compared
the A, B, and zebrafish flanking-gene orders.

Gene identity was assigned by the principle that **conserved syntenic
position overrides similarity-based NCBI naming**: where the A and B
copies share a flanking neighbourhood that matches the zebrafish locus,
both were treated as homeologs of the gene at that locus regardless of
divergent automated names, with the original NCBI annotation preserved in
every record. (The canonical example was the pair-7 B-homeolog, NCBI-named
"caspase a", relabelled casp23 by syntenic position in all three carps.)
In LOC-heavy regions, flanking genes were matched between homeologs and
between species on their `description` content rather than on gene
symbols, since the two subgenomes frequently annotate the same neighbour
under different identifiers. Within tandem clusters where 1:1 paralogue
pairing could not be settled by synteny, the slot was marked ambiguous,
its members grouped without forced pairing, and within-cluster identity
deferred to phylogeny; differing within-cluster paralogue counts between
subgenomes were described as asymmetric retention rather than as specific
losses.

Each functional gene's identity call carried a three-axis confidence
annotation — locus (is it at the expected syntenic position), identity
(is the specific paralogue identity resolvable), and model (is the gene
model structurally credible) — reported as a High/Medium/Low triple.
Pseudogenes and non-functional remnants were distinguished from functional
genes only on multiple lines of structural disruption (substantial
truncation relative to the orthologue, absent catalytic motif, reduced
exon count, minimal transcript support); copies judged likely
non-functional from annotation-level evidence but not formally annotated
as pseudogenes were recorded as candidate-non-functional and excluded from
functional counts. Assembly artefacts (e.g. subtelomeric near-identical
duplicates with anomalous transcript structure) were flagged and, where
multiple strong patterns coincided with species-uniqueness, excluded.

## Loss assessment

Empty homeolog slots were resolved in a single consolidated pass after
all pairs were drafted (Checkpoint 3). The strongest loss claim admitted
was **candidate loss with annotation-level evidence**, requiring that the
gene be present at the syntenic locus in zebrafish, present on the
homeologous chromosome in the same assembly, and absent from an in-region
annotation sweep of the empty chromosome's syntenic block. The sweep
examined every gene feature in the interval — not filtered by name — for
pseudogene biotypes, caspase-adjacent descriptions, and degraded or
absent protein models, and the syntenic block's quality on the empty
chromosome was graded (clear/partial/essentially absent). A negative
sweep over an intact block supported *candidate loss*; a pseudogene-
biotype or degraded model at the expected position instead yielded
*candidate non-functional locus*; a slot was left at the honest default
"absent — no specific search" only by explicit decision. Caspase-adjacent
features returned by a sweep (e.g. CARD-domain genes, cflar/CASP8–FADD-like
regulators, NLR-CARD genes) were verified against the retaining homeolog
to confirm they were distinct genes rather than mislabelled copies of the
missing member. "Confirmed loss" was never claimed, as it requires
out-of-scope sequence-level verification; tBLASTn confirmation of each
candidate loss was logged as a side project.

## Outputs and reproducibility

Each focal species yielded a hedged prose curation document, a structured
curation-data JSON encoding the slot structure, gene assignments,
confidence calls, loss states, and an interpretive functional grouping
(for caspases: executioner / initiator / inflammatory, designed with the
curator at Checkpoint 5), and a self-contained interactive HTML hierarchy
explorer rendered from that JSON. The explorer build validates every
status and loss value and refuses to render an empty slot lacking an
explicit loss decision, making the Checkpoint-3 requirement
correct-by-construction. Because the entire pipeline is driven by the
per-gene-set configuration file, the configuration together with this
procedure and the public RefSeq inputs is sufficient to reproduce the
analysis.
