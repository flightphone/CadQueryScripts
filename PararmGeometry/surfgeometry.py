import numpy as np
import pyvista as pv
from svgpathtools import Path, Line, CubicBezier, parse_path
import math

def surf_points(fn, umin = 0, umax = 1, vmin = 0, vmax = 1,  res_u = 100, res_v = 100):
    u = np.linspace(umin, umax, res_u)
    v = np.linspace(vmin, vmax, res_v)
    U, V = np.meshgrid(u, v)
    x, y, z = fn(U, V)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    return points

def surf_geom(fn, umin = 0, umax = 1, vmin = 0, vmax = 1,  res_u = 100, res_v = 100, repeat_u = 1, repeat_v = 1):
    points = surf_points(fn, umin, umax, vmin, vmax,  res_u, res_v)
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = [res_u, res_v, 1]

    geom = grid.extract_geometry()
    tex_u = np.linspace(0, 1, res_u)*repeat_u
    tex_v = np.linspace(0, 1, res_v)*repeat_v
    
    tex_u, tex_v = np.meshgrid(tex_u, tex_v)
    geom.active_texture_coordinates = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    geom = geom.compute_normals(
        cell_normals=False,
        point_normals=True
    )
    return geom


