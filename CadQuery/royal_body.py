import cadquery as cq
from ocp_vscode import show
import math
import numpy as np


def royal():
    th = 0.02
    body = [(0.736, 0.486), (0.552, 0.78), (0.17, 0.758), (0, 0.504)]
    
    
    loft = cq.Workplane("XY")
    for v in body:
        loft.workplane(offset=v[0]).circle(v[1]/2)

    bott = loft.loft(combine=True)    
    bott1 = bott.shell(th)
    

    #cy3 = cq.Workplane("XY").workplane(offset = body[0][0]-0.25).cylinder(1, body[0][1]/2 - 2*th)
    #bott1 = bott1.cut(cy3)
    bott1 = bott1.faces(">Z").workplane().hole(body[0][1] - 4*th, 0.5)
    
    
    bott1 = bott1.cut(bott)
    return bott1



res = royal()
#cq.exporters.export(res, "./stl/royal_body.stl")
#cq.exporters.export(res, "./stl/royal_body.step", exportType="STEP")
acc = cq.Assembly(name="royal")
acc.add(res.val(), name="royal_body")
acc.save('./stl/royal.glb')
show(res)