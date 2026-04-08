import cadquery as cq
from ocp_vscode import show
import math
import numpy as np


def diamond_disc(a, b, norm, d = 0.1, alf = math.pi/3):
    # a, b - ends of a segment
    # norm - normal to the surface of the solid
    # d - groove depth
    # alf - groove cutting angle
    ab = (b - a)
    len_ab = np.linalg.norm(ab)
    ab = ab/len_ab
    cos = np.dot(norm, ab)
    hv = norm - ab*cos
    hv = hv/np.linalg.norm(hv)  #
    # deep = len_ab*d, deep/(len_ab/2) = (len_ab/2)/h
    deep = len_ab*d
    h = len_ab / d / 4
    r = (h + deep)/2
    centre = (a + b)/2 + hv*(r-deep) 
    
    offs = r / math.tan(alf/2)
    r2 = r / math.sin(alf/2)

    norm2 = np.cross(ab, hv)
    norm2 = norm2 / np.linalg.norm (norm2)
    
    
    
    pl = cq.Plane(origin=(centre[0], centre[1], centre[2]), normal= (norm2[0], norm2[1], norm2[2]))
    sp1 = cq.Workplane(pl).workplane(offset=offs).sphere(r2)
    sp2 = cq.Workplane(pl).workplane(offset=-offs).sphere(r2)
    res = sp1.intersect(sp2)
    return res

def pattern0(r2, h):
    nn = 13
    nns = 5
    alf = math.tau/nn
    norm2 = np.array([0, 0, -1])
    pa = np.array([r2, 0, -h])
    pb = np.array([r2*math.cos(nns*alf), r2*math.sin(nns*alf), -h])
    disc = diamond_disc(pa, pb, norm2, 0.05, math.pi/3).val()
    discs = [disc.rotate((0, 0, 0), (0, 0, 1), 360 / nn * i) for i in range(nn)]
    combined_discs = discs[0]
    for d in discs[1:]:
        combined_discs = combined_discs.fuse(d)
    return combined_discs

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

def wave2 (n, r = 1, a = math.pi/4):
    def fn(t, n, r, d):
        r1 = r + d*r*math.sin(t*n)
        return (r1*math.cos(t), r1*math.sin(t))
    
    nn = 200
    d = 0.2
    h = r/math.tan(a)
    p = [fn (math.tau*i/nn, n, r, 0.1)  for i in range(nn)]
    res = cq.Workplane("XY").spline(p).close().workplane(offset=h).circle(0.01).loft()
    w = 2.0 * (r + d*r) + 0.5
    box = cq.Workplane("XY").box(w, w, h + 0.5, centered=(True, True, False))
    box = box.cut(res)
    #show(box)
    return box



def wave(n, r = 1) -> cq.Solid:
    alf = math.pi/n
    h = r/math.tan(alf/2) 
    cn = cq.Solid.makeCone(r, 0, h).rotate((0, 0, 0), (0, 1, 0), -90).translate((h, 0, 0))
    unioncn = [cn.rotate((0, 0, 0), (0, 0, 1), 360/n*i) for i in range(n)]
    cutn = [cn.rotate((0, 0, 0), (0, 0, 1), 360/n*i+180/n) for i in range(n)]
    ucomp = cq.Compound.makeCompound(unioncn)
    ccomp = cq.Compound.makeCompound(cutn)
    res = cq.Solid.makeCylinder(h, 2*r)
    res = res.fuse(ucomp)
    res = res.cut(ccomp)
    return res

def vase2():

    

    x_krita = [605, 575, 550, 537.5, 400, 300, 225, 150, 75]  # coords from krita project
    y_krita = [400, 400,  375, 387.5, 462.5, 462.5, 400, 387.5, 425] # coords from krita project
    y0 = 312.5  #coords from krita project

    x_coords = [(x_krita[0] - x)/100 for x in x_krita]
    y_coords = [(y - y0)/100 for y in y_krita]
    p = [(t, f) for t, f in zip(x_coords, y_coords)]
    res = (cq.Workplane("ZX").moveTo(0, 0).lineTo(x_coords[0], y_coords[0]).spline(p).lineTo(x_coords[-1], 0).close()
        .revolve(360, (0, 0, 0), (1, 0, 0))
    )
    
    w = 1./10  # width
    
    res = res.faces(">Z").shell(-w)
    res = res.edges().fillet(0.4*w)

    print(x_coords[0], x_coords[-1])
    
    ass = cq.Assembly(name="vase")
    ass.add(res.val(), name = "body")
    return ass
    #return res



res = vase2()    
#cq.exporters.export(res, "./stl/vase_body.stl")
res.save("./stl/vase_body.glb")
show(res)