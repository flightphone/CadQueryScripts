import cadquery as cq
import math
from ocp_vscode import show




def um_add(plane = cq.Workplane("XY"), z = 0, r = 1, n = 4) -> cq.Workplane:
    plane.workplane(offset=z).polygon(n, r)
    #return plane


def umbre():
    n = 8
    nn = 6
    r = 4
    res = cq.Workplane("XY")
    z0 = 0
    for i in range(nn):
        a = i/(nn-1)*math.pi*0.5
        z = r - r*math.cos(a)
        d = 2*r*math.sin(a) + 0.01
        #res = um_add(res, z-z0, d, n)
        #z0 = z
        um_add(res, z, d, n)
    

    res = res.loft(combine=True)
    res2 = res.translate((0, 0, 0.5))
    res = res.cut(res2)
    #res = res.shell(0.1)
    show(res)



umbre()