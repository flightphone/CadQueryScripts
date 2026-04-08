import pyvista as pv
import numpy as np

def create_egg_pyvista(L=2.0, B=1.5, res_u=50, res_v=50):
    # 1. Создаем сетку параметров (u - вокруг, v - от полюса до полюса)
    u = np.linspace(0, 2 * np.pi, res_u)
    v = np.linspace(0, np.pi, res_v)
    u, v = np.meshgrid(u, v)

    # 2. Формула овоида (модифицированная сфера)
    # z меняется от -L/2 до L/2
    z = -L/2 * np.cos(v)
    
    # Коэффициент формы: расширяем низ, сужаем верх
    # Формула: r = (B/2) * sin(v) * (1 + k * cos(v))
    # Где k — коэффициент «яйцевидности» (0.1 - 0.2)
    k = 0.2 
    r = (B/2) * np.sin(v) * (1 - k * np.cos(v))

    x = r * np.cos(u)
    y = r * np.sin(u)

    # 3. Создаем меш PyVista
    # Объединяем координаты в массив (N, 3)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = [res_u, res_v, 1]

    # 4. Генерируем нормали (автоматически)
    #grid.compute_normals(inplace=True, point_normals=True, cell_normals=False)
    
    
    

    # 5. Добавляем UV-координаты
    # Нормализуем u и v в диапазон [0, 1]
    tex_u = np.linspace(0, 1, res_u)
    tex_v = np.linspace(0, 1, res_v)
    tex_u, tex_v = np.meshgrid(tex_u * 5, tex_v * 5)
    
    surf =  grid.extract_geometry()
    surf.active_texture_coordinates = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    
    surface_with_normals = surf.compute_normals(
        cell_normals=False,
        point_normals=True,
       
    )
    return surface_with_normals

# Создаем объект
egg = create_egg_pyvista()

# Сохраняем в OBJ
#egg.save("./stl/egg_model.obj")

# Можно сразу посмотреть результат в окне (если есть GUI)
#egg.plot(show_edges=True)
tex = pv.read_texture("./stl/grid2.png")
tex.repeat = True

# Визуализация
p = pv.Plotter()
p.add_mesh(egg, texture=tex, smooth_shading=True)
#p.screenshot("my_egg_render.png") 
#p.add_mesh(egg,  smooth_shading=True)
p.show()



