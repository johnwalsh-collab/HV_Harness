#!/usr/bin/env python3
"""
Download protein sequences for the identified gene set from NCBI.

Generic Stage 2 driver. The gene set (and therefore output filename
prefix) is supplied by the gene-set config. The species list and short
codes come from the genome config.
"""

import argparse
import sys
import time
import pandas as pd
import requests
from pathlib import Path
from Bio import Entrez, SeqIO
from io import StringIO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import PROJECT_DIR, add_config_arg, resolve_output_dirs, load_configs, iter_species

# Entrez email set in main() from --email argument (required by NCBI)

RESULTS_DIR = PROJECT_DIR / "results" / "identification"
SEQUENCES_DIR = PROJECT_DIR / "data" / "sequences"


def fetch_protein_from_gene_id(gene_id, retries=3):
    """Fetch protein sequence from NCBI using gene ID."""
    for attempt in range(retries):
        try:
            # First, get the protein accession from the gene record
            handle = Entrez.efetch(db="gene", id=gene_id, rettype="gene_table", retmode="text")
            gene_info = handle.read()
            handle.close()

            # Try to get protein directly via elink
            handle = Entrez.elink(dbfrom="gene", db="protein", id=gene_id)
            link_result = Entrez.read(handle)
            handle.close()

            protein_ids = []
            for linkset in link_result:
                if 'LinkSetDb' in linkset:
                    for linkdb in linkset['LinkSetDb']:
                        if linkdb['DbTo'] == 'protein':
                            for link in linkdb['Link']:
                                protein_ids.append(link['Id'])

            if not protein_ids:
                return None, "No protein linked"

            # Fetch the first protein sequence (usually the longest/primary)
            handle = Entrez.efetch(db="protein", id=protein_ids[0], rettype="fasta", retmode="text")
            fasta = handle.read()
            handle.close()

            return fasta, None

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return None, str(e)

    return None, "Max retries exceeded"


def fetch_proteins_batch(gene_ids, batch_size=50):
    """Fetch protein sequences for multiple gene IDs in batches."""
    results = {}

    for i in range(0, len(gene_ids), batch_size):
        batch = gene_ids[i:i+batch_size]
        print(f"  Fetching batch {i//batch_size + 1} ({len(batch)} genes)...")

        try:
            # Link genes to proteins
            handle = Entrez.elink(dbfrom="gene", db="protein", id=batch)
            link_results = Entrez.read(handle)
            handle.close()

            # Collect protein IDs
            gene_to_protein = {}
            for linkset in link_results:
                gene_id = linkset['IdList'][0] if linkset['IdList'] else None
                if gene_id and 'LinkSetDb' in linkset:
                    for linkdb in linkset['LinkSetDb']:
                        if linkdb['DbTo'] == 'protein':
                            # Get first protein ID
                            if linkdb['Link']:
                                gene_to_protein[gene_id] = linkdb['Link'][0]['Id']
                                break

            # Fetch protein sequences
            protein_ids = list(gene_to_protein.values())
            if protein_ids:
                handle = Entrez.efetch(db="protein", id=protein_ids, rettype="fasta", retmode="text")
                fasta_text = handle.read()
                handle.close()

                # Parse FASTA and map back to gene IDs
                protein_to_gene = {v: k for k, v in gene_to_protein.items()}
                for record in SeqIO.parse(StringIO(fasta_text), "fasta"):
                    # Extract protein ID from record
                    prot_id = record.id.split('.')[0]
                    # Find matching gene
                    for pid, gid in protein_to_gene.items():
                        # Match by checking if this protein record matches
                        results[gid] = {
                            'protein_id': record.id,
                            'sequence': str(record.seq),
                            'description': record.description
                        }
                        break

            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"  Error in batch: {e}")
            time.sleep(1)

    return results


def main():
    global RESULTS_DIR, SEQUENCES_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_arg(parser)
    parser.add_argument(
        "--email",
        required=True,
        help="Email address to identify yourself to NCBI (required by Entrez).",
    )
    args = parser.parse_args()

    Entrez.email = args.email

    gs_cfg, genome_cfg, _ = load_configs(args.config)
    gene_set = gs_cfg["gene_set"]["name"]
    display_name = gs_cfg["gene_set"].get("display_name", gene_set)

    dirs = resolve_output_dirs(args.output_dir, gene_set)
    RESULTS_DIR   = dirs["identification"]
    SEQUENCES_DIR = dirs["sequences"]
    species_short = {s["full_name"]: s["short_code"]
                     for s in iter_species(genome_cfg)}

    print("=" * 70)
    print(f"Downloading {display_name} protein sequences from NCBI")
    print("=" * 70)

    SEQUENCES_DIR.mkdir(parents=True, exist_ok=True)

    # Load identified members
    input_tsv = RESULTS_DIR / f"{gene_set}_genes_all_species.tsv"
    df = pd.read_csv(input_tsv, sep='\t')
    print(f"\nTotal {gene_set} genes to fetch: {len(df)}")

    # Filter for valid gene IDs
    df = df[df['ncbi_gene_id'].notna() & (df['ncbi_gene_id'] != '')]
    df['ncbi_gene_id'] = df['ncbi_gene_id'].astype(str)
    print(f"Genes with valid NCBI IDs: {len(df)}")

    all_sequences = []
    failed_genes = []

    # Process by species
    for species in df['species'].unique():
        sp_df = df[df['species'] == species]
        sp_short = species_short.get(species, species[:4])

        print(f"\n{species} ({len(sp_df)} genes)...")

        gene_ids = sp_df['ncbi_gene_id'].tolist()

        # Fetch in batches
        for i in range(0, len(gene_ids), 20):
            batch = gene_ids[i:i+20]
            batch_df = sp_df[sp_df['ncbi_gene_id'].isin(batch)]

            print(f"  Batch {i//20 + 1}: fetching {len(batch)} sequences...")

            try:
                # Link genes to proteins
                handle = Entrez.elink(dbfrom="gene", db="protein", id=batch)
                link_results = Entrez.read(handle)
                handle.close()

                # Map gene IDs to protein IDs
                gene_to_protein = {}
                for linkset in link_results:
                    if linkset['IdList'] and 'LinkSetDb' in linkset:
                        gid = linkset['IdList'][0]
                        for linkdb in linkset['LinkSetDb']:
                            if linkdb['DbTo'] == 'protein' and linkdb['Link']:
                                # Get first protein (usually RefSeq)
                                gene_to_protein[gid] = linkdb['Link'][0]['Id']
                                break

                # Fetch protein sequences
                if gene_to_protein:
                    protein_ids = list(gene_to_protein.values())
                    handle = Entrez.efetch(db="protein", id=protein_ids, rettype="fasta", retmode="text")
                    fasta_text = handle.read()
                    handle.close()

                    # Parse and store
                    protein_id_to_gene = {v: k for k, v in gene_to_protein.items()}

                    for record in SeqIO.parse(StringIO(fasta_text), "fasta"):
                        # Find the gene ID for this protein
                        prot_acc = record.id.split('.')[0]
                        gene_id = None

                        # Try to match by protein ID in the mapping
                        for pid, gid in gene_to_protein.items():
                            # Fetch actual accession to compare
                            gene_id = gid
                            break

                        # Get gene info from dataframe
                        gene_row = batch_df[batch_df['ncbi_gene_id'] == gene_id]
                        if not gene_row.empty:
                            gene_name = gene_row.iloc[0]['gene_name']
                            gene_desc = gene_row.iloc[0]['description']
                        else:
                            gene_name = "unknown"
                            gene_desc = record.description

                        # Create clean header
                        header = f"{sp_short}_{gene_name}_{record.id}"

                        all_sequences.append({
                            'species': species,
                            'gene_id': gene_id,
                            'gene_name': gene_name,
                            'protein_id': record.id,
                            'header': header,
                            'sequence': str(record.seq),
                            'length': len(record.seq)
                        })

                # Track failed
                fetched_genes = set(gene_to_protein.keys())
                for gid in batch:
                    if gid not in fetched_genes:
                        gene_row = batch_df[batch_df['ncbi_gene_id'] == gid]
                        if not gene_row.empty:
                            failed_genes.append({
                                'species': species,
                                'gene_id': gid,
                                'gene_name': gene_row.iloc[0]['gene_name']
                            })

                time.sleep(0.5)

            except Exception as e:
                print(f"    Error: {e}")
                time.sleep(1)

    # Save all sequences to single FASTA
    print(f"\n\nWriting {len(all_sequences)} sequences to FASTA...")

    fasta_file = SEQUENCES_DIR / f"{gene_set}_proteins_all.fasta"
    with open(fasta_file, 'w') as f:
        for seq in all_sequences:
            f.write(f">{seq['header']}\n")
            # Wrap sequence at 70 characters
            seq_str = seq['sequence']
            for i in range(0, len(seq_str), 70):
                f.write(seq_str[i:i+70] + "\n")

    print(f"Saved to: {fasta_file}")

    # Save per-species FASTA files
    for species in df['species'].unique():
        sp_seqs = [s for s in all_sequences if s['species'] == species]
        sp_file = SEQUENCES_DIR / f"{gene_set}_proteins_{species_short.get(species, species[:4])}.fasta"
        with open(sp_file, 'w') as f:
            for seq in sp_seqs:
                f.write(f">{seq['header']}\n")
                seq_str = seq['sequence']
                for i in range(0, len(seq_str), 70):
                    f.write(seq_str[i:i+70] + "\n")

    # Save sequence info table
    seq_df = pd.DataFrame(all_sequences)
    seq_df.to_csv(SEQUENCES_DIR / f"{gene_set}_proteins_info.tsv", sep='\t', index=False)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total sequences downloaded: {len(all_sequences)}")
    print(f"Failed to fetch: {len(failed_genes)}")

    print("\nSequences per species:")
    for species in df['species'].unique():
        count = len([s for s in all_sequences if s['species'] == species])
        print(f"  {species}: {count}")

    if failed_genes:
        print(f"\nFailed genes saved to: {SEQUENCES_DIR / 'failed_genes.tsv'}")
        pd.DataFrame(failed_genes).to_csv(SEQUENCES_DIR / "failed_genes.tsv", sep='\t', index=False)


if __name__ == "__main__":
    main()
