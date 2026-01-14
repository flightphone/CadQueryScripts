import cadquery as cq
import numpy as np
import math
import random
from ocp_vscode import show



def voronoi(l, w, h, nx, ny, nz):
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
                #res = cq.Workplane("XY", origin=((ix-1)*sx, (iy-1)*sy, (iz - 1)*sz)).box(3*sx, 3*sy, 3*sz, centered=False).val()
                for x in range(nx):
                    for y in range(ny):
                        for z in range(nz):
                            vx = x #+ ix - 1
                            vy = y #+ iy - 1
                            vz = z #+ iz - 1
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
                            res2 = cq.Workplane(pl).box(1000, 1000, 1000, centered=(True, True, False)).val()
                            res = res.cut(res2)
                results.append(res)
    return results



text = "USSR"

letters = cq.Workplane("XY").text(text, 20, 5, valign="bottom", halign="left").combine().val()
bx = letters.BoundingBox()
letters = letters.translate((-bx.xmin, -bx.ymin, -bx.zmin))
bx = letters.BoundingBox()

l = bx.xlen
w = bx.ylen
h = bx.zlen

nz = 2     
ny = nz * int (w/h)
nx = nz * int (l/h)

voronoi_cells = voronoi(l, w, h, nx, ny, nz)

shards = []
for cell in voronoi_cells:
    # intersect
    fragment = cell.intersect(letters)
    
    # not null fragment
    if fragment and fragment.Volume() > 0.001:
        shards.append(fragment)

assembly = cq.Assembly()
for i, shard in enumerate(shards):
    vv = random.random()
    if (vv < 0.6):
        assembly.add(shard, name=f"shard_{i}")


assembly.save("./stl/cracked_text.gltf", exportType="GLTF")
show(assembly)
