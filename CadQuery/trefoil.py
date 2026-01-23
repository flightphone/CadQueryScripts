import cadquery as cq
from ocp_vscode import show
import math

# 1. define trefoil
def trefoil(t):
    x = math.sin(t) + 2.0 * math.sin(2.0 * t)
    y = math.cos(t) - 2.0 * math.cos(2.0 * t)
    z = -1.0 * math.sin(3.0 * t)
    return x, y, z



def Curve3D(fn, path, r):
    h = 0.005
    a = fn(0)
    b = fn(h)
    norm = (b[0]-a[0], b[1]- a[1], b[2]-a[2])
    pl = cq.Plane(origin=a, normal= norm)


    result = (
        cq.Workplane(pl) 
        .circle(r)         
        .sweep(path, isFrenet=True) 
    )
    return result

def trefoil3D():
    path = cq.Workplane("XY").parametricCurve(trefoil, start=0.0, stop = math.tau)
    r = 0.35
    res = Curve3D(trefoil, path, r)
    return res


def egg_box(u, v):
    x = u
    y = v

    a = 0.1 
    b = 0.1
    z = a * (math.sin(x / b) + math.sin(y / b))
    return cq.Vector(x, y, z)

def egg_box3D():
    surf = cq.Workplane("XY").parametricSurface(egg_box, start=-1, stop=1).extrude(0.1)
    #cube = cq.Workplane("XY").box(1.8, 1.8, 1.8).cut(surf)
    return surf

res = trefoil3D() #egg_box3D()
ass = cq.Assembly()
ass.add(res.val())
ass.save("./stl/trefoil.glb")
show(ass)
