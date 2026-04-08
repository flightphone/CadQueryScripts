import pyvista as pv
import numpy as np
import math

def trefoil(t):
    x = np.sin(t) + 2.0 * np.sin(2.0 * t)
    y = np.cos(t) - 2.0 * np.cos(2.0 * t)
    z = -1.0 * np.sin(3.0 * t)
    points = np.column_stack((x, y, z))
    return points

def polyline_from_points(points):
    poly = pv.PolyData()
    poly.points = points
    the_cell = np.arange(0, len(points), dtype=np.int_)
    the_cell = np.insert(the_cell, 0, len(points))
    poly.lines = the_cell
    return poly

# 1. Генерируем параметры кривой (например, спираль)
t = np.linspace(0, math.tau + 0.01, 200)
# Собираем точки в массив (N, 3)
points = trefoil(t)

polyline = polyline_from_points(points)

# 3. Превращаем линию в меш-трубку
# radius: толщина трубки
# n_sides: количество граней (чем больше, тем круглее сечение)
tube_mesh = polyline.tube(radius=0.5, n_sides=40)
tube_mesh = tube_mesh.extract_geometry()
tube_mesh.clean(tolerance=0.001)

# 4. Визуализация
p = pv.Plotter()
p.add_mesh(tube_mesh, color='gold', smooth_shading=True)
#p.add_mesh(polyline, color='black', line_width=2, label='Ось кривой')
p.show()

# Сохранение (как вы спрашивали ранее)
# tube_mesh.save("curved_tube.obj")
