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

    

    x_krita = [625, 575, 550, 537.5, 400, 300, 225, 150, 75]  # coords from krita project
    y_krita = [400, 400,  375, 387.5, 462.5, 462.5, 400, 387.5, 425] # coords from krita project
    y0 = 312.5  #coords from krita project

    x_coords = [(x_krita[0] - x)/10 for x in x_krita]
    y_coords = [(y - y0)/10 for y in y_krita]
    p = [(t, f) for t, f in zip(x_coords, y_coords)]
    res = (cq.Workplane("ZX").moveTo(0, 0).lineTo(x_coords[0], y_coords[0]).spline(p).lineTo(x_coords[-1], 0).close()
        .revolve(360, (0, 0, 0), (1, 0, 0))
    )
    
    sh = x_coords[2]  # start diamond
    h = x_coords[-1]*0.98 # stop diamond
    
    
    
    nn = 13  # count segments
    nna = 5  # count twist segments
    r = 100  # bounded radius 
    w = 1.2  # width
    r1 = w*0.5  # radius diamond
    sm = 1.15   #
    

    def helix0(t, sign):
        z = t
        alf = sign * (t - sh) / (h - sh) * nna / nn * math.tau
        x = r*math.cos(alf)
        y = r*math.sin(alf)

        d = (z-(sh + h)/2.)/(h-sh)*2.
        d = d*d*d*d*r1*sm

        line = cq.Edge.makeLine(cq.Vector(x, y, z), cq.Vector(0, 0, z))
        intersections = res.val().intersect(line)
        if intersections:
            return intersections.Vertices()[0].X - math.cos(alf)*d, intersections.Vertices()[0].Y - math.sin(alf)*d, intersections.Vertices()[0].Z
    
    def helix1(t):
        return helix0(t, 1)
        
    def helix2(t):
        return helix0(t, -1)
    
    box = cq.Workplane("XY").box(100, 100, 10, centered=(True, True, False))    
    path1 = cq.Workplane("XY").parametricCurve(helix1, N=25, start=sh, stop = h)
    line1 = Curve3D(helix1, path1, r1, sh)
    line1 = line1.cut(box.translate((0, 0, h)))
    line1 = line1.cut(box.translate((0, 0, -10)))

    path2 = cq.Workplane("XY").parametricCurve(helix2, N=25, start=sh, stop = h)
    line2 = Curve3D(helix2, path2, r1, sh)
    line2 = line2.cut(box.translate((0, 0, h)))
    line2 = line2.cut(box.translate((0, 0, -10)))

    res = res.faces(">Z").shell(-w)
    res = res.edges(">Z").fillet(0.4*w)
    res = res.edges("<Z").fillet(w)
    
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