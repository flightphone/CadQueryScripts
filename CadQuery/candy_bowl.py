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
    n = 5
    d = 0.2
    nn = 100

    def fn_wave(alf, r, n, d):
        x = r*math.cos(alf)
        y = r*math.sin(alf)
        z = d*(math.sin(alf*n)) #+ d/5*math.sin(alf*n*2.*math.tau)
        return x, y, z

    
    p = [fn_wave (-math.tau*i/nn, r*1.1, n, d)  for i in range(nn)]

    path = (cq.Workplane("XY").spline(p, periodic=True).close().workplane(offset=0.15).circle(0.5)
            .loft().translate((0, 0, -d-0.05)).val()
        )
    res = res.cut(path)
    res = res.fillet(0.4*w)
    #res = res.faces("<Z").fillet(w)
    ass = cq.Assembly()
    ass.add(res)
    return ass


def wave2 (n, r = 1, a = math.pi/4):
    def fn(t, n, r, d):
        r1 = r + d*r*abs(math.sin(t*n))
        return (r1*math.cos(t), r1*math.sin(t))
    
    nn = 50
    d = 0.2
    h = r/math.tan(a)
    p = [fn (math.tau*i/nn, n, r, 0.1)  for i in range(nn)]
    res = cq.Workplane("XY").spline(p, periodic=True).close().workplane(offset=h).circle(0.01).loft()
    w = 2.0 * (r + d*r) + 0.5
    box = cq.Workplane("XY").box(w, w, h + 0.5, centered=(True, True, False))
    box = box.cut(res)
    #show(box)
    return box


def candy_bowl2():
    r = 1
    h = 0.85
    w = 0.05
    box = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    res = (cq.Workplane("XY").sphere(r)
           .cut(box)
           .cut(box.translate((0, 0, -h-10))) 
           .faces(">Z").shell(-w)
           )
    n = 4
    d = 0.2
    nn = 100

    def fn_wave(alf, r, n, d):
        x = r*math.cos(alf)
        y = r*math.sin(alf)
        z = d*(abs(math.sin(alf*n))) #+ d/5*math.sin(alf*n*2.*math.tau)
        return x, y, z

    
    p = [fn_wave (-math.tau*i/nn, r*1.1, n, d)  for i in range(nn)]
    path = (cq.Workplane("XY").spline(p, periodic=True).close().workplane(offset=0.15).circle(0.5)
            .loft().translate((0, 0, -d-0.05)).val()
        )
    
    res = res.cut(path)
    res = res.fillet(0.4*w)
    
    ass = cq.Assembly()
    ass.add(res)
    return ass


res = candy_bowl()
#res = wave2(6)
#res.save("./stl/candy_bowl.glb")
show(res)
