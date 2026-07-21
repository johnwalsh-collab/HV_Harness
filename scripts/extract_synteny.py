#!/usr/bin/env python3
"""
Extract syntenic neighbourhoods around each gene-set member.

For each species in the genome config and each chromosome that carries
a gene-set member, this script gathers the N flanking genes on each
side of every cluster of members (gene-set members within
`max_gap_bp` of each other are merged into one cluster) and writes a
plain-text section per (species, homeolog_pair, subgenome) for use
in Stage 3e per-pair curation.

The section format follows the column layout the per-pair curation
reads (Stage 3e):

    === <pair_tag>_<species_short> (<N> genes) ===
            <start>       <end> <strand> <gene_name>     <description>
            ...

Generic Stage 3d driver. The gene set comes from the gene-set config
(via the inventory + identification rules); flanking-gene window
sizes come from `inventory.synteny` in the same config (with sensible
defaults).

Usage:
    python extract_synteny.py [--config config/<gene_set>.yaml]

Output:
    results/<gene_set>/identification/<gene_set>_synteny_extraction_all_pairs.txt
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


ANNOTATIONS_DIR = PROJECT_DIR / "data" / "annotations"
RESULTS_DIR = PROJECT_DIR / "results" / "identification"


# ---------------------------------------------------------------------------
# GFF parsing
# ---------------------------------------------------------------------------

def parse_attributes(attr_string: str) -> dict:
    out = {}
    for item in attr_string.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            out[k] = v.replace("%2C", ",").replace("%3B", ";").replace("%25", "%")
    return out


def gene_records_from_gff(gff_path: Path) -> dict[str, list[dict]]:
    """Return {chromosome_accession: [gene_record, ...]} from a species GFF.
    Each gene_record has: start, end, strand, name, description."""
    by_chr: dict[str, list[dict]] = defaultdict(list)
    # Capture product/description for genes whose own line carries none
    parent_products: dict[str, str] = {}

    opener = gzip.open if str(gff_path).endswith(".gz") else open
    with opener(gff_path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9:
                continue
            seqid, _, ftype, start, end, _, strand, _, attrs_str = fields
            attrs = parse_attributes(attrs_str)

            if ftype == "gene":
                name = attrs.get("Name", attrs.get("gene", ""))
                description = attrs.get("description", "")
                by_chr[seqid].append({
                    "gene_id": attrs.get("ID", ""),
                    "start": int(start),
                    "end": int(end),
                    "strand": strand,
                    "name": name,
                    "description": description,
                })
            elif ftype in ("mRNA", "CDS"):
                # First product seen per parent
                parent = attrs.get("Parent", "")
                product = attrs.get("product", "")
                if parent and product and parent not in parent_products:
                    parent_products[parent] = product

    # Backfill gene descriptions from mRNA/CDS product fields where empty
    for chrom, genes in by_chr.items():
        for g in genes:
            if not g["description"]:
                g["description"] = parent_products.get(g["gene_id"], "")
        genes.sort(key=lambda g: g["start"])

    return by_chr


# ---------------------------------------------------------------------------
# Cluster + window helpers
# ---------------------------------------------------------------------------

def cluster_members(member_positions: list[tuple[int, int]],
                    max_gap_bp: int) -> list[tuple[int, int]]:
    """Merge members closer than max_gap_bp into a single cluster.
    Returns list of (cluster_start, cluster_end) intervals."""
    if not member_positions:
        return []
    sorted_pos = sorted(member_positions)
    clusters = [list(sorted_pos[0])]
    for s, e in sorted_pos[1:]:
        last_s, last_e = clusters[-1]
        if s - last_e <= max_gap_bp:
            clusters[-1][1] = max(last_e, e)
        else:
            clusters.append([s, e])
    return [tuple(c) for c in clusters]


def window_around_cluster(genes: list[dict], cluster: tuple[int, int],
                          flanking_genes: int) -> list[dict]:
    """Return all genes that overlap the cluster span (gene start <=
    cluster end and gene end >= cluster start), plus `flanking_genes`
    immediately upstream and downstream of the cluster (by gene order on
    the chromosome)."""
    cs, ce = cluster
    # Indices (in the chromosome-wide list) of genes overlapping the cluster.
    overlapping = [i for i, g in enumerate(genes)
                   if g["start"] <= ce and g["end"] >= cs]
    if not overlapping:
        return []
    lo = max(0, min(overlapping) - flanking_genes)
    hi = min(len(genes), max(overlapping) + flanking_genes + 1)
    return genes[lo:hi]


# ---------------------------------------------------------------------------
# Section assembly
# ---------------------------------------------------------------------------

def format_section(tag: str, gene_list: list[dict]) -> str:
    """Format a section in the column layout the per-pair curation
    reads."""
    lines = [f"=== {tag} ({len(gene_list)} genes) ==="]
    for g in gene_list:
        # Truncate description to ~60 chars to match original style
        desc = g["description"][:60]
        lines.append(
            f"  {g['start']:>10} {g['end']:>12} {g['strand']} "
            f"{g['name']:<20} {desc}"
        )
    return "\n".join(lines)


def pair_tag(homeolog_pair: int, subgenome: str, chr_label: str,
             species_short: str, ploidy: str) -> str:
    """Build the section identifier.

    Tetraploid: P<pair>_<species_short>_<chr_label>
                (e.g. P10_Cgib_A10, P10_Caur_chr35)
    Diploid:    P<pair>_<short_alias>
                (e.g. P10_Zf, P10_Tb, P10_Gc)

    The species short is preserved so sections from different
    tetraploids covering the same homeolog pair don't collide.
    """
    if ploidy == "diploid":
        diploid_aliases = {"Drer": "Zf", "Ptet": "Tb", "Cide": "Gc"}
        short = diploid_aliases.get(species_short, species_short)
        return f"P{homeolog_pair}_{short}"
    return f"P{homeolog_pair}_{species_short}_{chr_label}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_arg(parser)
    parser.add_argument("--flanking-genes", type=int, default=None,
                        help="Flanking gene count on each side of a cluster "
                             "(default: from config or 12)")
    parser.add_argument("--max-gap-bp", type=int, default=None,
                        help="Merge members within this distance into one "
                             "cluster (default: from config or 500_000)")
    add_unattended_arg(parser)
    args = parser.parse_args()

    global RESULTS_DIR
    gs_cfg, genome_cfg, chr_map = load_configs(args.config)
    gene_set = gs_cfg["gene_set"]["name"]

    dirs = resolve_output_dirs(args.output_dir, gene_set)
    RESULTS_DIR = dirs["identification"]
    inv_cfg = gs_cfg.get("inventory", {}) or {}
    synteny_cfg = inv_cfg.get("synteny", {}) or {}
    flanking = args.flanking_genes or synteny_cfg.get("flanking_genes", 12)
    max_gap = args.max_gap_bp or synteny_cfg.get("max_gap_bp", 500_000)

    inventory_path = RESULTS_DIR / f"{gene_set}_gene_inventory.tsv"
    if not inventory_path.exists():
        sys.exit(f"Inventory not found at {inventory_path}; run build_gene_inventory.py first.")

    output_path = RESULTS_DIR / f"{gene_set}_synteny_extraction_all_pairs.txt"

    # Load the inventory to find member chromosomal positions
    with open(inventory_path) as fh:
        rows = list(csv.DictReader(
            (l for l in fh if not l.startswith("#")), delimiter="\t"))

    # {(species, accession): [(start, end), ...]} for member positions
    members_by_chrom: dict[tuple[str, str], list[tuple[int, int]]] = defaultdict(list)
    member_rows: list[dict] = []
    for r in rows:
        try:
            s, e = int(r["start"]), int(r["end"])
        except (ValueError, TypeError, KeyError):
            continue  # rows without coordinates can't anchor a window
        members_by_chrom[(r["species"], r["chromosome_accession"])].append((s, e))
        member_rows.append(r)

    sections: list[tuple[str, list[dict]]] = []

    # Sort species by homeolog_pair within each tetraploid for stable output
    species_by_name = {s["full_name"]: s for s in iter_species(genome_cfg)}

    # Group by (homeolog_pair, species, subgenome) so sections come out
    # ordered by pair across species, matching the original file's flow.
    by_pair: dict[int, list[tuple]] = defaultdict(list)
    skipped_accessions: dict[str, int] = defaultdict(int)
    for (species, acc), positions in members_by_chrom.items():
        chr_label, subgenome, h_num = get_chr_info(species, acc, chr_map)
        if h_num is None:
            skipped_accessions[species] += 1
            continue
        by_pair[h_num].append((species, acc, chr_label, subgenome, positions))

    # Report per-accession, not per-species: a species whose placed
    # chromosomes mapped fine can still have member loci on unplaced
    # scaffolds (no chromosome mapping). Those loci are omitted from
    # synteny, but the species itself is NOT dropped.
    for sp in sorted(skipped_accessions):
        sp_meta = species_by_name.get(sp, {})
        role = sp_meta.get("role", "unknown role")
        print(
            f"Note: {skipped_accessions[sp]} member-bearing accession(s) for "
            f"{sp} ({role}) had no chromosome-level mapping (e.g. unplaced "
            f"scaffolds) and were omitted from synteny; this species' mapped "
            f"chromosomes were still processed.",
            file=sys.stderr,
        )

    # Cache GFF parses per species
    gff_cache: dict[str, dict] = {}

    for h_num in sorted(by_pair):
        for species, acc, chr_label, subgenome, positions in by_pair[h_num]:
            if species not in gff_cache:
                gff_path = find_annotation_file(species, "gff", ann_dir=ANNOTATIONS_DIR)
                if gff_path is None:
                    print(f"warn: GFF missing for {species}, skipping", file=sys.stderr)
                    gff_cache[species] = {}
                    continue
                print(f"parsing {species} GFF...", file=sys.stderr)
                gff_cache[species] = gene_records_from_gff(gff_path)
            genes = gff_cache[species].get(acc, [])
            if not genes:
                continue

            clusters = cluster_members(positions, max_gap)
            sp_meta = species_by_name.get(species, {})
            short = sp_meta.get("short_code", species[:4])
            ploidy = sp_meta.get("ploidy", "tetraploid")
            for cs, ce in clusters:
                window = window_around_cluster(genes, (cs, ce), flanking)
                if not window:
                    continue
                # When a single chromosome has multiple clusters, append
                # a region marker so section tags stay unique.
                tag = pair_tag(h_num, subgenome, chr_label, short, ploidy)
                if sum(1 for c in clusters) > 1:
                    tag += f"_{cs}-{ce}"
                sections.append((tag, window))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as fh:
        fh.write(f"# Synteny extraction for the {gene_set} gene set\n")
        fh.write(f"# Source: {inventory_path.name}\n")
        fh.write(f"# Flanking genes per side: {flanking}; cluster merge gap: {max_gap} bp\n")
        fh.write(f"# Sections: {len(sections)}\n\n")
        for tag, gene_list in sections:
            fh.write(format_section(tag, gene_list))
            fh.write("\n\n")

    print(f"\nWrote {len(sections)} sections to {output_path}", file=sys.stderr)

    # Synteny is the last mechanical step before the agent's per-pair curation
    # stretch (no script runs again until the explorer). Plant the forward
    # gate notice here so the CP3/CP4 returns are not forgotten — these are
    # the boundaries Run F4 skipped.
    turn = (dict(i_continue="drafting all pairs unattended; I will stop at CP3 "
                            "(empty-slots) before building the visualization")
            if args.unattended else
            dict(your_move="say go to start per-pair curation (I'll pause "
                           "after each pair / on any ambiguous case)"))
    emit_banner(
        current=4,
        produced=str(output_path),
        next_action="Per-pair curation (playbook §5); flag every empty A/B "
                    "slot for the CP3 deep dive.",
        output_dir=args.output_dir,
        gates=["CP3", "CP4"],
        **turn,
    )


if __name__ == "__main__":
    main()
