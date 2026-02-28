import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

def Curve3D(fn, path, r, start):
    h = 0.0001
    a = fn(start)
    b = fn(start+ h)
    norm = (b[0]-a[0], b[1]- a[1], b[2]-a[2])
    pl = cq.Plane(origin=a, normal= norm)


    result = (
        cq.Workplane(pl) 
        .polygon(4, r)
        .offset2D(-r*0.1)  #Copilot
        .offset2D(r*0.1)
        .sweep(path, isFrenet=True) 
    )
    return result    

def vase():
    r1 = 4.6
    r2 = 9.6
    h = 6.8
    w = 0.75
    w3 = w*0.9
    k = 1.027
    bs = cq.Workplane("XZ").ellipseArc(r1, r2, 90, 270).close().revolve().translate((0, 0, r2))
    box = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    bs = bs.cut(box.translate((0, 0, h*k)))
    bs = bs.cut(box.translate((0, 0, -h*k - 10)))
    bs = bs.faces(">Z").shell(-w)

    nn = 22
    nna = 5

    def helix1(t):
        z = t
        r = r1*math.sqrt(1 - z*z/r2/r2) - z*z*z*z/h/h/h/h * w3/2
        #r = r1*math.sqrt(1 - z*z/r2/r2) 
        alf = (t + h) / 2 / h * nna / nn * math.tau
        x = r*math.cos(alf)
        y = r*math.sin(alf)
        return x, y, z
    
    def helix2(t):
        z = t
        r = r1*math.sqrt(1 - z*z/r2/r2) - z*z*z*z/h/h/h/h * w3/2
        #r = r1*math.sqrt(1 - z*z/r2/r2) 
        alf = (t + h) / 2 / h * nna / nn * math.tau
        x = r*math.cos(-alf)
        y = r*math.sin(-alf)
        return x, y, z
    
    path1 = cq.Workplane("XY").parametricCurve(helix1,  start=-h, stop = h)
    line1 = Curve3D(helix1, path1, w3, -h)
    #line1 = line1.cut(box.translate((0, 0, h)))
    #line1 = line1.cut(box.translate((0, 0, -h - 10.00)))


    path2 = cq.Workplane("XY").parametricCurve(helix2,  start=-h, stop = h)
    line2 = Curve3D(helix2, path2, w3, -h)
    #line2 = line2.cut(box.translate((0, 0, h)))
    #line2 = line2.cut(box.translate((0, 0, -h - 10.00)))


    bwres = [bs.val()]
    for i in range(nn):
        li1 = line1.rotate((0, 0, 0), (0, 0, 1), i / nn * 360)
        bwres.append(li1.val())
        li2 = line2.rotate((0, 0, 0), (0, 0, 1), i / nn * 360)
        bwres.append(li2.val())
        
    bwcomp = cq.Compound.makeCompound(bwres)
    ass = cq.Assembly()
    ass.add(bwcomp)
    return ass

res = vase()    
#res.save("./stl/vase.glb")
show(res)