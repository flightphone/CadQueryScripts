import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

#def um_add(plane = cq.Workplane("XY"), z = 0, r = 1, n = 4) -> cq.Workplane:
#    plane.workplane(offset=z).polygon(n, r)

def Curve3D(fn, path, r):
    h = 0.005
    a = fn(0)
    b = fn(h)
    norm = (b[0]-a[0], b[1]- a[1], b[2]-a[2])
    pl = cq.Plane(origin=a, normal= norm)


    result = (
        cq.Workplane(pl) 
        .polygon(4, r)     
        .sweep(path, isFrenet=True) 
    )
    return result    

def wineglass():
    stem_size = [(0.0, 1.7), (6.5, 3.6), (7.6, 1.9), (8.0, 1.9), (8.3, 2.6), (8.6, 1.9), (9.0, 1.9)]
    
    r2 = 1.7
    r3 = 5
    h3 = 0.9
    r4 = 1.2
    h4 = 1.
    

    bwr1 = 4
    bwr2 = 8
    bwh = 16
    fb = 2
    bwh2 = 14
    bwr11 = fb/bwh * (bwr2 - bwr1) + bwr1
    bwr22 = bwh2/bwh * (bwr2 - bwr1) + bwr1
    w1 = 0.4
    w = 0.7
    w3 = 0.6
    

    bwcone2 = cq.Solid.makeCone(bwr11  + w1, bwr22  + w1, bwh2 - fb) 
    bwcone3 = cq.Solid.makeCone(bwr11  - w1, bwr22  - w1, bwh2 - fb) 
    bwcut = bwcone2.cut(bwcone3) 
    bwcut = (cq.Workplane("XY")
             .add(bwcut)
             .fillet(w1*0.9)
             .translate((0, 0, fb))
             )
    
    
    bwcone = cq.Solid.makeCone(bwr1, bwr2, bwh)
    bw = cq.Workplane("XY").add(bwcone).edges("<Z").fillet(fb).faces(">Z").shell(-w).edges(">Z").fillet(0.2)
    bw = bw.cut(bwcut)
    
    nn = 12
    nna = 3

    def helix1(t):
        z = fb + t
        r = z/bwh * (bwr2 - bwr1) + bwr1 - w1
        alf = t / (bwh2 - fb) * nna / nn * math.tau
        x = r*math.cos(alf)
        y = r*math.sin(alf)
        return x, y, z
    
    def helix2(t):
        z = fb + t
        r = z/bwh * (bwr2 - bwr1) + bwr1 - w1
        alf = t / (bwh2 - fb) * nna / nn * math.tau
        x = r*math.cos(-alf)
        y = r*math.sin(-alf)
        return x, y, z
    
    path1 = cq.Workplane("XY").parametricCurve(helix1, start=0.0, stop = bwh2 - fb + 0.2)
    line1 = Curve3D(helix1, path1, w3)

    path2 = cq.Workplane("XY").parametricCurve(helix2, start=0.0, stop = bwh2 - fb + 0.2)
    line2 = Curve3D(helix2, path2, w3)


    bwres = [bw.val()]
    for i in range(nn):
        li1 = line1.rotate((0, 0, 0), (0, 0, 1), i / nn * 360)
        bwres.append(li1.val())
        li2 = line2.rotate((0, 0, 0), (0, 0, 1), i / nn * 360)
        bwres.append(li2.val())
        #bw = bw.cut(li1)
        #bw = bw.cut(li2)
    
    bwcomp = cq.Compound.makeCompound(bwres)
    #bwcomp = bw.val()
    
    
    
    
    stem = cq.Workplane("XY")
    for v in stem_size:
        z = v[0]
        r = v[1]
        stem.workplane(offset=z).polygon(6, r)
    stem = stem.loft(combine=True, ruled=True).fillet(0.2)    

    
    
    sp = cq.Workplane("XY").sphere(r2).translate((0, 0, stem_size[-1][0] - 0.2 + r2))
    stem = stem.union(sp)

    
    stem2 = cq.Workplane("XY").cylinder(h3, r3, centered=(True, True, False))
    stem3 = cq.Solid.makeCone(r3, r4, h4).translate((0, 0, h3))
    stem4 = cq.Workplane("XY").cylinder(h4, r4, centered=(True, True, False)).translate((0, 0, h3+h4)).fillet(0.1).val()
    stem6 = stem4.translate((0, 0, stem_size[-1][0] + 1.5 * r2))
    stem2 = stem2.add(stem3)
    stem2 = stem2.fillet(0.1)
    stem5 = cq.Solid.makeCone(0, h4, r3 + 0.01, pnt=(0, 0, 0.8*h3 + h4), dir= (1, 0, 0))
    n = 12
    for i in range(n):
        steamcut = stem5.rotate((0, 0, 0), (0, 0, 1), i/n * 360)
        stem2 = stem2.cut(steamcut)
    stem2 = stem2.add(stem4)
    stem2 = stem2.add(stem6)
    stem = stem.translate((0, 0, h3+h4 - 0.01))
    stem = stem.union(stem2)

    bwcomp = bwcomp.translate((0, 0, h3+h4 + stem_size[-1][0] + 2. * r2))
    res = cq.Compound.makeCompound([bwcomp, stem.val()])
    ass = cq.Assembly()
    ass.add(res)
    return ass
    

res = wineglass()    
#res.save("./stl/wineglass.glb")
show(res)