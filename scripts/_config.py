"""Shared config loader for the HV_Harness pipeline scripts.

Two config files drive every script:

- `config/<gene_set>.yaml` (gene-set-specific; user-edited per analysis)
- `data/genome_config.yaml` (project-level genome architecture; rarely edited)

Use:

    from _config import load_configs, get_chr_info

    gs_cfg, genome_cfg, chr_map = load_configs(args.config)
    label, subgenome, pair = get_chr_info("Carassius_gibelio",
                                          "NC_068371.1", chr_map)

`load_configs` resolves the gene-set config in this order:
  1. The explicit path passed in
  2. The `HV_HARNESS_CONFIG` environment variable
If neither is given it raises an error pointing at
`config/template.yaml`. The tool does not default to any one gene set.
"""

from __future__ import annotations

import os
import re
import sys
import csv
import gzip
import argparse
from pathlib import Path
from typing import Any

import yaml


PROJECT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_CONFIG = PROJECT_DIR / "config" / "template.yaml"
DEFAULT_GENOME_CONFIG = PROJECT_DIR / "data" / "genome_config.yaml"
ANNOTATIONS_DIR = PROJECT_DIR / "data" / "annotations"


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _resolve_gene_set_config(explicit: str | Path | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("HV_HARNESS_CONFIG")
    if env:
        return Path(env).resolve()
    raise SystemExit(
        "No gene-set config specified. Pass --config "
        "config/<your_gene_set>.yaml, or set the HV_HARNESS_CONFIG "
        "environment variable. To start a new gene set, copy "
        f"{TEMPLATE_CONFIG} and edit it."
    )


def load_gene_set_config(path: str | Path | None = None) -> dict:
    p = _resolve_gene_set_config(path)
    with open(p) as fh:
        cfg = yaml.safe_load(fh)
    cfg["__path__"] = str(p)
    return cfg


def load_genome_config(path: str | Path | None = None) -> dict:
    p = Path(path).resolve() if path else DEFAULT_GENOME_CONFIG
    with open(p) as fh:
        cfg = yaml.safe_load(fh)
    cfg["__path__"] = str(p)
    return cfg


def load_configs(gene_set_path: str | Path | None = None,
                 genome_path: str | Path | None = None
                 ) -> tuple[dict, dict, dict]:
    """Load both configs and derive the chromosome mapping table.

    Returns: (gene_set_cfg, genome_cfg, chromosome_mappings)
    """
    gs = load_gene_set_config(gene_set_path)
    gc = load_genome_config(genome_path)
    chr_map = derive_chromosome_mappings(gc, gs)
    return gs, gc, chr_map


# ---------------------------------------------------------------------------
# Annotation-file discovery
# ---------------------------------------------------------------------------

def find_annotation_file(species_full_name: str,
                         kind: str,
                         ann_dir: "str | Path | None" = None
                         ) -> "Path | None":
    """Locate a species' GFF or protein FASTA tolerantly.

    The pipeline does not require inputs to keep the canonical
    ``<species>_genomic.gff.gz`` / ``<species>_protein.faa.gz`` names. A
    user may drop in a file under its native RefSeq name (e.g.
    ``GCF_003368295.1_ASM336829v1_protein.faa.gz``) and it will still be
    found, as long as it sits in ``data/annotations/<species>/`` and is
    recognisably a GFF or protein FASTA.

    ``kind`` is ``"gff"`` or ``"protein"``. The canonical name is tried
    first (so an explicitly-named file always wins); then native-named
    fallbacks. Gzipped variants are preferred. If several candidates
    remain, the first (sorted) is used and a NOTE is printed naming the
    others, so an ambiguous folder is visible rather than silently
    resolved. Returns a ``Path`` or ``None`` if nothing matches.

    ``ann_dir`` defaults to the module-level ``ANNOTATIONS_DIR``, read at
    call time so tests can redirect it.
    """
    folder = Path(ANNOTATIONS_DIR if ann_dir is None else ann_dir) / species_full_name
    if not folder.is_dir():
        return None

    if kind == "gff":
        canonical = [f"{species_full_name}_genomic.gff.gz",
                     f"{species_full_name}_genomic.gff"]
        globs = ["*_genomic.gff.gz", "*_genomic.gff", "*.gff.gz", "*.gff"]
    elif kind == "protein":
        canonical = [f"{species_full_name}_protein.faa.gz",
                     f"{species_full_name}_protein.faa"]
        globs = ["*_protein.faa.gz", "*_protein.faa", "*.faa.gz", "*.faa"]
    else:
        raise ValueError(f"unknown annotation kind: {kind!r}")

    for name in canonical:
        p = folder / name
        if p.exists():
            return p

    seen: list[Path] = []
    for pattern in globs:
        for p in sorted(folder.glob(pattern)):
            if p.is_file() and p not in seen:
                seen.append(p)
    if not seen:
        return None
    if len(seen) > 1:
        sys.stderr.write(
            f"NOTE: multiple candidate {kind} files in {folder} — using "
            f"{seen[0].name} (also saw: "
            f"{', '.join(p.name for p in seen[1:])}).\n"
        )
    return seen[0]


# ---------------------------------------------------------------------------
# Chromosome mapping derivation
#
# Chromosome identity is read from each annotation itself, not from a
# hand-maintained accession table. Every NCBI GFF declares, on each
# molecule's `region` feature, a `chromosome=` attribute (e.g.
# `chromosome=A1`, `chromosome=12`) and a `Dbxref=taxon:NNNN`. We read
# those, so a new assembly version of any species works with no config
# edit: drop its GFF in and the labels come from the file. The scan is
# cached next to the GFF (keyed on name+mtime+size) so it runs once per
# annotation, not once per script invocation.
# ---------------------------------------------------------------------------

_REGION_CACHE_VERSION = "2"


def _scan_gff_regions(gff_path: Path) -> "tuple[list[tuple[str, str]], str | None]":
    """Read a GFF's assembled-chromosome ``region`` features.

    Returns ``(rows, taxon)`` where ``rows`` is a list of
    ``(accession, chromosome_value)`` for true chromosome molecules, and
    ``taxon`` is the NCBI taxon id read from the first region's
    ``Dbxref`` (or ``None``).

    Only records flagged ``genome=chromosome`` are kept. NCBI also tags
    many *unplaced* scaffolds with a best-guess ``chromosome=N`` under
    ``genome=genomic``; those are deliberately excluded so a scaffold can
    never be mistaken for a chromosome arm. Mitochondria
    (``genome=mitochondrion``) are likewise skipped.
    """
    rows: list[tuple[str, str]] = []
    taxon: str | None = None
    opener = gzip.open if str(gff_path).endswith(".gz") else open
    with opener(gff_path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9 or parts[2] != "region":
                continue
            acc = parts[0]
            chrom = None
            is_chromosome = False
            for item in parts[8].split(";"):
                if item.startswith("chromosome="):
                    chrom = item[len("chromosome="):].strip()
                elif item == "genome=chromosome":
                    is_chromosome = True
                elif taxon is None and "taxon:" in item:
                    m = re.search(r"taxon:(\d+)", item)
                    if m:
                        taxon = m.group(1)
            if chrom and is_chromosome:
                rows.append((acc, chrom))
    return rows, taxon


def _region_cache_path(species: str, gff_path: Path) -> Path:
    return Path(gff_path).parent / f".{species}.regions.tsv"


def _load_region_cache(cache_path: Path, gff_path: Path
                       ) -> "tuple[list[tuple[str, str]], str | None] | None":
    if not cache_path.exists():
        return None
    try:
        st = gff_path.stat()
        with open(cache_path) as fh:
            header = fh.readline()
            if not header.startswith("#"):
                return None
            meta = dict(
                kv.split("=", 1)
                for kv in header[1:].strip().split("\t")
                if "=" in kv
            )
            if (meta.get("ver") != _REGION_CACHE_VERSION
                    or meta.get("source") != gff_path.name
                    or meta.get("mtime") != str(int(st.st_mtime))
                    or meta.get("size") != str(st.st_size)):
                return None  # annotation changed or stale format -> rebuild
            taxon = meta.get("taxon") or None
            rows: list[tuple[str, str]] = []
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("accession"):
                    continue
                acc, chrom = line.split("\t")
                rows.append((acc, chrom))
            return rows, taxon
    except Exception:
        return None


def _write_region_cache(cache_path: Path, gff_path: Path,
                        taxon: "str | None",
                        rows: "list[tuple[str, str]]") -> None:
    try:
        st = gff_path.stat()
        with open(cache_path, "w") as fh:
            fh.write(f"# ver={_REGION_CACHE_VERSION}\tsource={gff_path.name}"
                     f"\tmtime={int(st.st_mtime)}\tsize={st.st_size}"
                     f"\ttaxon={taxon or ''}\n")
            fh.write("accession\tchromosome\n")
            for acc, chrom in rows:
                fh.write(f"{acc}\t{chrom}\n")
    except OSError:
        pass  # read-only annotations dir: derive in-memory each load


def _scan_gff_regions_cached(species: str, gff_path: Path
                             ) -> "tuple[list[tuple[str, str]], str | None]":
    cached = _load_region_cache(_region_cache_path(species, gff_path), gff_path)
    if cached is not None:
        return cached
    rows, taxon = _scan_gff_regions(gff_path)
    _write_region_cache(_region_cache_path(species, gff_path), gff_path,
                        taxon, rows)
    return rows, taxon


def _check_taxon(sp: dict, taxon: "str | None", gff_path: Path) -> None:
    """Guard against a file dropped into the wrong species folder."""
    expected = sp.get("taxon_id")
    if expected is None or taxon is None:
        return
    if str(expected) != str(taxon):
        raise SystemExit(
            f"Species/file mismatch: {gff_path} reports NCBI taxon "
            f"{taxon}, but data/genome_config.yaml lists "
            f"{sp['full_name']} as taxon {expected}. The wrong annotation "
            f"may be in data/annotations/{sp['full_name']}/."
        )


def _rows_to_map(rows: "list[tuple[str, str]]", rule: str
                 ) -> "dict[str, tuple[str, str, int]]":
    """Interpret scanned (accession, chromosome) rows per rule type."""
    out: dict[str, tuple[str, str, int]] = {}
    if rule == "explicit_ab":
        # Tetraploid whose chromosomes are named A1..An / B1..Bn in the
        # annotation; the letter is the subgenome and the number the
        # homeolog pair.
        for acc, chrom in rows:
            m = re.fullmatch(r"([AB])(\d+)", chrom.strip())
            if m:
                out[acc] = (chrom.strip(), m.group(1), int(m.group(2)))
    elif rule == "diploid":
        # Each numbered chromosome is its own homeolog pair. Non-numeric
        # molecules (mitochondrion, sex chromosomes) are skipped.
        for acc, chrom in rows:
            c = chrom.strip()
            if c.isdigit():
                n = int(c)
                out[acc] = (f"chr{n}", "diploid", n)
    else:
        raise ValueError(f"rule {rule!r} is not GFF-derivable")
    return out


def _build_lookup_map(sp: dict, gff_path: "Path | None"
                      ) -> "dict[str, tuple[str, str, int]]":
    """Map a tetraploid that lacks A/B labels in its annotation via a
    pre-built subgenome lookup TSV (currently goldfish). Validated
    against the assembly: the lookup's accessions must actually appear in
    the GFF, so a renumbered/replaced assembly fails loudly instead of
    silently mis-labelling.
    """
    lookup_rel = sp.get("subgenome_lookup")
    if not lookup_rel:
        raise SystemExit(
            f"{sp['full_name']} uses chromosome_rule from_lookup_file but "
            f"has no `subgenome_lookup` path in data/genome_config.yaml."
        )
    lookup_path = PROJECT_DIR / lookup_rel
    if not lookup_path.exists():
        raise SystemExit(
            f"{sp['full_name']}: subgenome lookup {lookup_path} not found. "
            f"Regenerate it with scripts/build_subgenome_lookup.py."
        )

    mapping: dict[str, tuple[str, str, int]] = {}
    with open(lookup_path) as fh:
        reader = csv.DictReader(
            (l for l in fh if not l.startswith("#")), delimiter="\t",
        )
        for row in reader:
            acc = row.get("goldfish_accession") or row.get("accession")
            sub = row.get("subgenome", "")
            pair = row.get("homeolog_number") or row.get("homeolog_pair")
            label = (row.get("goldfish_chr")
                     or row.get("assigned_label")
                     or row.get("label", acc))
            if acc and sub and pair:
                mapping[acc] = (label, sub, int(pair))

    # Validate against the actual assembly when its GFF is present.
    if gff_path is not None:
        rows, taxon = _scan_gff_regions_cached(sp["full_name"], gff_path)
        _check_taxon(sp, taxon, gff_path)
        gff_accs = {acc for acc, _ in rows}
        if gff_accs and not (set(mapping) & gff_accs):
            raise SystemExit(
                f"{sp['full_name']}: the subgenome lookup "
                f"({lookup_path.name}) does not match the assembly in "
                f"data/annotations/{sp['full_name']}/ — none of its "
                f"accessions appear in {gff_path.name}. The assembly was "
                f"likely renumbered or replaced; regenerate the lookup with "
                f"scripts/build_subgenome_lookup.py."
            )
    return mapping


def derive_chromosome_mappings(genome_cfg: dict,
                               gene_set_cfg: dict | None = None) -> dict:
    """Build the {species: {accession: (label, subgenome, pair)}} dict.

    Chromosome identity is read from each species' annotation (see the
    section comment above), driven by a per-species ``chromosome_rule``
    in ``data/genome_config.yaml``:

      - ``explicit_ab``     tetraploid with A1/B1-style chromosome names
                            (Cyprinus_carpio, Carassius_gibelio)
      - ``diploid``         each numbered chromosome is its own pair
                            (Danio_rerio and any added comparator)
      - ``from_lookup_file``tetraploid lacking A/B labels; mapped via a
                            pre-built subgenome lookup (Carassius_auratus)

    A species whose annotation is absent is skipped (a warning is printed
    for core / primary roles). A present annotation that yields no
    chromosome mapping raises, rather than silently leaving every gene
    ``unknown``.

    Overrides are then applied in two layers, gene-set winning over
    genome:
      1. genome_config.yaml -> chromosome_mappings.overrides
      2. the gene-set config -> chromosome_overrides

    Returns a dict-of-dicts keyed by species full_name.
    """
    out: dict[str, dict[str, tuple[str, str, int]]] = {}

    for sp in genome_cfg.get("species", []):
        rule = sp.get("chromosome_rule")
        if not rule:
            continue
        name = sp["full_name"]
        role = sp.get("role", "")
        gff_path = find_annotation_file(name, "gff")

        if gff_path is None:
            # Absent annotation is normal for on-demand comparators; for a
            # core/primary species it is worth flagging, but not fatal
            # (some flows derive mappings before Stage 1 has downloaded).
            if role in ("core", "primary_comparator"):
                sys.stderr.write(
                    f"WARNING: no GFF found for {name} (role={role}); its "
                    f"chromosomes cannot be mapped until an annotation is "
                    f"placed in data/annotations/{name}/.\n"
                )
            out[name] = {}
            continue

        if rule in ("explicit_ab", "diploid"):
            rows, taxon = _scan_gff_regions_cached(name, gff_path)
            _check_taxon(sp, taxon, gff_path)
            mapping = _rows_to_map(rows, rule)
            if not mapping:
                raise SystemExit(
                    f"{name}: no chromosome-level molecules with a "
                    f"`chromosome=` label matched chromosome_rule "
                    f"'{rule}' in {gff_path.name}. The assembly may be "
                    f"scaffold-level, or the rule is wrong for this "
                    f"species. Saw {len(rows)} region record(s)."
                )
            out[name] = mapping
        elif rule == "from_lookup_file":
            out[name] = _build_lookup_map(sp, gff_path)
        else:
            raise SystemExit(
                f"Unknown chromosome_rule '{rule}' for {name} in "
                f"data/genome_config.yaml (expected explicit_ab, diploid, "
                f"or from_lookup_file)."
            )

    # Apply overrides for unplaced scaffolds and similar special cases.
    # Genome-level layer first, then the gene-set layer on top so a
    # gene set's curation discoveries win.
    override_layers = [
        genome_cfg.get("chromosome_mappings", {}).get("overrides", {}) or {},
    ]
    if gene_set_cfg:
        override_layers.append(gene_set_cfg.get("chromosome_overrides", {}) or {})
    for layer in override_layers:
        for species, extras in layer.items():
            out.setdefault(species, {})
            for acc, triple in extras.items():
                label, sub, pair = triple
                out[species][acc] = (label, sub, int(pair))

    return out


def get_chr_info(species: str, accession: str,
                 chromosome_mappings: dict) -> tuple[str, str, int | None]:
    """Return (label, subgenome, pair_number) for an accession.

    Falls back to (accession, "unknown", None) if not found.
    """
    return chromosome_mappings.get(species, {}).get(
        accession, (accession, "unknown", None)
    )


# ---------------------------------------------------------------------------
# Convenience: species iteration
# ---------------------------------------------------------------------------

def iter_species(genome_cfg: dict, roles: list[str] | None = None):
    """Yield species entries from the genome config, optionally
    filtered by role (e.g. ["core"] or ["core", "primary_comparator"]).
    """
    for s in genome_cfg["species"]:
        if roles is None or s["role"] in roles:
            yield s


def species_full_names(genome_cfg: dict) -> list[str]:
    return [s["full_name"] for s in genome_cfg["species"]]


# ---------------------------------------------------------------------------
# Argparse helper for scripts
# ---------------------------------------------------------------------------

def add_config_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        default=None,
        help="Path to gene-set config YAML. Falls back to "
             "$HV_HARNESS_CONFIG; required if that is unset. Start from "
             "config/template.yaml.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        metavar="DIR",
        help="Root directory for all outputs. If omitted, outputs go into "
             "the HV_Harness project directory (results/, sequences/). "
             "Set this to a companion folder to keep test-run outputs "
             "separate from the tool itself.",
    )


def resolve_output_dirs(output_dir: "str | Path | None",
                        gene_set: "str | None" = None) -> dict:
    """Return resolved output directory paths for each script stage.

    If output_dir is provided, all outputs are rooted there:
        <output_dir>/results/<gene_set>/identification/
        <output_dir>/results/<gene_set>/explorers/
        <output_dir>/sequences/

    If omitted, defaults to the standard HV_Harness project layout
    (PROJECT_DIR/results/<gene_set>/..., PROJECT_DIR/data/sequences/).

    `gene_set` namespaces identification/ and explorers/ under a
    per-gene-set folder (e.g. results/caspase/identification/), so a
    second gene set run against the same repo lands in its own folder
    instead of sharing results/identification/ with every other gene
    set (namespaced only by filename prefix, previously). If omitted,
    identification/explorers fall back to the un-namespaced
    results/identification, results/explorers layout — callers that
    haven't loaded a gene-set config yet (rare) still work. A re-run of
    the same gene set overwrites its own folder in place; nothing is
    timestamped.

    Usage in each script's main() — load the gene-set config first so
    its name is available:
        gs_cfg, genome_cfg, _ = load_configs(args.config)
        gene_set = gs_cfg["gene_set"]["name"]
        dirs = resolve_output_dirs(args.output_dir, gene_set)
        global RESULTS_DIR, SEQUENCES_DIR   # (whichever apply)
        RESULTS_DIR   = dirs["identification"]
        SEQUENCES_DIR = dirs["sequences"]
    """
    base = Path(output_dir).resolve() if output_dir else PROJECT_DIR
    results_root = base / "results"
    if gene_set:
        results_root = results_root / gene_set
    sequences_dir = (base / "sequences") if output_dir \
        else (PROJECT_DIR / "data" / "sequences")
    return {
        "identification": results_root / "identification",
        "explorers":      results_root / "explorers",
        "sequences":      sequences_dir,
    }


# ──────────────────────────────────────────────────────────────────────
# Progress & hand-off banner (mechanized)
# ──────────────────────────────────────────────────────────────────────
# The banner is the harness's hand-off surface (docs/quick_start.md). It is
# emitted by the scripts — not left to the agent's discretion — so the
# position checklist and the whose-turn hand-off appear at every stage
# boundary and cannot silently drift (Run F4: no banner at the gene-list
# stage; no return at the CP3 boundary). Checkpoint gates are printed here
# too and are NON-SUPPRESSIBLE: batch/unattended mode changes only the
# whose-turn line, never whether a gate prints.

_BANNER_RULE = "━" * 47
_BANNER_THIN = "  " + "─" * 43

# Canonical pipeline position checklist, in order. The script that completes
# a step passes its index as `current`.
BANNER_STEPS = [
    "Stage 1 · Gene group & genomes confirmed",
    "Stage 2 · Search terms designed (CP1)",
    "Stage 3 · Gene list checked, inventory built",
    "CP2 · Review inventory & choose focal species",
    "Stage 4 · Per-pair curation (focal species)",
    "Stage 5 · Empty-slots deep dive (CP3)",
    "Stage 6 · Visualization design (CP4 & CP5)",
]

# Checkpoint gate texts, keyed by id. Printed by the script that sits at the
# boundary; non-suppressible.
CHECKPOINT_GATES = {
    "CP2": "CP2 — inventory review & focal-species choice: confirm the "
           "inventory baseline and name the focal species before per-pair "
           "curation.",
    "CP3": "CP3 — empty-slots deep dive: every empty A/B slot needs an "
           "explicit loss decision; the explorer will refuse to build "
           "without it.",
    "CP4": "CP4 — pre-visualization curation review: sign off the curation "
           "document before building the explorer.",
    "CP5": "CP5 — interpretive layer design: agree the interpretive overlay "
           "with the curator.",
}


def _results_root(output_dir: str | Path | None) -> Path:
    return (Path(output_dir).resolve() / "results") if output_dir \
        else (PROJECT_DIR / "results")


def render_banner(current: int, produced: str | None, next_action: str,
                  your_move: str | None = None,
                  i_continue: str | None = None,
                  parked: str = "(none)",
                  gates: list[str] | None = None) -> str:
    """Render the progress & hand-off banner as a string.

    `current` indexes BANNER_STEPS: earlier steps render ✅, the current one
    ▶️, later ones ⬜. Give exactly one of `your_move` (hand back to the
    curator) or `i_continue` (proceeding autonomously); the whose-turn line is
    never omitted. `gates` are non-suppressible checkpoint-gate lines (look up
    text in CHECKPOINT_GATES).
    """
    lines = [_BANNER_RULE]
    for i, label in enumerate(BANNER_STEPS):
        mark = "✅" if i < current else ("▶️" if i == current else "⬜")
        star = "**" if i == current else ""
        suffix = "   ← now" if i == current else ""
        lines.append(f"  {mark}  {star}{label}{star}{suffix}")
    lines.append(_BANNER_THIN)
    lines.append(f"  ✅ Just produced · {produced or '—'}")
    lines.append(f"  ▶  Next          · {next_action}")
    if i_continue is not None:
        lines.append(f'  ⤷  I\'ll continue · {i_continue} (say "pause" to stop)')
    else:
        lines.append(f"  ⤷  Your move     · {your_move or 'tell me how to proceed'}")
    lines.append(f"  ⏸  Parked        · {parked}")
    for g in (gates or []):
        text = CHECKPOINT_GATES.get(g, g)
        lines.append(f"  ⛔ CHECKPOINT {text}")
        lines.append("     (non-suppressible — batch mode does not waive this)")
    lines.append(_BANNER_RULE)
    return "\n".join(lines)


def emit_banner(current: int, produced: str | None, next_action: str,
                output_dir: str | Path | None = None,
                your_move: str | None = None,
                i_continue: str | None = None,
                parked: str = "(none)",
                gates: list[str] | None = None) -> None:
    """Print the banner to stderr and mirror it to results/SESSION_STATUS.md.

    Called by every pipeline driver at successful completion, so the hand-off
    surface is mechanical rather than discretionary.
    """
    banner = render_banner(current, produced, next_action, your_move,
                           i_continue, parked, gates)
    print("\n" + banner, file=sys.stderr)
    try:
        root = _results_root(output_dir)
        root.mkdir(parents=True, exist_ok=True)
        (root / "SESSION_STATUS.md").write_text(
            "```\n" + banner + "\n```\n", encoding="utf-8")
    except OSError as e:
        print(f"  (note: could not write SESSION_STATUS.md: {e})",
              file=sys.stderr)


def add_unattended_arg(parser: argparse.ArgumentParser) -> None:
    """Shared flag so the banner's whose-turn line reads correctly. Batch
    mode suppresses per-pair dialogue only — it never waives a checkpoint
    gate (those are printed regardless of this flag)."""
    parser.add_argument(
        "--unattended", action="store_true",
        help="Batch/unattended mode: the hand-off line reads 'I'll continue' "
             "instead of 'Your move'. Checkpoint gates still print.",
    )
