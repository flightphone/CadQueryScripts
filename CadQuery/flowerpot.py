import cadquery as cq
import math
from ocp_vscode import show


def tadj_onion(r1, al):
    cone_solid = cq.Solid.makeCone(r1*math.cos(al), 0, r1/math.cos(math.pi/2 - al) - r1*math.sin(al))
    cone_solid = cone_solid.translate((0, 0, r1*math.sin(al)))
    res = cq.Workplane("XY").sphere(r1).add(cone_solid)
    return res


def flow():
    r = 1
    r2 = 0.5*r
    h1 = -0.2*r
    h2 = 2*r
    h = 0.9 * (h2 - h1)
    w = 0.02*r
    al = math.pi*0.05
    res = tadj_onion(r, al)
    
    d = 10
    box = cq.Workplane("XY").box(d, d, d)
    res = res.cut(box.translate((0, 0, -d/2 + h1)))
    res = res.cut(box.translate((0, 0, d/2 + h2)))
    cyl = cq.Workplane("XY").cylinder(d, r2, centered=(True, True, False))
    res = res.cut(cyl)
    res = res.edges(">Z").fillet(0.05)
    
    show(res)
    ass = cq.Assembly(name="flowerpot")
    ass.add(res, name="body")
    ass.save("./stl/flowerpot2.glb")

    

flow()