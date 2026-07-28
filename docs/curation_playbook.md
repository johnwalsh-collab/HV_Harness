# Curation Playbook

A procedure for curating and visualizing a user-defined group of
genes at a time in the cyprinid Cs4R polyploid carp genomes —
common carp, Prussian carp, and goldfish — using publicly-available
annotations, with an AI assistant handling mechanical operations
and the human researcher providing curation judgment at specific
decision points.

---

## 0. About this playbook

### 0.1 What this is

The intended user is a biology-literate researcher who wants to
make sense of a gene group in the annotated carp polyploid genomes,
working with an AI assistant that handles the mechanical steps while
the researcher applies domain judgment. What they get: a
synthesized, hedged, navigable view of their gene group across all
three carp species, produced from publicly available annotations
without bioinformatic infrastructure.

This document describes a procedure. It is intended to be read by a
researcher who wants to apply the workflow to a group of genes they
care about, and to be referred to by an AI assistant who is helping
that researcher do the work.

The procedure operates on annotations — the GFF files and protein
FASTAs that NCBI (and similar databases) provide for the carp
polyploid reference genomes. It produces two outputs working
together: a *curation document* that captures the reasoning and
hedges what the annotations support, and an *interactive
visualization* that lets the result be navigated. Both come from
the same underlying analysis. Neither stands alone.

The procedure is described against a specific set of six genomes
(see section 2). It is not a general-purpose comparative genomics
pipeline. If you have a different polyploid system you want to
study, this playbook is a model for the *kind* of work you'd want
to do, but the specifics — which genomes, which comparator, what
counts as a syntenic block — would all need to be reset for that
system.

The user's group of genes is whatever they define. The worked case
that motivated the project is the caspase gene family, but the
procedure does not assume a formal gene family. A pathway, a
functional category, a custom list of genes the user has assembled
from their own work, or any other group identifiable in the
annotation can be the input. The depth of the procedure that
applies depends on how related the genes in the group are; this
is explained in section 1.2.

### 0.2 What you will produce

Two artefacts, designed to work together.

A **curation document** — markdown, one section per homeologous
chromosome pair that carries genes in the user's group. Each
section records the genes present, the evidence for their identity
(protein size, motifs where applicable, syntenic context), and the
curator's proposed call for each gene. Where the procedure cannot
settle an identity from the annotation alone, the curation document
says so explicitly and refers the question to a side-projects list.
The document is *hedged*: its strongest loss claim is "candidate
loss with annotation-level evidence," never "confirmed loss." Its
strongest identity claim is the syntenically-supported call, which
may override the NCBI gene name when the two conflict. The
reasoning behind every claim is in the document; a reader can
follow it back to the inputs.

An **interactive visualization** — a single self-contained HTML
file that renders the curation as a nested hierarchy: chromosome
map, the pairs that carry your genes, functional categories,
per-pair detail, zebrafish reference framework. The visualization preserves the
underlying NCBI identifiers in every cell so that nothing is lost
from the annotation, while letting the curator apply
domain-knowledge groupings (e.g. "executioner cluster" rather than
the inconsistent casp3/casp7 labels NCBI assigned) at the
display layer.

The two outputs are complementary. The curation document is where
the reasoning lives; the visualization is where the result becomes
shareable.

A worked example of both outputs already exists in the project, for
the caspase gene family in *Carassius gibelio* (Prussian carp). See
`examples/caspase_in_carp/` for pointers to the curation document
and the interactive explorer if you want to see what the
deliverables look like in practice.

### 0.3 Who this is for

The intended user is a biology-literate researcher — a student, a
postdoc, a faculty member, anyone with domain training but not
bioinformatic infrastructure — who wants to make sense of a group
of genes in the carp polyploid genomes. The user is comfortable
reading annotations and reasoning about gene biology, but does not
have the time or institutional resources to invest in a full
bioinformatic platform.

The user works alongside an AI assistant. The AI handles the
mechanical operations the curation procedure depends on: parsing
GFF files, extracting protein sequences, searching for motif
patterns, pulling out flanking-gene neighbourhoods, and producing
the formatted outputs. The user directs the work — defining what
their group of interest contains, judging which NCBI annotations to
override, deciding what functional grouping the visualization
should expose, and signing off on the final calls.

This division of labour is a deliberate design choice, not a
limitation. The AI is good at mechanical operations on structured
text; it is less reliable at domain judgement and worse at admitting
when it doesn't know something. The user is good at domain
judgement and good at refusing to over-claim, but slow at GFF
parsing. The procedure is built around playing to each side's
strengths.

The user is expected to be cautious about the AI's output. Sections
of this playbook (especially section 7) are written to help the
user catch the most common AI failure modes — fabricated evidence,
unsupported confidence, smoothed-over uncertainty. The user should
push back on the AI whenever a claim feels stronger than the
evidence supports. The procedure is built to support that
push-back; failure modes that survive the user's review are the
ones the playbook hasn't anticipated, and those should be added.

### 0.4 How to read this document

Read sections 1 to 4 once for orientation. They set the scope, the
inputs, and the principles that govern everything else. Most of
that content is conceptual rather than procedural.

Then loop through section 5 once per homeologous chromosome pair
that carries genes in your group. Section 5 is the operational
core; you will return to it repeatedly during the curation work.

Use section 6 once the per-pair curation is done, to build the
visualization. Section 7 is reference material for the AI
assistant; the user can skim it. Section 8 is the explicit list of
questions the procedure cannot answer, and what kinds of follow-up
work would answer them.

Section 9 invites updates to the playbook itself. The procedure
will be refined as it is used; the document should evolve.

A quick-start guide (`docs/quick_start.md`) is planned as a shorter
entry point for users who want to begin a first curation quickly.
It does not yet exist; this playbook is the full reference.

---

## 0.5 Terminology used in this playbook

The gene relationships in allopolyploid genomes involve several overlapping concepts that different sources use inconsistently. This section establishes the terms used in this playbook and explains the reasoning behind them.

**Allopolyploidization event.** The founding event for the three target species — a hybridization between two diploid ancestral species, followed by genome doubling that restored functional diploidy. This is the event that created the A and B subgenomes. The term *whole-genome duplication* (WGD) is avoided here because it implies a single genome duplicating itself (autopolyploidy), which is not what happened. The allopolyploidization was a two-step process: hybridization first, then chromosome doubling. Calling it WGD collapses that history and misrepresents the relationship between the subgenomes.

**Subgenome.** The A and B subgenomes each descend from one of the two diploid parental species. Within each subgenome, the genome is organized diploid-style: there are two copies of every A chromosome (e.g. two copies of A22) and two copies of every B chromosome (e.g. two copies of B22). The A and B subgenomes are distinct in origin and in sequence; they are not simply duplicates of each other.

**Homeologous chromosomes / homeologs.** A and B chromosomes derived from the same ancestral chromosome in the two parental species are *homeologous*. A22 and B22 are homeologous chromosomes. A gene on A22 and the corresponding gene on B22 are *homeologs*. This is the central relationship this tool is designed to visualize. The term *homologous* is avoided in this context because it is ambiguous: in a functional diploid, every chromosome has a genuine homolog (the two copies of A22 are homologs in the meiotic sense), and the word would create confusion between the within-subgenome and between-subgenome relationships.

**Pre- and post-hybridization divergence.** Any two homeologs have a two-phase history. Before the hybridization event, their ancestors existed in separate parental species and accumulated independent sequence changes — potentially for millions of years. After hybridization, both copies have been evolving together within the allopolyploid lineage. This means homeologs are not equivalent to the products of a simple within-genome duplication: they may carry substantial pre-existing divergence that has nothing to do with the allopolyploid event itself. This history is one reason NCBI's automated annotation sometimes assigns different names to two homeologs at the same locus — the sequence divergence may be real, but it reflects pre-hybridization evolution rather than a genuine difference in gene identity or function. Syntenic position is the primary evidence for homeolog identity precisely because it is robust to this pre-existing sequence divergence.

**Paralog.** Genes related by duplication *within* a subgenome. Paralogs share a common ancestral gene but diverged through duplication rather than through the allopolyploidization event. Homeologs are technically paralogs in the broadest sense, but this playbook reserves *paralog* for within-subgenome duplicates and uses *homeolog* for the A/B between-subgenome relationship.

**Ohnolog.** The term *ohnolog* (named after Susumu Ohno) refers to gene copies retained from a polyploidization event. It appears in the literature for both auto- and allopolyploid contexts. This playbook uses *homeolog* in preference to *ohnolog* because it is more specific to the relationship being described and does not carry the autopolyploidy connotations that *ohnolog* sometimes implies.

---

## 1. About the project

### 1.1 The problem this addresses

NCBI and Ensembl have done enormous work over the past decade
producing reference genomes for many polyploid species, including
the cyprinid carps that this playbook targets. Each genome arrives
with a structural annotation: tens of thousands of gene models,
each with a name, a description, coordinates, exon structure, and
sometimes expression evidence. This is publicly available data of
high quality, freely accessible to anyone who knows where to look.

In practice, that data is hard to use. The NCBI Genome Data Viewer
takes the user directly to gene-level detail — a single gene at a
time, in a chromosomal context, with neighbouring genes visible.
What it does not provide is a synthesizing layer: a way to look at
a *group* of genes (a family, a pathway, a custom list) all at
once across the polyploid genomes, with the homeolog relationships
made visible and the inconsistencies in the annotation flagged
rather than hidden.

Other platforms — Galaxy is the most prominent example — provide
the synthesis capabilities, but they assume a bioinformatic mode of
work. The user needs to learn the platform, understand the data
formats, configure the pipelines, debug the errors. For a
researcher whose strength is domain biology rather than
bioinformatics, the time cost of becoming competent in those
platforms can be higher than the value the analysis returns.

A biology-literate user with strong domain expertise but without
the time or resources to invest in platform-specific tooling has,
until recently, had no in-between option. They can use the NCBI
Viewer, gene by gene, and try to hold the synthesis in their head.
They can ask a bioinformatic collaborator to run the analysis,
which works when such a collaborator is available and reachable.
Or they can shelve the question.

This playbook describes an in-between option that has become
possible with AI assistance: an interactive workflow where the user
applies their domain expertise at specific decision points while
the AI handles the mechanical operations. The AI is the platform.
The user is the curator. Together they produce a synthesized view
of the gene group across the carp polyploid genomes — hedged to
what the annotations support, but coherent, navigable, and
defensible. This workflow sits alongside the Viewer and Galaxy
rather than replacing them: it uses the same public data the Viewer
exposes and produces well-bounded questions that platform-scale
tools are well suited to follow up.

### 1.2 The approach

The procedure has three structural features that distinguish it
from both the Viewer-only approach and the conventional
bioinformatic-platform approach.

**Annotation-level evidence only.** The procedure works on what
the annotation says — gene names, descriptions, coordinates, exon
structure, protein sequences, syntenic neighbourhoods. It does not
run sequence-level analyses (tBLASTn against unannotated genomic
regions, whole-genome alignments, novel gene prediction). It does
not attempt formal phylogenetic reconstruction. The scope is
deliberately confined to what the inputs can support. Stronger
claims that would require sequence-level work are explicitly
flagged for follow-up as side projects but are not made by the
procedure itself.

**A division of labour between the AI assistant and the human
curator.** The AI does the mechanical operations: parsing GFFs,
extracting protein sequences, searching for motif patterns, pulling
flanking gene neighbourhoods, producing draft text, generating the
visualization. The human directs the work and applies judgement at
four explicit conversation points (sections 3.4, 5.1, 6.1, 6.2)
where the procedure pauses for the curator to make choices. The
curator decides what the group contains, which NCBI calls to
override, how to interpret ambiguous evidence, and what functional
grouping the visualization should expose.

**Two-layer output.** The procedure produces both a curation
document (the reasoning layer, hedged appropriately) and an
interactive visualization (the navigation layer, with the curator's
domain groupings overlaid). Neither stands alone. The curation
document without the visualization is dense prose that's hard to
scan. The visualization without the curation document is a pretty
picture without a defensible basis. Together they are the actual
deliverable.

The depth of the per-pair procedure that applies depends on how
related the genes in the user's group are to each other. When the
group is a formal gene family — paralogues with shared domains and
motifs — the full procedure applies, including synteny-based
homeolog confirmation, motif-level identity checks, candidate-loss
analysis with reference to the zebrafish comparator, and
slot-based representation of tandem clusters. When the group is a
more arbitrary set whose members aren't expected to be paralogues
of each other, the chromosome-pair organization and visualization
still apply, but the homeolog-pairing logic only engages between
genes within the group that are themselves related (which the
user can specify). Checkpoint 1 (section 3.4) is where the depth
of procedure is settled.

### 1.3 What this is not

A list of things the procedure does not do is part of the contract
with the user, and worth being explicit about.

It does not run sequence-level analyses. tBLASTn against
unannotated genomic regions, whole-genome alignments,
deletion-mechanism analysis at the breakpoint, and similar
sequence-level work are out of scope. When the curation reaches a
question that requires sequence-level evidence (e.g. "is this
candidate loss a real evolutionary loss or just an annotation
gap?"), the procedure logs the question and moves on.

It does not run formal phylogenetic reconstruction. The procedure
uses zebrafish as a comparator (section 2.2) to approximate the
ancestral state at any given locus. This is a pragmatic shortcut,
not a tree. Where phylogenetic resolution is needed — for example
to distinguish within-cluster homeolog identity in a tandem
duplication — the question is flagged for follow-up.

It does not produce a comprehensive characterization of the user's
gene group. It produces a curation of what the annotations support,
with explicit hedging where they don't. A comprehensive
characterization would draw on expression data, functional studies,
protein structure prediction, and many other lines of evidence
that the annotation alone does not provide. The curation is a
foundation that more substantial work could be built on, not the
substantial work itself.

It does not generalize to other polyploid systems. The procedure
is described against the specific carp genomes named in section 2.
If you want a similar analysis for wheat, cotton, *Xenopus*, or any
other polyploid system, the methodology is a useful model — the
principles transfer — but the specifics need to be reset for the
new system. That would be a separate project; this playbook does
not attempt to be it.

What is in scope is captured in sections 2 through 9 below.

---

## 2. The genomes this tool works with

This section names the specific genomes the playbook is built
around. The tool is tested against these and only these. Any
application to a different genome system would be a separate
project.

### 2.1 The target genomes

The workflow is designed for the three cyprinid Cs4R allotetraploid
carp species: common carp, Prussian carp, and goldfish. All three
have chromosome-level reference assemblies in NCBI RefSeq. The
assemblies used for the caspase worked example are listed below as
a starting point; newer or higher-quality assemblies should be
substituted as they become available.

| Species | Common name | Worked-example assembly | Subgenome labels |
|---|---|---|---|
| *Cyprinus carpio* | Common carp | GCF_018340385.1 | Explicit A1–A25 / B1–B25 in chromosome names |
| *Carassius gibelio* | Prussian carp | GCF_023724105.1 | Explicit A1–A25 / B1–B25 in chromosome names |
| *Carassius auratus* | Goldfish | GCF_003368295.1 | Chromosomes numbered 1–50; subgenomes derived from one-time alignment to *C. gibelio* (see below) |

These three species share the Cs4R allotetraploidization event,
which occurred in the common ancestor of the cyprinid carps roughly
12 million years ago. Each species carries two retained subgenome
copies of every ancestral chromosome, labelled A and B by
convention. Genes that derive from the same pre-hybridization
ancestral gene are called homeologs; the chromosomes that carry
them are called homeologous chromosomes.

For common carp and Prussian carp, the subgenome assignment is
already in the assembly: chromosome names carry the A or B prefix
and the homeolog pair number directly (A1 pairs with B1, A23 with
B23, and so on). No additional work is needed to determine which
chromosome is which.

For goldfish, the chromosomes in the worked-example assembly are
numbered 1 through 50 without subgenome labels. The assignment is
recovered by aligning the goldfish assembly against the Prussian
carp assembly using NCBI's Datasets service: for each goldfish
chromosome, the best-aligned Prussian carp chromosome determines
its subgenome assignment. This is a one-time mechanical step, done
once to produce the lookup table that ships with the repository at
`config/goldfish_subgenome_lookup.tsv` and is re-used for every
curation; you do not need to repeat it for goldfish. All 50 goldfish chromosomes were
assigned with high confidence (79–98% best-hit agreement); 25 to
subgenome A, 25 to subgenome B. If a future goldfish assembly
carries native A/B subgenome labels in its chromosome names, this
alignment step is unnecessary and the assembly can be used directly.

**Choosing an anchor genome.** One species serves as the anchor —
the primary reference against which the other two are compared.
The anchor should be chosen based on assembly quality, not fixed
by convention. The criteria to apply are: highest contig N50
(better contiguity means more reliable syntenic neighbourhoods),
highest BUSCO completeness score, most recent assembly technology,
and — most importantly — explicit A/B subgenome labels in the
chromosome names. An assembly that requires a derived subgenome
lookup table is a weaker anchor than one where the labels are
native. For the caspase worked example, *C. gibelio*
(GCF_023724105.1; contig N50 5.1 Mb, BUSCO 99.5%, PacBio HiFi
2022, explicit A/B labels) was the strongest candidate by all
criteria and was chosen as anchor. A user working with updated
assemblies should re-apply these criteria and choose accordingly.
When the procedure refers to "the anchor," it means whichever
species the user has designated. Curation of the other two species
is done as comparison against the anchor, not from scratch.

### 2.2 The diploid comparator

Zebrafish (*Danio rerio*, NCBI RefSeq GCF_049306965.1, GRCz12tu) is the
primary comparator that the procedure uses to approximate the
pre-hybridization ancestral state at any given locus.

Zebrafish is chosen for four reasons:

It is a cyprinid, sharing a recent common ancestor with the carp
target species. The divergence between zebrafish and the carp
lineage predates the Cs4R event, so zebrafish does not carry the
subgenome structure that the procedure is designed to navigate. For
any given ancestral locus, a zebrafish chromosome carries one copy
— not two copies on paired subgenomes derived from different
parental species. Zebrafish thus approximates "what the locus
looked like before the hybridization event," without the A/B
pairing complexity. Note that zebrafish does have duplicated genes
and tandem clusters at some loci; the difference is that those
duplications have a within-genome history, not a
between-subgenome one.

It is well-characterized. Zebrafish has been a model organism for
decades; its annotation is more thoroughly curated than the carp
annotations, with proportionally more genes carrying proper names
rather than LOC identifiers, and proportionally more functional
characterization. When the procedure needs a flanking-gene
neighbourhood to anchor a syntenic block, zebrafish is the most
reliable source.

It has the same chromosome architecture. Zebrafish has 25
chromosomes; the carp targets have 25 ancestral chromosomes (each
present in A and B copies). Homeolog pair numbers in the carp
targets correspond to zebrafish chromosome numbers — pair 7 in
common carp corresponds to zebrafish chromosome 7, and so on. This
makes syntenic comparison straightforward.

The Cs4R event has been studied extensively in the carp lineage
using zebrafish as the comparison. Treating zebrafish as a proxy
for the ancestral state is the convention in the field.

Using zebrafish as comparator is a *pragmatic shortcut*. It is not
formal phylogenetic reconstruction. The assumption is that
zebrafish's gene complement at a locus approximates the pre-hybridization
state. This assumption is correct most of the time but can fail in
specific cases where zebrafish has undergone lineage-specific
change at the locus (loss, duplication, relocation). Section 4.2
and the conversation at Checkpoint 2 (section 5.1) are where the
curator decides whether to trust the zebrafish state at a
particular locus or cross-check it.

Zebrafish is a comparator that approximates the ancestral state,
never an ancestor of the carp genes; section 4.2 states what this
comparison does and does not claim.

### 2.3 Secondary diploid cyprinids for cross-check

Two additional diploid cyprinids are available for cross-checking
the zebrafish state at any specific locus where there is reason to
suspect a zebrafish-specific feature.

| Species | Common name | NCBI assembly | Role |
|---|---|---|---|
| *Puntigrus tetrazona* | Tiger barb | GCF_018831695.1 | Secondary cyprinid diploid; consulted at the curator's discretion |
| *Ctenopharyngodon idella* | Grass carp | GCF_019924925.1 | Secondary cyprinid diploid; consulted at the curator's discretion |

These two species are *not used by default*. The procedure does
not extract their syntenic context for every pair. They are
consulted only when a specific locus shows reason to suspect that
the zebrafish state is lineage-specific rather than ancestral
(e.g. zebrafish has a tandem cluster of paralogues at a locus
where the carp targets have only one paralogue per subgenome, or
zebrafish carries a gene that no other examined species has at
the equivalent locus). The procedure for invoking the cross-check
is in section 4.2.

### 2.4 What is not in scope

The primary design target of this tool is the three Cs4R cyprinid
allotetraploids, using zebrafish and optionally other diploid
cyprinids as comparators. The following are outside that scope:

- Other polyploid systems (wheat, cotton, *Xenopus laevis*,
  salmonids, *Capsella*, *Brassica*, and other allopolyploid or
  paleopolyploid systems). These systems share the general
  challenge but have different chromosome structures, annotation
  conventions, and subgenome histories. A related project on one
  of these systems would use this playbook as a methodological
  model, not apply the procedure as written.
- Autopolyploid systems without clear subgenome separation.
- Scaffold-only carp assemblies. The chromosome-pair organization
  the procedure depends on requires chromosome-level scaffolding.
- Carp assemblies from databases other than NCBI RefSeq. The
  procedure has been built and tested against RefSeq GFF
  conventions; Ensembl, Phytozome, or custom annotation formats
  would need adapting.

The choice of diploid comparator is not restricted. Zebrafish is
the default and the best-characterized option, but additional
diploid cyprinids (grass carp, tiger barb, or others) can be used
for cross-checking where informative.

Keeping the carp scope tight is what makes the procedure concrete
and the worked outcomes verifiable. The trade-off — that the tool
is not a general polyploid genome browser — is intentional.

---

## 3. Setting up

This section describes what needs to exist before the per-pair
curation procedure (section 5) can begin. Two things are covered.
First, an inventory of the inputs the procedure consumes — the
files the AI assistant will reach for at each step (section 3.1).
Second, the mechanical pipeline that produces those inputs from the
public GFFs (sections 3.2 and 3.3). The section closes with the
first conversational checkpoint (section 3.4), in which the user
and the AI assistant agree what the group of genes consists of and
how the GFFs will be searched to find its members.

The premise is that the AI assistant runs the mechanical pipeline
under the curator's direction. Each script accepts a
`--config config/<gene_set>.yaml` argument that names the gene
set, the inclusion and exclusion terms, the borderline cases, and
the visualization parameters. Once that config is in place, the
mechanical stages run end-to-end and produce the inputs section
3.1 lists.

### 3.1 Inputs you need

Seven inputs feed the per-pair curation procedure. All seven come
out of the mechanical pipeline described in section 3.2; for the
worked caspase case the sources, download dates, and assembly
versions are recorded in `docs/data_provenance.md`.

| Input | What it is | Standard location |
|---|---|---|
| Per-species GFF annotations | RefSeq GFF for each target species and the diploid comparator | `data/annotations/<species>/*.gff.gz` |
| Per-species protein FASTAs | All annotated proteins for the user's group, deduplicated | `data/sequences/<gene_set>_proteins_<species>_dedup.fasta` |
| Gene-level inventory | One row per group member across all species, with chromosome, subgenome, homeolog pair number, expected vs annotated identity, and gene-model quality flags. No separate homeolog-pair summary table is produced — the inventory's `homeolog_pair`/`subgenome` columns are the cross-species pair record. | `results/<gene_set>/identification/<gene_set>_gene_inventory.tsv` |
| Synteny extracts | Flanking-gene neighbourhoods (~12 genes each side, configurable) for every region the group occupies, per species | `results/<gene_set>/identification/<gene_set>_synteny_extraction_all_pairs.txt` |
| Subgenome assignment table | For every chromosome in every allopolyploid species, which subgenome it belongs to — derived from chromosome names where labels exist (common carp, Prussian carp) and from an assembly-to-assembly alignment for goldfish | `config/goldfish_subgenome_lookup.tsv` (ships pre-built; goldfish only — the other two species need no lookup) |
| Outgroup reference list | A short list of the group members in zebrafish — gene names, chromosome locations, protein lengths — used as the ancestral-state reference framework for every pair | a small TSV or list at the top of the curation document |

The synteny extract is the one input whose form depends on the
species being curated. Stage 3d's `extract_synteny.py` produces the
extracts for the anchor genome by default. For non-anchor species,
the same script can be re-run with the species and gene set
specified in the config, or — for a single locus during the
per-pair work — flanking genes can be pulled on the fly from the
GFF using the minimal procedure in section 3.3.

Any prior partial curation, prior gene-tree analysis, or notes from
the curator's own work on the gene group can also be brought in
alongside.

**Starting from a pre-defined gene list.** If you already have a
defined list of gene IDs from the annotation — for example, a small
set of specific genes you want to visualize in their homeologous
context — you can skip the GFF search step (Stage 2) and assemble
the gene inventory directly from those IDs. The synteny extraction,
homeolog pair summary, curation, and visualization steps all still
apply. Checkpoint 1 in this case becomes a shorter conversation
about which pipeline steps are needed rather than a full
search-term design session. This is a lighter entry point suited
to users who are using the tool for organization and visualization
rather than for discovery across the annotation.

### 3.2 The mechanical pipeline

The mechanical pipeline runs in three stages before the curation
starts, plus one conditional procedure for goldfish. Each stage is
a script in `scripts/` driven by the gene-set config. The full
stage table — including which script produces what, where the
outputs land, and how to re-run on a different gene set or a new
species — is in `docs/workflow.md`. The summary here is enough to
orient the curator without duplicating that table.

**Stage 1 — Acquire annotations.** Per-species RefSeq GFFs are
downloaded into `data/annotations/<species>/`. The species list is
fixed (section 2); the script does not need to be re-run for a new
gene set.

**Stage 2 — Identify gene-set members.** The config file's
inclusion and exclusion terms are applied against each species'
GFF. The output is a candidate gene list per species with
chromosome and coordinate information, and the corresponding
protein FASTAs are pulled from NCBI. This stage cannot run until
the Checkpoint 1 conversation (section 3.4) has produced a config.

**Stage 3 — Build the curation substrate.** Three sub-stages.
3a (conditional) runs the goldfish subgenome lookup if it does not
already exist; this is a one-time step shared across all gene
sets. 3b assembles the cross-species homeolog summary from the
gene list and the subgenome assignments. 3c produces the
gene-level inventory with quality flags. 3d extracts flanking-gene
neighbourhoods for every region the group occupies. After Stage 3
runs to completion, the seven inputs listed in section 3.1 exist
and the per-pair procedure (section 5) can begin.

Stages 3e (the per-pair curation) and 5 (hierarchy explorer) come
after the per-pair work and are described in their own sections
(5, and 6, of this playbook).

A first-time run on a new gene set produces all of the above by
running the four scripts named in `docs/workflow.md`'s "Minimum
viable re-run sequence" with the gene set's config passed at the
command line. If the curation is being resumed on a gene set
already processed, the inputs in section 3.1 should already exist
and Stage 3 does not need to be re-run.

### 3.3 GFF-based flanking-gene extraction (fallback procedure)

The Stage 3d synteny extracts produced by `extract_synteny.py`
cover every region the gene set occupies in every species, with the
flanking-gene window set by the config. In normal use that output
is the synteny substrate for the per-pair work, and no further
extraction is needed during curation.

The fallback case is when a single locus needs a quick flanking-
gene check during a per-pair conversation — for example, when the
curator wants to look ~50 kb further out than the configured
window, or when a candidate-loss assessment needs the empty
chromosome's syntenic block checked even though it carries no
group member. In those cases, flanking genes can be pulled on the
fly from the GFF.

A minimal procedure:

1. From the gene inventory (or the curator's question), get the
   chromosome accession and the coordinate range of interest.
2. Read the GFF for that species (gzipped is fine) and select all
   `gene` features on that chromosome within the desired window
   on each side of the focal coordinate range.
3. Record start, end, strand, gene name (`Name=` attribute,
   falling back to `ID=` if absent), and `gene_biotype`.
4. Hand the result to the curator as a small text block or TSV
   that section 5.3's per-pair procedure can consume.

A reference implementation (15–20 lines of Python using `gzip` and
`csv`) was used during the common-carp pilot and can be reused as
needed.

**Watch out for** the `Name=` attribute being a LOC identifier
rather than a meaningful gene name. This is common in the carp
annotations and most noticeable in the common carp's annotation,
which is more heavily LOC-based than the Prussian carp's. Section
5.4.2 covers how to handle LOC-heavy regions during the in-region
search and syntenic-block-quality assessment.

### 3.4 Checkpoint 1 — defining your group and directing the GFF search

This is the first of five conversational checkpoints in the
procedure. The five checkpoints (sections 3.4, 5.1, 6.1, 6.2, 6.3)
are where the procedure deliberately pauses for dialogue between the
curator and the AI assistant. They are not documentation steps or
self-audits; they are the moments where the curator's domain
expertise enters the work and where the AI's mechanical results
get interpreted into something coherent. Skipping a checkpoint —
or paying lip service to one without resolving the substantive
questions inside it — is a documented failure mode of the
procedure (section 7.2).

**When this checkpoint happens.** Before Stage 2 runs. The
output of the conversation is the gene-set config file
(`config/<gene_set>.yaml`, copied from `config/template.yaml`)
that Stage 2 and everything downstream depend on.

**What needs to be settled.** Two things, in this order: what the
group of genes is, and how the GFF search will be told to find
them.

The group of genes is whatever the user defines. The worked case
of the project is the caspase gene family — a formal family of
paralogues with shared domains and a defining catalytic motif —
but the procedure does not assume a formal family. Three broad
shapes that come up in practice:

- A *formal gene family*. Paralogues with shared protein domains,
  shared sequence motifs, and a common ancestor visible at the
  domain level. The caspases are this shape. Synteny-based homeolog
  confirmation, motif-level identity checks, candidate-loss
  analysis against a zebrafish reference — all of these apply to
  every member of the group.
- A *functional category*. Genes that act in a common pathway or
  share a regulatory role, but are not necessarily related to each
  other at the sequence level. Members of a signalling pathway, an
  enzyme cascade, or a receptor–ligand pair fit this shape. The
  chromosome-pair organization still applies to every member, and
  the visualization works for any group. But the synteny-based
  homeolog procedure only engages *between* genes within the group
  that are themselves paralogues.
- A *custom list*. Genes the user has assembled from their own work
  or from the literature — for example, the genes called out in a
  particular review paper, or the genes that responded in one of
  the curator's own experiments. The list does not need a unifying
  biological justification beyond the curator's reasons for caring
  about these genes together. Treatment is as for the functional
  category: chromosome organization and visualization apply
  universally; synteny-based homeolog work applies between members
  that are themselves related.

Settling which shape the group has determines the depth of the
per-pair procedure that applies. The conversation should produce
an explicit statement to that effect, recorded in the config file
or in the curation document's opening.

Once the group is defined, the GFF search needs directing. NCBI's
gene names and descriptions are *clues* about gene identity, not
perfect identifiers, and a search that takes them at face value
will miss real members and pick up unrelated genes. Three classes
of issue to anticipate:

- **False positives.** Names or descriptions that contain a
  keyword from the group's vocabulary but refer to genes that are
  not in the group. The canonical caspase example is `CARD9`,
  whose RefSeq description contains "caspase" (because of its CARD
  domain) but which is not itself a caspase. The conversation should
  list known false positives and add them to the config's exclusion
  terms.
- **False negatives.** Members of the group that do not carry the
  expected keyword in their name or description. Common reasons:
  the gene has been assigned a `LOC<number>` identifier by NCBI's
  automated annotation pipeline (Gnomon) with a generic description
  that does not mention the family; the family has subfamilies that
  use different naming conventions; the gene is annotated under a
  historical alternative name. A false negative can give the
  misleading impression that a homeolog is a singleton when in fact
  both homeologs are present and only one is named informatively.
- **Borderline cases.** Genes that are family-adjacent but whose
  inclusion is a judgement call. For caspases the canonical example
  is `cflar` (c-FLIP), which carries caspase-like domains but no
  catalytic activity. The decision can go either way; the
  conversation should make the call explicit and, if the borderline
  case is included, flag it as borderline in the config so
  downstream curation handles it visibly.

**The two-pass iteration.** The conversation does not happen once
and finish. It runs in two passes. Before any GFF search is
attempted, the curator and the AI brainstorm inclusion terms
(names, description keywords, regex patterns) and exclusion terms
(known false positives, disqualifying substrings) based on what
the curator knows about the family and what the AI can pull from
the literature. A first config is written and Stage 2 runs against
it, producing a candidate gene list. The conversation then
*resumes*: the candidate list is reviewed together, false
positives caught and added to the exclusion list, false negatives
caught and the inclusion list broadened, borderline cases settled.
The config is updated and Stage 2 re-runs. This iterates until the
candidate list is stable and the curator signs off.

Either pass can surface enough information to change the group
definition itself — a false negative may reveal a subfamily the
curator did not know about; a borderline case may force the
curator to commit to one shape of group over another. The
procedure expects this.

**Output of this checkpoint.** A `config/<gene_set>.yaml` file
that contains, at minimum: the gene set's short name, the
inclusion terms (names and description keywords), the exclusion
terms (false positives and disqualifying substrings), the
borderline-case list, and the curator's statement of which shape
the group has (formal family / functional category / custom list).
The config is the persistent record of the Checkpoint 1
conversation and is the input to every mechanical stage that
follows. It is also the artefact that allows another curator (or
the same curator at a later date) to reproduce the analysis: the
config plus the playbook plus the public GFFs is sufficient.

**Why this checkpoint matters.** The inventory that Stages 2 and 3
produce is the substrate every downstream step in the procedure
works on. An overly narrow search loses real members silently and
the curator will not know they are missing until — possibly —
much later, if ever. An overly broad search dilutes the analysis
with unrelated genes whose presence makes the visualization
harder to read and the per-pair conversations harder to focus.
Neither failure is recoverable without re-doing the inventory
from scratch. The cost of slowing down for this checkpoint is one
or two conversations; the cost of skipping it can be every
downstream output being subtly wrong.

**AI initiation.** The AI assistant is expected to initiate this
conversation if the human does not. A request like "please
identify the caspase genes" or "run the pipeline on the TLR
family" should be met with the AI proposing the checkpoint
conversation, not with the AI running Stage 2 against
best-guess defaults. Section 7.2 names this initiation
expectation explicitly, alongside the analogous expectation at the
three later checkpoints.

With the group defined and the config in place, the per-pair
procedure (section 5) can begin. Section 4 first sets out the
governing principles — annotation-level evidence, synteny over
similarity-based naming, the role of the zebrafish comparator —
that the per-pair procedure applies.

---

## 4. Governing principles

Five principles govern the per-pair procedure. The first two are
about how to read the annotation: where to trust it, and where
its labels should be set aside in favour of syntenic position
(section 4.1), and how to decide whether the zebrafish state at a
locus can be treated as ancestral or needs cross-checking against
the secondary diploid cyprinids (section 4.2). The third names
the standard of evidence the procedure commits to and what
stronger claims are out of scope (section 4.3). The fourth is the
orienting principle for both the curation document and the
visualization — clarity without over-claim (section 4.4). The
fifth describes the division of labour between the curator and
the AI assistant that the procedure is built around (section 4.5).

These principles are not procedure. The procedure that applies
them is section 5; the visualization principles play out in
section 6. The reason for stating the principles separately is
that they get cited throughout the procedure — most decision
rules trace back to one of these five — and a curator looking
back at a per-pair section that hedged or relabelled or deferred
should be able to find the principle that justified it.

### 4.1 Synteny over similarity-based naming

In a recently allopolyploidized genome, the two homeologs at any
given locus trace back to the same ancestral gene in two different
parental species. Before the hybridization event they diverged
independently in their respective lineages; after hybridization
they found themselves in the same genome. Each homeolog is
therefore more closely related to its counterpart than either is
to any single outgroup gene — not because they were duplicated
within one genome, but because they share a common
pre-hybridization ancestor that the outgroup also shares, and the
hybridization event brought both lineages together. The expected
gene-tree topology for any retained homeolog pair is:

```
((A_homeolog, B_homeolog), outgroup_ortholog)
```

Automated annotation pipelines do not see this topology. They
assign gene names by sequence similarity to a reference set, one
gene at a time. When the A copy and the B copy at the same
ancestral locus end up with *different* names — for example, A
labelled `casp23` and B labelled `caspa` — the pipeline is
implicitly asserting `((A, outgroup1), (B, outgroup2))`: that A
and B are not each other's nearest relatives, that they pair more
closely with two different outgroup genes than with each other.
That topology is biologically very unlikely after a recent allopolyploidization event.
What it usually means is that A and B diverged enough after the
duplication that the automated pipeline now assigns them to
different reference templates — but they remain homeologs of one
ancestral gene.

The default rule for this procedure is therefore: **in the
absence of stronger evidence, conserved syntenic position
overrides automated similarity-based gene names.** Two genes
sitting in the same flanking-gene neighbourhood on the A and B
chromosomes of the same homeologous pair should be treated as
homeologs of one ancestral locus, even when NCBI has labelled them
as different genes. The relabelling rule that operationalises
this is in section 5.4; here the principle is what matters.

The rule is *default*, not *absolute*. Several specific situations
can make synteny mislead, and the curator should hold the rule
loosely enough to recognise them:

- *Local tandem duplication and differential loss within a
  cluster.* When the ancestral locus carried a tandem cluster of
  paralogues, A and B may have retained different cluster members.
  Synteny on the cluster's flanking genes confirms the locus, but
  does not specify which paralogue identity each retained copy
  carries. Pair 10 in the caspase worked example (the casp3 /
  casp7 / casp17 cluster) is this case.
- *Gene conversion.* Two paralogues at the same locus can
  homogenise their sequences via gene conversion, masking the
  ancestral divergence that the names were tracking.
- *Chromosomal rearrangement.* A syntenic block can be broken or
  rearranged so that a gene ends up at a different position with
  different flanking neighbours. The syntenic-position-loss
  sub-case in the candidate-loss procedure (section 5.4) handles
  this explicitly.
- *Assembly collapse.* A genuine duplicate can be collapsed into a
  single representation in the assembly, making A and B look
  artificially identical or making one homeolog appear absent.
- *Derived outgroup state.* The diploid outgroup itself can have
  lineage-specific loss, duplication, or relocation at the locus.
  When that happens, the inferred ancestral slot structure is
  wrong and the synteny rule rests on bad foundations. Section 4.2
  covers the cross-check.

The default rule does most of the work. The exception cases are
why each per-pair section in the curation document carries an
explicit synteny argument rather than just a relabelling decision:
the argument is what lets a later reader see whether the rule
applied cleanly or whether an exception was active.

### 4.2 Zebrafish first, with secondary cross-checks when needed

Section 4.1's synteny rule rests on the diploid outgroup providing
a faithful view of the ancestral state. The procedure's default
outgroup is zebrafish (section 2.2). For most loci this default
works: zebrafish is a cyprinid that diverged from the carp lineage
before the Cs4R event, its annotation is well-curated, and its
chromosome architecture maps directly onto the carp homeolog pair
numbers.

But the zebrafish lineage has had ~150 million years of its own
evolution since diverging from the carp lineage. Lineage-specific
gain, loss, or relocation of individual genes is exactly the kind
of event that lurks in any single-comparator design. If zebrafish
has lost a gene at a locus where the ancestor carried it, the
inferred ancestral slot structure is missing that gene — and the
absence of a corresponding gene in the carp targets reads as
"absent in all examined species" rather than as "lost in the
zebrafish lineage but present elsewhere."

Other diploid cyprinids can serve as secondary comparators to
cross-check the zebrafish state at any locus where there is reason
to suspect a zebrafish-specific feature. Tiger barb
(*Puntigrus tetrazona*) and grass carp (*Ctenopharyngodon idella*)
are used in the caspase worked example for this purpose, but any
well-annotated diploid cyprinid the user has access to is
appropriate. Secondary comparators are not used by default —
extracting their syntenic context at every locus would be expensive
and unnecessary — but they are consulted when a specific locus
triggers concern.

The procedure: when in doubt about whether the zebrafish state at
a locus is ancestral, check whether tiger barb and grass carp
agree with it. If both secondaries carry the same feature
zebrafish does, the feature is more likely ancestral and the
zebrafish-based slot structure stands. If neither secondary
carries it, the feature is more likely zebrafish-specific and the
ancestral slot structure should be inferred from the secondaries
instead. If one agrees and one disagrees, the ancestral state is
genuinely uncertain at that locus and the curation document
should hedge.

Triggers for invoking the cross-check include: zebrafish has a
tandem cluster of paralogues at a locus where the carp targets
each have a single homeolog per subgenome; zebrafish carries a
gene that no carp target carries at the equivalent locus; the
slot structure derived from zebrafish predicts losses in the carp
targets that are widespread (e.g. on both subgenomes of multiple
species). The Checkpoint 2 conversation (section 5.1) is the
natural place for the curator to flag such cases when reviewing
the gene list, before per-pair curation begins.

**A note on direction.** Zebrafish is a comparator that
*approximates* the pre-hybridization state at a locus; it is not an
ancestor of the carp genes, and the carp homeologs do not descend
from the zebrafish paralogues. Whether a carp cluster and a
zebrafish cluster are related by a particular gene-tree topology —
which carp copy is closest to which zebrafish paralogue — is a
phylogenetic question this curation does not address and must not
assert. The zebrafish locus supplies the syntenic *reference
framework* (which slots to expect, and where); it does not supply a
line of descent.

### 4.3 Standard of evidence — annotation-level only

The procedure makes annotation-level claims. It does not run
sequence-level analyses, and it does not make sequence-level
claims. The strongest loss claim it commits to is **candidate
loss with annotation-level evidence**, which means all three of
the following hold:

- The gene is present at the syntenic locus in the diploid
  comparator (zebrafish, with secondary cross-check per section
  4.2 where needed).
- The gene is present on the homeologous chromosome in the same
  carp assembly — i.e. the homeolog on the other subgenome is
  retained.
- A search of the annotation on the affected chromosome, within
  and around the syntenic flanking-gene block, returns no
  candidate group member — neither a named member of the group
  nor a LOC identifier with a group-suggestive description nor a
  pseudogene biotype annotation.

That is supportive evidence for a real evolutionary loss. It is
not confirmation. The comparative-genomics literature reserves
"confirmed loss" for sequence-level analyses — typically tBLASTn
against the unannotated genomic region using outgroup and homolog
proteins as queries, plus sequence-level synteny alignment. This
procedure deliberately does not operate at that level.

What the procedure does instead is two things. It makes
candidate-loss claims with consistent hedging — never "lost in
*C. gibelio*" without a qualifier, always "candidate loss with
annotation-level evidence" or shorter forms that preserve the
hedge. And it logs the sequence-level follow-up question to the
side-projects list (section 8). A candidate loss in the curation
document is a flag that a sequence-level investigation could
either confirm or overturn — exactly the kind of well-bounded
follow-on work the procedure's scope choice is designed to make
visible.

The same logic applies to gene-identity questions that require
sequence-level resolution. Within-cluster homeolog identity in a
tandem duplication is the canonical case: synteny confirms the
locus but cannot distinguish which paralogue is which when the
cluster has expanded differently on A and B. The procedure flags
the ambiguity, names the cluster, preserves the underlying LOC
IDs, and logs the question. It does not guess.

### 4.4 Bring clarity, maintain humility

The curation document and the visualization should make the data
understandable without over-stating what it supports. This is the
orienting principle for both deliverables.

What it means in practice:

- Loss claims hedge to "candidate loss with annotation-level
  evidence" by default (section 4.3). The word "confirmed" stays
  out unless sequence-level work has been done — which, by the
  scope choice in section 1.3, is out of the procedure's scope.
- Identity calls within ambiguous clusters are marked ambiguous
  rather than guessed. The visualization preserves the underlying
  LOC IDs in every cell so that nothing is lost from the
  annotation, even when the curator's preferred identity call
  overrides the NCBI name.
- Visualization layers go from coarse to fine. The hierarchy
  explorer's chromosome-map layer commits the viewer to no
  specific identity claim; the per-pair layer carries the calls
  the curation has settled; the per-gene layer preserves the
  underlying identifiers regardless of what the higher layers
  display. A reader drilling down should not encounter a
  hedge-stripping transition that the curation document does
  not also make.

When in doubt: hedge. The curation is more defensible for it.

### 4.5 AI as parser, human as curator

The procedure is built around a deliberate division of labour
between the AI assistant and the human curator. This is not
incidental — it is the design choice that lets the procedure
work for a user who is not a bioinformatician but is a domain
expert. Naming the division explicitly is part of the procedure
because it changes how the curator approaches the work: not as a
self-sufficient analyst, and not as a passive reviewer of AI
output, but as a director of a collaboration in which each side
does what it is good at.

What the AI does well, and is expected to do: parse GFF files,
extract protein sequences, search for motif patterns, pull
flanking-gene neighbourhoods, run regex against annotation
descriptions, produce formatted draft text and tables, generate
the visualization HTML. These are mechanical operations on
structured text. The AI's failure rate on them is low and its
failure modes are visible — a mis-parsed GFF produces a wrong
table that the curator can spot.

What the AI does poorly, and is expected to *defer* on: domain
judgement, hedge calibration, recognition of when the evidence is
insufficient. The AI's failure modes here are not visible: a
fabricated motif citation reads exactly like a real one; a
smoothed-over uncertainty reads as confident. The curator has to
catch these. Section 7's anti-hallucination constraints exist to
make those failure modes harder for the AI to fall into in the
first place, but they are not sufficient on their own.

What the human curator does, and the procedure relies on them
for: defining the group of genes (Checkpoint 1, section 3.4);
overriding NCBI gene-name calls when synteny supports a different
identity (section 4.1, with the operational rule in section 5.4);
deciding when a slot is ambiguous and a question should be logged
rather than answered (section 4.3); resolving the flagged empty
slots into explicit loss calls (Checkpoint 3, section 6.1);
reviewing the curation as a whole for cross-pair inconsistencies
before the visualization is built (Checkpoint 4, section 6.2);
designing the visualization's interpretive grouping (Checkpoint 5,
section 6.3). The five conversational checkpoints (sections 3.4,
5.1, 6.1, 6.2, 6.3) are where the human's role is most
concentrated, but the procedure
expects the curator to be present throughout — to push back on AI
claims that feel stronger than the evidence supports, and to
flag any pattern that the procedure as written does not handle.

The procedure is not the AI working unsupervised and the curator
signing off at the end. It is also not the curator doing the
work and the AI typing it up. It is the two working in alternation,
with the checkpoints as the moments where the alternation
deliberately slows down.

---

## 5. Per-pair curation

This is the operational core of the procedure. With the inputs
from section 3 in place and the principles from section 4
internalised, the curator and the AI work through the
homeologous chromosome pairs that carry members of the group,
one pair at a time, producing one section of the curation
document per pair.

The section opens with Checkpoint 2, the conversation that frames
the pair-by-pair work and sets pacing expectations (section 5.1).
A per-pair checklist (section 5.2) functions as a working
self-audit during each pair. The per-pair procedure itself
(section 5.3) has six substeps that run in order; the decision
rules they invoke are gathered in section 5.4. Output templates
for the per-pair sections and the curation document's opening
matter (sections 5.5 and 5.6); a summary section (5.7) closes the
curation document.

### 5.1 Checkpoint 2 — reviewing the inventory and choosing the focal species

This is the second of the five conversational checkpoints (the
first was section 3.4; the third, fourth, and fifth are sections
6.1, 6.2, and 6.3). Like Checkpoint 1, it is a place where the procedure
deliberately pauses for dialogue. The substance is different:
Checkpoint 1 settled what the group of genes is and how the GFFs
were searched; Checkpoint 2 takes the output of that mechanical
work and sets the curator's expectations for what comes next.

**When this checkpoint happens.** After the gene inventory is
built (Stage 3c), so the inventory — which now also carries the
tentative homeolog-pair assignments — exists. Before the curator
begins per-pair curation. (A lighter preliminary look at the raw
gene list happens earlier, just after Stage 2; this checkpoint is
the substantive review, made against the built inventory.)

**What needs to be settled.** Four things.

First, the inventory itself, reviewed as the shared baseline.
Before any pair is curated, the curator and the AI look at the
built inventory together and confirm it as the starting point that
everything downstream rests on: the per-species row counts are
sensible, no expected member is missing or obviously spurious, and
the gene-model quality flags are understood. Confirming the
inventory here makes it the agreed baseline, so the per-pair
curation builds on it rather than re-litigating it — and if
something looks wrong now (a missing member, a miscount), it is far
cheaper to fix the config and rebuild the inventory at this point
than after curation has begun.

Second, the focal species for the curation. The inventory spans
every carp genome present in the repo, but everything from here on
— the per-pair curation, the empty-slots deep dive, and the
visualization — is always about **one** focal species: its A and B
subgenomes curated against the zebrafish comparator (section 2.2),
with the other carp genomes consulted only as supporting evidence (for
example, whether an empty slot is also empty in the other carps).
This choice belongs to the curator and must be made explicitly
here. The workflow must not slide silently into whichever genome
has the best annotation. Ask which genome the curator wants to
curate. If they want more than one, the curation runs once per
focal species — each taken all the way through to its own
visualization, one species at a time — rather than merged into a
single cross-species document.

Third, the status of the homeolog-pair assignments. The inventory
rows assign each gene to a homeologous chromosome pair *based on
chromosome name* — A7 and B7 are tentatively a pair, A23 and B23
are tentatively a pair, and so on. These assignments are
candidates, not confirmations. The synteny work that confirms them
(or exposes them as wrong) is the substance of the per-pair
curation ahead. The conversation should confirm the curator
understands this distinction before proceeding.

Fourth, a curation plan: which of the focal species' homeolog
pairs to tackle in what order.
There is no canonical order. Some curators prefer the
cleanest-looking pairs first to establish the section template
before harder cases; others prefer the hardest pairs first while
attention is freshest. Either works. The practical value of
working deliberately — one or two pairs at a time rather than
the whole inventory at once — is that cross-pair patterns emerge
as the curation builds and can be caught before they propagate.
But the curator should set the pace that works for them.

**The output of this checkpoint** is an agreed sequencing plan
and confirmation that synteny-based confirmation is required
before any pair's identity claims can be cited. The mechanical
inventory names a chromosome and a tentative homeolog pair
number; it does not establish an identity that can be relied on
until the synteny argument has been made.

**AI initiation.** As with Checkpoint 1, the AI assistant is
expected to initiate this conversation if the human does not.
Section 7.2 names the analogous expectation across all five
checkpoints.

### 5.2 Per-pair checklist

The checklist below is a working self-audit that the curator and
the AI run before each per-pair section is written. It is short
on purpose: each item maps to a substep of the per-pair procedure
(section 5.3) or to a decision rule (section 5.4), and the
checklist exists to make sure none of them is silently skipped.

If an item is genuinely not applicable to a pair, the per-pair
section should say so explicitly (e.g. "Motif check: not
applicable — this group does not have a defining catalytic
motif"). An item that is silently omitted is one the procedure
cannot tell from a missed step.

- [ ] **Outgroup locus identified.** Which gene(s) of the group
      sit at the equivalent locus in the zebrafish reference, and
      on which zebrafish chromosome.
- [ ] **A/B chromosomes identified.** Accession numbers and short
      labels (A*n*, B*n*) for the affected pair in the anchor
      genome.
- [ ] **Group members listed.** Every annotated member on A and B
      in the species being curated, from the inventory, including
      LOC IDs, NCBI names, and coordinates.
- [ ] **Local synteny extracted.** Flanking-gene neighbourhood for
      A and B, from the Stage 3d extract or freshly pulled from
      the GFF (section 3.3 fallback).
- [ ] **Protein evidence recorded.** For each gene, the protein
      length, defining-motif check (where applicable), exon count,
      and expression evidence. Marked "not assessed" rather than
      guessed where the data are missing.
- [ ] **Length compared to outgroup orthologue.** Recorded
      alongside the protein evidence.
- [ ] **NCBI conflict assessed.** When A and B carry different
      NCBI gene names from the same group, the synteny-vs-naming
      check from section 5.4 has been applied.
- [ ] **Absence search documented.** If any slot is empty, the
      search performed (or not performed) is recorded explicitly.
      "Candidate loss" requires a documented negative search;
      "absent — no specific search done" is the honest default
      otherwise.
- [ ] **Syntenic-block quality assessed.** For any candidate-loss
      slots, the syntenic-block-quality framework in section 5.4
      has been applied to the empty chromosome's flanking
      neighbourhood.
- [ ] **Secondary-outgroup cross-check considered.** For any pair
      where the slot structure is uncertain, the section 4.2
      cross-check has either been run or explicitly decided
      against with a reason.
- [ ] **Confidence assigned.** Each functional gene's identity
      call carries a confidence level from the three-axis rubric
      in section 5.4.
- [ ] **Deferred questions logged.** Anything the annotated inputs
      cannot resolve has been added to the side-projects list
      (section 8).

### 5.3 The per-pair procedure

Six substeps. They run in order, with the output of each substep
feeding the next. The procedure assumes the inputs from section
3.1 are all in place and that Checkpoint 2 has set the pacing.

**5.3.1 Establish the outgroup reference.** Look up which gene(s)
from the group sit at the equivalent locus in zebrafish. There
may be a single ancestral gene at the locus, several (tandem
clusters are the common case), or two distantly-located genes
that the allopolyploid carp genomes treat as one chromosome
position.

The zebrafish gene name is the *reference framework*, not
necessarily the correct identity for the carp homeologs. A
zebrafish chromosome may carry gene X, but the carp pair-X
homeologs may have been labelled by NCBI as gene Y on one
subgenome and gene Z on the other; the synteny argument in
substep 5.3.4 is what reconciles those labels. The caspase
worked example carries a textbook case: zebrafish chr7 carries
`casp23`; both carp pair-7 homeologs are homeologs of `casp23`;
NCBI labels one of them `caspa` because of sequence similarity,
but that label is wrong by syntenic position.

Record the zebrafish chromosome number, the group members at
that locus with their names and protein lengths, and — if there
are multiple — their relative positions on the zebrafish
chromosome.

When the zebrafish state at the locus is uncertain or unusual
(triggers listed in section 4.2), run the secondary-outgroup
cross-check before continuing. The cross-check procedure itself
is in section 4.2; this substep is where the curator decides
whether to invoke it for this pair.

**5.3.2 Identify the slot structure.** Determine the homeolog
slots for this pair. A *slot* is a syntenically bounded
ancestral gene position — derived from the outgroup framework
and confirmed by the carp genomes — not necessarily equivalent
to one modern gene.

Three slot types come up:

- *Single slot.* One ancestral gene at the locus; expected to
  give one A homeolog and one B homeolog in the carp genomes (or
  losses, handled in section 5.4).
- *Group (tandem-cluster) slot.* Multiple ancestral paralogues
  sitting close enough that 1:1 homeolog pairing within the
  cluster cannot be settled by synteny alone. The cluster's
  contents are listed; specific paralogue identities within the
  cluster are flagged ambiguous and deferred to phylogenetic
  follow-up (section 8).
- *Excluded slot.* Assembly artefacts that should not be counted
  as real homeologs (the criteria are in section 5.4). The slot
  label captures the artefact's position; the empty side of the
  slot does not receive a loss label.

Treating "slot" as synonymous with "gene" is a common error that
breaks the ambiguity logic and over-commits the curation to
specific 1:1 identities the evidence does not support. The
distinction is worth holding deliberately.

The outgroup gene set sets the maximum number of slots; the
empirical A/B counts in the carp anchor genome confirm or revise
that count; the secondary-outgroup cross-check refines it where
the zebrafish state is uncertain.

**5.3.3 Extract evidence for each gene.** For each annotated
group member on A and B in the anchor genome, record:

- Gene ID (LOC accession or named gene).
- NCBI annotation name as currently assigned.
- Protein length in amino acids.
- Protein length of the closest zebrafish orthologue, for
  comparison.
- Defining motif present, if the group has one (for the caspase
  worked case the catalytic QACxG motif is the relevant feature;
  for other groups the relevant feature is whatever defines the
  group at the sequence level, decided at Checkpoint 1).
- Number of CDS exons **per isoform** — use the representative
  (longest) transcript, read from the inventory's `cds_exons`
  column (computed mechanically; `transcript_variants` records how
  many coding transcripts the gene has). Do **not** sum CDS exons
  across all isoforms: that inflates multi-isoform members and makes
  clean homeolog pairs look structurally asymmetric. When comparing
  an A/B pair, compare representative-isoform counts like-for-like.
- Expression evidence (supporting proteins or SRA reads, from
  the GFF or RefSeq metadata).
- The gene-model quality flag from the inventory (`ok` / `check`
  / `suspect`).

If the gene sits on an unplaced scaffold, record the scaffold ID
and note that it is not chromosome-anchored. Unplaced-scaffold
genes carry their own per-pair-section variant (section 5.5).

**5.3.4 Synteny analysis.** For each region carrying a group
member — on A, on B, and in zebrafish — list the flanking gene
order. Use ~8–15 genes on each side of the focal region; the
Stage 3d synteny extracts produce these by default.

Compare three things:

- Whether A's flanking gene set and B's flanking gene set are
  the same. They should be.
- Whether they are in the same order, or whether one is inverted
  relative to the other. Pre-hybridization inversions are common in the
  carp lineage; post-hybridization inversions are rarer but happen.
- How both compare to the zebrafish reference framework. Same
  order, pre-hybridization inversion, post-hybridization rearrangement?

The synteny match between A and B is the *primary evidence of
homeolog identity*. If A and B share their flanking neighbourhood
and that neighbourhood matches the zebrafish locus, the genes at
the centre are homeologs of the zebrafish gene at that locus,
regardless of what NCBI named them. Section 4.1's principle is
applied here.

**5.3.5 Apply the decision rules.** Run through section 5.4's
decision rules in order, for this pair:

1. Synteny vs naming (5.4.1). Relabel any genes whose NCBI name
   conflicts with their syntenic position.
2. Flag empty slots (5.4.2). For any slot where A or B is empty,
   record it as `absent — no specific search` and flag it for the
   empty-slots deep dive (Checkpoint 3, section 6.1). The in-region
   sweep and the loss call are made there, not per-pair — do not
   attempt the full assessment now.
3. Ambiguity flagging (5.4.3). For any slot where 1:1 pairing
   within the slot cannot be settled by synteny alone, mark it
   ambiguous and group the genes.
4. Assembly artefacts (5.4.4). Flag any gene whose evidence
   pattern matches the artefact criteria.
5. Pseudogene identification (5.4.5). Flag any gene with the
   pseudogene evidence pattern.
6. Confidence call (5.4.6). Assign each functional gene a
   confidence level for its identity assignment, using the
   three-axis rubric.

**5.3.6 Write the section using the template.** Apply section
5.5's per-pair template. The output is one section in the
curation document for this pair. The template is structured
enough to keep per-pair sections comparable across pairs and
loose enough to absorb the variation that real pairs surface.

When all the pairs that carry group members have been curated,
the curation document is assembled in the order section 5.6
specifies and a summary section (5.7) is written to close it.
The curator then proceeds to the empty-slots deep dive
(Checkpoint 3, section 6.1), which resolves the flagged empty
slots, and then to the review of the curation as a whole
(Checkpoint 4, section 6.2) before the visualization is built.

### 5.4 Decision rules

The six rules below are the decisions a curator and the AI
assistant work through together at each pair. They run in order
during step 5.3.5: synteny vs naming, then loss assessment, then
ambiguity flagging, then assembly artefacts, then pseudogene
identification, then confidence calls. The ordering matters —
later rules read against the calls earlier rules have made — but
within a pair the curator may need to loop back when a later rule
surfaces something the earlier one missed.

Loss assessment (5.4.2) is the one exception to "worked at each
pair." During per-pair work an empty A or B side is only *flagged*
and recorded as `absent — no specific search`; the in-region sweep
and the loss call are executed in a single consolidated pass at the
empty-slots deep dive (Checkpoint 3, section 6.1), where the full
cross-species picture is available. The procedure in 5.4.2 documents
that method; it is invoked at the checkpoint, not piecemeal here.

Each rule has the same shape: a default statement, the procedure
that operationalises it, conditions under which the default does
not apply or needs supplementation, and a concrete illustration
from the caspase worked example.

#### 5.4.1 Synteny vs naming

**Default rule.** When A and B genes at the same syntenic locus
are labelled by NCBI with different group-family names, the
divergent label is most likely wrong. Both genes most likely
derive from the same pre-hybridization ancestor at this locus and should
carry the same identity (with a homeolog suffix). The reasoning
behind this default is in section 4.1; this rule is its
operational form. The AI's job here is to **highlight** such conflicts
— to surface the mismatch and the evidence for it — not to relabel on
its own authority. The relabelling decision belongs to the curator.

**Procedure.**

1. Confirm the two genes share their flanking-gene neighbourhood
   (substep 5.3.4 produces the evidence for this).
2. Confirm the zebrafish locus carries the gene that *one* of the
   two NCBI labels claims. For example, if NCBI labels A as
   `casp23` and B as `caspa`, check whether the zebrafish locus
   equivalent to this pair carries `casp23` or `caspa`.
3. If the secondary outgroups (section 4.2) agree with the
   zebrafish state on which gene was at the locus, the case for
   relabelling is strong. If they disagree, the ancestral state
   is itself uncertain and the case should be referred to side
   projects (section 8) rather than forced.
4. Whichever NCBI name matches the zebrafish (and ideally the
   secondaries') state at the locus is the candidate identity the
   synteny evidence points to for both homeologs; the other NCBI
   label is most likely a sequence-similarity-based mis-call.
5. **Highlight the mismatch for the curator.** Present the conflict
   and the synteny-supported candidate identity, and let the curator
   decide whether to relabel — the AI surfaces it, the human makes the
   call. If the curator does relabel, the convention is flexible —
   `<gene>` (A homeolog) / `<gene>` (B homeolog), or `<gene>a` /
   `<gene>b`, or another paired-suffix form — the biological claim
   (these are homeologs of one ancestor) is what matters.
6. Leave the original NCBI annotation visible in the per-gene
   metadata so a reader can see what was relabelled and why. This
   is the anti-hallucination requirement from section 7.1 applied
   in this case.

**When the rule does not apply.** Three situations:

- The zebrafish state at the locus is itself derived
  (section 4.2's cross-check has flagged it). In this case
  ancestral identity is uncertain; refer to side projects.
- The locus is a tandem cluster on both A and B (rule 5.4.3
  applies instead; do not relabel within the cluster).
- There is sequence-level or phylogenetic evidence (from a
  side-project run) that genuinely supports divergent homeolog
  identities at the locus. This is rare in the carp project as
  currently scoped, but the rule does not pretend it can never
  happen.

**Caspase example.** Pair 7 in the cyprinid carps. NCBI labels A7
as `casp23` and B7 as `caspa`. Zebrafish chr7 (the pair-7
ancestral chromosome) carries `casp23` only; `caspa` proper sits
on zebrafish chr16. Both A7 and B7 are therefore `casp23`
homeologs, and the NCBI `caspa` label on B7 is a similarity-based
mis-call. All three carp species show the same pattern, supporting
a single relabelling decision rather than a per-species
investigation.

#### 5.4.2 Loss assessment

**Where this runs.** This procedure is executed at the empty-slots
deep dive (Checkpoint 3, section 6.1), not during per-pair curation.
During per-pair work the empty side is only flagged and recorded as
`absent — no specific search`. What follows is the per-slot method
the checkpoint applies to each flagged slot; the checkpoint adds the
collaborative framing, the cross-species reasoning, and the
comparator-availability gate around it.

**Scope — whole-slot absences only.** A tandem cluster is a single
slot (5.3.2). This loss assessment, and the Checkpoint 3 deep dive,
apply to a slot that is empty on A or B — a locus-level absence.
Differing paralogue counts within a cluster that is *present* on
both subgenomes are *asymmetric retention* (5.4.3), not loss: the
procedure cannot say which paralogue is missing, so the curator
decides how to describe it, and the cluster is not decomposed into
per-paralogue slots routed to Checkpoint 3.

**Rule.** An empty A or B side at a slot is `absent` by default
and upgraded only if the curator has actively searched the
annotation in the syntenic region, established the syntenic
block's quality on the empty chromosome, and worked through the
in-region annotation sweep below. At the empty-slots checkpoint a
slot is left at the default `absent — no specific search` only by an
explicit decision that the sweep is not warranted, never by simply
not doing it.

Three outcome labels are available, in ascending order of
evidential strength:

- `absent on An/Bn — no specific search done` — the honest
  default when the substep has not been worked through.
- `absent on An/Bn — candidate loss (annotation-level)` — the
  in-region sweep is negative (no group-suggestive feature found),
  the syntenic block is intact or partially preserved, and the
  outgroup and homeologous chromosome retain the gene.
- `absent on An/Bn — candidate non-functional locus at syntenic
  position (annotation-level)` — the in-region sweep finds a
  degraded or biotype-flagged locus at the expected position. The
  locus is present in the annotation but the functional coding copy
  is not. The sequence-level question this flags ("is this a true
  pseudogene, and when did it arise?") is logged to the side-
  projects list (section 8); it is distinct from the standard
  candidate-loss follow-up question.

"Confirmed loss" or "lost" without a qualifier is reserved for
sequence-level work and is out of scope (section 4.3).

**Procedure for the upgrade.**

1. *Outgroup retention.* The gene is present at the syntenic
   locus in zebrafish (and, where the cross-check is invoked, in
   the secondary cyprinids).

2. *Homeologous-chromosome retention.* The gene is present on the
   homeologous chromosome in the same carp assembly — the homeolog
   on the other subgenome is retained.

3. *Syntenic-block quality.* The block of flanking genes that
   defines the locus is sufficiently intact on the empty
   chromosome that an absence claim can be supported. The
   syntenic-block-quality framework below operationalises this.

4. *In-region annotation sweep.* Pull every gene feature in the
   syntenic block interval from the GFF — not filtered by name or
   biotype. For each feature, examine three fields in order:

   a. *Biotype flag.* Check the `gene_biotype=` attribute. Values
      of `pseudogene`, `transcribed_pseudogene`, or
      `unitary_pseudogene` are explicit annotation-level signals
      that a locus is present but non-functional. A pseudogene-
      biotyped feature in the interval is the closest the
      annotation level gets to explaining the absent coding copy:
      the locus exists but the gene model is degraded. If found,
      the sweep result is `pseudogene biotype`; the slot takes
      the third outcome label, not the second.

   b. *Description field.* Check the `description=` attribute of
      every gene in the interval, including LOC-named genes. NCBI's
      automated annotation populates this field with a functional
      prediction even when the gene lacks a proper symbol. Apply
      family-relevant search terms to this field — for caspases:
      `caspase`, `cysteine-aspartic protease`, `ICE-like`,
      `apoptosis-related cysteine peptidase`, `CASP`, `CARD`. Any
      match is a candidate requiring the protein FASTA check
      before any label is assigned.

   c. *Protein FASTA header.* For any LOC gene in the interval
      that returned a match in step (b) — or that sits precisely
      within the flanking-gene block with a non-specific
      description — check whether a protein entry exists for that
      locus in the protein FASTA. Two signals are informative:

      - *No protein entry.* The locus has no annotated protein
        model. Consistent with a pseudogene or unannotated gap.
        Record as sweep result `absent protein model`.
      - *`LOW QUALITY PROTEIN:` prefix.* RefSeq's flag for a
        model built on a degraded locus — partial exons, internal
        stops, or frameshift corrections. Record as sweep result
        `LOW QUALITY PROTEIN`.

      Either finding from step (c) directs the slot to the third
      outcome label. A protein entry with a normal header and a
      family-adjacent description directs it to Checkpoint 2
      review: the gene may have been missed by the Stage 2
      mechanical search and should be added to the inventory
      before the loss claim is made.

   When the sweep returns nothing group-suggestive — no pseudogene
   biotype, no family-adjacent description, no degraded FASTA
   entry at the expected position — that negative result is itself
   evidence. It means the locus is not annotated in any
   recognisable form in the syntenic window. Record the sweep
   result as `negative` and proceed to step 5.

5. *Cross-species supportive evidence (optional).* If the same
   absence pattern is observed in the other carp species, the
   loss or non-functional state is more likely to predate their
   divergence than to reflect an annotation issue in one assembly.
   This strengthens but does not by itself establish the claim.

Assign the outcome label based on the sweep result. Document the
syntenic-block-quality assessment and the sweep result alongside
the label. The summary section (5.7) carries columns for both.

**Syntenic-block-quality framework.** The candidate-loss claim
rests on the block being recognisable on the empty chromosome.
Three quality levels, with the implication each carries:

- *Block clearly present.* Most of the expected named flanking
  genes are found on the empty chromosome in roughly the expected
  relative order (inversions allowed). The candidate-loss claim
  rests on solid ground: the block is here but the gene is not.
- *Block partially preserved.* Some expected named flanking
  genes are present, others are missing. The block is recognisable
  but degraded. The candidate-loss claim is weaker because the
  region itself shows signs of rearrangement or assembly
  inadequacy, and the missing gene may reflect that rather than a
  specific loss. Hedge the claim accordingly in the per-pair
  section.
- *Block essentially absent.* Only one or two scattered flanking
  hits are present. The block has not survived on this chromosome,
  or this chromosome's annotation does not capture it. The
  candidate-loss-at-this-position claim is undermined; the
  syntenic-position-loss sub-case below may apply instead.

The framework is judgement-based for the messy in-between cases.
"Named flanking genes" should be interpreted against the local
annotation density: in a heavily LOC-annotated region, even a few
named genes carry signal; in a densely named region, missing names
are more informative. The curator should record the call.

*In LOC-heavy regions,* "named flanking genes" should be
interpreted as genes whose `description=` field carries a specific
functional annotation — not "uncharacterized protein" or
"hypothetical protein." Even one or two such descriptively-named
genes in the expected relative positions carry meaningful signal.
The AI assistant should present both `Name=` and `description=`
fields when reporting syntenic context in these regions so the
curator can judge block quality against the functional content of
the neighbourhood rather than gene-symbol matches alone.

**Syntenic-position-loss sub-case.** A subtler loss pattern: the
chromosome carries a group member, but the member is *not* at the
expected syntenic position. The chromosome-level homeolog
assignment is correct, the inventory has assigned the gene to the
right pair, but the gene sits in a different syntenic
neighbourhood from the one the homeolog (or the outgroup) defines.

This produces two interpretive claims rather than one:

- The expected homeolog at the syntenic position is a **candidate
  loss** (the group is missing from the canonical syntenic block
  on this subgenome).
- The chromosome's group member is a **separate gene** at a
  different locus, with a tentative identity of "group-related,
  not at canonical syntenic position; identity unresolved." It is
  referred to side projects for sequence-level or phylogenetic
  follow-up.

The detection procedure is a chromosome-wide search for the
canonical flanking-gene block. If only sparse markers are present
(one or two of the canonical ten or so), the block is genuinely
absent and the syntenic-position-loss interpretation applies. The
per-pair section records both rows: the candidate loss at the
canonical position and the mis-located group member as a separate
entry. The common-carp pilot pair 14 is the worked illustration:
LOC109089113 sits on Cc A14 and is `casp3`-like at the protein
level, but the casp3b syntenic block (`fnta`, `pigg`, `snx25`,
`enpp6`, `irf2`, `cenpu`, `frmpd1`) is absent from Cc A14 — only
a single weak marker (`guf1` near the chromosome start) is
present. The interpretation: casp3b is a candidate loss on Cc A14;
LOC109089113 is a separate casp3b-related paralogue at an
unresolved locus.

**Caspase examples.**

*Clean negative sweep.* Cgib pair 5 A5. Zebrafish chr5 carries
`casp22`; B5 of all three carp species carries a clean `casp22`
homeolog. The in-region sweep of A5 returns no pseudogene biotype,
no caspase-adjacent description, and no FASTA entry at the
expected position — only an unrelated `card9` annotation in the
region. The flanking-gene block on A5 is clearly present
(*block-clearly-present*). The same absence pattern is observed in
Cc and Ca, supporting a pre-divergence loss. Sweep result:
`negative`. Upgraded to `absent on A5 — candidate loss
(annotation-level)`.

*Sweep returns a degraded model — candidate non-functional locus.*
Ca (goldfish) pair 9 A9. Zebrafish chr9 carries `casp10`; B9 of the
same assembly retains a clean `casp10` homeolog (520 aa). The
in-region sweep of A9 does not come back empty: LOC113053832 sits at
the A9 syntenic position with `gene_biotype=pseudogene` (NCBI
description "caspase-8-like"). The flanking-gene block on A9 is
clearly present. Because a feature *is* annotated at the expected
position but carries a pseudogene biotype, the slot resolves to
`candidate non-functional locus on A9`, not to candidate loss — the
locus is present but degraded. Note the contrast with the same slot
in Cgib, where the sweep is negative and the call is a clean
candidate loss: the two outcomes differ in kind, and the sweep result
is what separates them. (Worked record:
`examples/caspase_in_carp/example_identification/Caur_caspase_curation.md`.)

#### 5.4.3 Ambiguity flagging

**Rule.** When 1:1 homeolog pairing within a slot cannot be settled
by synteny alone, mark the slot ambiguous and group the genes
without committing to specific pairings.

This rule applies to tandem-cluster slots and to slots where the
A and B copies sit at the same locus but the cluster has expanded
differently. It does not apply to single-paralogue slots, which
section 5.4.1 handles directly.

**What the flag is and isn't for.** The ambiguity flag applies to
the carp-to-carp homeolog pairing question only: when the A copies
and the B copies within a cluster cannot be matched 1:1 by synteny.
(Zebrafish paralogues with distinct names may still serve as
*positional anchors* within the cluster — that is synteny, and it
is in scope; protein sequence similarity is at most weak
corroboration and never the primary basis for a pairing, per 4.1.)
The flag is *not* for the carp-to-zebrafish question — which carp
copy is phylogenetically closest to which zebrafish paralogue. That
is gene-tree topology, always out of scope here (section 8), and it
is never the basis for an ambiguity flag or a reduced-confidence
call.

**Procedure.**

1. Confirm the slot type from substep 5.3.2. If the slot is a
   single-paralogue slot, this rule does not apply.
2. If the slot is a tandem cluster on both A and B with multiple
   paralogues each, check whether synteny within the cluster can
   distinguish the paralogues: are the cluster members in the
   same order on A and B (after accounting for cluster
   inversion)? Are there zebrafish paralogues with distinct names
   that anchor specific positions within the cluster?
3. If the cluster is uninformative for within-cluster pairing,
   mark the slot **ambiguous**. Label it `<family> cluster — main
   syntenic locus`. List the A members and the B members
   separately. Add a note explaining what cannot be settled —
   usually that within-cluster paralogue identity awaits curated
   phylogeny (a side-project task; section 8).
4. Empty-side counts (e.g. "A retains 2 in this group, B retains
   3") are described as **asymmetric retention** rather than as
   specific losses, because the procedure cannot say *which*
   paralogue is absent on A.

**Caspase example.** Pair 10's main executioner cluster: A
retains two tandem paralogues, B retains two tandem paralogues,
NCBI labels them inconsistently as `casp3-like` and `casp7-like`
across A and B, and the cluster is inverted on B relative to A.
The cluster is marked ambiguous, the A genes are listed as a
group, the B genes are listed as a group, and within-cluster
`casp3` vs `casp7` identity is referred to phylogenetic
follow-up.

#### 5.4.4 Assembly artefacts

**Approach.** Genes that look like assembly artefacts are
*flagged*, and the curator decides whether to *exclude*,
*flag for review*, or *retain with uncertainty annotation*. The
thresholds in the patterns below are indicative, not bright lines:
a recent real tandem duplication can look very similar to a
haplotig artefact, and not every haplotig problem is subtelomeric.
The framework is evidence-graded, not rule-based.

**Strong artefact patterns include one or more of the following.**

- *Subtelomeric duplicate.* A gene within ~50 kb of the
  chromosome start or end whose protein sequence is ≥99%
  identical to another gene of the same group elsewhere on the
  same chromosome, with matching exon sizes.
- *Haplotig duplicate.* Two genes ≥99% identical on different
  scaffolds or distant chromosomal positions, often with
  inconsistent flanking-gene context — suggesting alternative
  haplotype copies of the same locus.
- *Anomalous gene model.* A gene with multiple non-overlapping
  transcript variants whose CDS regions sit at different genomic
  positions, suggesting duplicated sequence within the model.
- *Species-uniqueness.* The same gene is absent from all other
  carp species in the data set at the equivalent position. A real
  retention in one species would typically still register in the
  gene tree at a sister position; an artefact is unique to one
  assembly.

**Decision tiers, after weighing the evidence.**

- *Exclude as likely artefact.* Multiple strong patterns combine,
  and the cross-species check confirms uniqueness. Mark the slot
  as **excluded** (substep 5.3.2). The empty side of the slot
  does not receive a loss label — there was no homeolog there to
  lose.
- *Flag as possible artefact.* One or two suggestive patterns,
  but the evidence is not conclusive. Retain the gene in the
  inventory with an explicit "possible artefact" annotation; do
  not auto-exclude.
- *Retain but annotate uncertainty.* A pattern that might reflect
  a recent real duplication or a mild assembly issue. Retain the
  gene, note the concern in the curation, and refer the question
  to side projects (section 8) for sequence-level or
  cross-assembly verification.

**Watch out for** the recent-tandem-duplication / haplotig
ambiguity. Without sequence-level or cross-assembly comparison,
the two can look identical. When in doubt, do not auto-exclude:
flag and defer.

**Caspase examples.** Clear exclusion: Cgib B10 tip LOC127966001
— 99.6% identical to LOC127966003 elsewhere on B10, identical
exon sizes, subtelomeric (27 kb from chromosome start), absent
from the equivalent position in Cc and Ca, anomalous transcript
variants. Multiple strong patterns, species-unique; marked
excluded. Flag-only: Ca B14 carries two caspase genes 99.6%
identical to each other, 400 kb apart, with different flanking
gene contexts. Strong identity-pattern evidence but no clear
cross-species artefact confirmation (Cc B14 has a genuine
three-gene tandem expansion at the same locus that Ca's pattern
could mirror). Flagged in the comparative curation as "possible
assembly duplication artefact" without auto-exclusion; referred
to alternative-assembly cross-check on the side-projects list.

#### 5.4.5 Pseudogene or non-functional-remnant identification

**Approach.** A gene that lacks group-defining functional
features is flagged as either a **pseudogene** (strong claim,
requires multiple lines of structural disruption) or as a
**likely non-functional remnant** or **non-canonical paralogue**
(weaker claim, suggestive but not conclusive). Loss of a single
functional feature — for example, the catalytic motif — is not
sufficient on its own.

The distinction matters because in many gene families, loss of a
catalytic motif does not imply pseudogene. The protein may be a
non-catalytic paralogue with a regulatory or scaffolding role, a
dominant-negative variant, a receptor-like decoy, or an
alternative-function paralogue. For caspases, loss of QACxG is
strong evidence against canonical protease function but does not
by itself mean the locus is junk DNA.

**Strong pseudogene evidence** — use the term *pseudogene* when
multiple of the following are present:

- Protein length substantially shorter than the full-length
  zebrafish orthologue (typically less than 50%), suggesting
  truncation rather than alternative start.
- Defining functional motif absent.
- Disrupted gene structure: frameshift, premature stop codon,
  fragmentary or interrupted gene model, missing functional
  domains.
- Reduced CDS exon count compared to the group-typical structure.
- Minimal or absent transcript / expression evidence.

**Weaker remnant evidence** — use the term *likely non-functional
remnant* or *non-canonical paralogue* when only one or two of the
above features are present (e.g. catalytic motif absent but
length and exon structure intact, with normal expression). The
loss of function is noted; the strong pseudogene call is
deferred.

**Recording these in the explorer.** When you build the hierarchy
explorer (§6.4), each gene carries a `status`. Map the call as
follows: a gene NCBI annotates as a pseudogene → `pseudo`; an
assembly artefact → `artefact`; a copy you judge **likely
non-functional from annotation-level evidence but which NCBI has
*not* called a pseudogene and which is not an artefact** (the
"weaker remnant" / "likely non-functional remnant" case above) →
`candidate_nonfunctional`; everything else → `ok`. Do not use
`ok` for a copy you have judged non-functional — it would render
as a normal functional gene and inflate the functional counts. The
explorer build rejects any other `status` value, so a mistyped
flag fails the build rather than miscounting silently (see
`scripts/templates/CURATION_DATA_SCHEMA.md`).

**Caspase example.** Both A1 and B1 in Cgib carry truncated
`caspbl` remnants (143 aa on A1, 93 aa on B1, against a
full-length zebrafish reference). Neither has the active site.
Both have only two CDS exons against the family-typical five to
seven. Expression evidence is minimal. Multiple lines of
structural disruption are present on both homeologs — strong
pseudogene calls on both. The two truncations are different
lengths, supporting independent post-hybridization degradation rather than
a shared ancestral pseudogene.

#### 5.4.6 Confidence calls

**Approach.** Each functional gene's identity call carries
**three separate confidence axes** rather than one combined
score. The single-score approach compresses three different
kinds of uncertainty into one rubric and produces internal
contradictions — for example, "NCBI agreement" cannot
simultaneously be required for `High` confidence and overridable
under section 5.4.1. The three-axis version makes each kind of
uncertainty visible separately.

**Axis 1 — Locus confidence.** Is this gene at the expected
syntenic locus?

- *High* — the gene sits in the canonical syntenic flanking-gene
  block for this slot, with expected neighbouring genes in the
  expected order on both A and B.
- *Medium* — the gene is on the right chromosome (the homeolog
  pair number matches) but only some of the expected flanking
  genes are present, or the local synteny block is partly
  rearranged.
- *Low* — the gene is on the right chromosome but a
  chromosome-wide search reveals the syntenic block is absent or
  genuinely broken (the syntenic-position-loss sub-case in
  5.4.2).

**Axis 2 — Identity confidence.** Do we know which paralogue
identity (which ancestral group member) this gene should carry?

This axis is about which named paralogue within a carp cluster the
gene corresponds to, assessed relative to the other carp copies at
the same locus and the zebrafish-defined slot framework. It is
*not* about the phylogenetic relationship between the carp cluster
and the zebrafish reference cluster — which carp copy is closest to
which zebrafish paralogue is a gene-tree question logged to side
projects (section 8), and it does not lower this axis.

- *High* — the synteny-derived identity is unambiguous: the
  zebrafish locus carries one well-defined gene, the slot is a
  single-paralogue slot, and protein-level evidence (length,
  motif) is consistent with that identity. NCBI agreement is
  supportive but not required; when synteny and NCBI conflict
  and the synteny case is strong (rule 5.4.1), the synteny-derived
  identity is still `High`.
- *Medium* — the synteny-derived identity is well-supported but
  the gene is in an ambiguous group slot, or there are
  cross-homeolog or cross-species inconsistencies that don't
  undermine the call, or the gene is one of a handful of close
  paralogues at the locus.
- *Low* — the locus has known naming confusion (the executioner
  caspase cluster is the canonical example), or specific
  paralogue identity within an ambiguous group cannot be settled
  by synteny alone, or sequence-level / phylogenetic evidence
  would be needed to pin down identity.

**Axis 3 — Model confidence.** Is the gene model structurally
credible?

- *High* — full-length protein matching the group-typical size,
  intact functional motif (if applicable), group-typical exon
  count, normal expression evidence.
- *Medium* — somewhat shorter or longer than typical, atypical
  exon count, or limited expression evidence; structurally
  plausible but worth re-checking.
- *Low* — gene model is structurally suspect (very short, very
  long, anomalous transcript variants); the locus may not encode
  the protein the model implies.

**Reporting the three axes.** In the per-pair gene table, the
three axes can be reported either separately (`L=High,
I=Medium, M=High`) or as a compact triple (`H/M/H` for axes
1/2/3). The single-score legacy form (`High` / `Medium` / `Low`)
can still be used as a summary — its meaning is "the lowest of
the three axes" — but the three-axis breakdown should be
available where any axis differs from the others. For external
sharing or publication-shaped output, the three-axis breakdown
is recommended.

**What confidence is and isn't.** Confidence is in claims about
the gene's identity and structure, not in the gene's existence
(existence is given by annotation). A three-`High` gene is one we
are confident *is what we say it is, at the right place, with a
credible model*. A `High`-`Low`-`High` gene is one we are
confident sits at the right place and has a credible model but
whose specific paralogue identity we cannot pin down — typical
for cluster genes.

**On cross-species motif variation.** The defining motif of the
group can vary between species or between homeologs within a
species without lowering identity or model confidence, as long as
a valid motif is present and the rest of the evidence supports
the identity. The Cgib A7 `casp23` carries an unusual QSCRG (Ser
in position 2) variant; the Cc A7 `casp23` has the standard
QACRG. Both are `casp23` homeologs by synteny. Note such variants
in the per-pair section as features of interest, but do not let
them down-weight any of the three confidence axes.

### 5.5 Output template — per-pair section

The template below is the structure each per-pair section uses.
It is taken from the caspase worked example
(`examples/caspase_in_carp/example_identification/Cgib_caspase_curation.md`) and
has been tested across all twelve pairs that carry caspases. The structure
keeps per-pair sections comparable across pairs while leaving
enough room to absorb the real variation pairs surface.

Each section is written for the **focal species** chosen at
Checkpoint 2: the A‹n› and B‹n› rows are that species' two
subgenome copies, assessed against the zebrafish reference.
Evidence from the other carp genomes enters as supporting material
— in the Protein assessment prose or the Notes column (for example,
"the same slot is empty in the other carps") — not as additional
rows in the Genes table.

```markdown
## Pair <n> — <ancestral locus name> (zebrafish chr<n>)

**Chromosomes:** A<n> = <accession>, B<n> = <accession> (<size Mb>)

### Genes

| Chr | Gene ID | NCBI name | Protein | Length | Outgroup ref | Motif | CDS exons (repr. isoform) | Status |
|-----|---------|-----------|---------|--------|--------------|-------|--------------------------|--------|
| A<n> | <id> | <ncbi name> | <accession> | <length> aa | <length> aa (<ref name>) | <motif> | <count> | <status> |
| B<n> | <id> | <ncbi name> | <accession> | <length> aa | <length> aa (<ref name>) | <motif> | <count> | <status> |

### Protein assessment

<For each gene or each functional group, describe the protein-
level evidence. Length comparison to zebrafish, motif presence,
exon count, expression support. Group homeologs together.>

<Where the synteny-derived identity differs from the NCBI
annotation, explain explicitly. Use the language: "NCBI annotates
this gene as X, but synteny rules this out because [reason].
Therefore this gene is Y (B homeolog), not X.">

<For pseudogenes and assembly artefacts, document the evidence
pattern that supports the call.>

### Synteny

<Code block laying out the flanking gene order on the zebrafish
reference, A, and B. Mark inversions if present. Comment on
synteny conservation.>

\`\`\`
Zebrafish chr<n> (+ strand):
  <flanking gene order with the group member in caps>

A<n> (orientation):
  <flanking gene order>

B<n> (orientation):
  <flanking gene order>
\`\`\`

<Comment on the comparison: how many flanking genes are conserved,
whether the block is inverted between A and B or relative to
zebrafish, any rearrangements of note.>

### Proposed curation

| Gene ID | Current NCBI name | Proposed identity | Confidence (L/I/M) | Notes |
|---------|-------------------|-------------------|--------------------|-------|
| <id> | <ncbi name> | **<identity>** (A homeolog) | H/H/H | <key evidence; flag NCBI override if applicable> |
| <id> | <ncbi name> | **<identity>** (B homeolog) | H/H/H | <key evidence; flag NCBI override if applicable> |

<Optional naming note for ambiguous suffix conventions.>
```

The confidence column carries the three-axis triple from section
5.4.6 (Locus / Identity / Model). The compact `H/M/H` form is the
default; the verbose form (`L=High, I=Medium, M=High`) can be
used where it reads better.

**Variant — pair with a candidate loss.** Add a `[LOST]` row to
the Genes table indicating the missing slot, and document the
negative-search evidence and syntenic-block-quality call (section
5.4.2) in the Protein assessment subsection. The Proposed
curation table includes a row:

```markdown
| — | — | **<identity>** (A<n> candidate loss, annotation-level) | High | <evidence summary; syntenic-block-quality call; cross-species pattern if any> |
```

**Variant — pair with an assembly artefact.** Add a subsection
titled "Assembly artefact assessment for <gene ID>" between
Protein assessment and Synteny, documenting the evidence pattern
(section 5.4.4). The Proposed curation table includes:

```markdown
| <id> | <ncbi name> | **assembly artefact** | — | <evidence summary> |
```

The empty side of the excluded slot does not receive a loss label
(section 5.4.4).

**Variant — pair with an ambiguous slot.** The Genes table lists
all genes. Protein assessment groups them and explains what
cannot be settled. The Proposed curation table assigns the same
group identity to all members with a `Low` Identity-axis call and
a note explaining the ambiguity (typically: within-cluster
paralogue identity awaits curated phylogeny, logged to side
projects).

**Variant — pair with a syntenic-position loss.** Both rows from
section 5.4.2's sub-case appear in the Proposed curation table:
one for the candidate loss at the canonical syntenic position,
and one for the mis-located group member as a separate gene at
an unresolved locus.

### 5.6 Output document opening

Before any per-pair section, the curation document opens with two
short interpretive sections that tell the reader how to read the
claims that follow. Without these openers, a reader encountering
"candidate loss" or a relabelled NCBI gene name has no framework
for what the claim does and does not assert. With them, every
per-pair claim sits inside a stated standard of evidence.

The openers are not optional. They are the artefact-level
expression of the *bring clarity, maintain humility* principle
(section 4.4): a reader should never be made to infer the
hedging convention from context.

```markdown
## Standard of evidence — what "loss" and "absent" mean in this file

This curation operates on annotated inputs (RefSeq GFF and protein
FASTAs) and makes annotation-level claims. The strongest loss
claim it commits to is **candidate loss with annotation-level
evidence**: the gene is present at the syntenic locus in
zebrafish, the gene is present on the homeologous chromosome in
the same carp assembly, a search of the annotation in the
syntenic region returns no candidate member or family-adjacent
feature, and the syntenic block on the empty chromosome is
recognisable enough to support the absence claim.

That is supportive evidence for a real evolutionary loss. It is
not confirmation. Confirmed loss claims require sequence-level
work (tBLASTn against the unannotated genomic region, synteny
alignment) and are out of scope for this curation. Sequence-level
follow-up questions are logged to the project's side-projects
list.

Slots with no specific search are labelled **absent — no specific
search done**. This is the honest default. Slots are upgraded to
*candidate loss* only when the procedure in playbook section
5.4.2 has been worked through.

## Annotation principle for homeolog labelling

This curation treats **conserved syntenic position** as the
primary evidence for homeolog identity in the carp polyploid
genomes. When NCBI labels the A and B copies at the same
syntenic locus with different gene-family names, the divergent
label is most likely a sequence-similarity-based mis-call;
synteny-derived identity overrides automated naming by default.

The default is not absolute. Local tandem duplication with
differential within-cluster loss, gene conversion, chromosomal
rearrangement, assembly collapse, and lineage-specific change in
the zebrafish reference are situations where the synteny rule
needs supplementation. The exception cases are flagged inline
where they apply.

For every relabelled gene, the original NCBI annotation appears
in the per-pair Genes table and the Proposed-curation table's
"Current NCBI name" column. A reader can always map the
curation's calls back to the public annotation.
```

The exact wording can be adapted to the gene group being curated.
The substance — *what counts as a loss claim, what synteny is
allowed to override* — is the part that should not be diluted.
For verbatim model text, the caspase worked example carries
both openers at the top of
`examples/caspase_in_carp/example_identification/Cgib_caspase_curation.md`.

### 5.7 Summary section

After all per-pair sections, the curation document closes with a
summary that aggregates findings across pairs. The summary is
where cross-pair patterns become visible — copy-number
asymmetries between A and B subgenomes, candidate losses
clustered on one subgenome, recurring naming inconsistencies,
motif-variation distributions — and where the curator's final
sign-off lives.

```markdown
## Summary

### Gene count

<N> gene models across <P> homeolog pairs in <species>:

- <X> functional full-length genes
- <Y> pseudogenes / non-functional remnants
- <Z> assembly artefacts (excluded)
- <W> genuine paralogues at independent loci (where applicable)

### Empty slots — assessed (<count>)

This table is populated at the empty-slots deep dive (Checkpoint 3,
section 6.1); during per-pair work the slots are only flagged as
`absent — no specific search`. See the document-opening "Standard of
evidence" section for what these labels assert.

The Syntenic-block quality column carries the three-level call
from playbook section 5.4.2 (`clear` / `partial` / `essentially
absent`). The Interval sweep result column records what the
in-region annotation sweep found: `negative` (nothing
group-suggestive in the syntenic window), `pseudogene biotype`
(a `gene_biotype=pseudogene` feature at the expected position),
`LOW QUALITY PROTEIN` (a degraded protein model at the expected
position), or `absent protein model` (a LOC gene with a
family-adjacent description but no protein entry). The sweep
result determines which outcome label the slot carries: a
`negative` result supports `candidate loss (annotation-level)`;
any other result supports `candidate non-functional locus at
syntenic position (annotation-level)`. In a curation document,
the outcome label column may be shortened to `loss` /
`non-functional` for readability, since the standard-of-evidence
section at the document opening defines both.

| Missing gene | Chromosome | Outcome label | Syntenic-block quality | Interval sweep result | Shared with other species? |
|---|---|---|---|---|---|
| <gene> | <chr> | <loss / non-functional> | <clear/partial/essentially absent> | <negative / pseudogene biotype / LOW QUALITY PROTEIN / absent protein model> | <yes/no/needs check> |

### Motif / functional-feature variants

<Distribution of defining motif variants (or other group-specific
functional features) across the species. Useful for reference and
for spotting outliers — e.g. the Cgib A7 QSCRG variant in the
caspase worked example.>

### Synteny quality

<Brief commentary on which pairs showed the best synteny, any
notable rearrangements, any pre-hybridization inversions consistent across
the family. The "best synteny" call is a useful pointer for any
downstream phylogenetic or sequence-level work that wants to
start from the cleanest pairs.>

### Confidence summary

| Locus / Identity / Model triple | Count | Pairs |
|---------------------------------|-------|-------|
| H/H/H | <n> | <pair list> |
| H/M/H | <n> | <pair list> |
| H/L/H | <n> | <pair list> |
| Pseudogene | <n> | <pair list> |
| Artefact (excluded) | <n> | <pair list> |
| <other patterns as they arise> | | |
```

The confidence summary uses the three-axis triple from section
5.4.6. Rolling it up into a single legacy `High/Medium/Low`
column is possible but loses the most useful information — a
`H/L/H` pattern (confident in locus and model, ambiguous in
identity) reads quite differently from a `L/H/H` pattern (the
locus itself is in question), and the procedure has worked hard
to keep those distinguishable.

The summary section closes the curation document. The next step
is the empty-slots deep dive (Checkpoint 3, section 6.1), which
resolves the flagged empty slots and populates the table above,
followed by the review of the curation as a whole (Checkpoint 4,
section 6.2) before the visualization is built.

---

## 6. Building the visualization

The curation document is the reasoned, prose record of what was found. The hierarchy explorer is the navigable, visual form of the same information — organized by homeologous slot, with functional grouping layered on top. Both outputs are essential: without the curation document the visualization is ungrounded; without the visualization the curation document is just text.

This section describes the three conversations that happen before the visualization is built (Checkpoints 3, 4, and 5), and then the mechanics of building the explorer itself.

---

### 6.1 Checkpoint 3 — the empty-slots deep dive

*When:* After all per-pair sections are written, before the curation review (Checkpoint 4). The per-pair pass (section 5.4.2) only *flagged* each empty A or B side, recording it as `absent — no specific search`. This checkpoint is where those flags are resolved — with every pair curated, the full cross-species picture is available, and the curator is present.

*Why it matters:* An empty slot is the procedure's most interesting signal — a candidate loss. Per-pair work deliberately defers the assessment so it is not done piecemeal, slot by slot, in isolation from the cross-pair pattern and without the curator. If this pass is skipped, every empty slot stays at the honest default `absent — no specific search`, the loss signal is never examined, and the visualization silently understates what the annotation supports. This is the step most prone to being missed; the AI is responsible for not letting that happen.

*What to do — per flagged slot.* Apply the loss-assessment procedure documented in section 5.4.2 to each flagged slot: the in-region annotation sweep (biotype → description → protein-FASTA), the syntenic-block-quality call, outgroup retention (zebrafish), and homeolog retention (the other subgenome in the same assembly). Present the evidence for each slot to the curator and settle the outcome label together.

*Cross-species reasoning — what is always available vs optional.* Two distinct comparisons feed the call, and they must not be conflated:

- **Within the focal species, corroborated by the other carps (always available).** The empty slot belongs to the focal species chosen at Checkpoint 2. Ask first whether it is empty on *both* of the focal species' subgenomes or just one — a both-subgenome gap is a stronger, possibly pre-divergence loss, while a single empty side with the homeolog retained is a single-copy loss. Then corroborate against the other carp genomes in the repo: a slot empty in the focal species but retained in the other carps reads differently from one empty across multiple carp lineages. Zebrafish supplies the ancestral expectation. This reasoning needs no data beyond the genomes already in the repo.

- **Secondary diploid comparators (optional, conditional).** The cross-check against tiger barb / grass carp (section 4.2) exists only to test whether *zebrafish's* state is ancestral or zebrafish-lineage-specific. Engage it **only** when such an annotation is actually present — an entry in `data/genome_config.yaml` whose `assembly_name` is set and whose files have been downloaded. **In the default repository, zebrafish is the only diploid comparator.** When that is the case, do not attempt the secondary cross-check and do not treat its absence as a gap: proceed using zebrafish as the ancestral proxy, and record the standing section 4.2 caveat — a zebrafish-specific pattern cannot be excluded — as a hedge on the loss claim. The checkpoint must never stall waiting for comparators that are not in the repository.

*Outcome per slot.* Settle each flagged slot on one of the section 5.4.2 outcome labels — `candidate loss (annotation-level)`, `candidate non-functional locus at syntenic position (annotation-level)`, or a deliberate retention of `absent — no specific search`. The last is now a *decision*, not a default: a slot may end there only by explicit joint agreement that the sweep is not warranted, never by omission. If the sweep surfaces an explanation, update the curation accordingly: a missed functional gene is routed back into the inventory (a Checkpoint 2-style addition) before any loss claim is made; a pseudogene or degraded locus takes the non-functional label and a `[LOST]`/non-functional row is added to the pair's Genes table (section 5.5 variant); a sequence-level follow-up (e.g. tBLASTn confirmation) is logged to the side-projects list (section 8).

*Collaborative vs unattended.* In collaborative mode, walk the flagged slots one at a time and decide each together. In unattended mode the pass is **not** skipped — the AI runs the sweep for every flagged slot, drafts each outcome with a visible flag (e.g. **[EMPTY-SLOT REVIEW]**) and its supporting evidence, then presents the full set for the curator's sign-off. Only the interaction style changes, never whether the slots are assessed.

*Output:* Every flagged empty slot carries an explicit, evidence-backed outcome; the summary's "Empty slots — assessed" table (section 5.7) is populated from this pass; the side-projects list is updated with any sequence-level follow-ups. Record the outcome so it carries through to the explorer: a slot settled as a candidate loss must have its `A_loss`/`B_loss` set to `searched` when the curation JSON is built (section 6.4) — otherwise the explorer still shows it as `absent — no specific search`. Set this as part of writing the CP3 outcome, not as a separate later step, so the per-pair holding state and the CP3 result cannot drift (see `scripts/templates/CURATION_DATA_SCHEMA.md`).

*AI initiation.* If the curator moves toward the curation review (Checkpoint 4) or the visualization while flagged empty slots remain unresolved, the AI assistant initiates this checkpoint. It should list the flagged slots, work the sweep for each, and invite the curator to settle each call.

---

### 6.2 Checkpoint 4 — reviewing the curation before visualization

*When:* After the empty-slots deep dive (Checkpoint 3) is complete, before the hierarchy explorer is built.

*What to discuss:* Step back and look at the curation as a whole. Cross-pair inconsistencies that weren't visible from any single pair often surface here. The conversation should work through:

- **Cross-pair patterns.** Do any issues recur across multiple pairs — e.g. the same naming confusion appearing at several loci, or a confidence call that was made differently early vs late in the curation? If so, apply a consistent treatment across all affected pairs.
- **Identity calls that looked clean in isolation.** Are there pairs where the identity call was confident at the time but looks inconsistent relative to what was learned from later pairs? Revisit and adjust where needed.
- **Side-project items.** Review the accumulated list of deferred questions. Are they all genuinely logged? Is any of them actually resolvable at the annotation level — i.e. should it come back into the core curation rather than remain deferred?
- **Confidence calls.** Review the confidence triples across all pairs. Any that were assigned `Medium` on Axis 2 (identity) — is that still the right call in light of the full curation? Any `Low` on Axis 1 (locus) that subsequent pairs' synteny evidence might inform?
- **Wording consistency.** Loss claims, hedging language, and the standard-of-evidence qualifiers should be applied uniformly. Scan for any pair where the language is stronger or weaker than the evidence supports relative to the rest of the document.

*Why it matters:* The visualization is the output most likely to be shared with others. Inconsistencies at the curation level become inconsistencies in the published view. This is the last chance to catch them before they are locked into the visual form.

*Output:* A short list of adjustments to apply across the curation document — typically minor wording changes, confidence-call updates, and a confirmed and complete side-projects list. Apply the adjustments before proceeding to Checkpoint 5.

*AI initiation.* If the human curator does not initiate this review, the AI assistant should. Proceeding to visualization without this step is a documented failure mode. The AI should begin by summarizing the full set of pairs and confidence calls, flagging anything that looks inconsistent, and inviting the curator to weigh in on each flagged item.

---

### 6.3 Checkpoint 5 — designing the interpretive layer

*When:* After Checkpoint 4 adjustments are applied and the curation is locked down.

*What to discuss:* The hierarchy explorer's value comes partly from functional grouping that is not in the annotation — an interpretive layer that reflects the curator's domain knowledge about the gene group. This layer is designed in conversation, not inferred from the data.

The conversation should answer:

- **What functional groupings make sense for this gene group?** For caspases, the natural grouping is executioner / initiator / inflammatory — reflecting the biological role of each subfamily. For a different gene group the relevant grouping might be signalling pathway membership, structural class, receptor vs ligand vs inhibitor role, or pathway position. The right grouping comes from the curator's expertise and is family-specific.
- **What visual encoding should represent the groupings?** The explorer uses colour-coding by functional group. The curator should specify the groups and, optionally, preferred colours. If no preference is given, the AI will assign colours.
- **What should be visible at each level of the drill-down?** The explorer has five drill-down levels: functional group → homeolog pair → subgenome slot → gene → gene detail. The curator should indicate whether any genes or pairs should carry special labels or flags not captured in the confidence system.
- **Are there any pairs that should be highlighted or annotated?** For example, a pair with a particularly clean synteny story, or a pair with an unusually complex slot structure, might warrant a note visible from the pair-level view.

*Why it matters:* This is the layer that converts "list of genes organized by chromosome pair" into "navigable understanding of the gene family." Without it, the explorer is a prettier inventory. With it, it is an act of synthesis that the curator can defend and that a reader can learn from.

*Output:* A small specification — functional groups, colour scheme (or permission for the AI to assign), any pair-level annotations — that the AI uses as input when running `build_hierarchy_explorer.py`.

*AI initiation.* The AI should open this conversation by proposing a first-draft functional grouping based on the curation document, then asking the curator to confirm, adjust, or replace it. The AI should not build the visualization before this conversation has produced an agreed specification.

---

### 6.4 The hierarchy explorer

The hierarchy explorer is a self-contained HTML file that opens in any browser. It is built by `scripts/build_hierarchy_explorer.py` from two inputs: a curation-data JSON file (derived from the curation document) and the gene-set config. One explorer is built per focal species, from that species' curation (the `--species` argument below); curating several species produces several explorers, one each.

**What the explorer shows:**

The explorer organizes the curated inventory into five drill-down levels:

1. **Functional group** (top level) — the interpretive grouping designed at Checkpoint 5. Clicking a group expands it.
2. **Homeolog pair** — each pair shows the pair number, the ancestral gene identity, and a summary of what's on A and B (present / absent / pseudogene / ambiguous).
3. **Subgenome slot** — the A and B sides of each pair, with the gene count and overall confidence for that side.
4. **Gene** — each individual gene, with its NCBI ID, proposed identity, confidence triple, and any flags (NCBI override, pseudogene, artefact).
5. **Gene detail** — the full evidence record from the curation: protein length, active site, exon count, synteny quality, and the curator's reasoning for the identity call.

**How the curation feeds the explorer:**

The AI assistant, at the end of curation, derives a `curation_data.json` file from the completed curation document. This JSON encodes the slot structure, gene assignments, confidence calls, and functional grouping. The script reads this JSON, combines it with the gene-set config (for titles and colours), and renders the HTML using the template in `scripts/templates/hierarchy_explorer.html`.

The JSON schema is documented in `scripts/templates/CURATION_DATA_SCHEMA.md`.

**Reproducing the explorer:**

```bash
python scripts/build_hierarchy_explorer.py \
    --species <Species_name> \
    --curation-data results/<gene_set>/identification/<species>_<gene_set>_curation_data.json \
    --config config/<gene_set>.yaml
```

Output: `results/<gene_set>/explorers/<species_short>_<gene_set>_hierarchy.html`

---

### 6.5 Functional layers — worked example

The caspase explorer uses three functional groups: **Executioner**, **Initiator**, and **Inflammatory**. These reflect the canonical biological classification of caspases by their role in apoptosis and inflammation. The grouping is independent of the NCBI gene names — a gene annotated as `casp3` and a gene annotated as `casp7` at the same ambiguous tandem-cluster locus are both placed in the Executioner group, because the ambiguity is in their specific paralogue identity, not in their functional class.

This is the general principle: **functional grouping should be at a level of resolution the curation can support.** The executioner / initiator / inflammatory distinction is defensible from protein-level evidence (prodomain structure, substrate specificity) even when specific paralogue identity is uncertain. A grouping scheme that required knowing whether a gene is casp3 vs casp7 specifically would not be supportable for the ambiguous cluster slots.

For other gene groups, equivalent principles apply:

- A TLR family curation might use groupings based on subcellular localization (cell-surface TLRs vs endosomal TLRs) or by the PAMP they recognize — both are defensible from domain-level annotation.
- An MHC family curation might use Class I / Class II / Class III — a structural and functional distinction that holds regardless of specific allele identity.
- A cytokine family curation might use receptor-binding cluster membership, which is often derivable from sequence features even when specific paralogue naming is uncertain.

The Checkpoint 5 conversation is where the curator identifies the right grouping level for their gene family. The AI proposes; the curator confirms or adjusts.

---

## 7. For AI assistants — protocol and checkpoints

*[This section is written for the AI assistant. Human curators may skim it.]*

Section 7.2 below lists the six conduct rules that govern all AI contributions to this workflow. This section adds one further requirement: the AI is responsible for *initiating* the five conversational checkpoints if the human curator does not.

### 7.1 The five checkpoints and when to initiate them

| Checkpoint | When | AI initiation trigger |
|---|---|---|
| 1 — Directing the GFF search | Before Stage 2 extraction | If the human provides a gene group name and inputs without discussing search-term design, open the Checkpoint 1 conversation before running any script |
| 2 — Reviewing the inventory and choosing the focal species | After Stage 3c (the gene inventory is built; the homeolog-pair summary is part of it) | If the human asks to begin per-pair curation without reviewing the inventory as the baseline and explicitly choosing the focal species, pause and run Checkpoint 2 first — never default silently to the best-annotated genome |
| 3 — Empty-slots deep dive | After all per-pair sections complete, before the curation review | If the human moves toward the curation review or visualization while flagged empty slots remain unresolved, initiate the empty-slots deep dive |
| 4 — Reviewing the curation | After the empty-slots deep dive | If the human asks to build the visualization without a review pass, initiate Checkpoint 4 |
| 5 — Designing the interpretive layer | After Checkpoint 4 adjustments applied | If the human asks to run `build_hierarchy_explorer.py` without a functional-grouping conversation, initiate Checkpoint 5 |

Proceeding past a checkpoint without resolving it is a documented failure mode. The checkpoints exist because they are where the curator's domain expertise enters the work. Skipping them produces outputs that are technically complete but interpretively ungrounded.

### 7.2 Conduct within the curation

Beyond the checkpoints, the AI should:

- **Cite evidence for every claim.** If a proposed identity or confidence call cannot be traced to a specific protein feature, synteny observation, or cross-species comparison in the curation document, do not make the claim.
- **Never infer negative searches.** If a search was not performed, write "not assessed" — not "no evidence found" or "absent." A negative inference requires a documented search.
- **Use hedged language consistently.** Candidate losses are "candidate loss with annotation-level evidence." Ambiguous slots are "ambiguous — awaiting curated phylogeny." The standard of evidence section at the top of each curation document is the reference.
- **Preserve NCBI annotations.** When overriding an NCBI gene name, record the original NCBI annotation and the reason for the override explicitly. Do not silently substitute a different name.
- **Refer hard cases to side projects.** When a question requires sequence-level, alignment-level, or phylogenetic analysis to resolve, log it to the side-projects list rather than making an unsupported call.
- **Pace the curation.** At Checkpoint 2, agree on a sequencing plan. Work one or two homeolog pairs at a time. Moving through the full inventory in a single session produces a polished but un-interrogated document.
- **Carry the baton — never stop silently.** Every turn that completes work ends with an explicit hand-off: what was just produced, what the next action is, and whose turn it is. The AI does not finish a turn by trailing off after an output and waiting to be prodded. This is the same principle as the checkpoint-initiation rule (7.1), generalised to *every* transition, not just the five checkpoints. The operational form is the hand-off banner (section 7.3); the underlying rule is that a produced output is a baton to be passed, visibly, not set down.
- **Park tangents, don't chase them.** When the conversation drifts to a side topic, capture it in one line on the banner's **Parked** list, resolve or defer it, then return to the stated next action. A digression about an output must not become the silent end of the work.
- **A cluster is one slot.** A tandem cluster occupies a single slot (5.3.2). Within-cluster paralogue absence is asymmetric retention for the curator to decide (5.4.3), not an empty slot — do not give an individual missing within-cluster paralogue a Checkpoint 3 loss flag. Checkpoint 3 is for locus-level (whole-slot) absences.

### 7.3 Hand-off and session state

The workflow's hand-off surface is the progress-and-hand-off banner
defined in `docs/quick_start.md`. It exists to defeat the most common
real-run failure mode: after an output lands — especially when it is
followed by a tangent — the next step gets lost, the researcher cannot
tell a key output was produced, and (with a neutral agent whose
chain-of-thought buries the moment) neither party knows it is the
researcher's turn to say "continue."

The banner answers that in a fixed shape: a position checklist plus
four hand-off lines — *just produced*, *next*, *whose turn*, and
*parked*. The AI shows it at every output and every stage or checkpoint
boundary, not only at the checkpoints. The whose-turn line is never
omitted: either an explicit "your move — say X" or "I'll continue —
say pause," so a produced output is always an explicitly passed baton.

For continuity across sittings, the AI mirrors the latest banner to
`results/SESSION_STATUS.md` (a gitignored scratch file, not part of
the deliverable) and reads it first when resuming. That file records
only position and the pending hand-off; the curation document remains
the authority for everything substantive, so the mirror cannot drift
into a competing source of truth.

---

## 8. Out of scope and side projects

The core workflow produces annotation-level findings — findings that can be supported from GFF and protein FASTA inputs alone. Some questions are genuine and important but require more than these inputs can support. Those questions go on a side-projects list rather than into the curation document.

### 8.1 Defer to side projects

| Question | Why deferred | Method needed |
|---|---|---|
| Is this candidate gene loss a confirmed evolutionary loss? | Requires sequence-level verification | tBLASTn against the unannotated genomic region using outgroup and homeolog proteins as queries; sequence-level syntenic alignment |
| What is the specific identity within an ambiguous tandem cluster? | Requires phylogenetic analysis | Manually-curated alignment with broader outgroup sampling; post-curation homeolog identities as inputs |
| Is this near-identical gene pair a real tandem duplication or an assembly haplotig? | Requires comparison against alternative assemblies | Align candidate region against an alternative-strain assembly of the same species |
| What is the orphan gene at this anomalous chromosomal position? | Synteny is uninformative because flanking genes are unnamed LOC identifiers | Flanking-gene re-annotation, or properly-curated phylogeny |
| Did this deletion occur via TE insertion, microhomology, or NHEJ? | Requires alignment-level breakpoint analysis | Out of scope for annotation-level work |

### 8.2 Stop conditions

Stop curating a pair and log a side project when:

- The annotation-level evidence is insufficient to make a confident identity call and further work would require sequence-level analysis.
- The gene model is structurally suspect (very short, very long, anomalous transcript structure) and no reference from another species resolves it.
- Synteny is genuinely uninformative — flanking genes are largely uncharacterized across all species.
- A claim would require phylogenetic, alignment-level, or experimental evidence to support.

The side-projects list is not a failure — it is the intended output when the annotation-level inputs run out. Logging side projects is what keeps the core workflow honest and bounded, and what gives future collaborators a clear starting point for deeper work.

---

## 9. Updating this playbook

This playbook records what was learned from applying the workflow to the caspase gene family in the three Cs4R cyprinids. It will not be right in every detail for every gene group.

If you apply this playbook to a new gene group and find that:

- A pattern recurs that is not captured in the decision rules (section 5.4) or common patterns;
- A decision rule fails or produces the wrong outcome;
- A new exception emerges that the procedure does not handle;
- A checkpoint needs to happen at a different stage than described;
- The terminology or framing is wrong for your gene group or genome system;

**update the playbook.** Note the date, the gene group, and what prompted the change. The goal is for the playbook to accumulate the lessons of every application, not to remain frozen at the caspase version.

Updates to the governing principles (section 4) and decision rules (section 5.4) are the most consequential — they affect all future curations. Updates to the common patterns section are additive and lower-risk. When in doubt, add a dated note rather than rewriting, so the reasoning behind the change is preserved.

---
