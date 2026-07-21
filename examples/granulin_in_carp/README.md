# Second worked example — granulin genes in common carp

This is a smaller, deliberately narrower run than `examples/caspase_in_carp/`.
Its purpose is different too: it exists to demonstrate that the harness is
not caspase-shaped — that the same scripts, playbook, and checkpoint
protocol apply cleanly to an unrelated gene family, run by a different AI
agent. It is not a comprehensive granulin-family curation, and it is not
meant to be read as one.

Focal species: **Cyprinus carpio** (common carp) only, curated against the
*Danio rerio* (zebrafish) comparator. Per-pair curation covers three
homeolog pairs (3, 19, 24) — the pairs where common carp itself carries a
granulin-family member. The curation document's own header records its
status accurately: *"collaborative draft in progress."* That's intentional
here, not a gap to fill — the goal was proof of generality, not a finished
granulin-family inventory.

**A known, deliberately unaddressed observation.** The gene inventory (which
covers all four species, not just the focal one) shows *Carassius gibelio*
(Prussian carp) carrying granulin-family members at two additional homeolog
pairs (5 and 25) that do not appear anywhere in the common-carp gene list.
This curation does not investigate that — no per-pair section, no empty-slot
flag, no claim about what it means. The harness's per-pair procedure only
generates a section where the *focal* species has a member on at least one
side of the pair, so a pair entirely absent from the focal species doesn't
surface on its own. Flagging that boundary here rather than silently
omitting it, but deliberately not drawing any conclusion about common-carp
granulin biology from it.

## Contents

**`granulin_config_as_run_2026-07-21.yaml`** — the gene-set config that
drove this run, frozen (matches the naming convention used for the caspase
example's config snapshot).

**`example_identification/`**
- `Ccar_granulin_curation.md` — the per-pair curation document (pairs 3, 19, 24).
- `Ccar_granulin_curation_data.json` — the structured curation data behind the explorer.
- `granulin_gene_inventory.tsv` — the full gene inventory (all four species).
- `granulin_genes_all_species.tsv` — the raw Stage-2 candidate gene list.
- `granulin_synteny_extraction_all_pairs.txt` — the flanking-neighbourhood evidence behind the curation's synteny claims.

**`example_explorers/`**
- `Ccar_granulin_hierarchy.html` — the interactive hierarchy explorer for this run. Self-contained; open directly in a browser.

## On reproducibility

Same model as the caspase example: this is a historical snapshot, not a
live output, and won't regenerate automatically if the scripts or config
change later.
