# ---------------------------------------------------------------------------
# File: spherion/coordinate.py
# ---------------------------------------------------------------------------
"""Core geometry for Level‑0 **and** iterative refinement (oct‑tree‑like).

History & scope
───────────────
* **Level‑0**: As before, six overlapping hemispheres → a signed octant label
  `(sign_x, sign_y, sign_z)`.
* **Levels ≥ 1** (free‑tier): Each octant is recursively split into 8 equal
  sub‑octants by bisecting **local** `x, y, z`.  We record the branch taken at
  each depth as a triple of bits `(bx, by, bz)` with values ±1 (lower/upper
  half) – conceptually identical to an **oct‑tree** on the cube that encloses
  the spherical zone.

We store that path in `self.path`, a tuple of `(bx, by, bz)` triples – one per
refinement level.  All maths stay lightweight (pure Python, no numpy).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import atan2, cos, degrees, hypot, sin, sqrt
from typing import Iterable, List, Sequence, Tuple

__all__ = [
    "SpherionCoordinate",
    "cartesian_to_spherion",
    "spherical_to_spherion",
    "refine_by_measurement",
]

SQRT3 = sqrt(3.0)
INV_SQRT3 = 1.0 / SQRT3


@dataclass(slots=True, frozen=True)
class SpherionCoordinate:
    """Hierarchical label for a point in Spherion space (free‑tier depth ≤ 5)."""

    sign_x: int  # Base hemispheres ±1
    sign_y: int
    sign_z: int
    radius: float = 1.0
    path: Tuple[Tuple[int, int, int], ...] = ()  # Optional deeper bits

    # ============================================================
    # Public helpers
    # ============================================================
    def depth(self) -> int:
        """Return refinement depth (0 = Level‑0 only)."""
        return len(self.path)

    # ----------------------------- Cartesian centre -------------
    def to_cartesian(self) -> Tuple[float, float, float]:
        """Coordinates of **cell centre** (approx)."""
        # Start with Level‑0 centre
        x = self.sign_x * self.radius * INV_SQRT3
        y = self.sign_y * self.radius * INV_SQRT3
        z = self.sign_z * self.radius * INV_SQRT3

        # Each deeper level adds ± radius/(√3 * 2^(level+1)) along each axis
        for lvl, (bx, by, bz) in enumerate(self.path, start=1):
            step = self.radius * INV_SQRT3 / (2 ** (lvl + 1))
            x += bx * step
            y += by * step
            z += bz * step
        return x, y, z

    # ----------------------------- Spherical centre -------------
    def to_spherical(self) -> Tuple[float, float, float]:
        x, y, z = self.to_cartesian()
        r = hypot(hypot(x, y), z)
        if r == 0:
            return 0.0, 0.0, 0.0
        theta = atan2(hypot(x, y), z)
        phi = atan2(y, x)
        return theta, phi, r

    # ----------------------------- Pretty print -----------------
    def __repr__(self) -> str:  # pragma: no cover – debug nicety
        lvl0 = (
            "Right" if self.sign_x > 0 else "Left",
            "Front" if self.sign_y > 0 else "Back",
            "Top" if self.sign_z > 0 else "Bottom",
        )
        return (
            f"<SpherionCoordinate L0={lvl0} depth={self.depth()} r={self.radius:g}>"
        )


# ---------------------------------------------------------------------------
# Conversion helpers (Level‑0)
# ---------------------------------------------------------------------------

def cartesian_to_spherion(x: float, y: float, z: float) -> SpherionCoordinate:
    sx = 1 if x >= 0 else -1
    sy = 1 if y >= 0 else -1
    sz = 1 if z >= 0 else -1
    r = hypot(hypot(x, y), z)
    return SpherionCoordinate(sx, sy, sz, r)


def spherical_to_spherion(theta: float, phi: float, r: float = 1.0) -> SpherionCoordinate:
    x = r * sin(theta) * cos(phi)
    y = r * sin(theta) * sin(phi)
    z = r * cos(theta)
    return cartesian_to_spherion(x, y, z)


# ---------------------------------------------------------------------------
# Refinement logic (free‑tier: up to depth 5 -> ~1/32th resolution)
# ---------------------------------------------------------------------------

def _measurement_bits(value: float, radius: float, level: int) -> int:
    """Return ±1 indicating lower/upper half of the *current* local cell."""
    # Normalise abs(value) to [0, 1]
    ratio = abs(value) / radius
    threshold = 0.5 ** (level + 1)  # 0.25, 0.125, ...
    return 1 if ratio >= threshold else -1


def refine_by_measurement(
    coord: SpherionCoordinate,
    x: float,
    y: float,
    z: float,
    levels: int = 1,
    max_depth: int = 5,
) -> SpherionCoordinate:
    """Return a *new* coordinate refined by `levels` using measurement point.

    Parameters
    ----------
    coord
        SpherionCoordinate to refine (kept immutable).
    x, y, z
        Measurement Cartesian coordinates (same unit as `coord.radius`).
    levels
        How many additional levels to add (default 1).
    max_depth
        Hard cap to avoid overly deep recursion in free tier (default 5).
    """
    if levels <= 0 or coord.depth() >= max_depth:
        return coord

    new_path: List[Tuple[int, int, int]] = list(coord.path)
    for add_lvl in range(levels):
        if len(new_path) >= max_depth:
            break
        lvl_index = len(new_path) + 1  # 1‑based inside helper
        bx = _measurement_bits(x, coord.radius, lvl_index)
        by = _measurement_bits(y, coord.radius, lvl_index)
        bz = _measurement_bits(z, coord.radius, lvl_index)
        new_path.append((bx, by, bz))

    return replace(coord, path=tuple(new_path))

# Aliased for convenience within package namespace
refine = refine_by_measurement