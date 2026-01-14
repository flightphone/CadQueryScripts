import cadquery as cq
import math
from ocp_vscode import show


def sphere_toy():
    r = 1
    rc = 2
    res = cq.Solid.makeCone(2, 0.1, 2).translate((0, 0, -1.7))
    res = cq.Workplane("XY").sphere(r).cut(res).shell(0.1)
    return res

res = sphere_toy()
show(res)
