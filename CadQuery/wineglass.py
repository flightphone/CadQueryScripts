import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

def um_add(plane = cq.Workplane("XY"), z = 0, r = 1, n = 4) -> cq.Workplane:
    plane.workplane(offset=z).polygon(n, r)

def wineglass():
    stem_size = [(0.0, 1.2), (6.5, 2.5), (7.6, 1.2), (8.0, 1.2), (8.3, 1.8), (8.6, 1.2), (9.0, 1.2)]
    stem = cq.Workplane("XY")
    for v in stem_size:
        z = v[0]
        r = v[1]
        stem.workplane(offset=z).polygon(6, r)
    stem = stem.loft(combine=True, ruled=True).fillet(0.1)    

    
    r2 = 1.4
    
    sp = cq.Workplane("XY").sphere(r2).translate((0, 0, stem_size[-1][0] - 0.2 + r2))
    stem = stem.union(sp)
    show(stem, sp)

wineglass()    