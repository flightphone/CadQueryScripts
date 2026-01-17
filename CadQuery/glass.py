import cadquery as cq
import math
from ocp_vscode import show

def glass():
    h = 105
    r1 = 55/2
    r2 = 95/2
    htop = 25
    hbot = 10
    th = 3
    res_solid = cq.Solid.makeCone(r1, r2, h)
    res = cq.Workplane("XY").add(res_solid)
    glm = res.translate((0, 0, 0.1))
    res = res.cut(glm)
    res = res.shell(th)
    
    ha = h-htop-hbot
    k =  (r2-r1)/h
    ra1 = r1 + hbot*k + th-0.8
    ra2 = r1 + (h - htop)*k + th-0.8
    glm2_solid = cq.Solid.makeCone(ra1, ra2, ha).translate((0, 0, hbot))
    glm2 = cq.Workplane("XY").add(glm2_solid)
    box = cq.Workplane("XY").box(100, 100, ha, False).translate((-50, -50, hbot))
    box = box.cut(glm2)
    res = res.cut(box)
    
    re = 3
    eps = -2
    n = 10
    ae = math.atan2(r2-r1, h)
    he = ha/math.cos(ae) - 2*re
    edg = cq.Workplane("XY").box(100, 2*re, he, False).translate((-50, -re, 0))
    cy1 = cq.Workplane("YZ").cylinder(100, re)
    edg = edg.union(cy1)
    
    cy1 = cy1.translate((0, 0, he))
    edg = edg.union(cy1)
    
    edg = edg.rotate((0, 0, 0),(1, 0, 0), -ae*180/math.pi)
    edg = edg.translate((0, ra1-eps, hbot + re*0.8))
    for i in range(n):
        edg = edg.rotate((0, 0, 0),(0, 0, 1), 360/n)
        res = res.cut(edg)

    
    return res

def pot():
    rp = 20
    th = 2.5
    sp = 12
    h1 = math.sqrt(rp*rp - sp*sp)
    d2 = th*h1/rp
    res = cq.Workplane("XY").sphere(rp)
    box = cq.Workplane("XY").box(50, 50, 20, False).translate((-25, -25, -37))
    res = res.cut(box)
    
    res = res.shell(-th)
    #res = res.cut(res1)
    cy = cq.Workplane("XY").cylinder(30, sp).translate((0, 0, 10 + 15))
    res = res.cut(cy)
    #res = res.edges("%CIRCLE").chamfer(0.5)
    res = res.edges("%CIRCLE").fillet(0.5)
    

    #tor = Part.makeTorus(sp, d2, App.Vector(0, 0, h1 - d2))
    #res = res.fuse(tor)
    
    #res = res.makeFillet(1, [res.Edges[2], res.Edges[4]])
    return res            

res = glass()
assembly = cq.Assembly()
assembly.add(res.val(), name=f"glass")
assembly.export("./stl/glasss.glb")
show(assembly)
#cq.exporters.export(res, './stl/glass.step')   
#res = pot()
#show(res)
#cq.exporters.export(res, './stl/pot.stl')   
#print("ok!!!")