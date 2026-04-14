import numpy as np
import pyvista as pv
from surfgeometry import surf_geom, pv_boolean_difference, check_volume
import math



def wave_cone(u, v):
    u = u*math.tau
    h = 1
    r = 2.3
    n = 4
    hh = h*0.25
    dd = hh * np.sin(u*n)
    rt = v * r
    x = rt * np.cos(u)  
    y = rt * np.sin(u)
    z = h - v*(h + dd)
    return x, y, -z

def wave_cone_think():
    geom = surf_geom(wave_cone, vmin=0.2, vmax=1, res_u=200, res_v=50)
    geom = geom.clean(tolerance=0.001)
    geom = geom.fill_holes(hole_size=0.001)
    
    geom = geom.extrude((0, 0, -1.5), capping=True)
    geom = geom.clean(tolerance=0.001)
    geom = geom.fill_holes(hole_size=0.001)
    geom = geom.translate((0, 0, 2.4))
    geom = geom.rotate_z(-45/2)
    return geom


def tube(u, v):
    u = u * math.tau
    h = 4
    r = 1
    x = r*np.cos(u)
    y = r*np.sin(u)
    z = np.full_like(u, 0)
    z0 = np.full_like(u, -h)
    v1 = np.array([x, y, z])
    v0 = np.array([x, z, z0])
    res = v0 + v*(v1-v0)
    return res


def ellips(u, v):
    vmin = 0.15
    vmax = 0.65
    u = u*math.tau
    vv = 1 - np.abs((0.5 - v)*2)
    #wave
    n = 6
    ww = 0.1
    vv = vv*(1 + ww*np.cos(n*u))/(1 + ww)
    #wave
    vv = (vmin + vv*(vmax-vmin)) * math.pi
    a = 1.5
    b = 1
    c = 1
    w = 0.9

    aa = np.where(v < 0.5, a, a*w)
    bb = np.where(v < 0.5, b, b*w)
    cc = np.where(v < 0.5, c, c*w)

    x = aa*np.sin(vv)*np.cos(u)
    y = bb*np.sin(vv)*np.sin(u)
    z = cc*np.cos(vv)
    return x, y, -z

    


tex = pv.read_texture("./stl/grid.png")
tex.repeat = True
p = pv.Plotter()


#geom = wave_cone_think()
#geom.save("./stl/wave_cone.obj")
#geom = surf_geom(tube, vmin = 0.1, top=3)
geom = surf_geom(ellips, vmin=1, vmax=0, top = 3, res_u=200, repeat_u=6)

#p.show_bounds(grid='front', location='outer', all_edges=True)
#geom = geom.clean(tolerance=0.001)
#geom = geom.fill_holes(hole_size=0.001)
#geom.save("./stl/candy_vase.obj")
#print(check_volume(geom))
p.add_mesh(geom, texture=tex, smooth_shading=True)
#p.add_mesh(geom, smooth_shading=True)
#geom2 = wave_cone_think()
#geo = pv_boolean_difference(geom, geom2)
#p.add_mesh(geo, smooth_shading=True)
p.show()
