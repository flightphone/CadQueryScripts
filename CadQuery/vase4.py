import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

def multi_disc_comp(combined_discs, n2):
    discs2 = [combined_discs.rotate((0, 0, 0), (0, 0, 1), i*360/n2)  for i in range(n2)]
    combined_discs2 = cq.Compound.makeCompound(discs2)
    return combined_discs2   

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


def diamond_line(sol, h0, h1, alf_shift, deep, N = 100, bound_radius = 100, k = 0.0):
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

def intersect(sol, x, y, z):
    line = cq.Edge.makeLine(cq.Vector(x, y, z), cq.Vector(0, 0, z))
    intersections = sol.intersect(line)
    if intersections:
        return (intersections.Vertices()[0].X, intersections.Vertices()[0].Y, intersections.Vertices()[0].Z)



def surf_normal(sol, z, alf, bound_radius = 100):
    
    
    h = 0.001
    z0 = z - h
    x0 = bound_radius*math.cos(alf-h)
    y0 = bound_radius*math.sin(alf-h)

    z1 = z + h
    x1 = bound_radius*math.cos(alf+h)
    y1 = bound_radius*math.sin(alf+h)

    x = bound_radius*math.cos(alf)
    y = bound_radius*math.sin(alf)


    du = np.array(intersect(sol, x1, y1, z)) - np.array(intersect(sol, x0, y0, z))
    dv = np.array(intersect(sol, x, y, z1)) - np.array(intersect(sol, x, y, z0))
    point = np.array(intersect(sol, x, y, z))
    res = np.cross(du, dv), point
    return res



    
    

def vase4():

    

    x_krita = [605, 575, 550, 537.5, 400, 300, 225, 150, 75]  # coords from krita project
    y_krita = [400, 400,  375, 387.5, 462.5, 462.5, 400, 387.5, 425] # coords from krita project
    y0 = 312.5  #coords from krita project

    x_coords = [(x_krita[0] - x)/10 for x in x_krita]
    y_coords = [(y - y0)/10 for y in y_krita]
    p = [(t, f) for t, f in zip(x_coords, y_coords)]
    res = (cq.Workplane("ZX").moveTo(0, 0).lineTo(x_coords[0], y_coords[0]).spline(p).lineTo(x_coords[-1], 0).close()
        .revolve(360, (0, 0, 0), (1, 0, 0))
    )
    
    
    
    
    nn = 13  # count segments
    nna = 5  # count twist segments
    delta = math.tau/nn
    r = 100  # bounded radius 
    w = 1.  # width
    r1 = w*0.5  # radius diamond line
    sm = 1.15   # line shift coefficient
    

  

    
    
    #normal
    
    z = (x_coords[-1])*0.3
    alf = 0
    normz, apoint = surf_normal(res.val(), z, alf)
    
    normy = np.cross(normz, np.array([0, 0, -1]))
    normx = np.cross(normy, normz)

    normz = normz/np.linalg.norm(normz)
    normx = normx/np.linalg.norm(normx)
    normy = normy/np.linalg.norm(normy)


    
    cpoint = np.array(apoint) - 25*normz
    rr = 5
    points = [apoint + rr*normx*math.cos(i*delta) + rr*normy*math.sin(i*delta)  for i in range(nn)]
    
    pnts = []
    norms = []
    
    for p in points:
        line = cq.Edge.makeLine(cq.Vector(p[0], p[1], p[2]), cq.Vector(cpoint[0], cpoint[1], cpoint[2]))
        intersections = res.val().intersect(line)
        p = (intersections.Vertices()[0].X, intersections.Vertices()[0].Y, intersections.Vertices()[0].Z)
        pnts.append(np.array(p))
        z = p[2] 
        alf = math.atan2(p[1], p[0])
        norm, _  = surf_normal(res.val(), z, alf)
        norms.append(norm)

    discs = []  

    def patt1():
        ln0 = np.linalg.norm(pnts[nna] - pnts[0])
        for i in range(nn):
            j = (i + nna) % nn
            a = pnts[i]
            b = pnts[j]
            ln1 = np.linalg.norm(b - a)
            norm = norms[i] + norms[j]
            disc = diamond_disc(a, b, norm, 0.04*ln0/ln1).val()
            discs.append(disc)

    
    def patt2():
        a = pnts[0]
        for i in range(1, nn):
            b = pnts[i]
            norm = norms[0] + norms[i]
            disc = diamond_disc(a, b, norm, 0.02).val()
            discs.append(disc)    
    
    patt2()
    combined_discs = discs[0]
    for d in discs[1:]:
        combined_discs = combined_discs.fuse(d)    


    ng = 5
    
    sh = x_coords[2]  # start diamond
    h = x_coords[-1]*0.9 # stop diamond
    line = diamond_line(res.val(), sh, h, 0, 0.5)
    line = line.rotate((0, 0, 0), (0, 0, 1), 180/ng)
    combined_discs = combined_discs.fuse(line)

    combined2 =  multi_disc_comp(combined_discs, ng)



    
    wv = wave2(nn, y_coords[-1], a=math.pi/3)
    wv = wv.translate((0, 0, x_coords[-1]- 1.35)).rotate((0, 0, 0), (0, 0, 1), -90/nn)
    # - 1.35  - empirical bias
    res = res.faces(">Z").shell(-w)
    res = res.cut(wv)
    res = res.edges().fillet(0.4*w)

    

    r2 = y_coords[0]* 0.9
    disc0 = pattern0(r2, 0) 
    res = res.cut(disc0)   
    
    
    
    res = res.cut(combined2)
    ass = cq.Assembly()
    ass.add(res)
    #ass.add(line)
    return ass



res = vase4()    
res.save("./stl/vase4.glb")
show(res)