import cadquery as cq
from ocp_vscode import show
import math
import numpy as np


def royal():
    th = 2
    body = [(73.6, 48.6), (55.2, 78), (17, 75.8), (0, 50.4)]
    spout = [(0, 0, 35), (18, 0, 35), (35.0, 25, 15), (50.0, 40, 24)] 
    spouttr = (-28, 0, 35)
    
    loft = cq.Workplane("XY")
    for v in body:
        loft.workplane(offset=v[0]).circle(v[1]/2)

    bott = loft.loft(combine=True)    
    bott1 = bott.shell(th)
    

    cy3 = cq.Workplane("XY").workplane(offset = body[0][0]-25).cylinder(100, body[0][1]/2 - 2*th)
    bott1 = bott1.cut(cy3)
    bott1.fillet(0.5)
    
    
    
    
    

    loftsp = cq.Workplane("XY")
    for  v in spout:
        r = v[2]/2
        h = v[0]
        x = v[1]
        loftsp.workplane(offset=h).center(x, 0).ellipse(r, 0.5*r)
        
        
        
    spoutt = loftsp.loft(combine=True)
    spoutt2 = spoutt.faces(">Z or <Z").shell(-0.8)
    midd = spoutt.cut(spoutt2)
    v = spout[-1]
    r = v[2]/2
    h = v[0]
    x = v[1]
    top = cq.Workplane("XY").workplane(offset=h + r*0.3).center(x, 0).sphere(r*1.05)
    spoutt2 = spoutt2.cut(top)
    spoutt2.fillet(0.5)
    spoutt2 = spoutt2.rotate((0, 0, 0), (0, 1, 0), -90)
    spoutt2 = spoutt2.translate(spouttr)
    midd = midd.rotate((0, 0, 0), (0, 1, 0), -90)
    midd = midd.translate(spouttr)
    spoutt2 = spoutt2.cut(midd)
    spoutt2 = spoutt2.cut(bott)

    #bott1 = bott1.union(spoutt2)
    
    tor2 = cq.Solid.makeTorus(25, 4, dir = cq.Vector(0, 1, 0))
    tor2 = tor2.translate(cq.Vector(35, 0, 40))
    tor2 = tor2.cut(bott.val())
    #tor2 = tor2.cut(bott)
    
    bott1 = bott1.cut(bott)
    bott1 = bott1.cut(midd)
    
    ass = cq.Assembly()
    ass.add(bott1.val(), name="body", color=cq.Color("deepskyblue2"))
    ass.add(spoutt2.val(), name="spout", color=cq.Color("yellow2"))
    ass.add(tor2, name="hand", color=cq.Color("yellow2"))
    return ass



res = royal()
res.save("./stl/royal.glb")
show(res)