#!/usr/bin/env python3
"""Tests for the hierarchy-explorer build-time validation.

Locks the guard that turns the Run F3 / audit-#4 *silent* miscount into a
loud build failure: the explorer template only acts on a fixed set of
gene `status` and slot `A_loss`/`B_loss` values, and any other value used
to be swallowed (rendered as a normal functional gene / an un-searched
slot). `build_hierarchy_explorer.validate_curation` now rejects anything
outside the supported set.

Run standalone (no pytest required):
    python tests/test_explorer.py        # exit 0 = all pass
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_hierarchy_explorer as bhe  # noqa: E402


def _curation(status="ok", a_loss=None):
    slot = {"A": [{"id": "1", "role": "x", "status": status}], "B": []}
    if a_loss is not None:
        slot["A_loss"] = a_loss
    return {1: {"slots": [slot]}}


def _raises(curation):
    try:
        bhe.validate_curation(curation)
        return False
    except SystemExit:
        return True


def test_valid_statuses_pass():
    for st in ("ok", "pseudo", "artefact", "candidate_nonfunctional"):
        bhe.validate_curation(_curation(status=st))  # must not raise


def test_unknown_status_raises():
    assert _raises(_curation(status="check"))
    assert _raises(_curation(status="suspect"))
    assert _raises(_curation(status="functional"))


def test_loss_values():
    # empty A side with each loss value
    base = {1: {"slots": [{"A": [], "B": [{"id": "2", "role": "y", "status": "ok"}]}]}}
    for good in ("searched", "confirmed", "na"):
        c = {1: {"slots": [{"A": [], "B": [], "A_loss": good}]}}
        bhe.validate_curation(c)  # must not raise
    bad = {1: {"slots": [{"A": [], "B": [], "A_loss": "yes"}]}}
    assert _raises(bad)
    # field absent is fine (the honest un-searched holding state)
    bhe.validate_curation(base)


def test_missing_status_defaults_ok():
    # a gene entry without an explicit status is treated as ok (valid)
    c = {1: {"slots": [{"A": [{"id": "3", "role": "z"}], "B": []}]}}
    bhe.validate_curation(c)


# --- resolve_render_pairs: curation-authoritative pair list ---
# The template renders every layer by iterating GENE_SET_PAIRS. The pair
# list is now derived from the curation data (source of truth), with config
# homeolog_pairs as an ordering hint only — so an empty/stale config list
# can never blank or truncate the explorer.

def _pairs_raises(curation, homeolog_pairs):
    try:
        bhe.resolve_render_pairs(curation, homeolog_pairs)
        return False
    except SystemExit:
        return True


def test_pairs_empty_config_derives_from_curation():
    # empty / None config homeolog_pairs -> all curated pairs, numeric order
    curation = {3: {"slots": []}, 1: {"slots": []}}
    assert bhe.resolve_render_pairs(curation, []) == [1, 3]
    assert bhe.resolve_render_pairs(curation, None) == [1, 3]


def test_pairs_missing_curated_pair_auto_included():
    # config lists pair 1 only, but curation also has pair 3 -> 3 appended
    curation = {1: {"slots": []}, 3: {"slots": []}}
    assert bhe.resolve_render_pairs(curation, [1]) == [1, 3]


def test_pairs_config_ordering_respected_extras_skipped():
    curation = {1: {"slots": []}, 3: {"slots": []}}
    # config order honoured for present pairs; pairs absent from curation skipped
    assert bhe.resolve_render_pairs(curation, [3, 1]) == [3, 1]
    assert bhe.resolve_render_pairs(curation, [3, 1, 99]) == [3, 1]


def test_pairs_empty_curation_raises():
    # genuinely nothing to render -> loud failure
    assert _pairs_raises({}, [])
    assert _pairs_raises({}, [1, 3])


# --- validate_cp3_complete: empty slots need an explicit loss decision ---
# Run F4: the CP3 deep-dive outcome (the A_loss/B_loss field) could be left
# unset, so a searched slot still rendered as "no specific search done". The
# explorer now refuses to build until every empty slot carries an explicit
# loss value; deliberate non-search must be recorded as `na`, never omitted.

def _cp3_raises(curation):
    try:
        bhe.validate_cp3_complete(curation)
        return False
    except SystemExit:
        return True


def test_cp3_empty_slot_without_loss_raises():
    # empty A side, no A_loss -> incomplete CP3 -> build refused
    assert _cp3_raises({1: {"slots": [{"A": [], "B": [{"id": "1", "status": "ok"}]}]}})
    # empty B side, no B_loss
    assert _cp3_raises({1: {"slots": [{"A": [{"id": "1", "status": "ok"}], "B": []}]}})
    # side key entirely absent counts as empty
    assert _cp3_raises({1: {"slots": [{"A": [{"id": "1", "status": "ok"}]}]}})


def test_cp3_empty_slot_with_loss_passes():
    for good in ("searched", "confirmed", "na"):
        bhe.validate_cp3_complete(
            {1: {"slots": [{"A": [], "B": [{"id": "1", "status": "ok"}],
                            "A_loss": good}]}})  # must not raise


def test_cp3_populated_slot_needs_no_loss():
    # both sides present -> no empty slot -> no loss decision required
    bhe.validate_cp3_complete(
        {1: {"slots": [{"A": [{"id": "1", "status": "ok"}],
                        "B": [{"id": "2", "status": "ok"}]}]}})


# --- template renders `searched` as candidate loss (Run F4) ---
# The §J rename confirmed->searched updated the metric + validation but
# missed the cell renderer renderSlotSide, which only matched 'confirmed' —
# so `searched` slots rendered as "no specific search done" (the empty-slot
# analysis the curator saw missing). The JS isn't unit-testable here, so we
# guard the template source: the candidate-loss branch must match `searched`.

def test_template_renders_searched_as_candidate_loss():
    tpl = bhe.TEMPLATE_PATH.read_text()
    assert "renderSlotSide" in tpl
    assert "lossStatus === 'searched'" in tpl, \
        "renderSlotSide must treat 'searched' as a candidate loss (Run F4)"


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
