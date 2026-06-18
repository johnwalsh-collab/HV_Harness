#!/usr/bin/env python3
"""
Identify members of a chosen gene set from GFF annotation files.

This is the generic Stage 2 driver. What it searches for is supplied
entirely by the gene-set config (config/<gene_set>.yaml). There are no
gene-family defaults in this script. A new application is configured
by editing the config, not the code.

Usage:
    python identify_gene_set.py [--config config/<gene_set>.yaml]

Inputs:
    - data/annotations/<species>/<species>_genomic.gff.gz
      (one per species named in data/genome_config.yaml)
    - config/<gene_set>.yaml  (inclusion / exclusion rules)
    - data/genome_config.yaml (species list)

Outputs:
    - results/identification/<gene_set>_genes_all_species.tsv
      (one row per matching gene OR pseudogene; columns: species,
      gene_id, gene_name, chromosome, start, end, strand, description,
      ncbi_gene_id, match_reason, plus the NCBI quality signals
      gene_biotype, feature_type, partial, exception, protein_id)

Both protein-coding genes and pseudogenes are extracted. Pseudogenes are
a distinct GFF feature type (exon-only children, no mRNA/CDS); they carry
NCBI's explicit non-functional call (gene_biotype=pseudogene) and must
not be silently skipped.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

import pandas as pd

# Local sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import (
    PROJECT_DIR,
    add_config_arg,
    add_unattended_arg,
    emit_banner,
    resolve_output_dirs,
    iter_species,
    load_configs,
    find_annotation_file,
)


ANNOTATIONS_DIR = PROJECT_DIR / "data" / "annotations"
RESULTS_DIR = PROJECT_DIR / "results" / "identification"


# ---------------------------------------------------------------------------
# GFF parsing helpers
# ---------------------------------------------------------------------------

def parse_attributes(attr_string: str) -> dict:
    """Parse a GFF3 attributes column into a dict."""
    attrs = {}
    for item in attr_string.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            value = value.replace("%2C", ",").replace("%3B", ";").replace("%25", "%")
            attrs[key] = value
    return attrs


# ---------------------------------------------------------------------------
# Inclusion / exclusion engine
# ---------------------------------------------------------------------------

class GeneSetMatcher:
    """Encapsulates the inclusion/exclusion logic from a gene-set
    config. All rules are user-supplied; no defaults."""

    def __init__(self, identification_cfg: dict):
        inc = identification_cfg.get("inclusion", {}) or {}
        exc = identification_cfg.get("exclusion", {}) or {}

        # Compile name regexes once
        self._name_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in (inc.get("name_patterns") or [])
        ]
        # Lower-case keyword/exclusion lists for case-insensitive substring tests
        self._description_keywords = [
            k.lower() for k in (inc.get("description_keywords") or [])
        ]
        self._exclude_names = {
            n.lower() for n in (exc.get("gene_names") or [])
        }
        self._exclude_desc_patterns = [
            p.lower() for p in (exc.get("description_patterns") or [])
        ]

    # --- Inclusion checks ---
    def _name_matches(self, name: str) -> bool:
        return any(p.match(name) for p in self._name_patterns)

    def _description_matches(self, description: str) -> bool:
        desc = description.lower()
        return any(k in desc for k in self._description_keywords)

    # --- Exclusion checks ---
    def _is_excluded(self, name: str, description: str) -> bool:
        if name.lower() in self._exclude_names:
            return True
        desc = description.lower()
        return any(p in desc for p in self._exclude_desc_patterns)

    # --- Public API ---
    def classify(self, attrs: dict) -> tuple[bool, str, str]:
        """Return (is_member, gene_name, reason) for a GFF gene entry."""
        gene_name = attrs.get("Name", attrs.get("gene", ""))
        description = attrs.get("description", "")

        if self._is_excluded(gene_name, description):
            return False, gene_name, "excluded"

        if self._name_matches(gene_name):
            return True, gene_name, "name match"
        if self._description_matches(description):
            return True, gene_name, "description match"
        return False, gene_name, "no match"

    def product_indicates_member(self, product: str) -> bool:
        """Two-pass logic: an mRNA/CDS whose product field contains an
        inclusion keyword and no exclusion pattern flags its parent gene
        as a candidate (handles LOC genes with informative product strings
        but uninformative gene Names)."""
        prod = product.lower()
        if not any(k in prod for k in self._description_keywords):
            return False
        if any(p in prod for p in self._exclude_desc_patterns):
            return False
        return True


# ---------------------------------------------------------------------------
# Per-species extraction
# ---------------------------------------------------------------------------

def extract_from_gff(gff_path: Path, species_name: str,
                     matcher: GeneSetMatcher) -> list[dict]:
    """Two-pass GFF extraction.

    Pass 1: scan all features, collect (a) every gene entry's attributes,
    and (b) any mRNA/CDS whose product indicates membership (records the
    parent gene ID as a candidate).

    Pass 2: emit one row per unique gene that either matches by name /
    description or is the parent of a member mRNA/CDS.
    """
    gene_data: dict[str, dict] = {}
    candidate_parents: dict[str, str] = {}
    protein_ids: dict[str, list] = {}      # GeneID -> [protein accession, ...]
    child_exceptions: dict[str, set] = {}  # GeneID -> {exception strings}

    def _geneid(a: dict) -> str:
        for ref in a.get("Dbxref", "").split(","):
            if ref.startswith("GeneID:"):
                return ref.replace("GeneID:", "")
        return ""

    opener = gzip.open if str(gff_path).endswith(".gz") else open
    with opener(gff_path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9:
                continue
            seqid, _, ftype, start, end, _, strand, _, attribute_str = fields
            attrs = parse_attributes(attribute_str)

            # Collect protein-coding genes AND pseudogenes. Pseudogenes are a
            # distinct feature type with exon-only children (no mRNA/CDS);
            # ignoring them would silently drop NCBI's explicit non-functional
            # calls — the strongest annotation-level loss signal.
            if ftype in ("gene", "pseudogene"):
                gene_data[attrs.get("ID", "")] = {
                    "seqid": seqid,
                    "start": int(start),
                    "end": int(end),
                    "strand": strand,
                    "attrs": attrs,
                    "ftype": ftype,
                }
            elif ftype in ("mRNA", "CDS"):
                product = attrs.get("product", "")
                parent = attrs.get("Parent", "")
                if parent and matcher.product_indicates_member(product):
                    candidate_parents.setdefault(parent, product)
                # Capture the protein accession (for the FASTA low-quality
                # lookup) and any per-feature exception, keyed by GeneID.
                gid = _geneid(attrs)
                if gid:
                    if ftype == "CDS":
                        pid = attrs.get("protein_id") or attrs.get("Name", "")
                        if pid:
                            protein_ids.setdefault(gid, [])
                            if pid not in protein_ids[gid]:
                                protein_ids[gid].append(pid)
                    exc = attrs.get("exception", "")
                    if exc:
                        child_exceptions.setdefault(gid, set()).add(exc)

    results: list[dict] = []
    seen: set[str] = set()
    for gene_id, data in gene_data.items():
        attrs = data["attrs"]
        is_member, name, reason = matcher.classify(attrs)
        if not is_member and gene_id in candidate_parents:
            is_member, reason = True, "product match"

        if not is_member or gene_id in seen:
            continue
        seen.add(gene_id)

        description = attrs.get("description", "").replace("%2C", ",")
        if not description and gene_id in candidate_parents:
            description = candidate_parents[gene_id]

        ncbi_gene_id = _geneid(attrs)

        # Annotation-level quality signals, taken verbatim from NCBI.
        gene_biotype = attrs.get("gene_biotype", "")
        partial = "true" if attrs.get("partial", "").lower() == "true" else ""
        exceptions = set(child_exceptions.get(ncbi_gene_id, set()))
        if attrs.get("exception"):
            exceptions.add(attrs["exception"])
        exception = "; ".join(sorted(exceptions))
        protein_id = ";".join(protein_ids.get(ncbi_gene_id, []))

        results.append({
            "species": species_name,
            "gene_id": gene_id.replace("gene-", ""),
            "gene_name": name,
            "chromosome": data["seqid"],
            "start": data["start"],
            "end": data["end"],
            "strand": data["strand"],
            "description": description,
            "ncbi_gene_id": ncbi_gene_id,
            "match_reason": reason,
            "gene_biotype": gene_biotype,
            "feature_type": data["ftype"],
            "partial": partial,
            "exception": exception,
            "protein_id": protein_id,
        })

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    global RESULTS_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_arg(parser)
    add_unattended_arg(parser)
    args = parser.parse_args()

    dirs = resolve_output_dirs(args.output_dir)
    RESULTS_DIR = dirs["identification"]

    gs_cfg, genome_cfg, _ = load_configs(args.config)
    gene_set_name = gs_cfg["gene_set"]["name"]
    display_name = gs_cfg["gene_set"].get("display_name", gene_set_name)
    matcher = GeneSetMatcher(gs_cfg.get("identification", {}))

    print("=" * 70)
    print(f"Identifying {display_name} members from genome annotations")
    print(f"Gene-set config: {gs_cfg['__path__']}")
    print("=" * 70)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    for species in iter_species(genome_cfg):
        sp_name = species["full_name"]
        gff_path = find_annotation_file(sp_name, "gff", ann_dir=ANNOTATIONS_DIR)
        if gff_path is None:
            print(f"\n{species['common_name']}: no GFF found in "
                  f"{ANNOTATIONS_DIR / sp_name}/")
            continue

        print(f"\nProcessing {species['common_name']} ({sp_name})...")
        rows = extract_from_gff(gff_path, sp_name, matcher)
        all_rows.extend(rows)
        unique_names = sorted({r["gene_name"] for r in rows})
        print(f"  Found {len(rows)} {gene_set_name} genes:")
        print(f"  {', '.join(unique_names)}")

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df = df.sort_values(["species", "chromosome", "start"])

    output_file = RESULTS_DIR / f"{gene_set_name}_genes_all_species.tsv"
    df.to_csv(output_file, sep="\t", index=False)
    print(f"\nSaved detailed results to: {output_file}")
    print(f"Total genes: {len(df)}")

    turn = (dict(i_continue="extracting sequences, then building the inventory")
            if args.unattended else
            dict(your_move="review the gene list above for false positives / "
                           "missing members, then say go to extract sequences "
                           "and build the inventory"))
    emit_banner(
        current=2,
        produced=str(output_file),
        next_action="Preliminary gene-list check (false positives / missing "
                    "members), then extract sequences and build the inventory.",
        output_dir=args.output_dir,
        **turn,
    )


if __name__ == "__main__":
    main()
