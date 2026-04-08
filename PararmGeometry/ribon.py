import pyvista as pv
import numpy as np

# 1. Создаем путь (кривую)
theta = np.linspace(0, 4 * np.pi, 100)
z = np.linspace(0, 5, 100)
points = np.column_stack((np.sin(theta), np.cos(theta), z))
path = pv.lines_from_points(points)

# 2. Создаем профиль (прямоугольник в плоскости XY)
# Регулируйте width и height для размеров сечения
profile = pv.Rectangle()

# 3. Протягиваем профиль вдоль пути (Extrude along path)
# Используем метод sweep (в PyVista это делается через специальный фильтр)
# Для версий 0.32+ самый простой способ — создать Ribbon или использовать сканирование
mesh = path.ribbon(width=0.5) # Это создаст плоскую ленту

# Чтобы получить именно ОБЪЕМНЫЙ прямоугольник (короб):
# Мы используем встроенный в VTK алгоритм, доступный через sweep_line или кастомную функцию
def create_box_tube(path, width=0.4, height=0.2):
    # Создаем "ленту" (горизонтальные грани)
    top = path.ribbon(width=width)
    # Сдвигаем её вверх и вниз для создания толщины
    # (В реальных задачах лучше использовать фильтр 'extrude')
    return top.extrude([0, 0, height], capping=True)

# Но самый "чистый" способ для сложной кривой — это создать 
# PolyData вручную или использовать плагин (например, 'section-properties')
# Для базовой визуализации прямоугольной "ленты" идеально подходит ribbon:
ribbon = path.ribbon(width=0.6)

# 4. Визуализация
p = pv.Plotter()
p.add_mesh(ribbon, color='orange', smooth_shading=True, show_edges=True)
p.add_mesh(path, color='black', line_width=2)
p.show()
