import cadquery as cq
from ocp_vscode import show
import math
w = 0.1
res = cq.Workplane("XY").box(1+w, 1+w, 1, centered=(True, True, False))
res = res.edges("|Z").fillet(w/2)
res = res.cut(
    cq.Workplane("XY").box(1, 1, 2)
)
#cq.exporters.export(res, "./stl/box3.step", exportType="STEP")
#show(res)
#res2 = cq.Workplane("XY").box(1, 1, 1+w).faces(">Z").shell(-w/2)
ass = cq.Assembly(name = "box")
ass.add(res.val(), name="skin")
#ass.add(res2.val(), name="body")
ass.save("./stl/box2.glb")
show(ass)
