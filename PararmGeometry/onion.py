import numpy as np
import pyvista as pv
from surfgeometry import surf_geom
import math


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


tex = pv.read_texture("./img/lines.png")
tex.repeat = True
geom = surf_geom(onion, res_u=500, res_v=50, vmin=0, vmax=1)
p = pv.Plotter()
p.add_mesh(geom, texture = tex, smooth_shading=True)
p.show()
