#!/usr/bin/env python3
"""
Clean and deduplicate protein sequences.
Keep only the longest isoform per gene and fix headers.

Reads <gene_set>_genes_all_species.tsv plus the per-gene download
metadata, dedups isoforms, and writes per-species + combined FASTAs
plus a metadata table.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import (PROJECT_DIR, add_config_arg, add_unattended_arg, emit_banner,
                     resolve_output_dirs, load_configs, iter_species)

RESULTS_DIR = PROJECT_DIR / "results" / "identification"
SEQUENCES_DIR = PROJECT_DIR / "data" / "sequences"


def short_code_map(genome_cfg: dict) -> dict[str, str]:
    """{full_name: short_code} from the genome config."""
    return {s["full_name"]: s["short_code"] for s in iter_species(genome_cfg)}


def build_display_name(gene_name: str, description: str, type_rules: list,
                       gene_set_name: str) -> str:
    """Generate a clean header for a gene. If the gene is a LOC entry
    with an informative description, prepend the inferred canonical
    type as a `<type>_like_<suffix>` label.

    Generic across gene sets: uses the type_rules from the gene-set
    config rather than caspase-specific case-matching.
    """
    if not gene_name.startswith("LOC") or not description:
        return gene_name

    desc_lower = description.lower()
    for rule in type_rules:
        type_name = rule.get("type")
        if not type_name:
            continue
        for needle in rule.get("matches", []):
            if needle.lower() in desc_lower:
                return f"{type_name}_like_{gene_name[-4:]}"
    return f"{gene_set_name}_like_{gene_name[-4:]}"


def main() -> None:
    global RESULTS_DIR, SEQUENCES_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_arg(parser)
    add_unattended_arg(parser)
    args = parser.parse_args()

    gs_cfg, genome_cfg, _ = load_configs(args.config)
    gene_set = gs_cfg["gene_set"]["name"]

    dirs = resolve_output_dirs(args.output_dir, gene_set)
    RESULTS_DIR   = dirs["identification"]
    SEQUENCES_DIR = dirs["sequences"]
    type_rules = gs_cfg.get("classification", {}).get("type_rules", []) or []
    sp_short = short_code_map(genome_cfg)

    print("=" * 70)
    print(f"Cleaning and deduplicating {gene_set} protein sequences")
    print("=" * 70)

    # Load gene info (prefer dedup file if available; fall back to raw)
    dedup_file = RESULTS_DIR / f"{gene_set}_genes_all_species_dedup.tsv"
    raw_file = RESULTS_DIR / f"{gene_set}_genes_all_species.tsv"
    src = dedup_file if dedup_file.exists() else raw_file
    genes_df = pd.read_csv(src, sep="\t")
    genes_df["ncbi_gene_id"] = genes_df["ncbi_gene_id"].astype(str)

    gene_info = {}
    for _, row in genes_df.iterrows():
        gene_info[row["ncbi_gene_id"]] = {
            "species": row["species"],
            "gene_name": row["gene_name"],
            "description": row["description"],
        }

    # Load sequence info
    seq_df = pd.read_csv(SEQUENCES_DIR / f"{gene_set}_proteins_info.tsv", sep="\t")
    seq_df["gene_id"] = seq_df["gene_id"].astype(str)

    print(f"Total sequences: {len(seq_df)}")
    print(f"Unique genes:    {seq_df['gene_id'].nunique()}")

    # Keep the longest isoform per (species, gene_id).
    # Grouping by both columns prevents same-named genes in different species
    # (e.g. gsdmea in zebrafish and C. gibelio) from collapsing into one entry.
    best_seqs = {}
    for (species, gene_id), group in seq_df.groupby(["species", "gene_id"]):
        longest = group.loc[group["length"].idxmax()]
        info = gene_info.get(gene_id, {})
        gene_name = info.get("gene_name", gene_id)
        description = info.get("description", "")
        short = sp_short.get(species, species[:4])
        display = build_display_name(gene_name, description, type_rules, gene_set)
        best_seqs[f"{species}|{gene_id}"] = {
            "species": species,
            "gene_id": gene_id,
            "gene_name": gene_name,
            "display_name": display,
            "protein_id": longest["protein_id"],
            "header": f"{short}_{display}",
            "sequence": longest["sequence"],
            "length": longest["length"],
            "description": description,
        }

    print(f"After deduplication: {len(best_seqs)} sequences")

    # Combined FASTA
    fasta_file = SEQUENCES_DIR / f"{gene_set}_proteins_deduplicated.fasta"
    with open(fasta_file, "w") as fh:
        for _, sd in sorted(best_seqs.items(),
                            key=lambda x: (x[1]["species"], x[1]["display_name"])):
            fh.write(f">{sd['header']}\n")
            s = sd["sequence"]
            for i in range(0, len(s), 70):
                fh.write(s[i:i + 70] + "\n")
    print(f"Saved combined to: {fasta_file}")

    # Metadata table
    info_df = pd.DataFrame(list(best_seqs.values()))
    info_df.to_csv(SEQUENCES_DIR / f"{gene_set}_proteins_deduplicated_info.tsv",
                   sep="\t", index=False)

    # Per-species FASTAs
    for species in genes_df["species"].unique():
        sp = [s for s in best_seqs.values() if s["species"] == species]
        short = sp_short.get(species, species[:4])
        sp_file = SEQUENCES_DIR / f"{gene_set}_proteins_{short}_dedup.fasta"
        with open(sp_file, "w") as fh:
            for sd in sorted(sp, key=lambda x: x["display_name"]):
                fh.write(f">{sd['header']}\n")
                s = sd["sequence"]
                for i in range(0, len(s), 70):
                    fh.write(s[i:i + 70] + "\n")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nSequences per species:")
    for species in genes_df["species"].unique():
        count = len([s for s in best_seqs.values() if s["species"] == species])
        expected = len(genes_df[genes_df["species"] == species])
        print(f"  {species} ({sp_short.get(species, '???')}): {count}/{expected}")
    lengths = [s["length"] for s in best_seqs.values()]
    if lengths:
        print(f"\nSequence lengths: min={min(lengths)}, max={max(lengths)}, "
              f"mean={sum(lengths)/len(lengths):.1f} aa")

    turn = (dict(i_continue="building the gene inventory")
            if args.unattended else
            dict(your_move="say go and I'll build the gene inventory"))
    emit_banner(
        current=2,
        produced=str(SEQUENCES_DIR),
        next_action="Build the gene inventory (build_gene_inventory.py) — "
                    "then CP2 review.",
        output_dir=args.output_dir,
        **turn,
    )


if __name__ == "__main__":
    main()
