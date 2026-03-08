import cadquery as cq
from ocp_vscode import show
import math
import numpy as np


def diamond_disc(a, b, norm, d = 0.1, alf = math.pi/3, ext = False):
    # a, b - ends of a segment
    # norm - normal to the surface of the solid
    # d - groove depth
    # alf - groove cutting angle
    ab = (b - a)
    len_ab = np.linalg.norm(ab)
    ab = ab/len_ab
    cos = np.dot(norm, ab)
    hv = norm - ab*cos
    hv = hv/np.linalg.norm(hv)  #
    # deep = len_ab*d, deep/(len_ab/2) = (len_ab/2)/h
    deep = len_ab*d
    h = len_ab / d / 4
    r = (h + deep)/2
    centre = (a + b)/2 + hv*(r-deep) 
    
    offs = r / math.tan(alf/2)
    r2 = r / math.sin(alf/2)

    norm2 = np.cross(ab, hv)
    norm2 = norm2 / np.linalg.norm (norm2)
    
    
    
    pl = cq.Plane(origin=(centre[0], centre[1], centre[2]), normal= (norm2[0], norm2[1], norm2[2]))
    sp1 = cq.Workplane(pl).workplane(offset=offs).sphere(r2)
    sp2 = cq.Workplane(pl).workplane(offset=-offs).sphere(r2)
    res = sp1.intersect(sp2)
    if ext:
        return res, norm2, centre
    else: 
        return res

def multi_disc(combined_discs, n2):
    discs2 = [combined_discs.rotate((0, 0, 0), (0, 0, 1), i*360/n2)  for i in range(n2)]
    combined_discs2 = discs2[0]
    for d in discs2[1:]:
        combined_discs2 = combined_discs2.fuse(d)
    return combined_discs2   


def diamond_disc_spike(a, b, norm, d = 0.1, alf = math.pi/3, d2 = 0.3, alf2 = math.pi/4, n = 6):
    disc, norm2, centre = diamond_disc(a, b, norm, d, alf, True)
    c = 2*centre - a
    disc2 = diamond_disc(a, c, norm2, math.tan(alf/2)*d2, alf2)
    pl = cq.Plane(origin=(centre[0], centre[1], centre[2]), normal= (norm2[0], norm2[1], norm2[2]))
    box = cq.Workplane(pl).box(100, 100, 100, centered=(True, True, False))
    disc2 = disc2.cut(box)
    disc2 = disc2.union(disc2.rotate((a[0], a[1], a[2]), (c[0], c[1], c[2]), 180))
    r = np.linalg.norm(a - centre)
    alf = math.acos(np.dot(a - centre, b - centre)/r/r)
    axi = centre + norm2
    discs = [disc2.rotate((centre[0], centre[1], centre[2]), (axi[0], axi[1], axi[2]), i/n * alf * 180/math.pi )  for i in range (1, n)]
    for d in discs:
        disc = disc.union(d)
    return disc    



a = np.array((1, 0, 0))
b = np.array((-1, 0, 0))
norm = np.array((0, 0, 1))
alf = math.pi/3
disc = diamond_disc_spike(a, b, norm, 0.1, math.pi/3)

show(disc)