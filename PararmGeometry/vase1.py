import numpy as np
import pyvista as pv
from svgpathtools import Path, Line, CubicBezier, parse_path
import math
from scipy.spatial import KDTree


def vase():
    res_v = 200
    res_u = 100
    
    svg_path_data = "M184.878 666.827C173.839 655.639 120.215 616.592 91.112 569.852C68.5831 533.669 42.5387 452.238 34.4687 413.768C15.91 325.298 152.694 277.817 152.822 208.168C153.017 102.317 146.864 26.6875 140.811 16.5506C129.463 -2.4521 134.265 -0.301435 115.264 0.508066C112.121 2.46313 108.481 -4.43829 105.553 19.9292C101.834 50.8902 107.56 103.925 122.733 179.033C122.977 191.448 121.981 199.664 119.745 203.683C110.175 220.881 71.9349 233.021 36.8321 270.163C28.2703 279.222 13.9606 297.409 6.95349 327.679C3.61849 342.086 -5.52836 370.854 4.71259 427.773C12.9745 473.694 31.327 524.677 45.7957 554.757C64.9094 594.495 83.2406 612.971 92.1077 622.731C115.092 648.03 158.439 681.68 175.021 701.91C179.548 706.329 177.379 712.761 175.021 722.078C173.358 728.648 171.01 740.06 163.817 754.197C160.936 759.858 156.325 769.778 146.636 781.088C143.421 784.842 137.445 790.568 128.709 798.269L230.468 802.232"
    path = parse_path(svg_path_data)
    u = np.linspace(0, math.tau, res_u)
    
    # Общая длина всего пути
    total_length = path.length()
    distances = np.linspace(0, total_length, res_v)
    v = []
    r = []
    for d in distances:
        # ilength находит параметр t, соответствующий пройденному пути d
        t = path.ilength(d)
        point = path.point(t)
        r.append(point.real/100)
        v.append(point.imag/100)

    r = np.array(r)    
    v = np.array(v)

    r = np.max(r) - r + 0.2
    v = -v
    v -= np.min(v) # Ставим на плоскость Z=0
    
    U, V = np.meshgrid(u, v)
    _, R = np.meshgrid(u, r)
    x = R * np.cos(U)
    y = R * np.sin(U)
    z = V
    
    x0 = x[0, :]
    y0 = y[0, :]
    z0 = z[0, :]

    x1 = x[-1, :]
    y1 = y[-1, :]
    z1 = z[-1, :]

    
    # 1. Получаем индексы точек верхнего и нижнего краев
    # Для res_u точек в ряду:
    top_points = np.column_stack((x[0, :], y[0, :], z[0, :]))
    bottom_points = np.column_stack((x[-1, :], y[-1, :], z[-1, :]))

    # 2. Создаем полигоны (грани)
    # Формат PyVista для одной грани: [количество_точек, id1, id2, ..., idN]
    top_face = np.hstack([[res_u], np.arange(res_u)])
    bottom_face = np.hstack([[res_u], np.arange(res_u)])

    # 3. Создаем PolyData для крышечек
    grid0 = pv.PolyData(top_points, faces=top_face)
    grid1 = pv.PolyData(bottom_points, faces=bottom_face)
    #grid0 = pv.PolyData(top_points).delaunay_2d()


    #grid = pv.StructuredGrid(x, y, z)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = [res_u, res_v, 1]



    merged_grid = grid.extract_geometry()
    merged_grid = merged_grid.merge(grid0).merge(grid1)
    
    

    tex_u = np.linspace(0, 1, res_u)*5
    tex_v = np.linspace(0, 1, res_v)
    mn = 0.6
    mx = 0.8
    tex_v = (np.clip(tex_v, mn, mx) - mn)/(mx - mn)

    

    tex_u, tex_v = np.meshgrid(tex_u, tex_v)
    merged_grid.active_texture_coordinates = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    
    
    #merged_grid = merged_grid.clean(tolerance=1e-5)  #убираем шов
    #merged_grid = merged_grid.fill_holes(1.0)  #заклеиваем дырки
    
    sp = pv.Sphere(3.5).triangulate()
    #merged_grid = merged_grid.flip_faces().triangulate()

    #surface_with_normals = merged_grid.clip_surface(sp, invert=False)
    #surface_with_normals = merged_grid.boolean_difference(sp)
    #surface_with_normals = surface_with_normals.extract_geometry()
    
    surface_with_normals = merged_grid.compute_normals(
        cell_normals=False,
        point_normals=True,
       
    )

    #sp = pv.Cylinder((0, 0, 3), radius= 0.5, height=10)
    #surface_with_normals = surface_with_normals.clip_surface(sp, invert=False)
    #surface_with_normals = surface_with_normals.clip((0, 0, 1), (0, 0, 4.))



    
    
    #surface_with_normals.save("./stl/amf_model4.obj")
    

    tex = pv.read_texture("./stl/grid5.png")
    tex.repeat = True

    # Визуализация
    p = pv.Plotter()
    p.add_mesh(surface_with_normals, texture=tex, smooth_shading=True)
    #p.add_mesh(sp)
    #p.add_mesh(grid0,  show_edges=True)
    #p.add_mesh(grid1,  show_edges=True)
    p.show()






def bridge_loops(points_inner, points_outer):
    """
    Создает меш-ленту между двумя наборами точек (окружностями).
    Работает, даже если количество точек разное.
    """
    # 1. Выравниваем начало: найдем точку в outer, ближайшую к points_inner[0]
    tree = KDTree(points_outer)
    _, start_idx = tree.query(points_inner[0])
    points_outer = np.roll(points_outer, -start_idx, axis=0)

    # 2. Объединяем точки в один массив для меша
    all_pts = np.vstack([points_inner, points_outer])
    n_inner = len(points_inner)
    n_outer = len(points_outer)

    faces = []
    
    # 3. Алгоритм "двух указателей" для триангуляции
    # Идем по обеим окружностям одновременно, соединяя их в ленту
    i, j = 0, 0
    while i < n_inner or j < n_outer:
        # Текущие индексы в общем массиве
        curr_i = i % n_inner
        curr_j = (j % n_outer) + n_inner
        
        # Следующие индексы
        next_i = (i + 1) % n_inner
        next_j = ((j + 1) % n_outer) + n_inner
        
        # Выбираем, какой треугольник построить следующим, 
        # чтобы "догнать" более длинную окружность
        # (Упрощенно: шагаем по очереди или по соотношению длин)
        if (i + 1) / n_inner <= (j + 1) / n_outer:
            faces.append([3, curr_i, next_i, curr_j])
            i += 1
        else:
            faces.append([3, curr_i, next_j, curr_j])
            j += 1
            
        # Условие выхода, чтобы не зациклиться
        if i >= n_inner and j >= n_outer:
            break

    return pv.PolyData(all_pts, faces=np.hstack(faces))

def bri():
    # --- ПРИМЕР ИСПОЛЬЗОВАНИЯ ---
    # Допустим, вы получили pts_1 и pts_2 через .strip().points
    # Для теста создадим две окружности с разным числом точек
    theta_1 = np.linspace(0, 2*np.pi, 50, endpoint=False)
    theta_2 = np.linspace(0, 2*np.pi, 80, endpoint=False)

    pts_1 = np.c_[np.cos(theta_1), np.sin(theta_1), np.zeros(50)] * 0.5 # Внутренняя
    pts_2 = np.c_[np.cos(theta_2), np.sin(theta_2), np.zeros(80)] * 1.0 # Внешняя

    # Создаем "крышечку"
    bridge_mesh = bridge_loops(pts_1, pts_2)

    # Визуализация
    pl = pv.Plotter()
    pl.add_mesh(bridge_mesh, color="lightblue", show_edges=True, label="Локальная заплатка")
    pl.add_points(pts_1, color="red", point_size=10)
    pl.add_points(pts_2, color="green", point_size=10)
    pl.add_legend()
    pl.show()

vase()   

