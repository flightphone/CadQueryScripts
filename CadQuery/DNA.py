import cadquery as cq
from ocp_vscode import show
import math

def line_edge(a = (0, 0, 0), b = (1, 1, 1), w = 0.5):
    norm = (b[0]-a[0], b[1]- a[1], b[2]-a[2])
    l = math.sqrt(norm[0]*norm[0] + norm[1]*norm[1] + norm[2]*norm[2])
    pl = cq.Plane(origin=a, normal= norm)
    res = cq.Workplane(pl).cylinder(l, w, centered=(True, True, False))
    return res.val()


def dna():
    # helix parametrs
    r = 1.   # radius  (width DNA)
    h = 15    # height DNA
    p = 10    # pitch = height DNA = 360 degree
    r0 = 0.05 # radius chain
    r1 = 0.2 
    n = int(10 * h /p) + 1    # 10 nitrogenous bases per turn of DNA  
    
     
    # helix trace
    helix = cq.Wire.makeHelix(pitch=p, height=h, radius=r)
    chain1 = (
        cq.Workplane("XY")
        .center(r, 0)
        .circle(r0)
        .sweep(cq.Workplane(obj=helix), isFrenet=True)
    )
    chain2 = chain1.rotate((0, 0, 0), (0, 0, 1), 180)
    ass = cq.Assembly()
    ass.add(chain1.val(), name="chain1", color=cq.Color("blue"))
    ass.add(chain2.val(), name="chain2", color=cq.Color("blue"))
    
    spl = []
    spr = []
    lines = []
    for i in range(n):
        alf = math.pi/5 * i
        a = (r*math.cos(alf), r*math.sin(alf), alf/2/math.pi * p)
        b = (r*math.cos(alf + math.pi), r*math.sin(alf+ math.pi), alf/2/math.pi * p)
        sp1 = cq.Workplane("XY", origin=a).sphere(r1).val()
        spl.append(sp1)
        sp2 = cq.Workplane("XY", origin=b).sphere(r1).val()
        spr.append(sp2)
        ln = line_edge(a, b, r0)
        lines.append(ln)

    cml = cq.Compound.makeCompound(spl)
    cmr = cq.Compound.makeCompound(spr)
    cms = cq.Compound.makeCompound(lines)
    ass.add(cml, name="left", color=cq.Color("red"))
    ass.add(cmr, name="right", color=cq.Color("green"))
    ass.add(cms, name="steps", color=cq.Color("yellow"))

    return ass


ass = dna()
ass.export('./stl/dna.glb')
show(ass)