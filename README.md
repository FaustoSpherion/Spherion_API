# ---------------------------------------------------------------------------
# File: README.md  (excerpt – keep concise here)
# ---------------------------------------------------------------------------
# ```markdown
# # Spherion Basic Conversion ⟶ with Refinement
# The package now offers **two free‑tier capabilities**:
# 1. Convert Cartesian `(x, y, z)` or spherical `(θ, φ, r)` points to a
#    hierarchical **SpherionCoordinate** (Level‑0 plus optional deeper path).
# 2. **Refine** an existing coordinate using a new measurement point, adding
#    depth (more bits) to narrow the uncertainty zone.
#
# ## CLI cheatsheet
# ```bash
# # ➊ Initial conversion
# spherion --cartesian 1 2 3                # →  Level‑0 label
#
# # ➋ Refinement with a new observation (same programme)
# spherion refine \
#          --coord '{"sign_x":1,"sign_y":1,"sign_z":1,"radius":3.742}' \
#          --cartesian 0.9 2.1 3.2 --levels 2
# ```
# ```
