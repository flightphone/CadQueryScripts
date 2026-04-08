import pyvista as pv
import numpy as np

# 1. Создаем две выпуклые поверхности (внешняя и внутренняя)
outer = pv.Sphere(radius=1.0, end_phi=90, phi_resolution=30, theta_resolution=30)
inner = pv.Sphere(radius=0.7, end_phi=90, phi_resolution=30, theta_resolution=30) 
# Важно: разрешение (количество точек) должно быть одинаковым!

# 2. Вычисляем векторы от внешней поверхности к внутренней
# Так как обе поверхности - полусферы с одинаковым разрешением, 
# точки с одинаковыми индексами соответствуют друг другу.
vectors = inner.points - outer.points

# 3. Используем extrude_custom для создания объема
# Это создаст стенки (бока) и соединит поверхности
thick_shell = outer.extrude(vectors, capping=True)

# 4. Чтобы сделать объект по-настоящему "Solid" (закрыть дно):
# Нужно добавить саму внутреннюю поверхность и объединить всё
final_solid = (thick_shell + inner).clean()

# Проверка и визуализация
print(f"Объем: {final_solid.volume:.4f}")
final_solid.plot(show_edges=True, color='tan')

import pyvista as pv
import numpy as np

# 1. Допустим, у нас есть две сетки (поверхности)
# grid1.dimensions == [res_u, res_v, 1]
# grid2.dimensions == [res_u, res_v, 1]

# Собираем все точки в один массив
# Сначала идут все точки первой поверхности, затем все точки второй
all_points = np.vstack((grid1.points, grid2.points))

# 2. Создаем новую сетку с 2 слоями по оси Z (глубине)
res_u, res_v, _ = grid1.dimensions
vol_grid = pv.StructuredGrid()
vol_grid.points = all_points
vol_grid.dimensions = [res_u, res_v, 2] # Теперь это 3D объем

# 3. Визуализация и проверка
print(f"Тип объекта: {type(vol_grid)}")
print(f"Объем: {vol_grid.cast_to_unstructured_grid().volume:.4f}")

vol_grid.plot(show_edges=True, color='tan')


import pyvista as pv
import numpy as np

# 1. Создаем две вогнутые поверхности (StructuredGrid 20x20x1)
u, v = np.meshgrid(np.linspace(0, 1, 20), np.linspace(0, 1, 20))
z1 = u**2 + v**2        # Верхняя поверхность
z2 = z1 - 0.2           # Нижняя поверхность (сдвинута вниз на 0.2)

grid1 = pv.StructuredGrid(u, v, z1)
grid2 = pv.StructuredGrid(u, v, z2)

# 2. Объединяем точки в один массив (слой 1, затем слой 2)
all_points = np.vstack((grid1.points, grid2.points))

# 3. Создаем объемную сетку 20 x 20 x 2
# Теперь у нас 1 слой ячеек в толщину, который соединяет верх и низ
vol_grid = pv.StructuredGrid()
vol_grid.points = all_points
vol_grid.dimensions = [20, 20, 2] 

# 4. Превращаем в UnstructuredGrid для корректного расчета объема и нормалей
solid = vol_grid.cast_to_unstructured_grid()

print(f"Замкнут (Manifold): {solid.extract_surface().is_manifold}")
print(f"Объем: {solid.volume:.4f}")

# Визуализация (увидите "толстый лист" со стенками по периметру)
solid.plot(show_edges=True, color='tan')
