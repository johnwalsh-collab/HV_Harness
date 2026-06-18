#!/usr/bin/env python3
"""Environment check for HV_Harness — run this first.

Verifies the Python version and that the packages the pipeline needs
are importable, before any pipeline script is run. It exists so an
agent or user does not have to discover the environment requirements
by trial and error (the common "which Python / is pyyaml installed /
do I need a venv" fumbling at the start of a session).

Usage:
    python scripts/check_env.py

No arguments, no config, no network — safe to run from anywhere, at
any time, including before the Checkpoint 1 conversation.

Exit code 0 = ready to run the core pipeline.
Exit code 1 = something required is missing (the fix is printed).
"""

import importlib
import sys

# The code uses `from __future__ import annotations`, so PEP 604
# unions do not force 3.10 at runtime; 3.10 is set as a clean, safe
# floor rather than a hard technical minimum.
MIN_PYTHON = (3, 10)

# import name -> (pip package name, what needs it)
REQUIRED = {
    "yaml":   ("PyYAML", "all scripts (config loading)"),
    "pandas": ("pandas", "gene identification, inventory, sequence handling"),
}

# Needed only for the NCBI download fallback (scripts/download_sequences.py).
# The preferred local path (extract_sequences.py) does not need these.
OPTIONAL = {
    "requests": ("requests", "NCBI download fallback only"),
    "Bio":      ("biopython", "NCBI download fallback only"),
}

_COLOR = sys.stdout.isatty()


def _c(code: str) -> str:
    return code if _COLOR else ""


GREEN, RED, YELLOW, RESET = _c("\033[32m"), _c("\033[31m"), _c("\033[33m"), _c("\033[0m")


def _ok(msg: str) -> None:
    print(f"  {GREEN}OK{RESET}      {msg}")


def _fail(msg: str) -> None:
    print(f"  {RED}MISSING{RESET} {msg}")


def _warn(msg: str) -> None:
    print(f"  {YELLOW}NOTE{RESET}    {msg}")


def check_python() -> bool:
    v = sys.version_info
    cur = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= MIN_PYTHON:
        _ok(f"Python {cur} (>= {MIN_PYTHON[0]}.{MIN_PYTHON[1]})")
        return True
    _fail(f"Python {cur} — need {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer")
    return False


def check_imports(table: dict, required: bool) -> list:
    missing = []
    for mod, (pkg, why) in table.items():
        try:
            importlib.import_module(mod)
            _ok(f"{mod} ({pkg}) — {why}")
        except ImportError:
            missing.append(pkg)
            (_fail if required else _warn)(
                f"{mod} ({pkg}) not importable — {why}")
    return missing


def main() -> int:
    print("HV_Harness environment check")
    print("-" * 48)

    print("Python:")
    py_ok = check_python()

    print("Required packages:")
    missing_required = check_imports(REQUIRED, required=True)

    print("Optional packages (NCBI download fallback only):")
    missing_optional = check_imports(OPTIONAL, required=False)

    print("-" * 48)

    if py_ok and not missing_required:
        print(f"{GREEN}Ready.{RESET} The core pipeline can run.")
        if missing_optional:
            print("(The optional NCBI-fallback packages are absent; the "
                  "preferred local sequence path does not need them.)")
        return 0

    print(f"{RED}Not ready.{RESET} To fix:")
    if not py_ok:
        print(f"  - Install Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ "
              "(system package manager, pyenv, or conda).")
    if missing_required:
        print("  - Install the dependencies:")
        print("        pip install -r requirements.txt")
        print("    A virtual environment is recommended but optional:")
        print("        python -m venv .venv && source .venv/bin/activate")
    return 1


if __name__ == "__main__":
    sys.exit(main())
