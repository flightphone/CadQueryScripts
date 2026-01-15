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
                for x in range(nx):  #nx
                    for y in range(ny): #ny
                        for z in range(nz): #nz
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
                            res2 = cq.Workplane(pl).box(1000, 1000, 1000, centered=(True, True, False)).val()
                            res = res.cut(res2)
                results.append(res)
    return results


def voronoi_cube(nx, ny, nz, dx = 1):
    l = nx*dx
    w = ny*dx
    h = nz*dx
    
    av = [[[(0, 0, 0) for _ in range(nz)]  for _ in range(ny)] for _ in range(nx)]

    sx = dx
    sy = dx
    sz = dx
    #this algoritm for sx = sy = sz = dx

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
                #For Cube Only where sx = sy = sz
                for x in range(5):  #nx
                    for y in range(5): #ny
                        for z in range(5): #nz
                            ign = 0
                            if x == 0 or x == 4:
                                ign = ign + 1
                            if y == 0 or y == 4:
                                ign = ign + 1    
                            if z == 0 or z == 4:
                                ign = ign + 1    
                            if ign > 1:
                                continue    
    

                            vx = x + ix - 2
                            vy = y + iy - 2
                            vz = z + iz - 2
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


def craked_text(text, level) -> cq.Assembly:
    
    letters = cq.Workplane("XY").text(text, 20, 5, valign="bottom", halign="left").combine().val()
    bx = letters.BoundingBox()
    letters = letters.translate((-bx.xmin, -bx.ymin, -bx.zmin))
    bx = letters.BoundingBox()

    l = bx.xlen
    w = bx.ylen
    h = bx.zlen

    nz = 2     
    ny = nz * math.ceil(w/h)
    nx = nz * math.ceil(l/h)
    #ny = nz * int(w/h)
    #nx = nz * int(l/h)
    dx = l/nx

    #voronoi_cells = voronoi(l, w, h, nx, ny, nz)   # 184 sec
    voronoi_cells = voronoi_cube(nx, ny, nz, dx)  # 62 sec

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
        if (vv < level):
            assembly.add(shard, name=f"shard_{i}")
    return assembly        

def craked_cube(nx, ny, nz, level = 1):
    voronoi_cells = voronoi_cube(nx, ny, nz)  #125 - 35, 46 sec
    #voronoi_cells = voronoi(nx, ny, nz, nx, ny, nz) #125 - 91 sec
    assembly = cq.Assembly()
    for i, shard in enumerate(voronoi_cells):
        vv = random.random()
        if (vv < level):
            assembly.add(shard, name=f"shard_{i}")
    return assembly        

import time

start = time.time()
assembly = craked_text("GREEK", 1) #50
assembly.save("./stl/cracked_text3.gltf", exportType="GLTF")
#assembly = craked_cube(12, 10, 4) #120 - 24 sec, 125 - 35sec, 240 - 65, 480 - 101 sec, 208 
#assembly = craked_cube(15, 15, 1) # 16 sec

print(f"run: {time.time() - start} sec")  
show(assembly)
