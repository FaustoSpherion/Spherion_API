# ---------------------------------------------------------------------------
# File: spherion/cli.py
# ---------------------------------------------------------------------------
"""Console script: `spherion` (convert) and `spherion refine` (refinement).

Examples
────────
➜ spherion --cartesian 1 2 3
<SpherionCoordinate L0=('Right', 'Front', 'Top') depth=0 r=3.74166>

➜ spherion refine --coord '{"sign_x":1,"sign_y":1,"sign_z":1,"radius":3.742}' \
                  --cartesian 0.9 2.1 3.2 --levels 1 --out cartesian
(0.558, 1.96, 1.75)
"""
from __future__ import annotations

import argparse
import json
import sys
from ast import literal_eval
from typing import Any, Dict, Tuple

from .coordinate import (
    SpherionCoordinate,
    cartesian_to_spherion,
    refine_by_measurement,
    spherical_to_spherion,
)


# ============================================================
# Helper formatters
# ============================================================

def _fmt_coord(obj: Any) -> str:
    if isinstance(obj, SpherionCoordinate):
        return repr(obj)
    if isinstance(obj, Tuple):
        return "(" + ", ".join(f"{v:.3g}" for v in obj) + ")"
    return str(obj)


# ============================================================
# Parsers
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="spherion", description="Spherion free‑tier CLI")
    subparsers = p.add_subparsers(dest="command", required=False)

    # ---------- Main (convert) ----------
    main = subparsers.add_parser("convert", help="Cartesian / spherical → Spherion (default)")
    _add_input_args(main)
    main.add_argument(
        "--out",
        choices=["spherion", "cartesian", "spherical", "json"],
        default="spherion",
        help="Output representation (default: spherion)",
    )

    # ---------- Refine ----------
    refine = subparsers.add_parser("refine", help="Refine an existing Spherion coordinate")
    refine.add_argument(
        "--coord",
        required=True,
        help="Original coordinate as JSON string or Python‑dict literal",
    )
    _add_input_args(refine)
    refine.add_argument("--levels", type=int, default=1, help="Levels to add (≤ 5)")
    refine.add_argument(
        "--out",
        choices=["spherion", "cartesian", "spherical", "json"],
        default="spherion",
    )

    # Default command = convert
    p.set_defaults(command="convert")
    return p


def _add_input_args(sub):
    g = sub.add_mutually_exclusive_group(required=True)
    g.add_argument("--cartesian", nargs=3, metavar=("X", "Y", "Z"), type=float)
    g.add_argument("--spherical", nargs=3, metavar=("THETA", "PHI", "R"), type=float)


# ============================================================
# Entrypoint
# ============================================================

def main(argv: list[str] | None = None):  # noqa: D401
    if argv is None:
        argv = sys.argv[1:]
    args = build_parser().parse_args(argv)

    if args.command == "convert":
        coord = _parse_input(args)
    else:  # refine
        orig = _json_to_coord(args.coord)
        measurement = _parse_input(args)
        coord = refine_by_measurement(
            orig,
            *measurement.to_cartesian(),  # Measurement in Cartesian (centre approx OK)
            levels=args.levels,
        )

    # Output
    if args.out == "spherion":
        print(coord)
    elif args.out == "cartesian":
        print(_fmt_coord(coord.to_cartesian()))
    elif args.out == "spherical":
        theta, phi, r = coord.to_spherical()
        print(_fmt_coord((degrees(theta), degrees(phi), r)))
    else:  # json
        out = {
            "sign_x": coord.sign_x,
            "sign_y": coord.sign_y,
            "sign_z": coord.sign_z,
            "radius": coord.radius,
            "path": coord.path,
        }
        print(json.dumps(out))


def _parse_input(args) -> SpherionCoordinate:
    if args.cartesian:
        return cartesian_to_spherion(*args.cartesian)
    theta, phi, r = args.spherical
    return spherical_to_spherion(theta, phi, r)


def _json_to_coord(text: str) -> SpherionCoordinate:
    data = literal_eval(text) if (text.strip().startswith("{")) else json.loads(text)
    return SpherionCoordinate(
        data["sign_x"], data["sign_y"], data["sign_z"], data["radius"],
        tuple(tuple(t) for t in data.get("path", ()))
    )


if __name__ == "__main__":  # pragma: no cover
    main()