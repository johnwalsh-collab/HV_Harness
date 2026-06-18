#!/usr/bin/env python3
"""Fixture-based tests for the gene-inventory pipeline.

Locks the invariants the inventory trades on, against tiny in-memory
fixtures (no network, no real genome data):

  - OUTPUT_COLUMNS — the inventory column schema (order + count)
  - extract_from_gff — pseudogenes are captured (distinct feature type)
    and the NCBI QC signals (gene_biotype, partial, protein_id) come through
  - assess_model_quality — NCBI-flag precedence, no length heuristics
  - dedup_by_geneid — one row per (species, ncbi_gene_id); placed beats
    unplaced; a pattern-found row beats a manual addition (the regression
    that inflated the caspase count by one)
  - load_low_quality_proteins — the LOW QUALITY PROTEIN defline lookup

Run standalone (no pytest required):
    python tests/test_inventory.py        # exit 0 = all pass
It is also pytest-discoverable (test_* functions).
"""

import gzip
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import identify_gene_set as ig          # noqa: E402
import build_gene_inventory as bgi      # noqa: E402


def _write(path, lines):
    Path(path).write_text("\n".join(lines) + "\n")


def _gff_row(ftype, start, end, attrs, seqid="NC_1", strand="+", phase="."):
    return "\t".join([seqid, "Gnomon", ftype, str(start), str(end),
                      ".", strand, phase, attrs])


FIXTURE_GFF = [
    # normal protein-coding gene (gene + mRNA + CDS)
    _gff_row("gene", 100, 2000,
             "ID=gene-LOCN;Dbxref=GeneID:111;Name=LOCN;description=widget protein;gene_biotype=protein_coding"),
    _gff_row("mRNA", 100, 2000,
             "ID=rna-r1;Parent=gene-LOCN;Dbxref=GeneID:111;product=widget protein"),
    _gff_row("CDS", 100, 2000,
             "ID=cds-XP_1;Parent=rna-r1;Dbxref=GeneID:111,GenBank:XP_1;Name=XP_1;product=widget protein;protein_id=XP_1", phase="0"),
    # pseudogene (distinct feature type, exon-only children) — must be captured
    _gff_row("pseudogene", 3000, 4000,
             "ID=gene-LOCP;Dbxref=GeneID:222;Name=LOCP;description=widget protein;gene_biotype=pseudogene;pseudo=true", strand="-"),
    _gff_row("exon", 3000, 3500,
             "ID=id-LOCP;Parent=gene-LOCP;Dbxref=GeneID:222;pseudo=true", strand="-"),
    # partial protein-coding gene (partial flag on the gene feature)
    _gff_row("gene", 5000, 6000,
             "ID=gene-LOCQ;Dbxref=GeneID:333;Name=LOCQ;description=widget protein;gene_biotype=protein_coding;partial=true;start_range=.,5000"),
    _gff_row("CDS", 5000, 6000,
             "ID=cds-XP_3;Parent=rna-r3;Dbxref=GeneID:333,GenBank:XP_3;Name=XP_3;partial=true;protein_id=XP_3", phase="0"),
]


def test_output_columns_schema():
    expected = [
        "species", "gene_id", "ncbi_annotation_name", "ncbi_gene_id",
        "chromosome_accession", "chromosome_label", "subgenome", "homeolog_pair",
        "start", "end", "strand", "gene_length_bp",
        "cds_exons", "transcript_variants", "description", "gene_biotype",
        "annotation_confidence", "confidence_reasons", "model_status", "model_quality_notes",
        "on_unplaced_scaffold", "possible_haplotig", "assembly_artefact_notes",
        "curation_status", "proposed_identity", "curation_notes", "reviewed_by", "review_date",
    ]
    assert bgi.OUTPUT_COLUMNS == expected, bgi.OUTPUT_COLUMNS
    assert len(bgi.OUTPUT_COLUMNS) == 28


def test_cds_exons_per_isoform():
    # Gene with two isoforms: a 2-exon short variant and a 3-exon long
    # variant. The representative (longest-CDS) count must be 3, and the
    # transcript-variant count 2 — NOT the 5 a naive sum would give.
    gff_lines = [
        _gff_row("gene", 100, 4000,
                 "ID=gene-LOCM;Dbxref=GeneID:9;Name=LOCM;gene_biotype=protein_coding"),
        # long isoform: 3 CDS segments, total 600 bp
        _gff_row("mRNA", 100, 4000, "ID=rna-long;Parent=gene-LOCM"),
        _gff_row("CDS", 100, 300, "ID=c1;Parent=rna-long;protein_id=XP_L", phase="0"),
        _gff_row("CDS", 1000, 1200, "ID=c2;Parent=rna-long;protein_id=XP_L", phase="0"),
        _gff_row("CDS", 3800, 3999, "ID=c3;Parent=rna-long;protein_id=XP_L", phase="0"),
        # short isoform: 2 CDS segments, total 200 bp
        _gff_row("mRNA", 100, 1300, "ID=rna-short;Parent=gene-LOCM"),
        _gff_row("CDS", 100, 200, "ID=d1;Parent=rna-short;protein_id=XP_S", phase="0"),
        _gff_row("CDS", 1200, 1299, "ID=d2;Parent=rna-short;protein_id=XP_S", phase="0"),
    ]
    with tempfile.TemporaryDirectory() as d:
        ann = Path(d) / "Sp"
        ann.mkdir()
        with gzip.open(ann / "Sp_genomic.gff.gz", "wt") as fh:
            fh.write("\n".join(gff_lines) + "\n")
        old = bgi.ANNOTATIONS_DIR
        bgi.ANNOTATIONS_DIR = Path(d)
        try:
            counts = bgi.cds_exon_counts("Sp", {"LOCM"})
        finally:
            bgi.ANNOTATIONS_DIR = old
    assert counts["LOCM"] == (3, 2), counts


def test_extract_captures_pseudogene_and_qc():
    with tempfile.TemporaryDirectory() as d:
        gff = Path(d) / "mini.gff"
        _write(gff, FIXTURE_GFF)
        matcher = ig.GeneSetMatcher({"inclusion": {"description_keywords": ["widget"]}})
        rows = {r["gene_id"]: r for r in ig.extract_from_gff(str(gff), "Sp", matcher)}
    assert set(rows) == {"LOCN", "LOCP", "LOCQ"}, set(rows)
    # the pseudogene was captured, not silently dropped
    assert rows["LOCP"]["feature_type"] == "pseudogene"
    assert rows["LOCP"]["gene_biotype"] == "pseudogene"
    # protein accession threaded through for the FASTA lookup
    assert rows["LOCN"]["protein_id"] == "XP_1"
    # partial flag read from the gene feature
    assert rows["LOCQ"]["partial"] == "true"


def test_model_quality_precedence():
    amq = bgi.assess_model_quality
    assert amq("pseudogene", "pseudogene", "", "", False)[0] == "pseudogene"
    assert amq("protein_coding", "gene", "true", "", False)[0] == "partial"
    assert amq("protein_coding", "gene", "", "", True)[0] == "low_quality"
    assert amq("protein_coding", "gene", "", "unclassified discrepancy", False)[0] == "flagged"
    assert amq("protein_coding", "gene", "", "", False)[0] == "ok"
    # pseudogene takes precedence over every other flag
    assert amq("pseudogene", "pseudogene", "true", "x", True)[0] == "pseudogene"


def test_dedup_by_geneid():
    genes = [
        {"species": "Sp", "ncbi_gene_id": "1", "chromosome": "NC_1", "match_reason": "name match"},
        {"species": "Sp", "ncbi_gene_id": "1", "chromosome": "NW_9", "match_reason": "name match"},        # unplaced dup -> drop
        {"species": "Sp", "ncbi_gene_id": "2", "chromosome": "NC_1", "match_reason": "manual_addition"},   # manual placed
        {"species": "Sp", "ncbi_gene_id": "2", "chromosome": "NC_1", "match_reason": "description match"}, # found placed -> keep
        {"species": "Sp", "ncbi_gene_id": "3", "chromosome": "NW_9", "match_reason": "name match"},        # unplaced only -> keep
    ]
    kept, dropped = bgi.dedup_by_geneid(genes)
    assert dropped == 2, dropped
    by = {g["ncbi_gene_id"]: g for g in kept}
    assert by["1"]["chromosome"] == "NC_1"                  # placed beats unplaced
    assert by["2"]["match_reason"] == "description match"   # pattern-found beats manual addition
    assert by["3"]["chromosome"] == "NW_9"                  # unplaced-only retained
    assert len(kept) == 3


def test_low_quality_lookup():
    with tempfile.TemporaryDirectory() as d:
        sp_dir = Path(d) / "Sp"
        sp_dir.mkdir()
        with gzip.open(sp_dir / "Sp_protein.faa.gz", "wt") as fh:
            fh.write(">XP_1 widget protein [Sp]\nMAAA\n")
            fh.write(">XP_2 LOW QUALITY PROTEIN: widget protein [Sp]\nMBBB\n")
        old = bgi.ANNOTATIONS_DIR
        bgi.ANNOTATIONS_DIR = Path(d)
        try:
            lq, present = bgi.load_low_quality_proteins("Sp")
        finally:
            bgi.ANNOTATIONS_DIR = old
    assert present is True
    assert lq == {"XP_2"}, lq
    # a species with no FASTA degrades gracefully (no crash, flag unavailable)
    lq2, present2 = bgi.load_low_quality_proteins("NoSuchSpecies_zzz")
    assert present2 is False and lq2 == set()


def _run():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run())
