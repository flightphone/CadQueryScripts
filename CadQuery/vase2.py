import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

def Curve3D(fn, path, r, start):
    h = 0.01
    a = fn(start)
    b = fn(start+ h)
    norm = (b[0]-a[0], b[1]- a[1], b[2]-a[2])
    pl = cq.Plane(origin=a, normal= norm)


    result = (
        cq.Workplane(pl) 
        .circle(r)
        .sweep(path, isFrenet=True) 
    )
    return result   
 
def vase2():

    

    x_krita = [ 550, 537.5, 400, 300, 225, 150, 75]
    y_krita = [ 375, 387.5, 462.5, 462.5, 400, 387.5, 425]
    y0 = 312.5

    x_coords = [(x_krita[0] - x)/10 for x in x_krita]
    y_coords = [(y - y0)/10 for y in y_krita]
    p = [(t, f) for t, f in zip(x_coords, y_coords)]
    res = (cq.Workplane("ZX").moveTo(0, 0).lineTo(x_coords[0], y_coords[0]).spline(p).lineTo(x_coords[-1], 0).close()
        .revolve(360, (0, 0, 0), (1, 0, 0))
    )
    h = x_coords[-1]
    nn = 13
    nna = 5
    r = 100
    w = 1
    r1 = w*0.7
    

    
    def helix1(t):
        z = t
        alf = t / h * nna / nn * math.tau
        x = r*math.cos(alf)
        y = r*math.sin(alf)
        line = cq.Edge.makeLine(cq.Vector(x, y, z), cq.Vector(0, 0, z))
        intersections = res.val().intersect(line)
        if intersections:
            return intersections.Vertices()[0].X, intersections.Vertices()[0].Y, intersections.Vertices()[0].Z
        
    def helix2(t):
        z = t
        alf = t / h * nna / nn * math.tau
        x = r*math.cos(-alf)
        y = r*math.sin(-alf)
        line = cq.Edge.makeLine(cq.Vector(x, y, z), cq.Vector(0, 0, z))
        intersections = res.val().intersect(line)
        if intersections:
            return intersections.Vertices()[0].X, intersections.Vertices()[0].Y, intersections.Vertices()[0].Z    
    
    box = cq.Workplane("XY").box(100, 100, 10, centered=(True, True, False))    
    path1 = cq.Workplane("XY").parametricCurve(helix1,  start=0.01, stop = 0.99*h)
    line1 = Curve3D(helix1, path1, r1, 0)
    line1 = line1.cut(box.translate((0, 0, x_coords[-1])))
    line1 = line1.cut(box.translate((0, 0, -10)))

    path2 = cq.Workplane("XY").parametricCurve(helix2,  start=0.01, stop = 0.99* h)
    line2 = Curve3D(helix2, path2, r1, 0)
    line2 = line2.cut(box.translate((0, 0, x_coords[-1])))
    line2 = line2.cut(box.translate((0, 0, -10)))

    res = res.faces(">Z").shell(-w)
    res = res.edges(">Z").fillet(0.4*w)
    
    lines = [res.val()]
    
    for i in range(nn):
        li1 = line1.rotate((0, 0, 0), (0, 0, 1), i / nn * 360)
        lines.append(li1.val())
        li2 = line2.rotate((0, 0, 0), (0, 0, 1), i / nn * 360)
        lines.append(li2.val())
    
    bwcomp = cq.Compound.makeCompound(lines)   
    ass = cq.Assembly()
    ass.add(bwcomp)
    return ass

res = vase2()    
res.save("./stl/vase2.glb")
show(res)