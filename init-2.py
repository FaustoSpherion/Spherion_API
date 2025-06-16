# ---------------------------------------------------------------------------
# File: spherion/__init__.py
# ---------------------------------------------------------------------------
"""Public interface for the *free‑tier* Spherion library (conversion + refinement)."""
from importlib.metadata import version, PackageNotFoundError

from .coordinate import (
    SpherionCoordinate,
    cartesian_to_spherion,
    spherical_to_spherion,
    refine_by_measurement,
)

__all__ = [
    "SpherionCoordinate",
    "cartesian_to_spherion",
    "spherical_to_spherion",
    "refine_by_measurement",
]

try:
    __version__ = version(__name__.replace("_", "-"))
except PackageNotFoundError:  # pragma: no cover – during editable install
    __version__ = "0.0.0+local"