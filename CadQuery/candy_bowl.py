import cadquery as cq
from ocp_vscode import show
import math


def candy_bowl():
    r = 1
    h = 0.85
    w = 0.08
    box = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    res = (cq.Workplane("XY").sphere(r)
           .cut(box)
           .cut(box.translate((0, 0, -h-10))) 
           .faces(">Z").shell(-w)
           )
    n = 7
    d = 0.1
    nn = 100

    def fn_wave(alf, r, n, d):
        x = r*math.cos(alf)
        y = r*math.sin(alf)
        z = d*(math.sin(alf*n)) #+ d/5*math.sin(alf*n*2.*math.tau)
        return x, y, z

    
    p = [fn_wave (-math.tau*i/nn, r*1.1, n, d)  for i in range(nn)]

    path = (cq.Workplane("XY").spline(p).close().workplane(offset=0.15).circle(0.5)
            .loft().translate((0, 0, -d-0.05)).val()
        )
    res = res.cut(path)
    res = res.fillet(0.4*w)
    ass = cq.Assembly()
    ass.add(res)
    return ass


res = candy_bowl()
res.save("./stl/candy_bowl.glb")
show(res)
