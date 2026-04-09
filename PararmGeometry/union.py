import numpy as np
import pyvista as pv

def onion_dome_mesh(res_u=40, res_v=60, n_lobes=8):
    # Параметры сетки
    u = np.linspace(0, 2 * np.pi, res_u)
    v = np.linspace(np.pi, 0, res_v)
    i_lobes = np.arange(n_lobes)

    # Создаем 3D сетку параметров: [доли, v, u]
    # Такой порядок важен, чтобы потом объединить доли в одну ленту
    I, V, U = np.meshgrid(i_lobes, v, u, indexing='ij')

    # 1. Профиль и РАЗДУТИЕ
    p = np.pi/2 + 35/180 * np.pi
    R_base = 1.0
    
    # Добавляем "пузатость": увеличиваем радиус в середине дуги v
    R = np.where(V > p, R_base / np.cos(V - p), R_base) 
    
    xl = R * np.cos(V)
    yl = np.abs(R * np.sin(V))

    # 2. Геометрия дольки и Twist
    twist = (np.cos(V) + 1) / 4 * np.pi
    al = 2 * np.pi / n_lobes
    r_small = yl * np.sin(al / 2)
    
    _x = r_small * np.cos(U) + yl * np.cos(al / 2)
    _y = r_small * np.sin(U)
    _z = xl * 0.9

    # 3. Поворот вокруг оси Z
    angle = al * I + twist
    x = _x * np.cos(angle) - _y * np.sin(angle)
    y = _x * np.sin(angle) + _y * np.cos(angle)
    z = _z

    # 4. Сборка в StructuredGrid
    # Чтобы pyvista понял сетку, вытягиваем все доли в одну длинную ленту по оси U
    # Новые размеры: [res_u * n_lobes, res_v, 1]
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    
    grid = pv.StructuredGrid()
    grid.points = points
    # Порядок размерностей: [длина по горизонтали, длина по вертикали, глубина]
    grid.dimensions = [res_u, res_v * n_lobes , 1] 

    # --- РАБОТА С ТЕКСТУРОЙ ---
    # Генерируем UV: u_tex идет по кругу дольки, v_tex по высоте
    # Чтобы полоски шли вдоль долек, привяжем 'u' к индексу дольки I
    u_tex = (U / (2 * np.pi)).ravel() 
    v_tex = (V / np.pi).ravel()
    
    geom = grid.extract_geometry()
    geom.active_texture_coordinates = np.column_stack((u_tex, v_tex))
    geom = geom.compute_normals(
        cell_normals=False,
        point_normals=True,
       
    )
    return geom

# Создаем и рисуем
tex = pv.read_texture("./stl/lines.png")
tex.repeat = True

geom = onion_dome_mesh(n_lobes=10)
p = pv.Plotter()
p.add_mesh(geom, texture=tex, smooth_shading=True)
p.show_bounds(grid='front', location='outer', all_edges=True)
p.show()
