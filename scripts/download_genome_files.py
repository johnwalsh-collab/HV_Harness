#!/usr/bin/env python3
"""
Download genome data files (GFF annotation + protein FASTA) for the
HV_Harness target species directly from NCBI's file server.

This is the reliable, one-step way to obtain the inputs the pipeline
needs. It downloads the bulk reference files over plain HTTPS from
ftp.ncbi.nlm.nih.gov -- NOT the Entrez/E-utilities API, which is
rate-limited and frequently times out. Once the per-species protein
FASTA is local, extract_sequences.py pulls just the gene-set members
out of it; there is no need to fetch sequences one accession at a time.

Species, assembly accessions, and assembly names come from
data/genome_config.yaml -- the single source of truth shared with the
manual curl commands in GETTING_STARTED.md, so the two never drift.

Usage:
    # the focal set (the three carps + zebrafish):
    python scripts/download_genome_files.py

    # only what you need (recommended: one carp + zebrafish to start):
    python scripts/download_genome_files.py --species Carassius_gibelio Danio_rerio

    # see what would be downloaded, or print the equivalent curl
    # commands, without downloading anything:
    python scripts/download_genome_files.py --dry-run
    python scripts/download_genome_files.py --print-commands

Files land in data/annotations/<species>/<species>_genomic.gff.gz and
data/annotations/<species>/<species>_protein.faa.gz. Re-running skips
files that already exist unless you pass --force.
"""

import argparse
import gzip
import sys
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import PROJECT_DIR, load_genome_config

ANNOTATIONS_DIR = PROJECT_DIR / "data" / "annotations"
NCBI_BASE = "https://ftp.ncbi.nlm.nih.gov/genomes/all"

# file-type key -> (NCBI suffix, local filename suffix)
FILE_TYPES = {
    "gff": ("genomic.gff.gz", "genomic.gff.gz"),
    "protein": ("protein.faa.gz", "protein.faa.gz"),
}

# Species roles (from genome_config.yaml) included when --species is omitted.
DEFAULT_ROLES = {"core", "primary_comparator"}


def assembly_dir_url(accession: str, assembly_name: str) -> tuple[str, str]:
    """Return (directory_url, full_dir_name) for an assembly on the
    NCBI file server.

    e.g. GCF_023724105.1 + carGib1.2-hapl.c ->
      https://.../GCF/023/724/105/GCF_023724105.1_carGib1.2-hapl.c
    """
    prefix = accession.split("_")[0]                 # GCF
    digits = accession.split("_")[1].split(".")[0]   # 023724105
    p1, p2, p3 = digits[0:3], digits[3:6], digits[6:9]
    full = f"{accession}_{assembly_name}"
    return f"{NCBI_BASE}/{prefix}/{p1}/{p2}/{p3}/{full}", full


def file_url(accession: str, assembly_name: str, kind: str) -> str:
    dir_url, full = assembly_dir_url(accession, assembly_name)
    ncbi_suffix, _ = FILE_TYPES[kind]
    return f"{dir_url}/{full}_{ncbi_suffix}"


def local_path(species: str, kind: str) -> Path:
    _, local_suffix = FILE_TYPES[kind]
    return ANNOTATIONS_DIR / species / f"{species}_{local_suffix}"


def curl_command(url: str, dest: Path) -> str:
    return f'curl -L "{url}" -o "{dest}"'


def verify_gzip(path: Path) -> bool:
    """Read the first chunk through the gzip decoder to confirm the
    download is a valid, non-truncated gzip file."""
    try:
        with gzip.open(path, "rb") as fh:
            fh.read(1024)
        return True
    except Exception:
        return False


def download_one(url: str, dest: Path) -> tuple[bool, str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp, open(tmp, "wb") as out:
            while True:
                chunk = resp.read(1 << 16)
                if not chunk:
                    break
                out.write(chunk)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        tmp.unlink(missing_ok=True)
        return False, f"download failed ({e})"
    if not verify_gzip(tmp):
        tmp.unlink(missing_ok=True)
        return False, "downloaded file is not a valid gzip (truncated?)"
    tmp.replace(dest)
    size_mb = dest.stat().st_size / (1024 * 1024)
    return True, f"{size_mb:.1f} MB"


def select_species(genome_cfg: dict, requested: list[str] | None) -> list[dict]:
    species = genome_cfg["species"]
    by_name = {s["full_name"]: s for s in species}
    if requested:
        chosen = []
        for name in requested:
            if name not in by_name:
                sys.exit(f"Unknown species '{name}'. Known: {', '.join(by_name)}")
            chosen.append(by_name[name])
        return chosen
    return [s for s in species if s.get("role") in DEFAULT_ROLES]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--species", nargs="+", metavar="FULL_NAME",
                    help="One or more species full_names (e.g. Carassius_gibelio). "
                         "Default: the focal set (core species + zebrafish).")
    ap.add_argument("--genome-config", default=None,
                    help="Path to genome config (default: data/genome_config.yaml).")
    ap.add_argument("--force", action="store_true",
                    help="Re-download even if the target file already exists.")
    ap.add_argument("--dry-run", action="store_true",
                    help="List what would be downloaded, then exit.")
    ap.add_argument("--print-commands", action="store_true",
                    help="Print the equivalent manual curl commands, then exit.")
    args = ap.parse_args()

    genome_cfg = load_genome_config(args.genome_config)
    chosen = select_species(genome_cfg, args.species)

    if args.print_commands:
        for s in chosen:
            if not s.get("assembly_name"):
                print(f"# {s['full_name']}: assembly_name not set in genome_config.yaml")
                continue
            for kind in FILE_TYPES:
                url = file_url(s["assembly"], s["assembly_name"], kind)
                print(curl_command(url, local_path(s["full_name"], kind)))
        return 0

    print(f"Target species: {', '.join(s['full_name'] for s in chosen)}\n")

    failures, skipped = [], []
    for s in chosen:
        name = s["full_name"]
        if not s.get("assembly_name"):
            print(f"[skip] {name}: no assembly_name in genome_config.yaml "
                  f"(accession {s['assembly']}). Add it to enable download.")
            skipped.append(name)
            continue
        for kind in FILE_TYPES:
            url = file_url(s["assembly"], s["assembly_name"], kind)
            dest = local_path(name, kind)
            label = f"{name} {kind}"
            if dest.exists() and not args.force:
                print(f"[have] {label}: {dest.relative_to(PROJECT_DIR)}")
                continue
            if args.dry_run:
                print(f"[plan] {label}: {url}")
                continue
            print(f"[get ] {label} ...", flush=True)
            ok, msg = download_one(url, dest)
            if ok:
                print(f"[done] {label}: {msg} -> {dest.relative_to(PROJECT_DIR)}")
            else:
                print(f"[FAIL] {label}: {msg}")
                print(f"       manual fallback: {curl_command(url, dest)}")
                failures.append(label)

    print()
    if args.dry_run:
        print("Dry run only -- nothing downloaded.")
    elif failures:
        print(f"Completed with {len(failures)} failure(s): {', '.join(failures)}")
        print("Re-run to retry, or use the manual curl command(s) printed above.")
        return 1
    else:
        print("All requested files present.")
    if skipped:
        print(f"Skipped (no assembly_name): {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
