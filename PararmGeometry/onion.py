import numpy as np
import pyvista as pv
import math

def surf_points(fn, umin = 0, umax = 1, vmin = 0, vmax = 1,  res_u = 100, res_v = 100):
    u = np.linspace(umin, umax, res_u)
    v = np.linspace(vmin, vmax, res_v)
    U, V = np.meshgrid(u, v)
    x, y, z = fn(U, V)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    top_points = np.column_stack((x[0, :], y[0, :], z[0, :]))
    bottom_points = np.column_stack((x[-1, :], y[-1, :], z[-1, :]))
    return points, top_points, bottom_points

def surf_geom(fn, umin = 0, umax = 1, vmin = 0, vmax = 1,  res_u = 100, res_v = 100, repeat_u = 1, repeat_v = 1, top = 0, clear = False):
    
    points, top_points, bottom_points = surf_points(fn, umin, umax, vmin, vmax,  res_u, res_v)
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = [res_u, res_v, 1]

    geom = grid.extract_geometry()
    if clear:
        geom = geom.clean(tolerance=0.0001)
        geom = geom.fill_holes(hole_size=0.0001)
    
    dv = 0
    if (top & 1):
         top_face = np.hstack([[res_u], np.arange(res_u)])
         grid0 = pv.PolyData(top_points, faces=top_face)
         geom = geom.merge(grid0, merge_points=False)
         dv += 1

    if (top & 2):
         bottom_face = np.hstack([[res_u], np.arange(res_u)])
         grid1 = pv.PolyData(bottom_points[::-1], faces=bottom_face)
         geom = geom.merge(grid1, merge_points=False)     
         dv += 1

    if not clear:
        tex_u = np.linspace(0, 1, res_u)*repeat_u 
        tex_v = np.linspace(0, 1, res_v + dv)*repeat_v
        
        tex_u, tex_v = np.meshgrid(tex_u, tex_v)
        geom.active_texture_coordinates = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    
    geom = geom.compute_normals(
        cell_normals=False,
        point_normals=True
    )
    return geom


def onion(u, v, n_lobes=10):
    uu = u*n_lobes
    I = np.floor(uu)
    U = (uu-I)*math.pi - math.pi/2
    V = v*math.pi
    # contour
    p = np.pi/2 + 35/180 * np.pi
    R_base = 1.0
    
    # onion
    R = np.where(V > p, R_base / np.cos(V - p), R_base) 
    
    z = - R * np.cos(V)
    r_big = np.abs(R * np.sin(V))

    # Twist
    twist = (np.cos(V) + 1) / 4 * np.pi
    al = 2 * np.pi / n_lobes
    r_small = r_big * np.sin(al / 2)
    
    _x = r_small * np.cos(U) + r_big * np.cos(al / 2)
    _y = r_small * np.sin(U)
    

    # rotation
    angle = al * I + twist
    x = _x * np.cos(angle) - _y * np.sin(angle)
    y = _x * np.sin(angle) + _y * np.cos(angle)
    return x, y, z


#tex = pv.read_texture("./img/lines.png")
#tex.repeat = True
geom = surf_geom(onion, res_u=500, res_v=50, vmin=0, vmax=1)
p = pv.Plotter()
p.add_mesh(geom, smooth_shading=True)
p.show()
