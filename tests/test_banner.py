#!/usr/bin/env python3
"""Tests for the mechanized progress & hand-off banner (_config.render_banner).

Run F4: the banner and the checkpoint returns were left to the agent's
discretion and were silently dropped (no banner at the gene-list stage; no
return at the CP3 boundary). The banner is now emitted by the scripts via a
single renderer, so these tests lock its shape: the position marker, the
always-present whose-turn line, and the non-suppressible checkpoint gate.

Run standalone (no pytest required):
    python tests/test_banner.py        # exit 0 = all pass
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import _config  # noqa: E402


def test_position_markers():
    b = _config.render_banner(3, "out.tsv", "do next", your_move="go")
    # earlier steps done, current active, later pending
    assert b.count("✅") >= 3          # 3 completed steps + "Just produced" line
    assert "▶️" in b                   # exactly the current step
    assert b.count("⬜") == 3          # three later steps
    assert "← now" in b


def test_whose_turn_always_present_your_move():
    b = _config.render_banner(2, "x", "next", your_move="confirm the list")
    assert "Your move" in b
    assert "confirm the list" in b
    assert "I'll continue" not in b


def test_whose_turn_unattended():
    b = _config.render_banner(4, "x", "next", i_continue="drafting all pairs")
    assert "I'll continue" in b
    assert "drafting all pairs" in b
    assert 'say "pause" to stop' in b
    assert "Your move" not in b


def test_whose_turn_never_omitted():
    # neither given -> still emits a Your-move fallback, never blank
    b = _config.render_banner(0, None, "next")
    assert "Your move" in b


def test_produced_dash_when_none():
    b = _config.render_banner(0, None, "next", your_move="go")
    assert "Just produced · —" in b


def test_gate_is_nonsuppressible_and_labelled():
    b = _config.render_banner(3, "x", "next", your_move="go", gates=["CP2"])
    assert "⛔ CHECKPOINT CP2" in b
    assert "non-suppressible" in b
    assert "batch mode does not waive" in b


def test_multiple_gates():
    b = _config.render_banner(4, "x", "next", i_continue="go", gates=["CP3", "CP4"])
    assert "CP3" in b and "CP4" in b
    assert b.count("⛔ CHECKPOINT") == 2


def test_unknown_gate_id_falls_back_to_literal():
    b = _config.render_banner(0, "x", "next", your_move="go", gates=["CPX custom"])
    assert "⛔ CHECKPOINT CPX custom" in b


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
