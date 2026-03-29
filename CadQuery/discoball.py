import cadquery as cq
import math
from ocp_vscode import show

def um_add2(z, z0, d, d0,  n) -> cq.Workplane:
    res = (cq.Workplane("XY")
           .workplane(offset=z0)
           .polygon(n, d0)
           .workplane(offset=z-z0).polygon(n, d)
           .loft(combine=True)
    )
    return res.val()

def discoball():
    n = 20
    nn = 13
    r = 4
    res = cq.Workplane("XY")
    z0 = 0
    d0 = 0.01
    steps = []
    for i in range(1, nn):

        a = i/(nn-1)*math.pi
        z = r - r*math.cos(a)
        d = 2*r*math.sin(a) + 0.01
        steps.append(um_add2(z, z0, d, d0, n))
        z0 = z
        d0 = d

    res = cq.Compound.makeCompound(steps)    
    return res
    

#res = discoball()
#ass = cq.Assembly()
#ass.add(res)
#ass.export('./stl/disco.glb')
#show(ass)

def uv(p, h1, h2):
    if (p[2] < h1 or p[2] > h2):
        return None
    
    x = p[0]
    y = p[1]
    z = p[2]
    a = ((math.atan2(y, x) + math.tau) % math.tau) / math.tau
    b = (p[2] - h1) / (h2 - h1)
    return (a, b)



print(uv ((0, 1, 3), 0, 6))


    

