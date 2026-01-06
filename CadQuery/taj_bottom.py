import cadquery as cq
import math
from ocp_vscode import show
#https://cadquery.readthedocs.io/en/latest/workplane.html

def addline(l, pa, dd, w2, plane = cq.Workplane("XY")) -> cq.Workplane:
    x0 = -l/2+pa + dd/2
    y0 = -w2/2 + pa + dd/2
    y1 = 0.05*w2
    x1 = l/2-pa - dd/2
    r = (x1-x0)/4
    y2 = y1 + r
    x2 = x0 + r

    x2d = x2 - r/math.sqrt(2)
    y2d = y1 + r/math.sqrt(2)

    

    y3 = y2 + r
    x3 = 0

    y4 = y2
    x4 = x1 - (x2 - x0)

    x4d = x1 - (x2d - x0)
    y4d = y2d

    arc1 = (
             plane
            .moveTo(x0, y0)
            .lineTo(x0, y1)
            .threePointArc((x2d, y2d),(x2, y2))
            .threePointArc((x3, y3),(x4, y4))
            .threePointArc((x4d, y4d),(x1, y1))
            .lineTo(x1, y0)
            .close()
        )
    return arc1


def tile(l):
    w = 2*l
    h1 = 0.2*l
    h2 = 0.2 *h1
    pa = 0.1*l
    br = 0.4*pa
    br1 = 0.45*pa 
    dd = 2*br

    w1 = w/4
    w2 = w - w1
    tl1 = (cq.Workplane("XY").rect(l, w1).rect(l - 2*pa, w1 - 2*pa).extrude(h1).faces(">Z")
           .workplane().rect(l - 2*pa, w1 - 2*pa).rect(l - 2*pa + 2*br, w1 - 2*pa + 2*br).extrude(h2))
    tl2 = (cq.Workplane("XY").rect(l, w2).rect(l - 2*pa, w2 - 2*pa).extrude(h1)
           .faces(">Z")
           .workplane().rect(l - 2*pa, w2 - 2*pa).rect(l - 2*pa + 2*br, w2 - 2*pa + 2*br).extrude(h2)
    )
    
    tl3 = cq.Workplane("XY").rect(l - 2*pa, w2 - 2*pa)
    tl3 = addline(l, pa, dd, w2, tl3).extrude(0.7*h1)
    tl3 = (tl3           
           .faces(">Z")
           .workplane()
           .pushPoints([(2.3*pa-l/2, w2/2 - 2.3*pa), (-2.3*pa + l/2, w2/2 - 2.3*pa)])
           .circle(0.08*l).extrude(0.3*h1)
        )

    #tl2 = tl2.union(tl3)

    tl4 = addline(l, pa, dd, w2).offset2D(br)
    tl4 = addline(l, pa, dd, w2, tl4).extrude(h1)
    
    
    steps = [tl1.translate((0, ( w - w1/2 - w/2), 0)).val(),
             tl2.translate((0, w2/2 - w/2, 0)).val(),
             tl3.translate((0, w2/2 - w/2, 0)).val(),
             tl4.translate((0, w2/2 - w/2, 0)).val()
             ]
    
    res = cq.Compound.makeCompound(steps)
    return res.rotate((0, 0, 0), (1, 0, 0), 90)
    
def but():
    n = 4
    h = 2
    points = [(0.5 + i - n/2, 0) for i in range(n)]
    steps1 = [tile(1).translate((0.5 + i - n/2, -n/2, 0)) for i in range(n)]
    res1 = cq.Compound.makeCompound(steps1)
    steps2 = [res1.rotate((0, 0, 0), (0, 0, 1), 90*i) for i in range(n)]
    bx = cq.Solid.makeBox(n, n, h).translate((-n/2, -n/2, -h/2))
    steps2.append(bx)
    res2 = cq.Compound.makeCompound(steps2)
    return res2

    
    

res = but()
#res = tile(1)
cq.exporters.export(res, './stl/bottom.step')   
show(res)
