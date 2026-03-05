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
    nn = 19
    nns = 7
    alf = math.tau/nn
    norm2 = np.array([0, 0, -1])
    pa = np.array([r2, 0, -h])
    pb = np.array([r2*math.cos(nns*alf), r2*math.sin(nns*alf), -h])
    disc = diamond_disc(pa, pb, norm2, 0.07, math.pi/3).val()
    discs = [disc.rotate((0, 0, 0), (0, 0, 1), 360 / nn * i) for i in range(nn)]
    combined_discs = discs[0]
    for d in discs[1:]:
        combined_discs = combined_discs.fuse(d)
    return combined_discs

def pattern1(r, n2 = 6):
    n = 9
    delta = math.tau / n 
    alf = 0.1*math.pi
    r2 = r*math.sin(alf)
    z = r*math.cos(alf)
    points = [(r2*math.cos(delta*i), r2*math.sin(delta*i), z) for i in range(n)]
    discs = []
    a = np.array(points[0])
    for p in points[1:]:
        b = np.array(p)
        disc = diamond_disc(a, b, (a+b)/2, 0.05, math.pi/3)
        discs.append(disc.val())

    combined_discs = discs[0]
    for d in discs[1:]:
        combined_discs = combined_discs.fuse(d)
    combined_discs = combined_discs.rotate((0, 0, 0), (0, 1, 0), 110).rotate((0, 0, 0), (0, 0, 1), 90/n2)    
    discs2 = [combined_discs.rotate((0, 0, 0), (0, 0, 1), i*360/n2)  for i in range(n2)]
    combined_discs2 = discs2[0]
    for d in discs2[1:]:
        combined_discs2 = combined_discs2.fuse(d)
    return combined_discs2    


def pattern2(r, n2 = 6):
    alf0 = 0
    alf = 0.25*math.pi
    a = np.array([r*math.cos(alf0), 0, -r*math.sin(alf0)])
    b = np.array([r*math.cos(alf0+alf), 0, -r*math.sin(alf0+alf)])
    disc = diamond_disc(a, b, (a+b)/2, 0.01, math.pi/2)
    disc = disc.rotate((0, 0, 0), (0, 0, 1),  -90/n2).val()

    discs = [disc.rotate((0, 0, 0), (0, 0, 1), i*360/n2)  for i in range(n2)]
    combined_discs = discs[0]
    for d in discs[1:]:
        combined_discs = combined_discs.fuse(d)
    return combined_discs    
    

    

def candy_bowl():
    r = 1
    h = 0.9
    h0 = 0.4
    w = 0.09
    
    box = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    res = (cq.Workplane("XY").sphere(r)
           .cut(box.translate((0, 0, h0)))
           .cut(box.translate((0, 0, -h-10))) 
           .faces(">Z").shell(-w)
           )
    n = 6
    d = 0.15
    nn = 100

    def fn_wave(alf, r, n, d):
        x = r*math.cos(alf)
        y = r*math.sin(alf)
        z = d*(math.sin(alf*n)) #+ d/5*math.sin(alf*n*2.*math.tau)
        return x, y, z

    
    p = [fn_wave (-math.tau*i/nn, r*1.1, n, d)  for i in range(nn)]
    path = (cq.Workplane("XY").spline(p, periodic=True).close().workplane(offset=0.).circle(0.5)
            .loft().translate((0, 0, h0-d)).val()
        )
    res = res.cut(path)
    res = res.fillet(0.4*w)
    #res = res.edges("<Z").fillet(0.2*w)
    r2 = math.sqrt(r*r - h*h) * 0.95
    
    
    disc0 = pattern0(r2, h) 
    res = res.cut(disc0)   
    
    disc1 = pattern1(r, n) 
    res = res.cut(disc1)   

    disc2 = pattern2(r, n)
    res = res.cut(disc2)

    ass = cq.Assembly()
    ass.add(res)
    return ass





res = candy_bowl()
res.save("./stl/candy_bowl.glb")
show(res)
