import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

def diamond_line(sol, h0, h1, alf_shift, deep, N = 100, bound_radius = 100, k = -0.0):
    def helix(t):
        z = h0 + t*(h1 - h0)
        alf = alf_shift * t
        x = bound_radius*math.cos(alf)
        y = bound_radius*math.sin(alf)

        d = (t - 0.5)*2
        d = d*d*deep/2 + k*t*t*t*deep

        line = cq.Edge.makeLine(cq.Vector(x, y, z), cq.Vector(0, 0, z))
        intersections = sol.intersect(line)
        if intersections:
            return intersections.Vertices()[0].X + math.cos(alf)*d, intersections.Vertices()[0].Y + math.sin(alf)*d, intersections.Vertices()[0].Z
        else:
            return (x, y, z)
    path = cq.Workplane("XY").parametricCurve(helix, N=N, start=0, stop = 1)    
    h = 0.001
    a = helix(0)
    b = helix(h)
    norm = (b[0]-a[0], b[1]- a[1], b[2]-a[2])
    pl = cq.Plane(origin=a, normal= norm)
    result = (
        cq.Workplane(pl) 
        .polygon(4, abs(deep))     
        .sweep(path, isFrenet=False) 
    )
    return result.val()    


def pattern0(sol, hp0, hp1, nn, n, deep, k):
    alf = math.tau/nn * n
    line0 = diamond_line(sol, hp0, hp1, alf, deep, N=25, bound_radius=10, k = k)
    line1 = diamond_line(sol, hp0, hp1, -alf, deep, N=25, bound_radius=10, k = k)
    
    line0 = line0.rotate((0, 0, 0), (0, 0, 1),  90/nn)
    line1 = line1.rotate((0, 0, 0), (0, 0, 1),  90/nn)
    combined = []
    for i in range(nn):
        combined.append(line0.rotate((0, 0, 0), (0, 0, 1), i*360/nn))    
        combined.append(line1.rotate((0, 0, 0), (0, 0, 1), i*360/nn))    
    return combined    


def vase():
    r1 = 0.46
    r2 = 0.96
    h = 0.68
    w = 0.075
    w3 = w*0.9
    k = 1.028
    bs = cq.Workplane("XZ").ellipseArc(r1, r2, 90, 270).close().revolve().translate((0, 0, r2))
    box = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    bs = bs.cut(box.translate((0, 0, h*k)))
    bs = bs.cut(box.translate((0, 0, -h*k - 10)))
    
    
    nn = 17
    nna = 5

    lines = pattern0(bs.val(), -0.95*h, 0.95*h, nn, nna, -0.05, 0)
    bs = bs.faces(">Z").shell(-w)
    lines.append(bs.val())
    res = cq.Compound.makeCompound(lines)

    
    ass = cq.Assembly()
    ass.add(res)
    return ass

res = vase()    
#res.save("./stl/vase.glb")
show(res)