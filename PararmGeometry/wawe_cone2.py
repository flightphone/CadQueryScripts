import numpy as np
import pyvista as pv
from surfgeometry import surf_geom2, surf_geom
import math



def ellips(u, v):
    vmin = 0.15
    vmax = 0.45
    u = u*math.tau
    vv = 1 - np.abs((0.5 - v)*2)
    #wave
    n = 6
    ww = 0.08
    vv = vv*(1 + ww*np.cos(n*u) + ww*np.cos(n*u*15)/5)/(1 + ww)
    #wave
    vv = (vmin + vv*(vmax-vmin)) * math.pi
    a = 1
    b = 1
    c = 1
    w = 0.95

    aa = np.where(v < 0.5, a, a*w)
    bb = np.where(v < 0.5, b, b*w)
    cc = np.where(v < 0.5, c, c*w)

    x = aa*np.sin(vv)*np.cos(u)
    y = bb*np.sin(vv)*np.sin(u)
    z = cc*np.cos(vv)
    return x, y, -z

    


#tex = pv.read_texture("./stl/lens3.png")
#tex.repeat = True
p = pv.Plotter()


geom = surf_geom(ellips, vmin=1, vmax=0, res_u=300, res_v = 50, repeat_u=1, top=3, clear=True)
geom.save("./stl/candy_wave.obj")
p.add_mesh(geom, show_edges=True)
p.show()
