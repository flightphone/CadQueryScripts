import cadquery as cq
from ocp_vscode import show
import math
import numpy as np


def pencil():
    h = 7
    r = 1
    r2 = 0.3
    w = 0.1
    fi = 0.05

    rc1 = 1.1
    rc2 = 0.15
    hc = 2.2
    skin = cq.Workplane("XY").polygon(6, 2*r).polygon(6, 2*(r-w)).extrude(h).edges("|Z").fillet(fi).val()
    body = cq.Workplane("XY").polygon(6, 2*(r-w)).extrude(h).faces(">Z").workplane().hole(2*r2).val()
    coal = cq.Workplane("XY").cylinder(h, r2, centered=(True, True, False)).val()

    cone = cq.Solid.makeCone(rc1, rc2, hc)
    tg_alf = (rc1-rc2)/hc
    dh = rc2*tg_alf
    rd = math.sqrt(dh*dh + rc2*rc2)
    coneadd = cq.Workplane("XY").sphere(rd).translate((0, 0, hc - dh)).val()
    cone = cone.fuse(coneadd)

    pencil_sharpener = cq.Workplane("XY").box(2.5*rc1, 2.5*rc1, 1.5*hc, centered=(True, True, False)).val()
    pencil_sharpener = pencil_sharpener.cut(cone)

    #pencil sharpenered!!!
    pencil_sharpener = pencil_sharpener.translate((0, 0, h - hc - rd))
    skin = skin.cut(pencil_sharpener)
    body = body.cut(pencil_sharpener)
    coal = coal.cut(pencil_sharpener)

    
    ass = cq.Assembly()
    ass.add(skin, name="skin", color=cq.Color("gold1"))
    ass.add(body, name="body", color=cq.Color("burlywood"))
    ass.add(coal, name="coal", color=cq.Color("blue4"))
    return ass

res = pencil()    
res.save("stl/pencil.glb")
show(res)