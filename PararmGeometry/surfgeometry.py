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
        # clean
        tri_mesh = pv_mesh.triangulate().clean()
        v = tri_mesh.points
        # create faces
        f = tri_mesh.faces.reshape(-1, 4)[:, 1:]
        return trimesh.Trimesh(vertices=v, faces=f)


def check_volume(pv_mesh):
    tri = to_trimesh(pv_mesh)
    # fill
    tri.fill_holes()
    # fix
    tri.fix_normals()
    # correct
    tri.process(validate=True)
    return tri.is_volume



def pv_boolean_difference(target_pv, cutter_pv, transform_matrix=None):
    """
    (Difference) by Trimesh/Manifold.
    :param target_pv: main mesh
    :param cutter_pv: cutter mesh
    :param transform_matrix: transorm matrix
    :return:  pyvista.PolyData
    """
    
    def to_trimesh(pv_mesh):
        # triangulate
        tri_mesh = pv_mesh.triangulate().clean()
        v = tri_mesh.points
        # generate faces
        f = tri_mesh.faces.reshape(-1, 4)[:, 1:]
        return trimesh.Trimesh(vertices=v, faces=f)

    def tryclear(target):    
       # fill
        target.fill_holes()
        # fix
        target.fix_normals()
        # correct
        target.process(validate=True)
    
    # 1. to Trimesh
    target_tri = to_trimesh(target_pv)
    cutter_tri = to_trimesh(cutter_pv)



    
    
    # 2. transform
    if transform_matrix is not None:
        cutter_tri.apply_transform(transform_matrix)

    # 3. clear
    tryclear(target_tri)
    tryclear(cutter_tri)
    
    #print(f"Target is volume: {target_tri.is_volume}")
    #print(f"Cutter is volume: {cutter_tri.is_volume}")

    if not target_tri.is_volume or not cutter_tri.is_volume:
        return None



    # 4. boolean Manifold
    # engine='manifold' 
    result_tri = target_tri.difference(cutter_tri, engine='manifold')

    # 5. to PyVista
    v_out = result_tri.vertices
    f_out = result_tri.faces
    # create faces
    faces_pv = np.column_stack((np.full(len(f_out), 3), f_out)).ravel()
    
    return pv.PolyData(v_out, faces_pv)