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
    r1 = 0.15
    r2 = 0.2
    r3 = 0.5

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
    hand = cq.Workplane("XY").cylinder(2*r, r1).translate((0, 0, r))
    res = res.union(hand)

    hand2 = cq.Workplane("XY").circle(r2).revolve(180, (-r3, 1, 0), (-r3, 0, 0)).faces("<Z").workplane().sphere(r2).translate((2*r3, 0, 2*r - 0.01))
    res = res.union(hand2)
    
    hand3 = cq.Workplane("XY").cylinder(2*r2, r2).translate((0, 0, 2*r - r2 ))
    res = res.union(hand3)
    return res
    
    



res = umbre()
show(res)
#cq.exporters.export(res, './stl/umbr.stl')  