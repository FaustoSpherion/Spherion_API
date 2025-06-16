# ---------------------------------------------------------------------------
# File: tests/test_coordinate.py  (expanded)
# ---------------------------------------------------------------------------
"""Regression checks for conversion **and** refinement."""
from math import isclose

import pytest

from spherion.coordinate import cartesian_to_spherion, refine_by_measurement


@pytest.mark.parametrize(
    "point, signs",
    [((1, 2, 3), (1, 1, 1)), ((-1, 0, 5), (-1, 1, 1)), ((0, -4, -4), (1, -1, -1))],
)

def test_signs(point, signs):
    coord = cartesian_to_spherion(*point)
    assert (coord.sign_x, coord.sign_y, coord.sign_z) == signs


def test_refinement_depth():
    coord = cartesian_to_spherion(1, 1, 1)
    refined = refine_by_measurement(coord, 0.9, 0.9, 0.9, levels=2)
    assert refined.depth() == 2
    # Radius must stay unchanged
    assert isclose(refined.radius, coord.radius)