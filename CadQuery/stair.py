import cadquery as cq
from ocp_vscode import show

def stair():
    # helix parametrs
    r = 8    # radius
    p = 40       # pitch
    h = 40      # 
    hs = 2.5 
    alf = 360/p * hs
    r1 = 2

    ax = cq.Workplane("XY").cylinder(height=h + hs, radius = r1).translate((0, 0, (h + hs)/2 - hs / 2))
    step = cq.Workplane("XY").cylinder(height=hs - 0.01, radius = (2*r - r1 + 0.01), angle=alf).rotate((0, 0, 0), (0, 0, 1), -alf)
    n = int(h / hs)
    steps = [step.rotate((0, 0, 0), (0, 0, 1), i* alf).translate((0, 0, i * hs)).val()  for i in range(n + 1)]
    steps_union = cq.Workplane("XY").add(steps).union()

    # helix trace
    helix = cq.Wire.makeHelix(pitch=p, height=h - 0.01, radius=r - 0.05)

    # profile
    strip = (
        cq.Workplane("XZ")
        .center(r, 0)
        .rect(2.*(r-r1), hs)
        .sweep(cq.Workplane(obj=helix), isFrenet=True)
    )
    ass = cq.Assembly()
    ass.add(ax.val(), name="Column", color=cq.Color("gold"))
    ass.add(steps_union.val(), name="steps", color=cq.Color("burlywood3"))
    ass.add(strip.val(), name="strip", color=cq.Color("deeppink"))
    return ass

res = stair()    
res.export('./stl/stair.glb')
show(res)
#cq.exporters.export(res, './stl/stair.step')   
