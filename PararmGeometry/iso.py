import pyvista as pv
import numpy as np

# 1. Создаем расчетную сетку (объем, в котором будем "искать" эллипсоид)
n = 30
x = np.linspace(-15, 15, n)
y = np.linspace(-15, 15, n)
z = np.linspace(-15, 15, n)
grid_x, grid_y, grid_z = np.meshgrid(x, y, z, indexing='ij')
grid = pv.StructuredGrid(grid_x, grid_y, grid_z)

# 2. Задаем параметры эллипсоида (полуоси)
a, b, c = 12.0, 8.0, 5.0

# 3. Вычисляем скалярное поле функции эллипсоида
# Для каждой точки (x,y,z) считаем значение функции
pts = grid.points
field = (pts[:, 0]**2 / a**2) + (pts[:, 1]**2 / b**2) + (pts[:, 2]**2 / c**2)
grid.point_data['ellipsoid_func'] = field

# 4. Вычисляем градиент (нормали) во всем объеме
grid = grid.compute_derivative(scalars='ellipsoid_func', gradient='norm_vec')

# 5. Извлекаем изоповерхность, где значение функции равно 1.0
# Это и есть наш эллипсоид
iso_ellipsoid = grid.contour(isosurfaces=[1.0], scalars='ellipsoid_func')

smoothed_ellipsoid = iso_ellipsoid.smooth(n_iter=100, relaxation_factor=0.05)

# ВАЖНО: После сглаживания точки сместились, поэтому старые нормали 
# могут чуть-чуть "врать". Пересчитаем их для идеального вида:
smoothed_ellipsoid.compute_normals(inplace=True)

# 6. Визуализация
p = pv.Plotter()

# Рисуем сам эллипсоид
p.add_mesh(iso_ellipsoid, color='cyan', opacity=0.6, smooth_shading=True, label='Ellipsoid Surface')

# Рисуем векторы нормалей (градиенты) на поверхности
# Используем прореживание [::5], чтобы стрелки не сливались
p.add_arrows(iso_ellipsoid.points[::5], 
             iso_ellipsoid.point_data['norm_vec'][::5], 
             mag=2.0, 
             color='red', 
             label='Surface Normals')


'''
# Отображаем сглаженный эллипсоид
p.add_mesh(smoothed_ellipsoid, 
           color='skyblue', 
           smooth_shading=True, 
           show_edges=False, 
           label='Smoothed (Laplace)')

# Добавляем обновленные нормали
p.add_arrows(smoothed_ellipsoid.points[::10], 
             smoothed_ellipsoid.point_data['Normals'][::10], 
             mag=1.5, 
             color='red')
'''

p.add_legend()
p.show()
