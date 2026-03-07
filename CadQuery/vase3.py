import cadquery as cq
from ocp_vscode import show
import math
import numpy as np
'''
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
'''
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

def multi_disc(combined_discs, n2):
    discs2 = [combined_discs.rotate((0, 0, 0), (0, 0, 1), i*360/n2)  for i in range(n2)]
    combined_discs2 = discs2[0]
    for d in discs2[1:]:
        combined_discs2 = combined_discs2.fuse(d)
    return combined_discs2   

def pattern0(sol, hp0, hp1, nn, n, deep):
    alf = math.tau/nn * n
    line0 = diamond_line(sol, hp0, hp1, alf, deep, N=25, bound_radius=10)
    line1 = diamond_line(sol, hp0, hp1, -alf, deep, N=25, bound_radius=10)
    line = line0.fuse(line1)
    line = line.rotate((0, 0, 0), (0, 0, 1),  90/nn)
    combined = multi_disc(line, nn)
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
    
    
    
    
    

    nn = 13
    nna = 5

    lines0 = pattern0(bs.val(), -0.95*h, 0.95*h, nn, nna, -0.05)
    bs = bs.faces(">Z").shell(-w)
    res = bs
    #res = res.cut(lines0)
    res = res.union(lines0)
    '''
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
    '''
    ass = cq.Assembly()
    ass.add(res)
    return ass

res = vase()    
#res.save("./stl/vase.glb")
show(res)