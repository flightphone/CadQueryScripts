import cadquery as cq
from ocp_vscode import show

def stair():
    # helix parametrs
    r = 6      # radius
    p = 20       # pitch
    h = 40      # 
    hs = 2.5
    alf = 360/p * hs
    r1 = 2

    ax = cq.Workplane("XY").cylinder(height=h + hs, radius = r1).translate((0, 0, (h + hs)/2 - hs / 2))
    step = cq.Workplane("XY").cylinder(height=hs, radius = (2*r - r1 + 0.01), angle=alf).rotate((0, 0, 0), (0, 0, 1), -alf)
    n = int(h / hs)
    steps = [step.rotate((0, 0, 0), (0, 0, 1), i* alf).translate((0, 0, i * hs))  for i in range(n + 1)]

    # helix trace
    helix = cq.Wire.makeHelix(pitch=p, height=h, radius=r)

    # profile
    strip = (
        cq.Workplane("XZ")
        .center(r, 0)
        .rect(2.*(r-r1), hs)
        .sweep(cq.Workplane(obj=helix), isFrenet=True)
    )
    
    for s in steps:
        ax = ax.union(s)
    ax = ax.union(strip)
    return ax

res = stair()    
show(res)
cq.exporters.export(res, './stl/stair.stl')