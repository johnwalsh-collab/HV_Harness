# Worked example — caspase genes in polyploid carp

This is the finished, signed-off worked example that validated the HV_Harness
methodology. The caspase gene family was curated independently in each of the
three focal cyprinid carp species — *Cyprinus carpio* (common carp), *Carassius
gibelio* (Prussian carp), and *Carassius auratus* (goldfish) — each against the
*Danio rerio* (zebrafish) comparator, per the harness's one-focal-species-at-a-time
model (`docs/curation_playbook.md` §5.1). All three runs are bundled here so the
example is self-contained: nothing in this folder depends on a companion project
or an external host.

Curation completed and signed off **2026-06-30** (Checkpoints 1–5 all cleared;
see each curation document's revision history for the checkpoint trail).

## Contents

**`caspase_config_as_run_2026-06-30.yaml`** — the exact gene-set config that
drove this run, frozen. Byte-identical to `config/caspase_example.yaml` as of
2026-06-30; kept here too so it sits alongside the outputs it produced and
can't be mistaken for the current canonical copy. If `config/caspase_example.yaml`
is edited later, this one stays exactly as it was — a record of what actually
generated the files below, not a stale duplicate.

**`caspase_workflow_methods.md`** — a draft Methods section describing the
procedure as applied to this specific run, written for reuse in the companion
manuscript. Complements `docs/curation_playbook.md` (the general methodology)
with the as-run specifics (accessions, parameters, dates).

**`example_identification/`**
- `Cgib_caspase_curation.md`, `Ccar_caspase_curation.md`, `Caur_caspase_curation.md`
  — the per-pair curation document for each focal species: evidence, synteny,
  confidence calls, and the empty-slot/candidate-loss assessments.
- `Carassius_gibelio_caspase_curation_data.json`,
  `Cyprinus_carpio_caspase_curation_data.json`,
  `Carassius_auratus_caspase_curation_data.json` — the structured curation data
  behind each explorer below (Cgib ↔ *Carassius_gibelio*, Ccar ↔ *Cyprinus_carpio*,
  Caur ↔ *Carassius_auratus*; these are named by full species name rather than
  the short code used on the curation docs and explorers).
- `caspase_gene_inventory.tsv` — the full gene inventory: one row per caspase
  gene across all four species (three carps + zebrafish reference).
- `caspase_genes_all_species.tsv` — the raw Stage-2 candidate gene list, before
  the inventory was built (Checkpoint 1 output).
- `caspase_synteny_extraction_all_pairs.txt` — the flanking-gene-neighbourhood
  evidence behind every synteny claim made in the three curation documents.

**`example_explorers/`**
- `Cgib_caspase_hierarchy.html`, `Ccar_caspase_hierarchy.html`,
  `Caur_caspase_hierarchy.html` — self-contained interactive hierarchy explorers,
  one per focal species. Open directly in a browser; no server, network, or
  build step required.

## On reproducibility

This is a historical snapshot, not a live output — it will not regenerate
automatically if the scripts, playbook, or `config/caspase_example.yaml`
change later. It stands as the worked example referenced by
`docs/curation_playbook.md` (§5.5, §5.6) and the companion paper. To reproduce
or extend it, follow `docs/quick_start.md` with `config/caspase_example.yaml`
(or a copy of it) as the starting config.
