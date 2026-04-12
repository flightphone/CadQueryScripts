import numpy as np
import pyvista as pv
from svgpathtools import Path, Line, CubicBezier, parse_path
import math
import trimesh

def surf_points(fn, umin = 0, umax = 1, vmin = 0, vmax = 1,  res_u = 100, res_v = 100):
    u = np.linspace(umin, umax, res_u)
    v = np.linspace(vmin, vmax, res_v)
    U, V = np.meshgrid(u, v)
    x, y, z = fn(U, V)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    top_points = np.column_stack((x[0, :], y[0, :], z[0, :]))
    bottom_points = np.column_stack((x[-1, :], y[-1, :], z[-1, :]))

    #top_points = np.column_stack((x[:, 0], y[:, 0], z[:, 0]))
    #bottom_points = np.column_stack((x[:, -1], y[:, -1], z[:, -1]))

    return points, top_points, bottom_points
    
def surf_geom(fn, umin = 0, umax = 1, vmin = 0, vmax = 1,  res_u = 100, res_v = 100, repeat_u = 1, repeat_v = 1, top = 0):
    
    points, top_points, bottom_points = surf_points(fn, umin, umax, vmin, vmax,  res_u, res_v)
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = [res_u, res_v, 1]

    geom = grid.extract_geometry()
    
    dv = 0
    if (top & 1):
         top_face = np.hstack([[res_u], np.arange(res_u)])
         grid0 = pv.PolyData(top_points, faces=top_face)
         geom = geom.merge(grid0, merge_points=False)
         dv += 1

    if (top & 2):
         bottom_face = np.hstack([[res_u], np.arange(res_u)])
         grid1 = pv.PolyData(bottom_points, faces=bottom_face)
         geom = geom.merge(grid1, merge_points=False)     
         dv += 1


    tex_u = np.linspace(0, 1, res_u)*repeat_u
    tex_v = np.linspace(0, 1, res_v + dv)*repeat_v
    
    tex_u, tex_v = np.meshgrid(tex_u, tex_v)
    geom.active_texture_coordinates = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    
    geom = geom.compute_normals(
        cell_normals=False,
        point_normals=True
    )
    return geom

def to_trimesh(pv_mesh):
        # Обязательно триангулируем и чистим перед конвертацией
        tri_mesh = pv_mesh.triangulate().clean()
        v = tri_mesh.points
        # Форматируем грани из [3, v1, v2, v3...] в [[v1, v2, v3]...]
        f = tri_mesh.faces.reshape(-1, 4)[:, 1:]
        return trimesh.Trimesh(vertices=v, faces=f)


def check_volume(pv_mesh):
    tri = to_trimesh(pv_mesh)
    # Заполняет плоские дыры
    tri.fill_holes()
    # Исправляет ориентацию граней (лицо/изнанка)
    tri.fix_normals()
    # Пытается сделать меш герметичным
    tri.process(validate=True)
    return tri.is_volume
