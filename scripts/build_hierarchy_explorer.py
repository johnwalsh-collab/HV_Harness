#!/usr/bin/env python3
"""
Build the interactive hierarchy explorer (output #2 of the project)
from a curation-data JSON file plus the gene-set / genome configs.

Generic Stage 5 driver. It reads a curation-data JSON file describing
the pairs / slots / genes and renders a self-contained HTML by
substituting the data into the template at
`scripts/templates/hierarchy_explorer.html`. The JSON format is
documented in `scripts/templates/CURATION_DATA_SCHEMA.md`.

To build an explorer for a gene set you need:

1. A curation-data JSON file describing the pairs / slots / genes
   (typically derived from the curation markdown by the AI assistant
   during Stage 3e).
2. A gene-set config (`config/<gene_set>.yaml`) — for the title and
   homeolog pair list.
3. A genome config (`data/genome_config.yaml`) — for species names.

Usage:
    python build_hierarchy_explorer.py \
        --species <Genus_species> \
        --curation-data results/<gene_set>/identification/<short>_<gene_set>_curation_data.json \
        [--config config/<gene_set>.yaml]

Output:
    results/<gene_set>/explorers/<species_short>_<gene_set>_hierarchy.html
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import (PROJECT_DIR, add_config_arg, add_unattended_arg, emit_banner,
                     resolve_output_dirs, load_configs, iter_species)

TEMPLATE_PATH = PROJECT_DIR / "scripts" / "templates" / "hierarchy_explorer.html"
EXPLORERS_DIR = PROJECT_DIR / "results" / "explorers"

# Values the template's renderer acts on. Anything else would be
# silently treated as a normal functional gene / un-searched slot, so we
# reject it at build time rather than let the explorer miscount.
ALLOWED_STATUS = {"ok", "pseudo", "artefact", "candidate_nonfunctional"}
ALLOWED_LOSS = {"searched", "confirmed", "na"}  # 'confirmed' = kept alias of 'searched'


def validate_curation(curation: dict) -> None:
    """Fail loudly on any gene `status` or slot `*_loss` value the
    template does not handle (the F3 / audit-#4 silent-miscount class)."""
    errors: list[str] = []
    for pair, pdata in curation.items():
        if not isinstance(pdata, dict):
            continue
        for si, slot in enumerate(pdata.get("slots", []) or []):
            for side in ("A", "B"):
                for g in (slot.get(side) or []):
                    st = g.get("status", "ok")
                    if st not in ALLOWED_STATUS:
                        errors.append(
                            f"pair {pair} slot {si} {side} gene "
                            f"{g.get('id', g.get('role', '?'))}: status={st!r}")
                loss = slot.get(f"{side}_loss")
                if loss not in (None, "") and loss not in ALLOWED_LOSS:
                    errors.append(f"pair {pair} slot {si}: {side}_loss={loss!r}")
    if errors:
        raise SystemExit(
            "Curation data has values the explorer would silently "
            "miscount:\n  " + "\n  ".join(errors)
            + f"\n\nAllowed status: {sorted(ALLOWED_STATUS)}"
            + f"\nAllowed *_loss: {sorted(ALLOWED_LOSS)} (or omit the field)."
            + "\nSee scripts/templates/CURATION_DATA_SCHEMA.md."
        )


def validate_cp3_complete(curation: dict) -> None:
    """Hard CP3 gate: every EMPTY A/B slot must carry an explicit loss
    decision before the explorer will build.

    An omitted loss field used to render silently as "no specific search
    done" even after the CP3 sweep had been performed (Run F4: searched
    slots still read as un-searched, because the agent left the field unset).
    Requiring an explicit value converts that silent default into a forced
    decision: deliberate non-search is expressible as `na`, but never by
    omission. The explorer therefore cannot be built until the empty-slots
    deep dive has been recorded for every empty slot.
    """
    missing: list[str] = []
    for pair, pdata in curation.items():
        if not isinstance(pdata, dict):
            continue
        for si, slot in enumerate(pdata.get("slots", []) or []):
            for side in ("A", "B"):
                has_genes = bool(slot.get(side))
                loss = slot.get(f"{side}_loss")
                if not has_genes and loss in (None, ""):
                    missing.append(f"pair {pair} slot {si} side {side}")
    if missing:
        raise SystemExit(
            "CP3 (empty-slots deep dive) is incomplete — these empty slots "
            "carry no explicit loss decision, so the explorer will not "
            "build:\n  " + "\n  ".join(missing)
            + "\n\nSet each empty slot's `A_loss`/`B_loss` to one of "
            f"{sorted(ALLOWED_LOSS)}: use 'searched' (in-region sweep done → "
            "candidate loss · annotation-level) or 'na' (deliberately not "
            "searched). This is the CP3 return; batch mode does not waive it. "
            "See playbook §6.1 and scripts/templates/CURATION_DATA_SCHEMA.md."
        )


def resolve_render_pairs(curation: dict, homeolog_pairs: list) -> list:
    """Authoritative pair list (and order) for the explorer to render.

    The template renders every layer by iterating GENE_SET_PAIRS. Driving
    that off config `classification.homeolog_pairs` alone meant an empty or
    stale config list silently blanked or truncated the explorer (the
    2026-06-17 failure). So the **curation JSON is the source of truth** for
    which pairs carry curated members; config `homeolog_pairs` is treated
    only as an optional *ordering hint*. This makes drift impossible: every
    curated pair always renders.

    Order: config-listed pairs that exist in the curation come first (in
    config order), then any remaining curated pairs in numeric order. Pairs
    listed in config but absent from the curation are skipped (they would
    otherwise render as empty cards). Raises only when the curation has no
    pairs at all — there is then genuinely nothing to render.
    """
    curated = sorted(curation.keys())
    if not curated:
        raise SystemExit(
            "Curation data contains no homeolog pairs — nothing to render. "
            "The curation JSON should be a non-empty object keyed by pair "
            "number. See scripts/templates/CURATION_DATA_SCHEMA.md.")
    cfg = list(homeolog_pairs or [])
    ordered = [p for p in cfg if p in curation] + \
              [p for p in curated if p not in cfg]
    # Surface drift without failing — every curated pair still renders.
    if not cfg:
        print(f"  note: config homeolog_pairs is empty — pair list derived "
              f"from the curation data: {ordered}")
    else:
        missing = [p for p in curated if p not in cfg]
        extra = [p for p in cfg if p not in curation]
        if missing:
            print(f"  note: config homeolog_pairs omits curated pair(s) "
                  f"{missing} — auto-included from the curation data")
        if extra:
            print(f"  note: config homeolog_pairs lists pair(s) {extra} not "
                  f"in the curation data — skipped")
    return ordered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_arg(parser)
    parser.add_argument("--species", required=True,
                        help="Full species name (e.g. Carassius_gibelio).")
    parser.add_argument("--curation-data", required=True,
                        help="Path to the curation-data JSON file.")
    parser.add_argument("--output", default=None,
                        help="Optional output path (default: "
                             "results/<gene_set>/explorers/<short>_<gene_set>_hierarchy.html).")
    add_unattended_arg(parser)
    args = parser.parse_args()

    global EXPLORERS_DIR
    gs_cfg, genome_cfg, _ = load_configs(args.config)
    gene_set = gs_cfg["gene_set"]["name"]
    display_name = gs_cfg["gene_set"].get("display_name", gene_set)

    dirs = resolve_output_dirs(args.output_dir, gene_set)
    EXPLORERS_DIR = dirs["explorers"]
    homeolog_pairs = list(gs_cfg.get("classification", {}).get("homeolog_pairs") or [])

    species_meta = {s["full_name"]: s for s in iter_species(genome_cfg)}
    if args.species not in species_meta:
        sys.exit(f"Species {args.species!r} not in genome config. "
                 f"Known: {sorted(species_meta)}")
    sp = species_meta[args.species]
    species_display = f"{args.species.replace('_', ' ')} ({sp['common_name'].lower()})"
    short = sp["short_code"]

    # Load curation data
    curation_path = Path(args.curation_data)
    if not curation_path.exists():
        sys.exit(f"Curation data not found: {curation_path}")
    curation = json.loads(curation_path.read_text())
    # JSON object keys are strings; normalise to ints for the JS side
    # (the renderer indexes pairs by integer keys).
    curation_int_keys = {int(k): v for k, v in curation.items()}

    # Reject unrenderable status / loss values before building (loud, not
    # silent). See CURATION_DATA_SCHEMA.md.
    validate_curation(curation_int_keys)

    # Hard CP3 gate: refuse to build until every empty slot has an explicit
    # loss decision (the Run F4 failure). batch mode does not waive this.
    validate_cp3_complete(curation_int_keys)

    # Derive the render pair list from the curation data (authoritative),
    # using config homeolog_pairs only as an ordering hint. This makes it
    # impossible for an empty/stale config list to blank or truncate the
    # explorer; raises only if the curation itself has no pairs.
    render_pairs = resolve_render_pairs(curation_int_keys, homeolog_pairs)

    # Load template
    if not TEMPLATE_PATH.exists():
        sys.exit(f"Template not found: {TEMPLATE_PATH}")
    html = TEMPLATE_PATH.read_text()

    # Substitute placeholders
    species_name = args.species.replace('_', ' ')
    title = f"{display_name} hierarchy explorer — {species_name}"
    categories = (gs_cfg.get("visualization", {}) or {}).get("categories", [])

    html = html.replace("__TITLE__", title)
    html = html.replace("__GENE_SET_DISPLAY__", display_name)
    html = html.replace("__SPECIES_ITALIC__", species_name)
    html = html.replace("__CURATION_SOURCE__", str(curation_path))
    html = html.replace("__PAIRS_JSON__", json.dumps(curation_int_keys, indent=2))
    html = html.replace("__GENE_SET_PAIRS__", json.dumps(render_pairs))
    html = html.replace("__CATEGORIES_JSON__", json.dumps(categories, indent=2))

    EXPLORERS_DIR.mkdir(parents=True, exist_ok=True)
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = EXPLORERS_DIR / f"{short}_{gene_set}_hierarchy.html"
    out_path.write_text(html)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")

    emit_banner(
        current=6,
        produced=str(out_path),
        next_action="CP5 — design the interpretive layer (category labels / "
                    "colours, framing) with the curator; sanity-check the "
                    "explorer against the curation document.",
        output_dir=args.output_dir,
        your_move="open the explorer, then design the interpretive overlay",
        gates=["CP5"],
    )


if __name__ == "__main__":
    main()
