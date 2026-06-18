# Curation data schema (hierarchy explorer input)

`scripts/build_hierarchy_explorer.py` consumes a JSON file describing
the curated gene set in the structure the hierarchy explorer renders.
This document is the schema. The file is conventionally named
`results/identification/<species_short>_<gene_set>_curation_data.json`
and is produced during Stage 3e per-pair curation (see "How this is
produced" below). The worked example (caspase in *C. gibelio*) is one
instance of this format.

## Top-level shape

A JSON object keyed by integer homeolog-pair number. Each value
describes the slot structure of that pair.

```json
{
  "1": { "zf_chr": 1, "zf_locus": "...", "note": "...", "slots": [...] },
  "3": { "zf_chr": 3, "zf_locus": "...", "note": "...", "slots": [...] },
  ...
}
```

## Pair object

| Field | Type | Required | Description |
|---|---|---|---|
| `zf_chr` | int | yes | Zebrafish chromosome that maps to this homeolog pair |
| `zf_locus` | string | yes | Plain-language description of what's at the zebrafish locus |
| `note` | string | yes | Curator's narrative about the pair's overall pattern |
| `slots` | array | yes | One entry per homeolog slot at this pair (see below) |

## Slot object

A slot is one homeolog "role" — typically a gene at the pair with both
an A-subgenome copy and a B-subgenome copy. Tandem clusters and lost
slots are both modelled by appropriate `A`/`B` arrays.

| Field | Type | Required | Description |
|---|---|---|---|
| `label` | string | yes | Short label for the slot (e.g. `"casp3a"`, `"caspb"`) |
| `sub` | string | no | Sub-categorisation displayed under the label |
| `category` | string | yes | Functional category — drives colour. Caspase example uses `executioner` / `initiator` / `inflammatory` |
| `ambiguous` | bool | no | True if the slot represents an identity that synteny can't resolve |
| `badge` | string | no | Short tag rendered alongside the label (e.g. `"identity unresolved"`) |
| `note` | string | no | Optional slot-level narrative beyond what `sub` carries |
| `A` | array | yes | A-subgenome gene entries (empty if A is lost) |
| `B` | array | yes | B-subgenome gene entries (empty if B is lost) |
| `A_loss` | string | yes *if `A` is empty* | Loss state of the A side when `A` is empty (see values below) |
| `B_loss` | string | yes *if `B` is empty* | Loss state of the B side when `B` is empty (see values below) |

**`A_loss` / `B_loss` values** (read by the explorer's `renderSlotSide`):

| Value | Rendered label | Meaning |
|---|---|---|
| `"searched"` | `candidate loss · annotation-level` | The CP3 in-region sweep was done and returned negative. It renders as the *hedged* "candidate loss · annotation-level" (there is no separate sequence-level "confirmed loss" state in this view). **Set it as part of writing the CP3 outcome**, so the per-pair holding state and the CP3 result can't drift apart. |
| `"confirmed"` | `candidate loss · annotation-level` | Deprecated alias of `"searched"`, still accepted so older curation JSONs keep working. Prefer `"searched"` in new data. |
| `"na"` | `—` | No loss claim for this empty side: an excluded/artefact slot, or a slot the curator deliberately chose **not** to search. This is the explicit way to record "no claim / not searched" — by decision, never by omission. |

> **CP3 hard gate (Run F4).** An empty slot side (`A` or `B` empty) **must**
> carry an explicit `*_loss` value. Omitting the field used to render silently
> as "no specific search done" even after CP3 had searched the slot — the
> field would just be left unset. `build_hierarchy_explorer.py` now **refuses
> to build** (exit 1, nothing written) if any empty slot lacks a loss
> decision, listing the exact slots. Deliberate non-search is expressible as
> `"na"`; what is no longer possible is leaving it silent. This is the CP3
> return made correct-by-construction, and batch mode does not waive it.

## Gene entry

Each element of the `A` and `B` arrays is a gene at that subgenome+slot.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | NCBI Gene ID |
| `role` | string | yes | Plain-language role at the slot (`"casp3a"`, `"caspb pseudogene"`, etc.) |
| `aa` | int | no | Protein length in amino acids |
| `ncbi` | string | yes | NCBI annotation name as displayed (may differ from `role` when curation overrides naming) |
| `category` | string | yes | Functional category (same set as the slot's `category` field) |
| `confidence` | string | yes | `high` / `medium` / `low` |
| `status` | string | yes | `ok` / `pseudo` / `artefact` / `candidate_nonfunctional` (see note) |

**`status` values** — the explorer's renderer acts on four values:

| Value | Meaning | Layer-2 metric | Layer-3 functional counts |
|---|---|---|---|
| `ok` | normal functional gene | — | included |
| `pseudo` | NCBI-annotated pseudogene (gene_biotype=pseudogene) | "pseudogenes" | excluded |
| `artefact` | assembly artefact (e.g. subtelomeric duplicate) | "assembly artefacts" | excluded |
| `candidate_nonfunctional` | a copy the curator judges likely non-functional from annotation-level evidence (truncated, motif-less, minimal expression) but which is **not** a formally annotated pseudogene or an assembly artefact | "candidate non-functional" | excluded |

`candidate_nonfunctional` is the correct home for the truncated, motif-less
copies that would otherwise be forced into `pseudo` (over-claims a formal
pseudogene call) or `ok` (renders them as functional). It is rendered struck
through and excluded from functional totals, like `pseudo`/`artefact`.

**Validation is enforced at build time.** `build_hierarchy_explorer.py` rejects
any `status` outside this set and any `A_loss`/`B_loss` outside
`searched` / `confirmed` / `na`, with an error naming the offending entry —
so a mistyped or unsupported value fails the build instead of silently
miscounting (the Run F3 / audit-#4 failure mode). Earlier drafts listed
`check` / `suspect`; those are **not** accepted — use `candidate_nonfunctional`.

## How this is produced

During Stage 3e per-pair curation, the AI assistant collects the slot
decisions for each pair as the curator works through them and produces
this JSON alongside the curation markdown. The relationship is
intentional: the curation markdown is the prose layer; this JSON is the
structured form of the same decisions. The two should always agree.

(Worked example: the caspase-in-*C. gibelio* data was originally
hand-curated into an inline `PAIRS = {...}` object in a bespoke explorer
HTML and extracted into this JSON format once. New gene sets produce the
JSON directly during curation, as above.)

## Validation

`build_hierarchy_explorer.py` doesn't validate the schema today —
malformed entries will produce empty cells or broken layout in the
rendered HTML. A future improvement is a small validator that runs
before rendering and reports schema deviations.
