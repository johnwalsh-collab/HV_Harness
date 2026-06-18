#!/usr/bin/env python3
"""
Build a goldfish chromosome-to-subgenome lookup table using
NCBI assembly-to-assembly alignment between goldfish (GCF_003368295.1)
and Prussian carp (GCF_023724105.1).

The alignment GFF maps Prussian carp chromosomes (column 1, with A/B subgenome
labels) to goldfish chromosomes (Target field). By summing alignment lengths
per goldfish chromosome -> Prussian carp chromosome pair, we determine which
Prussian carp chromosome (and therefore which subgenome) each goldfish
chromosome corresponds to.
"""

import argparse
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import PROJECT_DIR, load_genome_config

# Default output path matches where genome_config.yaml expects the
# lookup to live (config/), so regenerating overwrites the shipped
# file in place. The lookup ships pre-built in the repo; this script
# is only needed to regenerate it or to build one for a new
# unlabelled tetraploid. Override with --output to write elsewhere.
DEFAULT_OUTPUT_PATH = (
    PROJECT_DIR
    / "config" / "goldfish_subgenome_lookup.tsv"
)

# Prussian carp chromosome -> subgenome label mapping
# NC_068371.1 = A1, NC_068372.1 = A2, ..., NC_068395.1 = A25
# NC_068396.1 = B1, NC_068397.1 = B2, ..., NC_068420.1 = B25
CGIB_CHR = {}
for i in range(25):
    acc_a = f"NC_0683{71 + i:02d}.1" if (71 + i) < 100 else f"NC_068{371 + i}.1"
    acc_b = f"NC_0683{96 + i:02d}.1" if (96 + i) < 100 else f"NC_068{396 + i}.1"
    CGIB_CHR[f"NC_068{371 + i}.1"] = f"A{i + 1}"
    CGIB_CHR[f"NC_068{396 + i}.1"] = f"B{i + 1}"

# Goldfish chromosome -> name mapping
CAUR_CHR = {}
for i in range(50):
    CAUR_CHR[f"NC_039{243 + i}.1"] = f"chr{i + 1}"

def parse_alignment_gff(filepath):
    """Parse the NCBI alignment GFF and sum alignment lengths per pair."""
    # goldfish_chr -> {prussian_carp_chr: total_aligned_bases}
    alignments = defaultdict(lambda: defaultdict(int))

    with open(filepath) as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            if len(fields) < 9:
                continue

            cgib_acc = fields[0]  # Prussian carp accession
            start = int(fields[3])
            end = int(fields[4])
            align_len = end - start + 1
            attrs = fields[8]

            # Extract Target accession
            target_match = re.search(r'Target=(\S+)', attrs)
            if not target_match:
                continue
            target_parts = target_match.group(1).split()
            caur_acc = target_parts[0]

            # Only consider goldfish chromosomes (NC_039xxx) aligned to
            # Prussian carp chromosomes (NC_068xxx)
            if caur_acc not in CAUR_CHR:
                continue
            if cgib_acc not in CGIB_CHR:
                continue

            alignments[caur_acc][cgib_acc] += align_len

    return alignments

def build_lookup(alignments):
    """For each goldfish chromosome, determine the best-matching Prussian carp chromosome."""
    results = []

    for caur_acc in sorted(CAUR_CHR.keys(), key=lambda x: int(x.split('.')[0][-3:])):
        caur_name = CAUR_CHR[caur_acc]

        if caur_acc not in alignments:
            results.append({
                'caur_chr': caur_name,
                'caur_acc': caur_acc,
                'subgenome': 'Unknown',
                'cgib_chr': 'N/A',
                'cgib_acc': 'N/A',
                'aligned_bases': 0,
                'total_aligned': 0,
                'pct_best': 0,
            })
            continue

        chr_aligns = alignments[caur_acc]
        total_aligned = sum(chr_aligns.values())

        # Sort by alignment length descending
        sorted_pairs = sorted(chr_aligns.items(), key=lambda x: x[1], reverse=True)
        best_cgib_acc, best_bases = sorted_pairs[0]
        best_cgib_name = CGIB_CHR[best_cgib_acc]
        subgenome = best_cgib_name[0]  # 'A' or 'B'
        homeolog_num = best_cgib_name[1:]
        pct_best = (best_bases / total_aligned * 100) if total_aligned > 0 else 0

        # Check second best for potential split chromosomes
        second_cgib = ''
        second_bases = 0
        if len(sorted_pairs) > 1:
            second_cgib_acc, second_bases = sorted_pairs[1]
            second_cgib = CGIB_CHR[second_cgib_acc]

        results.append({
            'caur_chr': caur_name,
            'caur_acc': caur_acc,
            'subgenome': subgenome,
            'homeolog_num': homeolog_num,
            'cgib_chr': best_cgib_name,
            'cgib_acc': best_cgib_acc,
            'aligned_bases': best_bases,
            'total_aligned': total_aligned,
            'pct_best': pct_best,
            'second_cgib_chr': second_cgib,
            'second_bases': second_bases,
        })

    return results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("alignment_gff", nargs="?",
                        help="Path to the assembly-to-assembly alignment GFF "
                             "(default: from data/genome_config.yaml).")
    parser.add_argument("--output", default=None,
                        help="Override the output TSV path.")
    args = parser.parse_args()

    if args.alignment_gff:
        gff_path = Path(args.alignment_gff)
    else:
        genome_cfg = load_genome_config()
        gff_path = PROJECT_DIR / genome_cfg["subgenome_lookup"]["alignment_file"]

    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT_PATH

    print(f"Parsing alignment GFF: {gff_path}", file=sys.stderr)
    alignments = parse_alignment_gff(gff_path)

    print(f"Found alignments for {len(alignments)} goldfish sequences", file=sys.stderr)

    results = build_lookup(alignments)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as out:
        out.write("# Goldfish Chromosome to Subgenome Lookup Table\n")
        out.write("# Generated from NCBI assembly alignment: GCF_003368295.1 (C. auratus) vs GCF_023724105.1 (C. gibelio)\n")
        out.write("# Subgenome assigned based on best-matching Prussian carp chromosome\n")
        out.write("#\n")
        out.write("goldfish_chr\tgoldfish_accession\tsubgenome\thomeolog_number\tassigned_label\t"
                  "best_cgib_chr\tcgib_accession\taligned_bases\ttotal_aligned_bases\t"
                  "pct_to_best\tsecond_best_cgib_chr\tsecond_best_bases\n")

        for r in results:
            label = f"{r['subgenome']}{r.get('homeolog_num', '')}" if r['subgenome'] != 'Unknown' else 'Unknown'
            out.write(f"{r['caur_chr']}\t{r['caur_acc']}\t{r['subgenome']}\t"
                      f"{r.get('homeolog_num', 'N/A')}\t{label}\t"
                      f"{r['cgib_chr']}\t{r.get('cgib_acc', 'N/A')}\t"
                      f"{r['aligned_bases']}\t{r['total_aligned']}\t"
                      f"{r['pct_best']:.1f}\t"
                      f"{r.get('second_cgib_chr', '')}\t{r.get('second_bases', 0)}\n")

    print(f"\nLookup table written to: {output_path}", file=sys.stderr)

    # Print summary to stdout
    print("\nGoldfish Chromosome -> Subgenome Assignment")
    print("=" * 75)
    print(f"{'Goldfish Chr':<14} {'Accession':<16} {'Subgenome':<10} {'Assigned':<10} "
          f"{'Best C.gib':<10} {'Aligned bp':<12} {'% to best':<10}")
    print("-" * 75)

    a_count = sum(1 for r in results if r['subgenome'] == 'A')
    b_count = sum(1 for r in results if r['subgenome'] == 'B')

    for r in results:
        label = f"{r['subgenome']}{r.get('homeolog_num', '')}" if r['subgenome'] != 'Unknown' else 'Unknown'
        print(f"{r['caur_chr']:<14} {r['caur_acc']:<16} {r['subgenome']:<10} {label:<10} "
              f"{r['cgib_chr']:<10} {r['aligned_bases']:<12,} {r['pct_best']:<10.1f}")

    print("-" * 75)
    print(f"Subgenome A: {a_count} chromosomes")
    print(f"Subgenome B: {b_count} chromosomes")
    print(f"Unknown: {50 - a_count - b_count} chromosomes")

if __name__ == '__main__':
    main()
