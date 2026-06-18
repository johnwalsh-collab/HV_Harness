#!/usr/bin/env python3
"""
Extract protein sequences for an identified gene set from local protein FASTA files.

Generic Stage 2 driver — replaces NCBI API calls with local file extraction.
Requires per-species protein FASTA files at:
    data/annotations/<species>/<species>_protein.faa.gz   (gzipped)
    data/annotations/<species>/<species>_protein.faa      (uncompressed)

These are the standard RefSeq protein FASTA files distributed with each assembly.
Download them once alongside the GFF and they serve all gene sets.

How it works:
    1. Reads the gene list produced by identify_gene_set.py
    2. Parses the GFF to find protein accessions for each gene
    3. Extracts matching sequences from the local protein FASTA
    4. Writes per-species and combined FASTAs to data/sequences/

Outputs match the format expected by clean_sequences.py and build_gene_inventory.py.

Usage:
    python scripts/extract_sequences.py --config config/<gene_set>.yaml
    python scripts/extract_sequences.py --config config/<gene_set>.yaml --output-dir ../MyRun
"""

from __future__ import annotations

import argparse
import csv
import gzip
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import (
    PROJECT_DIR,
    add_config_arg,
    add_unattended_arg,
    emit_banner,
    resolve_output_dirs,
    load_configs,
    iter_species,
    find_annotation_file,
)

ANNOTATIONS_DIR = PROJECT_DIR / "data" / "annotations"


# ---------------------------------------------------------------------------
# GFF helpers
# ---------------------------------------------------------------------------

def get_protein_accessions_from_gff(gff_path: Path, gene_ids: set[str]) -> dict[str, list[str]]:
    """Return {gene_id: [protein_accession, ...]} for each gene_id in the set.

    Searches the GFF for CDS features whose Parent chain leads back to a
    gene in gene_ids. The protein_id attribute on CDS lines is the accession
    to look up in the protein FASTA.
    """
    gene_to_proteins: dict[str, set[str]] = defaultdict(set)
    mrna_to_gene: dict[str, str] = {}

    opener = gzip.open if str(gff_path).endswith(".gz") else open

    with opener(gff_path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            ftype = parts[2]
            attrs_str = parts[8]

            attrs: dict[str, str] = {}
            for item in attrs_str.split(";"):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    attrs[k.strip()] = v.strip()

            if ftype in ("mRNA", "transcript"):
                mrna_id = attrs.get("ID", "")
                parent = attrs.get("Parent", "")
                # Parent of mRNA is gene-XXXXX or gene:XXXXX
                gene_id = parent.replace("gene-", "").replace("gene:", "")
                if gene_id in gene_ids and mrna_id:
                    mrna_to_gene[mrna_id] = gene_id

            elif ftype == "CDS":
                protein_id = attrs.get("protein_id", "")
                if not protein_id:
                    continue
                parent = attrs.get("Parent", "")
                # Parent can be rna-XM_... or transcript:... or mRNA ID
                # Try direct lookup first
                if parent in mrna_to_gene:
                    gene_id = mrna_to_gene[parent]
                    gene_to_proteins[gene_id].add(protein_id)

    return {gid: list(accs) for gid, accs in gene_to_proteins.items()}


def load_protein_fasta(faa_path: Path) -> dict[str, str]:
    """Load a protein FASTA into {accession: sequence} dict.

    Accession is the first word of the header line (without '>').
    Handles both gzipped and plain files.
    """
    seqs: dict[str, str] = {}
    current_acc = None
    current_seq: list[str] = []

    opener = gzip.open if str(faa_path).endswith(".gz") else open

    with opener(faa_path, "rt") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if current_acc:
                    seqs[current_acc] = "".join(current_seq)
                current_acc = line[1:].split()[0]
                current_seq = []
            else:
                current_seq.append(line)
        if current_acc:
            seqs[current_acc] = "".join(current_seq)

    return seqs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    global SEQUENCES_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_arg(parser)
    add_unattended_arg(parser)
    args = parser.parse_args()

    dirs = resolve_output_dirs(args.output_dir)
    results_dir = dirs["identification"]
    SEQUENCES_DIR = dirs["sequences"]
    SEQUENCES_DIR.mkdir(parents=True, exist_ok=True)

    gs_cfg, genome_cfg, _ = load_configs(args.config)
    gene_set = gs_cfg["gene_set"]["name"]
    display_name = gs_cfg["gene_set"].get("display_name", gene_set)

    print("=" * 70)
    print(f"Extracting {display_name} protein sequences from local FASTAs")
    print(f"Gene-set config: {gs_cfg['__path__']}")
    print("=" * 70)

    # Load the gene list
    gene_list_path = results_dir / f"{gene_set}_genes_all_species.tsv"
    if not gene_list_path.exists():
        sys.exit(
            f"Gene list not found at {gene_list_path}\n"
            f"Run identify_gene_set.py first."
        )

    genes_df = pd.read_csv(gene_list_path, sep="\t")

    # Short species codes for output filenames
    species_short = {s["full_name"]: s["short_code"] for s in iter_species(genome_cfg)}

    all_rows: list[dict] = []
    missing_fasta: list[str] = []

    for species_meta in iter_species(genome_cfg):
        sp_name = species_meta["full_name"]
        sp_short = species_meta.get("short_code", sp_name[:4])

        sp_genes = genes_df[genes_df["species"] == sp_name]
        if sp_genes.empty:
            print(f"\n{sp_name}: no genes in list, skipping.")
            continue

        gene_ids = set(sp_genes["gene_id"].astype(str).tolist())
        print(f"\n{species_meta['common_name']} ({sp_name}): {len(gene_ids)} genes")

        # Find the protein FASTA (tolerant of native RefSeq filenames)
        ann_dir = ANNOTATIONS_DIR / sp_name
        faa_path = find_annotation_file(sp_name, "protein", ann_dir=ANNOTATIONS_DIR)
        if faa_path is None:
            print(
                f"  WARNING: no protein FASTA found in {ann_dir}/\n"
                f"  Place the species' protein FASTA there — the canonical "
                f"{sp_name}_protein.faa[.gz] or the native RefSeq name "
                f"(e.g. GCF_..._protein.faa.gz) are both accepted.\n"
                f"  Skipping {sp_name} — no sequences will be written for this species."
            )
            missing_fasta.append(sp_name)
            continue

        # Find the GFF (tolerant of native RefSeq filenames)
        gff_path = find_annotation_file(sp_name, "gff", ann_dir=ANNOTATIONS_DIR)
        if gff_path is None:
            print(f"  WARNING: no GFF found in {ann_dir}/, skipping.")
            continue

        print(f"  Scanning GFF for protein accessions...")
        gene_to_proteins = get_protein_accessions_from_gff(gff_path, gene_ids)

        found_accs: set[str] = set()
        for accs in gene_to_proteins.values():
            found_accs.update(accs)

        print(f"  Loading protein FASTA ({faa_path.name})...")
        protein_seqs = load_protein_fasta(faa_path)

        # Write per-species FASTA
        sp_fasta_path = SEQUENCES_DIR / f"{gene_set}_proteins_{sp_short}.fasta"
        written = 0
        missing_accs = []

        with open(sp_fasta_path, "w") as out:
            for gene_id in gene_ids:
                accs = gene_to_proteins.get(gene_id, [])
                if not accs:
                    # Try alternate gene_id format (some GFFs use LOC-prefixed IDs)
                    alt_id = f"gene-{gene_id}" if not gene_id.startswith("gene-") else gene_id
                    accs = gene_to_proteins.get(alt_id, [])

                if not accs:
                    missing_accs.append(gene_id)
                    continue

                # Use the first (canonical) protein accession
                acc = accs[0]
                seq = protein_seqs.get(acc)
                if seq:
                    out.write(f">{acc} gene_id={gene_id} species={sp_name}\n")
                    # Wrap at 80 chars
                    for i in range(0, len(seq), 80):
                        out.write(seq[i:i+80] + "\n")
                    written += 1
                    all_rows.append({
                        "gene_id": gene_id,
                        "species": sp_name,
                        "protein_id": acc,
                        "length": len(seq),
                        "sequence": seq,
                        "source": "local_fasta",
                    })
                else:
                    missing_accs.append(gene_id)

        print(f"  Wrote {written}/{len(gene_ids)} sequences to {sp_fasta_path.name}")
        if missing_accs:
            print(f"  No sequence found for {len(missing_accs)} gene(s): "
                  f"{', '.join(missing_accs[:5])}{'...' if len(missing_accs) > 5 else ''}")

    # Combined FASTA
    combined_path = SEQUENCES_DIR / f"{gene_set}_proteins_all.fasta"
    total = 0
    with open(combined_path, "w") as out:
        for sp_meta in iter_species(genome_cfg):
            sp_short = sp_meta.get("short_code", sp_meta["full_name"][:4])
            sp_fasta = SEQUENCES_DIR / f"{gene_set}_proteins_{sp_short}.fasta"
            if sp_fasta.exists():
                with open(sp_fasta) as fh:
                    for line in fh:
                        out.write(line)
                        if line.startswith(">"):
                            total += 1

    print(f"\nCombined FASTA: {combined_path} ({total} sequences)")

    # Info TSV (matches format expected by clean_sequences.py)
    if all_rows:
        info_df = pd.DataFrame(all_rows)
        info_path = SEQUENCES_DIR / f"{gene_set}_proteins_info.tsv"
        info_df.to_csv(info_path, sep="\t", index=False)
        print(f"Info TSV: {info_path}")

    if missing_fasta:
        print(
            f"\nWARNING: protein FASTA missing for: {', '.join(missing_fasta)}\n"
            f"Download with:\n"
            f"  curl -L <ncbi_ftp_url> -o data/annotations/<species>/<species>_protein.faa.gz\n"
            f"See GETTING_STARTED.md for assembly accessions and FTP paths."
        )

    print("\nDone. Run clean_sequences.py next to deduplicate.")

    turn = (dict(i_continue="running clean_sequences.py")
            if args.unattended else
            dict(your_move="say go and I'll run clean_sequences.py"))
    emit_banner(
        current=2,
        produced=str(SEQUENCES_DIR),
        next_action="Dedup/QC the protein FASTAs (clean_sequences.py), then "
                    "build the inventory.",
        output_dir=args.output_dir,
        **turn,
    )


if __name__ == "__main__":
    main()
