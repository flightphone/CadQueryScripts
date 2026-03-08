import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

def diamond_line(sol, h0, h1, alf_shift, deep, N = 100, bound_radius = 100, k = 0.45):
    def helix(t):
        z = h0 + t*(h1 - h0)
        alf = alf_shift * t
        x = bound_radius*math.cos(alf)
        y = bound_radius*math.sin(alf)

        d = (t - 0.5)*2
        d = d*d*deep/2 + k*(1-t)*(1-t)*(1-t)*deep

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
        .polygon(4, deep)     
        .sweep(path, isFrenet=False) 
    )
    return result.val()    

def diamond_disc(a, b, norm, d = 0.1, alf = math.pi/3, ext = False):
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
    if ext:
        return res, norm2, centre
    else: 
        return res

def multi_disc(combined_discs, n2):
    discs2 = [combined_discs.rotate((0, 0, 0), (0, 0, 1), i*360/n2)  for i in range(n2)]
    combined_discs2 = discs2[0]
    for d in discs2[1:]:
        combined_discs2 = combined_discs2.fuse(d)
    return combined_discs2   

def multi_disc_comp(combined_discs, n2):
    discs2 = [combined_discs.rotate((0, 0, 0), (0, 0, 1), i*360/n2)  for i in range(n2)]
    combined_discs2 = cq.Compound.makeCompound(discs2)
    return combined_discs2   

def pattern0(r2, h):
    nn = 19
    nns = 7
    alf = math.tau/nn
    norm2 = np.array([0, 0, -1])
    pa = np.array([r2, 0, -h])
    pb = np.array([r2*math.cos(nns*alf), r2*math.sin(nns*alf), -h])
    disc = diamond_disc(pa, pb, norm2, 0.07, math.pi/3).val()
    combined_discs = multi_disc(disc, nn)
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
    combined_discs = combined_discs.rotate((0, 0, 0), (0, 1, 0), 105).rotate((0, 0, 0), (0, 0, 1), 90/n2)    
    
    combined_discs2 = multi_disc_comp(combined_discs, n2)
    return combined_discs2    


def pattern2(r, n2 = 6):
    n = 13
    ns = 5
    delta = math.tau / n 
    alf = 0.06*math.pi
    r2 = r*math.sin(alf)
    z = r*math.cos(alf)
    a = np.array((r2*math.cos(0), r2*math.sin(0), z))
    b = np.array((r2*math.cos(delta*ns), r2*math.sin(delta*ns), z))
    norm = a + b
    disc = diamond_disc(a, b, norm, 0.07, math.pi/3).val()
    combined_discs =  multi_disc(disc, n)
    combined_discs = combined_discs.rotate((0, 0, 0), (0, 1, 0), 135).rotate((0, 0, 0), (0, 0, 1), -90/n2)    
    
    combined_discs2 = multi_disc_comp(combined_discs, n2)
    return combined_discs2 
    

def pattern3(sol, hp0, hp1, nn, n):
    alf = math.tau/nn * n
    line0 = diamond_line(sol, hp0, hp1, alf, 0.12, N=50, bound_radius=3)
    line0 = line0.rotate((0, 0, 0), (0, 0, 1),  90/nn)
    line1 = diamond_line(sol, hp0, hp1, -alf, 0.12, N=50, bound_radius=3)
    line1 = line1.rotate((0, 0, 0), (0, 0, 1),  90/nn)
    lines0 = multi_disc_comp(line0, nn)
    lines1 = multi_disc_comp(line1, nn)
    combined = lines0.fuse(lines1)
    line = line0.fuse(line1)
    combined = multi_disc(line, nn)
    return combined    

def pattern4(sol, nn):
    lines = [(0.07 - 0.03*i, (0.15 - 0.02*i)*math.pi) for i in range(7)]
    dlines = [diamond_line(sol, p[0], p[0], p[1], 0.01, 50, 10, 0.).rotate((0, 0, 0), (0, 0, 1),  -90/nn - p[1]/2*360/math.tau) for p in lines]
    combined = dlines[0]
    for d in dlines[1:]:
        combined = combined.fuse(d)
    combined2 = multi_disc_comp(combined, nn)
    return combined2


   

def candy_bowl():
    r = 1
    h = 0.9
    h0 = 0.4
    w = 0.09
    
    box = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    res = (cq.Workplane("XY").sphere(r)
           .cut(box.translate((0, 0, h0)))
           .cut(box.translate((0, 0, -h-10))) 
           )
    n = 6
    d = 0.15
    nn = 100

    hp0 = -0.89
    hp1 = 0.3
    dline0 = pattern3(res.val(), hp0, hp1, n, 1)
    dline1 = pattern4(res.val(), n)
    res = res.faces(">Z").shell(-w)


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

    r2 = math.sqrt(r*r - h*h) * 0.95
    res = res.cut(dline0)
    res = res.cut(dline1)
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
