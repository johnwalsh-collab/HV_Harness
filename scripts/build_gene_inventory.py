#!/usr/bin/env python3
"""
Build a comprehensive gene inventory with annotation confidence, gene
model quality flags (from NCBI's own annotation flags), assembly
artefact flags, and curation status columns.

Generic Stage 3c driver. All gene-family-specific behaviour (type
classification, confusion patterns, manual additions) is supplied by
the gene-set config. Chromosome → subgenome / homeolog-pair mapping is
derived from the genome config. Model-quality flags are read directly
from NCBI annotation signals (gene_biotype, partial, exception, and the
protein FASTA's LOW QUALITY PROTEIN prefix) — no length heuristics.

Usage:
    python build_gene_inventory.py [--config config/<gene_set>.yaml]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import (
    PROJECT_DIR,
    add_config_arg,
    add_unattended_arg,
    emit_banner,
    resolve_output_dirs,
    get_chr_info,
    iter_species,
    load_configs,
    find_annotation_file,
)


RESULTS_DIR = PROJECT_DIR / "results" / "identification"
ANNOTATIONS_DIR = PROJECT_DIR / "data" / "annotations"


# =============================================================================
# Helpers
# =============================================================================

def is_unplaced(accession: str) -> bool:
    return accession.startswith("NW_")


def classify_type(gene_name: str, description: str, type_rules: list) -> str:
    """Walk the config's type_rules in order; first matching rule wins.
    A rule matches if any of its `matches` strings appears (case-
    insensitive) in `<gene_name> <description>`. Returns 'unknown' if
    no rule matches."""
    haystack = f"{gene_name} {description}".lower()
    for rule in type_rules:
        for needle in rule.get("matches", []):
            if needle.lower() in haystack:
                return rule["type"]
    return "unknown"


def load_low_quality_proteins(species_name: str) -> tuple[set, bool]:
    """Return (set of protein accessions flagged 'LOW QUALITY PROTEIN:' in
    the species' RefSeq protein FASTA, file_found). NCBI applies that defline
    prefix to models it corrected for frameshifts or internal stops."""
    faa = find_annotation_file(species_name, "protein", ann_dir=ANNOTATIONS_DIR)
    if faa is None:
        return set(), False
    lq: set = set()
    opener = gzip.open if str(faa).endswith(".gz") else open
    with opener(faa, "rt") as fh:
        for line in fh:
            if line.startswith(">") and "LOW QUALITY PROTEIN:" in line:
                lq.add(line[1:].split()[0])
    return lq, True


def _parse_gff_attrs(attr_str: str) -> dict:
    attrs: dict[str, str] = {}
    for item in attr_str.split(";"):
        item = item.strip()
        if "=" in item:
            k, v = item.split("=", 1)
            attrs[k.strip()] = v.strip()
    return attrs


def cds_exon_counts(species_name: str, gene_ids: set) -> dict:
    """Per-isoform CDS-exon counts read mechanically from the GFF.

    Returns ``{gene_id: (repr_cds_exons, n_transcripts)}`` where
    ``repr_cds_exons`` is the number of CDS segments (coding exons) in the
    gene's *representative* transcript — the one with the longest total
    CDS — and ``n_transcripts`` is the number of distinct coding
    transcripts. Reporting the representative isoform (not the sum across
    all variants) is what playbook 5.3.3 calls for; summing inflates
    multi-isoform genes and makes clean homeolog pairs look asymmetric.

    Genes with no CDS (pseudogenes, unannotated, or manual additions not
    in the GFF) are simply absent from the result. Mirrors the
    Parent-chain walk in extract_sequences.get_protein_accessions_from_gff.
    """
    gff = find_annotation_file(species_name, "gff", ann_dir=ANNOTATIONS_DIR)
    if gff is None:
        return {}
    mrna_to_gene: dict[str, str] = {}
    tx_cds_count: dict[str, int] = defaultdict(int)
    tx_cds_len: dict[str, int] = defaultdict(int)

    opener = gzip.open if str(gff).endswith(".gz") else open
    with opener(gff, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            ftype = parts[2]
            if ftype in ("mRNA", "transcript"):
                attrs = _parse_gff_attrs(parts[8])
                mid = attrs.get("ID", "")
                parent = (attrs.get("Parent", "")
                          .replace("gene-", "").replace("gene:", ""))
                if mid and parent in gene_ids:
                    mrna_to_gene[mid] = parent
            elif ftype == "CDS":
                parent = _parse_gff_attrs(parts[8]).get("Parent", "")
                if parent in mrna_to_gene:
                    try:
                        seglen = int(parts[4]) - int(parts[3]) + 1
                    except ValueError:
                        seglen = 0
                    tx_cds_count[parent] += 1
                    tx_cds_len[parent] += seglen

    gene_tx: dict[str, list] = defaultdict(list)
    for mid, gid in mrna_to_gene.items():
        if tx_cds_count[mid] > 0:
            gene_tx[gid].append((tx_cds_len[mid], tx_cds_count[mid]))

    out: dict[str, tuple[int, int]] = {}
    for gid, txs in gene_tx.items():
        txs.sort(reverse=True)            # longest total CDS first
        out[gid] = (txs[0][1], len(txs))  # representative exon count, #variants
    return out


def assess_confidence(gene_name: str, gene_type: str, h_num: int | None,
                      subgenome: str, confusion_pairs: dict) -> tuple[str, str]:
    """Assign an *identity*-confidence level (high/medium/low) and a short
    reason. This axis is about how sure we are of the gene's identity; model
    quality is a separate axis (see assess_model_quality). Confusion-pair
    behaviour is supplied by the config."""
    reasons: list[str] = []
    confidence = "high"
    is_loc = gene_name.startswith("LOC")

    # Confusion-pair rules from config. Each entry's `confidence_effect`
    # (low | medium | none) drives the behaviour, not the entry's key
    # name — so any gene set can define its own confusion categories
    # without this script knowing their names.
    low_effect_pairs: set = set()
    for kind, spec in (confusion_pairs or {}).items():
        if not spec:
            continue
        pairs = spec.get("pairs") or []
        types = spec.get("affected_types") or []
        reason = spec.get("reason", "")
        effect = (spec.get("confidence_effect") or "none").lower()
        if effect == "low":
            low_effect_pairs.update(pairs)
        if h_num in pairs and gene_type in types:
            if effect == "low":
                confidence = "low"
            elif effect == "medium" and confidence != "low":
                confidence = "medium"
            # effect == "none": a legitimate divergence (e.g.
            # subfunctionalization) — records a reason but does not
            # lower confidence.
            if reason:
                reasons.append(reason)

    if is_loc:
        if confidence == "high":
            confidence = "medium"
        reasons.append("LOC identifier (automated annotation, no curated gene symbol)")

    # Only a `low` confidence_effect blocks the "named gene at expected
    # locus → high" upgrade. medium / none entries record a reason but
    # don't prevent confidence being restored to high for cleanly-named
    # genes.
    if not is_loc and h_num not in low_effect_pairs:
        if confidence != "low":
            confidence = "high"
        if not reasons:
            reasons.append("named gene with consistent annotation")

    if not reasons:
        reasons.append("no specific concerns")
    return confidence, "; ".join(reasons)


def assess_model_quality(gene_biotype: str, feature_type: str, partial: str,
                         exception: str, low_quality: bool) -> tuple[str, str]:
    """Gene-model status taken from NCBI's own annotation flags — no length
    heuristics. Returns (status, notes). Precedence, most decisive first:
    pseudogene → partial → low-quality protein → other annotation exception
    → ok."""
    if feature_type == "pseudogene" or "pseudogene" in (gene_biotype or "").lower():
        return "pseudogene", f"NCBI gene_biotype={gene_biotype or 'pseudogene'} (non-functional copy)"
    if partial:
        return "partial", "NCBI partial=true (model incomplete / runs off a contig end)"
    if low_quality:
        return "low_quality", "NCBI 'LOW QUALITY PROTEIN' (frameshift/internal-stop correction)"
    if exception:
        return "flagged", f"NCBI exception: {exception}"
    return "ok", ""


def assess_assembly_artefacts(acc: str) -> tuple[str, str, str]:
    # Placed/unplaced redundancy (a gene annotated on both a chromosome and an
    # unplaced scaffold) is removed upstream in the dedup step, so any unplaced
    # gene reaching here has no placed counterpart. possible_haplotig is kept
    # (always "no") for output-column stability.
    on_unplaced = "yes" if is_unplaced(acc) else "no"
    notes = ["gene on unplaced scaffold"] if is_unplaced(acc) else []
    return on_unplaced, "no", "; ".join(notes)


OUTPUT_COLUMNS = [
    "species", "gene_id", "ncbi_annotation_name", "ncbi_gene_id",
    "chromosome_accession", "chromosome_label", "subgenome",
    "homeolog_pair",
    "start", "end", "strand", "gene_length_bp",
    "cds_exons", "transcript_variants", "description",
    "gene_biotype",
    "annotation_confidence", "confidence_reasons",
    "model_status", "model_quality_notes",
    "on_unplaced_scaffold", "possible_haplotig", "assembly_artefact_notes",
    "curation_status", "proposed_identity", "curation_notes",
    "reviewed_by", "review_date",
]


def dedup_by_geneid(genes: list) -> tuple[list, int]:
    """Collapse rows that share an ncbi_gene_id — they are the same NCBI
    gene, never two genes. Keep one row per (species, ncbi_gene_id),
    preferring a placed chromosome over an unplaced scaffold, and a
    pattern-found row over a manual addition. This removes both
    placed/unplaced assembly redundancy and a manual addition that
    duplicates a gene the inclusion patterns already find. Rows with no
    ncbi_gene_id are kept as-is. Returns (deduped_genes, n_dropped)."""
    def rank(g: dict) -> tuple:
        placed = 0 if not is_unplaced(g.get("chromosome", "")) else 1
        manual = 1 if g.get("match_reason") == "manual_addition" else 0
        return (placed, manual)  # lower is better; best sorts first

    by_gene: dict = defaultdict(list)
    kept: list = []
    for g in genes:
        gid = g.get("ncbi_gene_id", "")
        if gid:
            by_gene[(g.get("species", ""), gid)].append(g)
        else:
            kept.append(g)
    dropped = 0
    for group in by_gene.values():
        group.sort(key=rank)
        kept.append(group[0])
        dropped += len(group) - 1
    return kept, dropped


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    global RESULTS_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_arg(parser)
    add_unattended_arg(parser)
    args = parser.parse_args()

    gs_cfg, genome_cfg, chr_map = load_configs(args.config)
    gene_set = gs_cfg["gene_set"]["name"]

    dirs = resolve_output_dirs(args.output_dir, gene_set)
    RESULTS_DIR = dirs["identification"]
    cls = gs_cfg.get("classification", {})
    inv = gs_cfg.get("inventory", {})
    type_rules = cls.get("type_rules", []) or []
    confusion_pairs = cls.get("confusion_pairs", {}) or {}
    manual_additions = inv.get("manual_additions", []) or []

    # Note: subgenome-lookup presence/validity (for from_lookup_file
    # species like goldfish) is now checked loudly in
    # _config.derive_chromosome_mappings when the config is loaded above,
    # so no separate warning is needed here.

    species_order = {s["full_name"]: i for i, s in enumerate(genome_cfg["species"])}

    # Read the raw per-species gene list. Placed/unplaced redundancy is
    # resolved in-code below (see the dedup step), so this script no longer
    # depends on an externally-produced *_dedup.tsv file.
    input_path = RESULTS_DIR / f"{gene_set}_genes_all_species.tsv"
    output_path = RESULTS_DIR / f"{gene_set}_gene_inventory.tsv"

    print(f"Reading from: {input_path}", file=sys.stderr)

    genes: list[dict] = []
    with open(input_path) as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            genes.append(row)

    # Apply manual additions from config
    for ma in manual_additions:
        genes.append({
            "species": ma["species"],
            "gene_id": ma["gene_id"],
            "gene_name": ma["gene_name"],
            "chromosome": ma["chromosome"],
            "start": ma.get("start", ""),
            "end": ma.get("end", ""),
            "strand": ma.get("strand", ""),
            "description": ma.get("description") or ma.get("reason", ""),
            "ncbi_gene_id": ma.get("ncbi_gene_id", ma["gene_id"].replace("LOC", "")),
            "match_reason": "manual_addition",
        })

    print(f"Read {len(genes)} genes (incl. {len(manual_additions)} manual additions)", file=sys.stderr)

    genes, n_dropped = dedup_by_geneid(genes)
    if n_dropped:
        print(f"Deduplicated {n_dropped} duplicate row(s) by ncbi_gene_id "
              f"(placed > unplaced; pattern-found > manual addition)",
              file=sys.stderr)

    # Pre-scan each species' protein FASTA once for NCBI 'LOW QUALITY
    # PROTEIN' flags (keyed by protein accession).
    low_quality_by_species: dict[str, set] = {}
    fasta_missing: list[str] = []
    for sp in sorted({g["species"] for g in genes}):
        lq, present = load_low_quality_proteins(sp)
        low_quality_by_species[sp] = lq
        if not present:
            fasta_missing.append(sp)
    if fasta_missing:
        print(f"\nNOTE: protein FASTA not found for {fasta_missing}; the "
              f"'low_quality' model flag is unavailable for those species.",
              file=sys.stderr)

    # Per-isoform CDS-exon counts, read mechanically from each species'
    # GFF (one scan per species), keyed by gene_id.
    exon_counts_by_species: dict[str, dict] = {}
    for sp in sorted({g["species"] for g in genes}):
        sp_gene_ids = {g["gene_id"] for g in genes
                       if g["species"] == sp and g.get("gene_id")}
        exon_counts_by_species[sp] = cds_exon_counts(sp, sp_gene_ids)

    rows: list[dict] = []
    for g in genes:
        species = g["species"]
        gene_name = g["gene_name"]
        acc = g["chromosome"]
        description = g.get("description", "")
        chr_label, subgenome, h_num = get_chr_info(species, acc, chr_map)

        # Unplaced scaffolds (NW_ accessions) without an explicit
        # override entry: label as "unplaced" rather than echoing the
        # accession back.
        if subgenome == "unknown" and is_unplaced(acc):
            chr_label = "unplaced"
            h_num = None

        # Diploid secondaries without explicit chromosome mappings
        if subgenome == "unknown" and species in (
            "Puntigrus_tetrazona", "Ctenopharyngodon_idella"
        ):
            subgenome = "diploid"
            chr_label = acc

        try:
            start = int(g["start"])
            end = int(g["end"])
            gene_length = end - start + 1
        except (ValueError, TypeError, KeyError):
            start = g.get("start", "")
            end = g.get("end", "")
            gene_length = 0

        gene_type = classify_type(gene_name, description, type_rules)
        confidence, conf_reasons = assess_confidence(
            gene_name, gene_type, h_num, subgenome, confusion_pairs)

        # NCBI annotation-level quality signals (from the gene list + FASTA).
        gene_biotype = g.get("gene_biotype", "")
        feature_type = g.get("feature_type", "gene")
        partial = g.get("partial", "")
        exception = g.get("exception", "")
        protein_ids = [p for p in g.get("protein_id", "").split(";") if p]
        low_quality = any(p in low_quality_by_species.get(species, set())
                          for p in protein_ids)
        model_status, model_notes = assess_model_quality(
            gene_biotype, feature_type, partial, exception, low_quality)
        on_unplaced, haplotig, artefact_notes = assess_assembly_artefacts(acc)

        ec = exon_counts_by_species.get(species, {}).get(g.get("gene_id", ""))
        cds_exons = ec[0] if ec else ""
        transcript_variants = ec[1] if ec else ""

        rows.append({
            "species": species,
            "gene_id": g.get("gene_id", ""),
            "ncbi_annotation_name": gene_name,
            "ncbi_gene_id": g.get("ncbi_gene_id", ""),
            "chromosome_accession": acc,
            "chromosome_label": chr_label,
            "subgenome": subgenome,
            "homeolog_pair": str(h_num) if h_num is not None else "",
            "start": start,
            "end": end,
            "strand": g.get("strand", ""),
            "gene_length_bp": gene_length if gene_length > 0 else "",
            "cds_exons": cds_exons,
            "transcript_variants": transcript_variants,
            "description": description,
            "gene_biotype": gene_biotype,
            "annotation_confidence": confidence,
            "confidence_reasons": conf_reasons,
            "model_status": model_status,
            "model_quality_notes": model_notes,
            "on_unplaced_scaffold": on_unplaced,
            "possible_haplotig": haplotig,
            "assembly_artefact_notes": artefact_notes,
            "curation_status": "unreviewed",
            "proposed_identity": "",
            "curation_notes": "",
            "reviewed_by": "",
            "review_date": "",
        })

    subgenome_order = {"diploid": 0, "A": 1, "B": 2, "unplaced": 3, "unknown": 4}

    def sort_key(r):
        sp = species_order.get(r["species"], 99)
        sg = subgenome_order.get(r["subgenome"], 99)
        hp = int(r["homeolog_pair"]) if r["homeolog_pair"] else 99
        try:
            pos = int(r["start"])
        except (ValueError, TypeError):
            pos = 0
        return (sp, sg, hp, pos)

    rows.sort(key=sort_key)

    unknown_count = sum(1 for r in rows if r["subgenome"] == "unknown")
    if unknown_count:
        print(
            f"\nWARNING: {unknown_count} gene(s) have subgenome=unknown in the inventory. "
            f"Check that Stage 3a has been run for any species using a lookup file.",
            file=sys.stderr,
        )

    with open(output_path, "w", newline="") as out:
        out.write(f"# {gs_cfg['gene_set'].get('display_name', gene_set)} gene inventory\n")
        out.write(f"# Source: {input_path.name}\n")
        out.write(f"# Config: {gs_cfg['__path__']}\n")
        out.write("#\n")
        out.write("# COLUMN GROUPS:\n")
        out.write("#   Cols 1-16:  Core identity + structure (incl. NCBI gene_biotype,\n")
        out.write("#               cds_exons = representative-isoform CDS-exon count,\n")
        out.write("#               transcript_variants = # coding transcripts)\n")
        out.write("#   Cols 17-18: Annotation confidence (identity)\n")
        out.write("#   Cols 19-20: Gene model quality (from NCBI annotation flags)\n")
        out.write("#   Cols 21-23: Assembly artefact flags\n")
        out.write("#   Cols 24-28: Curation status (fill during manual review)\n")
        out.write("#\n")
        out.write("# CDS_EXONS: coding-exon count of the longest isoform (per isoform, not summed across variants)\n")
        out.write("# CONFIDENCE (identity): high (named, consistent) / medium (LOC or minor identity issue) / low (known confusion locus)\n")
        out.write("# MODEL STATUS (NCBI flags): ok / pseudogene / partial / low_quality / flagged (exception)\n")
        out.write("# CURATION: unreviewed / in_progress / reviewed / flagged\n")
        out.write("#\n")
        writer = csv.DictWriter(out, fieldnames=OUTPUT_COLUMNS, delimiter="\t",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nInventory written to: {output_path}", file=sys.stderr)
    print(f"Total genes: {len(rows)}", file=sys.stderr)

    by_conf = defaultdict(int)
    by_model = defaultdict(int)
    by_species = defaultdict(int)
    for r in rows:
        by_conf[r["annotation_confidence"]] += 1
        by_model[r["model_status"]] += 1
        by_species[r["species"]] += 1
    print("\nBy species:", file=sys.stderr)
    for sp in sorted(by_species, key=lambda x: species_order.get(x, 99)):
        print(f"  {sp}: {by_species[sp]}", file=sys.stderr)
    print("\nAnnotation confidence:", file=sys.stderr)
    for level in ["high", "medium", "low"]:
        print(f"  {level}: {by_conf[level]}", file=sys.stderr)
    print("\nModel status (NCBI flags):", file=sys.stderr)
    for status in ["ok", "pseudogene", "partial", "low_quality", "flagged"]:
        print(f"  {status}: {by_model[status]}", file=sys.stderr)

    # CP2 is a checkpoint: the curator reviews the inventory baseline and
    # names the focal species before per-pair curation. The gate prints
    # regardless of --unattended (batch mode is local to per-pair work).
    emit_banner(
        current=3,
        produced=str(output_path),
        next_action="Review the inventory baseline (counts, coverage, quality "
                    "flags), choose the focal species, then extract synteny.",
        output_dir=args.output_dir,
        your_move="confirm the inventory and name the focal species to curate",
        gates=["CP2"],
    )


if __name__ == "__main__":
    main()
