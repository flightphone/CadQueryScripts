import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

n = 10
k = 0.8
y_coords = [ math.cos(math.pi  * (1 - k*i/n))  for i in range(n)]
x_coords = [ math.sin(math.pi  * (1 - k*i/n)) * (math.sin(math.pi / 2 * (1 - k*i/n)) ** 2)  for i in range(n)]

p = [(t, f) for t, f in zip(x_coords, y_coords)]
res = (cq.Workplane("ZX").moveTo(x_coords[0], 0).lineTo(x_coords[0], y_coords[0]).spline(p).lineTo(x_coords[-1], 0).close()
        .revolve(360, (0, 0, 0), (0, 1, 0)).rotate((0, 0, 0), (0, 1, 0), -90).translate((0, 0, 1))
    )
#box = cq.Workplane("XY").workplane(offset=max(x_coords) + 1).box(1, 1, 1, centered=(True, True, False))
show(res)
#cq.exporters.export(res, './stl/larme.stl')
#cq.exporters.export(res, './stl/larme.step')
acc = cq.Assembly(name="larme")
acc.add(res.val(), name="body")
acc.save('./stl/larme.glb')
#print(max(x_coords) + 1) 
#1.64