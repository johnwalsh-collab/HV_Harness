# Quick start — instructions for the AI assistant

⚠️ **If you have not yet read `CLAUDE.md` in the project root, read
it now before continuing.** This file and CLAUDE.md together govern
the session. Neither stands alone.

This file governs how a user session begins. It takes precedence
over any task the user has described.

---

## Progress & hand-off banner — show at every output and checkpoint

This banner is the workflow's hand-off surface. Its job is to make
two things impossible to miss: *what just happened* and *whose turn
it is next*. A neutral agent's chain-of-thought output tends to bury
those; the banner's fixed shape cuts through it. The top block tracks
position; the footer is the hand-off.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Stage 1 · Gene group & genomes confirmed
  ✅  Stage 2 · Search terms designed (CP1)
  ✅  Stage 3 · Gene list checked, inventory built
  ▶️  **CP2 · Review inventory & choose focal species**   ← now
  ⬜  Stage 4 · Per-pair curation (focal species)
  ⬜  Stage 5 · Empty-slots deep dive (CP3)
  ⬜  Stage 6 · Visualization design (CP4 & CP5)
  ───────────────────────────────────────────
  ✅ Just produced · results/<gene_set>/identification/<gene_set>_gene_inventory.tsv
  ▶  Next          · Review the inventory; choose which species to curate
  ⤷  Your move     · confirm the inventory, then name the focal species
  ⏸  Parked        · (none)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When to show it.** At every checkpoint, *and* every time an output
or artifact is produced or a stage completes — i.e. at every
transition, not only checkpoints. It takes two seconds and keeps both
the researcher and the AI oriented.

**The scripts emit it for you.** Each pipeline driver prints this banner
itself on completion (via `_config.emit_banner`) and mirrors it to
`results/SESSION_STATUS.md`, with the position checklist, the four footer
lines, and any checkpoint gate already filled in. Relay and enrich that
banner with the conversational detail — never skip it, replace it with a
bare "done", or let it scroll past unremarked. The script output is the
floor; the agent adds the judgement. Scripts that sit at a checkpoint also
print a `⛔ CHECKPOINT` gate line, which is **non-suppressible**: it appears
regardless of curation mode (see Step 7).

**The four footer lines, always present:**

- **Just produced** — the file or artifact that just landed, with its
  path (or `—` if this turn produced none).
- **Next** — the single next action.
- **Your move / I'll continue** — the whose-turn marker, and it is
  never omitted. When handing back, write `⤷ Your move ·` followed by
  the *exact* thing the researcher can say or do to continue. When
  proceeding autonomously (unattended mode), write `⤷ I'll continue ·
  <next action> (say "pause" to stop)` instead. The agent never ends a
  turn by simply stopping — it always states the next action and whose
  turn it is.
- **Parked** — short sidebar topics captured so a tangent does not
  derail the thread (see below), or `(none)`.

**Parking tangents.** When the conversation drifts into a side topic,
add a one-line entry to **Parked**, deal with it or agree to defer it,
then return to **Next**. Clear an item from Parked once it is resolved.
This keeps a digression about an output from swallowing the next step.

**Persisting for resume.** After showing the banner, also write it to
`results/SESSION_STATUS.md` (overwrite each time). This file is a
scratch mirror, not a deliverable — it is gitignored. On starting or
resuming a session, read `results/SESSION_STATUS.md` first, if it
exists, to re-orient. The curation document remains the source of
truth for substance; the status file only records position and the
pending hand-off.

---

## Before running any script

Do not open any config file, do not run any pipeline script, and do
not propose search terms or species until the conversation below has
been completed. The scripts are fast; the conversation is the work.

**One exception — confirm the environment first.** Before Step 1, run:

```bash
python scripts/check_env.py
```

This is read-only, needs no config or network, and is the only
mechanical action permitted before the conversation. If it reports
anything `MISSING`, resolve it (the script prints the exact command)
before going further. This avoids discovering a missing package
mid-pipeline.

---

## Step 1 — Establish the gene group

Ask the researcher what gene group they want to explore. Wait for
an answer before proceeding. A gene group can be a formal gene
family, a pathway, a functional category, or any custom list — the
workflow does not require it to be a formal family.

Example opening:
> "What gene group do you want to explore? It can be a gene family,
> a pathway, or any set of genes you have in mind."

---

## Step 2 — Confirm the species and check annotation files

Explain that the workflow supports three allotetraploid carp genomes
(*Cyprinus carpio*, *Carassius gibelio*, *Carassius auratus*) and
uses *Danio rerio* (zebrafish) as a high-quality diploid comparator.

Ask the researcher which carp genome they want to start with. The
recommended approach is to begin with one carp species alongside
zebrafish, establish the gene set and homeolog assignments there,
and extend to the other species later. But follow the researcher's
preference.

Do not default to all species. Starting species is a decision the
researcher makes, not a pipeline default.

**Before proceeding, check that the genome files are present for the
chosen species:**

```bash
ls data/annotations/<species>/
```

Each species that will be searched needs a folder containing both a
`<species>_genomic.gff.gz` and a `<species>_protein.faa.gz` file.
These are not included in the repository because they are too large.
If any are missing, fetch them in one step:

```bash
# all four genomes (three carps + zebrafish), or pass --species to
# fetch only what you need:
python scripts/download_genome_files.py --species <species> ...
```

This downloads both files for each species directly from the NCBI
file server and verifies each one. If a download fails, the script
prints the exact manual `curl` command; the same commands are listed
in `GETTING_STARTED.md`.

Do not proceed to Step 3 until both files for the chosen species are
confirmed present.

---

## Step 3 — Checkpoint 1 (search-term design)

This is Checkpoint 1 from the curation playbook (section 3.4).

Read playbook section 3 to understand the search strategy. Then
work through the following with the researcher:

1. What gene names should be included? Are there naming patterns
   (e.g. a prefix like `casp` for caspases)?
2. Are there description keywords that would catch LOC-named genes
   that belong to the group?
3. Are there known false positives to exclude — genes whose names
   match the pattern but are not group members?

The output of this conversation is a populated config file at
`config/<gene_set>.yaml` (copied from `config/template.yaml`).
Build this file incrementally during the conversation; do not ask
the researcher to fill it in themselves.

When both you and the researcher are satisfied with the search
terms, run Stage 2:

```bash
python scripts/identify_gene_set.py --config config/<gene_set>.yaml
```

---

## Step 4 — Preliminary gene-list check (before Checkpoint 2)

After Stage 2 runs, present the gene counts per species and the
full gene list to the researcher before proceeding. Ask:

- Are there obvious false positives?
- Are there known group members that are missing?

Iterate on the config if needed and re-run until the list is stable.
This is a preliminary pass on the raw gene list. The substantive
**Checkpoint 2** — reviewing the *built inventory* as the baseline —
comes after `build_gene_inventory.py` (Step 6, and playbook section 5.1).

---

## Step 5 — Protein sequences

Before running the inventory or curation, protein sequences for the
identified gene set are needed. Check whether they already exist:

```bash
ls data/sequences/<gene_set>_proteins_*.fasta
```

**If sequences are already present**, skip to Step 6.

**If sequences are not present**, use the local extraction script as
the primary approach:

### Option A — Extract from local protein FASTA (preferred)

```bash
python scripts/extract_sequences.py --config config/<gene_set>.yaml
python scripts/clean_sequences.py   --config config/<gene_set>.yaml
```

This reads protein sequences directly from the local
`data/annotations/<species>/<species>_protein.faa.gz` files — no
internet connection required. If a species is missing its protein
FASTA, the script skips it and prints a clear warning with
instructions for downloading the missing file.

If the protein FASTA files are not present, download them once with
curl (see GETTING_STARTED.md for the exact commands and FTP paths)
and place them in the correct species folder. Then re-run.

### Option B — Download from NCBI (fallback)

Only use this if the protein FASTA files cannot be obtained manually.

```bash
python scripts/download_sequences.py --config config/<gene_set>.yaml --email <researcher_email>
python scripts/clean_sequences.py    --config config/<gene_set>.yaml
```

Note: NCBI access can be unreliable. If downloads time out or fail,
return to Option A and obtain the protein FASTA files manually.

### Option B — Manual download

Generate a download manifest from the gene list:

1. Read `results/<gene_set>/identification/<gene_set>_genes_all_species.tsv`
2. Extract the `ncbi_gene_id` column values
3. Write them to `data/sequences/<gene_set>_download_manifest.txt`,
   one ID per line, with these instructions at the top:

```
# Manual download instructions for <gene_set> protein sequences
# 
# 1. Go to https://www.ncbi.nlm.nih.gov/gene
# 2. Use "Search" → paste IDs below into the search box using OR
#    (e.g. 127966001[uid] OR 127966003[uid])
# 3. Use "Send to" → "Coding Sequences" → "FASTA Protein" → "File"
# 4. Save the downloaded file as:
#    data/sequences/<gene_set>_proteins_all.fasta
# 5. Tell the AI when the file is in place.
#
# Alternatively, use NCBI Datasets CLI:
#   datasets download gene gene-id <ID1> <ID2> ... --include protein
#
# Gene IDs:
```

Tell the researcher what to do and wait for them to confirm the
file is in place before proceeding. Then run clean_sequences.py:

```bash
python scripts/clean_sequences.py --config config/<gene_set>.yaml
```

---

## Step 6 — Build the inventory, then Checkpoint 2 (review + choose focal species)

Once sequences are in place, build the gene inventory:

```bash
python scripts/build_gene_inventory.py --config config/<gene_set>.yaml
```

**Checkpoint 2 — review the built inventory as the baseline.** Before
per-pair curation, pause and look at the inventory with the researcher:
confirm the per-species counts are sensible, no expected member is
missing or obviously spurious, and the gene-model quality flags are
understood. Confirming it here makes it the agreed baseline (playbook
section 5.1) — the substantive review that the Step 4 gene-list check
only previewed. If something looks wrong, fix the config and rebuild now
rather than after curation has begun.

**Then choose the focal species.** The inventory covers every carp
genome in the repo, but the per-pair curation and visualization that
follow are about one focal species. Ask the researcher which genome they
want to curate — do not default to the best-annotated one. If they want
more than one, run the curation once per species, each through to its own
visualization (playbook section 5.1).

Then extract synteny (mechanical prep for the per-pair work):

```bash
python scripts/extract_synteny.py      --config config/<gene_set>.yaml
```

---

## Step 7 — Ask about curation mode before starting Stage 4

Before beginning the per-pair curation, ask the researcher how they
want to work through it:

> "The curation phase works through each homeologous pair one by one.
> This can take a while depending on how many pairs there are. Would
> you prefer:
>
> **A — Collaborative:** I pause after each pair (or after any
> ambiguous or uncertain case) so we can discuss before moving on.
>
> **B — Unattended:** I work through all pairs and produce a complete
> draft curation document you can review when ready. I'll flag
> uncertain cases clearly so you know where to focus your attention."

Wait for the researcher's answer. Then proceed accordingly.

**In collaborative mode (A):**
- Work one pair at a time.
- After each pair, briefly summarise the call and any uncertainties
  before moving to the next.
- Stop and discuss immediately whenever you encounter: a candidate
  loss, an ambiguous cluster, an artefact call, or any case where
  the evidence is mixed.
- Show the progress banner at the start of each pair so the
  researcher can see how far through the curation you are.

**In unattended mode (B):**
- Work through all pairs without pausing **for per-pair dialogue**.
- Write a curation document that clearly marks every uncertain call
  with a visible flag (e.g. **[NEEDS REVIEW]**) and a plain-language
  explanation of why it is uncertain.
- At the end, present a summary of all flagged items so the
  researcher can focus their review efficiently.
- Show the progress banner when you begin and again when you finish.

**Batch/unattended mode is local — it suppresses per-pair dialogue
only.** It is *not* a licence to drop the harness scaffolding. Two things
remain mandatory in either mode:

- **The banner stays on at every stage boundary** — including the
  gene-list build, not just the start and end of the curation. (The
  scripts emit it; relay it.)
- **The checkpoint returns that bracket the batch segment are
  non-suppressible.** After the pair-by-pair pass, return to the curator
  at **Checkpoint 3** (the empty-slots deep dive) before anything else,
  and again at **Checkpoint 4** before the visualization is built. Do not
  run `build_hierarchy_explorer.py` until CP3 is done — it will refuse to
  build while any empty slot lacks an explicit loss decision (see the
  curation-data schema). Unattended means "draft the pairs without
  checking in on each one," never "skip the checkpoints."

---

## Checkpoints during and after curation

From here, follow `docs/workflow.md` for the remaining pipeline
stages and `docs/curation_playbook.md` for the curation procedure.
The playbook governs all methodology decisions; when in doubt,
consult it before acting.

Checkpoint 2 (inventory review and focal-species choice), Checkpoint 3 (the empty-slots deep
dive — resolving the empty A/B slots flagged during per-pair work
into explicit loss calls), Checkpoint 4 (pre-visualization curation
review), and Checkpoint 5 (interpretive layer design) all require
pausing for researcher input. Initiate each checkpoint explicitly —
do not proceed through them silently. Show the progress banner at
each one.
