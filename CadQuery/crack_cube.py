import cadquery as cq
import numpy as np
import math
import random
from ocp_vscode import show

h = 1
l = 1
w = 1

nx = 4
ny = 4
nz = 4
av = [[[(0, 0, 0) for _ in range(nz)]  for _ in range(ny)] for _ in range(nx)]

sx = l/nx
sy = w/ny
sz = h/nz

for x in range(nx):
    for y in range(ny):
        for z in range(nz):
            dx = random.random()
            dy = random.random()
            dz = random.random()

            v = ((x + dx)*sx,
                 (y + dy)*sy,
                 (z + dz)*sz
            )
            av[x][y][z] = v

results = []
'''
a naive implementation of the Voronoi covering search algorithm
'''
for ix in range(nx):
    for iy in range(ny):
        for iz in range(nz):
            a0 = av[ix][iy][iz]
            res = cq.Workplane("XY").box(l, w, h, centered=False).val()
            for x in range(nx):
                for y in range(ny):
                    for z in range(nz):
                        vx = x
                        vy = y
                        vz = z
                        if (vx, vy, vz) == (ix, iy, iz):
                            continue
                        if vx < 0 or vy < 0 or vz < 0:
                            continue
                        if vx >= nx or vy >= ny or vz >= nz:
                            continue    
                        a1 = av[vx][vy][vz]
                        norm = (a1[0] - a0[0], a1[1] - a0[1], a1[2] - a0[2])
                        ori = ((a1[0] + a0[0]) / 2 , (a1[1] + a0[1]) / 2 , (a1[2] + a0[2]) / 2 )
                        pl = cq.Plane(origin=ori, normal= norm)
                        res2 = cq.Workplane(pl).box(10, 10, 10, centered=(True, True, False)).val()
                        res = res.cut(res2)
            results.append(res)

results2 = []
for e in results:
    vv = random.random()
    if vv > 0.5:
        results2.append(e)



cres = cq.Compound.makeCompound(results2)
cq.exporters.export(cres, "./stl/crack.step")
show(cres)


