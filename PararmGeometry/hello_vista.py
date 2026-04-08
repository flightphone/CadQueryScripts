from __future__ import annotations
import pyvista as pv

pl = pv.Plotter()
sphere = pv.Sphere()
sphere.compute_normals()
pl.add_mesh(sphere, color='lightblue', show_edges=True)

pl.show()