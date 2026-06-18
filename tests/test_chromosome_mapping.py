#!/usr/bin/env python3
"""Fixture-based tests for the genome layer (chromosome mapping + file
discovery) in scripts/_config.py.

These lock the invariants that make the harness work off *any* annotation
file or version — the path that previously broke silently when the
zebrafish assembly was updated and when a protein FASTA arrived under its
native RefSeq name. No network, no real genome data: every fixture is a
tiny in-memory GFF written to a temp dir.

  - derive_chromosome_mappings reads labels from the GFF's `region`
    features (genome=chromosome only), per the per-species
    `chromosome_rule`:
      * diploid      -> chr1..chrN, each its own pair
      * explicit_ab  -> A1/B1 -> (label, A|B, pair)
  - a genome=genomic scaffold tagged with a guessed chromosome=N is NOT
    treated as a chromosome (no scaffold leak)
  - a present annotation that maps nothing raises (no silent `unknown`)
  - a taxon that disagrees with genome_config raises (wrong-folder guard)
  - a subgenome lookup that doesn't match the assembly raises
  - gene-set chromosome_overrides win over derived labels
  - find_annotation_file tolerates native RefSeq filenames and reports
    None when nothing matches

Run standalone (no pytest required):
    python tests/test_chromosome_mapping.py     # exit 0 = all pass
It is also pytest-discoverable (test_* functions).
"""

import gzip
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import _config  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _region(acc, chrom, taxon="7955", genome="chromosome"):
    attrs = f"ID={acc}:1..100;Dbxref=taxon:{taxon};Name={chrom}"
    if chrom is not None:
        attrs += f";chromosome={chrom}"
    attrs += f";genome={genome}"
    return "\t".join([acc, "RefSeq", "region", "1", "100", ".", "+", ".", attrs])


def _write_gff(folder: Path, species: str, region_lines):
    folder.mkdir(parents=True, exist_ok=True)
    gff = folder / f"{species}_genomic.gff.gz"
    with gzip.open(gff, "wt") as fh:
        fh.write("##gff-version 3\n")
        for line in region_lines:
            fh.write(line + "\n")
    return gff


@contextmanager
def _annotations(species_regions: dict):
    """Build a temp data/annotations tree, point _config at it, restore
    afterwards. `species_regions` maps species_full_name -> [region lines]."""
    old = _config.ANNOTATIONS_DIR
    with tempfile.TemporaryDirectory() as d:
        ann = Path(d) / "annotations"
        for sp, regions in species_regions.items():
            _write_gff(ann / sp, sp, regions)
        _config.ANNOTATIONS_DIR = ann
        try:
            yield ann
        finally:
            _config.ANNOTATIONS_DIR = old


def _genome_cfg(species_entries, overrides=None):
    cfg = {"species": species_entries}
    if overrides is not None:
        cfg["chromosome_mappings"] = {"overrides": overrides}
    return cfg


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_diploid_derivation():
    regions = [_region("NC_900001.1", "1"),
               _region("NC_900002.1", "2"),
               _region("NC_900003.1", "3")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg([{"full_name": "Danio_test", "role": "primary_comparator",
                            "chromosome_rule": "diploid", "taxon_id": 7955}])
        m = _config.derive_chromosome_mappings(cfg)["Danio_test"]
    assert m["NC_900001.1"] == ("chr1", "diploid", 1), m
    assert m["NC_900003.1"] == ("chr3", "diploid", 3), m
    assert len(m) == 3, m


def test_explicit_ab_derivation():
    regions = [_region("NC_1.1", "A1", taxon="7962"),
               _region("NC_2.1", "A2", taxon="7962"),
               _region("NC_3.1", "B1", taxon="7962"),
               _region("NC_4.1", "B2", taxon="7962")]
    with _annotations({"Cyprinus_test": regions}):
        cfg = _genome_cfg([{"full_name": "Cyprinus_test", "role": "core",
                            "chromosome_rule": "explicit_ab", "taxon_id": 7962}])
        m = _config.derive_chromosome_mappings(cfg)["Cyprinus_test"]
    assert m["NC_1.1"] == ("A1", "A", 1), m
    assert m["NC_3.1"] == ("B1", "B", 1), m
    assert len(m) == 4, m


def test_genome_genomic_scaffold_excluded():
    # A real chromosome plus a scaffold NCBI assigned a guessed chromosome=1.
    regions = [_region("NC_900001.1", "1"),
               _region("NW_88888.1", "1", genome="genomic")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg([{"full_name": "Danio_test", "role": "primary_comparator",
                            "chromosome_rule": "diploid", "taxon_id": 7955}])
        m = _config.derive_chromosome_mappings(cfg)["Danio_test"]
    assert "NC_900001.1" in m and "NW_88888.1" not in m, m
    assert len(m) == 1, m


def test_diploid_skips_nonnumeric():
    regions = [_region("NC_900001.1", "1"),
               _region("NC_900099.1", "MT"),
               _region("NC_900098.1", "Z")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg([{"full_name": "Danio_test", "role": "primary_comparator",
                            "chromosome_rule": "diploid", "taxon_id": 7955}])
        m = _config.derive_chromosome_mappings(cfg)["Danio_test"]
    assert set(m) == {"NC_900001.1"}, m


def test_unmappable_assembly_raises():
    # GFF present but only scaffolds -> no chromosome maps -> loud failure,
    # not a silent map of `unknown` (the zebrafish regression).
    regions = [_region("NW_1.1", "1", genome="genomic")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg([{"full_name": "Danio_test", "role": "primary_comparator",
                            "chromosome_rule": "diploid", "taxon_id": 7955}])
        try:
            _config.derive_chromosome_mappings(cfg)
        except SystemExit:
            return
    raise AssertionError("expected SystemExit for an unmappable assembly")


def test_new_assembly_version_just_works():
    # The whole point: brand-new accession scheme, no config change. Labels
    # come from the file, so an updated assembly maps correctly.
    regions = [_region("CM_NEW_77.1", "1"), _region("CM_NEW_78.1", "2")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg([{"full_name": "Danio_test", "role": "primary_comparator",
                            "chromosome_rule": "diploid", "taxon_id": 7955}])
        m = _config.derive_chromosome_mappings(cfg)["Danio_test"]
    assert m["CM_NEW_77.1"] == ("chr1", "diploid", 1), m


def test_taxon_mismatch_raises():
    regions = [_region("NC_900001.1", "1", taxon="7955")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg([{"full_name": "Danio_test", "role": "primary_comparator",
                            "chromosome_rule": "diploid", "taxon_id": 9999}])
        try:
            _config.derive_chromosome_mappings(cfg)
        except SystemExit:
            return
    raise AssertionError("expected SystemExit for a taxon mismatch")


def test_taxon_check_lenient_when_unset():
    # taxon_id null (on-demand comparators) -> no guard, no crash.
    _config._check_taxon({"full_name": "X", "taxon_id": None}, "7955", Path("x"))
    _config._check_taxon({"full_name": "X", "taxon_id": 7955}, None, Path("x"))


def test_overrides_win():
    regions = [_region("NC_900001.1", "1")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg(
            [{"full_name": "Danio_test", "role": "primary_comparator",
              "chromosome_rule": "diploid", "taxon_id": 7955}],
            overrides={"Danio_test": {"NW_unplaced.1": ["unplaced", "diploid", 9]}},
        )
        gs = {"chromosome_overrides":
              {"Danio_test": {"NC_900001.1": ["override", "diploid", 1]}}}
        m = _config.derive_chromosome_mappings(cfg, gs)["Danio_test"]
    assert m["NW_unplaced.1"] == ("unplaced", "diploid", 9), m   # genome layer
    assert m["NC_900001.1"] == ("override", "diploid", 1), m     # gene-set wins


def test_lookup_mismatch_raises():
    # from_lookup_file whose accessions don't appear in the assembly -> raise.
    regions = [_region("NC_REAL_1.1", "1", taxon="7957")]
    with _annotations({"Carassius_test": regions}) as ann:
        lookup = ann.parent / "lookup.tsv"
        lookup.write_text(
            "goldfish_chr\tgoldfish_accession\tsubgenome\thomeolog_number\n"
            "chr1\tNC_STALE_9.9\tA\t1\n")
        # An absolute subgenome_lookup path resolves cleanly: in
        # _build_lookup_map, PROJECT_DIR / <abs path> collapses to the
        # abs path.
        cfg = _genome_cfg([{"full_name": "Carassius_test", "role": "core",
                            "chromosome_rule": "from_lookup_file",
                            "taxon_id": 7957,
                            "subgenome_lookup": str(lookup)}])
        try:
            _config.derive_chromosome_mappings(cfg)
        except SystemExit:
            return
    raise AssertionError("expected SystemExit when the lookup misses the assembly")


def test_find_annotation_file():
    with _annotations({}) as ann:
        sp = ann / "Sp_one"
        sp.mkdir(parents=True)
        # native RefSeq names, not the canonical <species>_ names
        (sp / "GCF_123_ASM1_protein.faa.gz").write_bytes(b"")
        (sp / "GCF_123_ASM1_genomic.gff.gz").write_bytes(b"")
        prot = _config.find_annotation_file("Sp_one", "protein", ann_dir=ann)
        gff = _config.find_annotation_file("Sp_one", "gff", ann_dir=ann)
        assert prot is not None and prot.name.endswith("_protein.faa.gz"), prot
        assert gff is not None and gff.name.endswith("_genomic.gff.gz"), gff
        # canonical name wins when present
        (sp / "Sp_one_protein.faa.gz").write_bytes(b"")
        assert _config.find_annotation_file("Sp_one", "protein", ann_dir=ann).name \
            == "Sp_one_protein.faa.gz"
        # nothing for an empty species
        (ann / "Sp_two").mkdir()
        assert _config.find_annotation_file("Sp_two", "gff", ann_dir=ann) is None
        assert _config.find_annotation_file("Missing", "gff", ann_dir=ann) is None


def test_region_cache_roundtrip():
    regions = [_region("NC_900001.1", "1"), _region("NC_900002.1", "2")]
    with _annotations({"Danio_test": regions}):
        cfg = _genome_cfg([{"full_name": "Danio_test", "role": "primary_comparator",
                            "chromosome_rule": "diploid", "taxon_id": 7955}])
        first = _config.derive_chromosome_mappings(cfg)
        # second call hits the on-disk cache; must be identical
        second = _config.derive_chromosome_mappings(cfg)
    assert first == second, "cache reload changed the mapping"


def _run():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run())
