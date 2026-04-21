import numpy as np
import pyvista as pv
import math

res_u = 240
res_v = 60
u = np.linspace(0, 1, res_u)*math.tau
x = np.cos(u)
y = np.sin(u)
z = np.full_like(u, 0)


v = np.linspace(0, 1, res_v)
X, V = np.meshgrid(x, v)
Y, _ = np.meshgrid(y, v)
Z, _ = np.meshgrid(z, v)

xr = X*V
yr = Y*V
zr = Z


points = np.column_stack((xr.ravel(), yr.ravel(), zr.ravel()))
grid = pv.StructuredGrid()
grid.points = points
grid.dimensions = [res_u, res_v, 1]

geom = grid.extract_geometry()
tex_u = np.linspace(0, 1, res_u)*math.tau
tex_v = np.linspace(0, 1, res_v)
tex_u, tex_v = np.meshgrid(tex_u, tex_v)

res_u = tex_v * np.cos(tex_u) / 2 + 0.5
res_v = tex_v * np.sin(tex_u) / 2 + 0.5
geom.active_texture_coordinates = np.column_stack((res_u.ravel(), res_v.ravel()))

geom = geom.extrude((0, 0, 0.5), capping=True)
geom.save("./stl/tablet.obj")

tex = pv.read_texture("./stl/lens.png")
tex.repeat = True

p = pv.Plotter()
p.add_mesh(geom, texture=tex)
#p.add_mesh(geom, show_edges=True)
p.show()