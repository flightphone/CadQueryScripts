import cadquery as cq
import math
from ocp_vscode import show

def ring (r, w):
    res = (cq.Workplane("XY")
    .cylinder(w, r)
    .faces(">Z")
    .workplane()
    .hole(2*r - 2*w))
    return res

    

def hyp():
    r = 8   #big radius
    w = 0.15 # radius edge
    n = 22  #count lines
    n2 = 4  #section
    h = 16  #height hyperboloid

    x = r * math.cos(n2/n * 2 * math.pi)
    y = r * math.sin(n2/n * 2 * math.pi)
    l = math.sqrt(4*y*y + h*h)
    cy0 = cq.Workplane("XY").cylinder(l, w, direct=(0, y, h/2)).translate((x, 0, 0))
    cy1 = cq.Workplane("XY").cylinder(l, w, direct=(0, y, -h/2)).translate((x, 0, 0))
    res = cy0.union(cy1)
    
    steps = [res.rotate((0, 0, 0), (0, 0, 1), i * 360 / n).val() for i in range(n)]
    ring1 = ring (x + w, 2*w)
    ring2 = ring (r + w, 2*w).translate((0, 0, h/2))
    ring3 = ring (r + w, 2*w).translate((0, 0, -h/2))
    steps.append(ring1.val())
    steps.append(ring2.val())
    steps.append(ring3.val())
    res1 = cq.Compound.makeCompound(steps)

    #steps2 = [res1, res1.translate((0, 0, h)), res1.translate((0, 0, -h))]
    #res2 = cq.Compound.makeCompound(steps2)
    return res1
    



res = hyp()
show(res)
#res.export('stl/hyper.step')
#cq.exporters.export(res, './stl/hyper.stl')   

