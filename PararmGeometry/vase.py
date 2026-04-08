import numpy as np
import pyvista as pv
from svgpathtools import Path, Line, CubicBezier, parse_path
import math

def create_vase_profile(height=100, thickness=5):
    # Внешний контур (параболическая или S-образная кривая)
    outer = CubicBezier(start=20+0j, c1=50+30j, c2=10+70j, end=30+height*1j)
    # Горлышко (горизонтальная линия вовнутрь)
    top = Line(outer.end, outer.end - thickness)
    # Внутренний контур (сдвиг внешнего на толщину)
    inner = CubicBezier(start=top.end, c1=top.end-20j, c2=15+20j, end=15+thickness*1j)
    # Дно
    bottom = Line(inner.end, outer.start)
    
    return Path(outer, top, inner, bottom)


def vase():
    #path = create_vase_profile()
    path_string = "M 0,0 C 10,10 20,-10 30,0 L 40,20"
    path = parse_path(path_string)

    # 1. Получаем 100 точек профиля (равномерно по длине)
    total_len = path.length()
    dist = np.linspace(0, total_len, 50)
    points_2d = np.array([path.point(path.ilength(d)) for d in dist])

    # 2. Переводим в 3D (X, Y, Z=0)
    points_3d = np.column_stack((points_2d.real, points_2d.imag, np.zeros(len(points_2d))))

    # 3. Создаем линию профиля в PyVista
    profile_line = pv.PolyData(points_3d)
    # Соединяем точки линиями, чтобы revolve понимал, что это поверхность
    cells = np.full((len(points_3d)-1, 3), 2, dtype=np.int_)
    cells[:, 1] = np.arange(0, len(points_3d)-1)
    cells[:, 2] = np.arange(1, len(points_3d))
    profile_line.lines = cells

    # 4. Вращаем вокруг оси Y [0, 1, 0]
    vase_mesh = profile_line.extrude_rotate(resolution=60, rotation_axis=(0, 1, 0))

    # Визуализация
    vase_mesh.plot(show_edges=True, color='tan')




def get_points_from_svg_path(path_string, num_points=100):
    # Парсим строку пути
    path = parse_path(path_string)
    
    # Общая длина всего пути
    total_length = path.length()
    
    # Генерируем равномерные отрезки расстояний от 0 до total_length
    distances = np.linspace(0, total_length, num_points)
    
    # Находим точки (x, y) для каждого расстояния
    points = []
    for d in distances:
        # ilength находит параметр t, соответствующий пройденному пути d
        t = path.ilength(d)
        point = path.point(t)
        points.append([point.real,  0.0, point.imag]) # z=0 для PyVista

    
    res =  np.array(points)
    res = res / 100
    

    return res

def pp():
    res_v = 50
    res_u = 50
    svg_path_data = "M234.027 0C192.124 0.239641 151.74 0.480542 112.873 0.722704C109.73 2.67777 106.493 9.15148 103.162 20.1438L120.342 179.248C120.586 191.663 119.59 199.879 117.354 203.898C107.784 221.096 69.5439 233.236 34.4411 270.378C25.8793 279.437 11.4305 297.592 4.56245 327.894C1.97442 339.313 -0.47988 359.002 0.0806447 386.905C0.245821 395.127 -0.536603 409.052 2.32155 427.988C4.1706 440.238 7.25181 460.961 16.5139 488.492C21.079 502.062 27.2846 525.743 43.4047 554.972C51.3139 569.313 65.1911 593.26 89.7167 622.946C100.813 636.377 116.182 663.767 148.727 687.185C160.691 695.794 170.24 699.075 172.63 703.619C174.169 706.544 174.988 712.976 172.63 722.293C170.967 728.863 168.619 740.275 161.426 754.412C158.545 760.073 153.934 769.993 144.245 781.303C141.03 785.057 135.054 790.783 126.318 798.484L228.077 802.447" 
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

    r = np.max(r) - r
    v = -v
    v -= np.min(v) # Ставим на плоскость Z=0

    R = r.reshape(-1, 1)
    V = v.reshape(-1, 1)
    x = R * np.cos(u)
    y = R * np.sin(u)
    z = V * np.ones_like(u)
    grid = pv.StructuredGrid(x, y, z)
    merged_grid = grid.extract_geometry()
    
    tex_u = np.linspace(0, 1, res_u)
    tex_v = np.linspace(0, 1, res_v)
    tex_u, tex_v = np.meshgrid(tex_u * 5, tex_v * 5)
    merged_grid.active_texture_coordinates = np.column_stack((tex_v.ravel(), tex_u.ravel()))


    merged_grid = merged_grid.clean(tolerance=1e-5)  #убираем шов
    merged_grid = merged_grid.fill_holes(1.0)  #заклеиваем дырки
    
    surface_with_normals = merged_grid.compute_normals(
        cell_normals=False,
        point_normals=True,
       
    )
    
    surface_with_normals.save("./stl/amf_model.obj")
    surface_with_normals.plot(show_edges=True)


def pp2():
    res_v = 100
    res_u = 100
    svg_path_data = "M234.027 0C192.124 0.239641 151.74 0.480542 112.873 0.722704C109.73 2.67777 106.493 9.15148 103.162 20.1438L120.342 179.248C120.586 191.663 119.59 199.879 117.354 203.898C107.784 221.096 69.5439 233.236 34.4411 270.378C25.8793 279.437 11.4305 297.592 4.56245 327.894C1.97442 339.313 -0.47988 359.002 0.0806447 386.905C0.245821 395.127 -0.536603 409.052 2.32155 427.988C4.1706 440.238 7.25181 460.961 16.5139 488.492C21.079 502.062 27.2846 525.743 43.4047 554.972C51.3139 569.313 65.1911 593.26 89.7167 622.946C100.813 636.377 116.182 663.767 148.727 687.185C160.691 695.794 170.24 699.075 172.63 703.619C174.169 706.544 174.988 712.976 172.63 722.293C170.967 728.863 168.619 740.275 161.426 754.412C158.545 760.073 153.934 769.993 144.245 781.303C141.03 785.057 135.054 790.783 126.318 798.484L228.077 802.447" 
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

    r = np.max(r) - r
    v = -v
    v -= np.min(v) # Ставим на плоскость Z=0
    
    U, V = np.meshgrid(u, v)
    _, R = np.meshgrid(u, r)
    x = R * np.cos(U)
    y = R * np.sin(U)
    z = V
    
    #grid = pv.StructuredGrid(x, y, z)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = [res_u, res_v, 1]

    merged_grid = grid.extract_geometry()
    
    

    tex_u = np.linspace(0, 1, res_u)*5
    tex_v = np.linspace(0, 1, res_v)
    mn = 0.4
    mx = 0.7
    tex_v = (np.clip(tex_v, mn, mx) - mn)/(mx - mn)


    

    tex_u, tex_v = np.meshgrid(tex_u, tex_v)
    merged_grid.active_texture_coordinates = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    
    #merged_grid = merged_grid.clean(tolerance=1e-5)  #убираем шов
    #merged_grid = merged_grid.fill_holes(1.0)  #заклеиваем дырки
    
    surface_with_normals = merged_grid.compute_normals(
        cell_normals=False,
        point_normals=True,
       
    )
    
    #surface_with_normals.save("./stl/amf_model2.obj")
    #surface_with_normals.plot(show_edges=True)

    tex = pv.read_texture("./stl/grid5.png")
    tex.repeat = True

    # Визуализация
    p = pv.Plotter()
    p.add_mesh(surface_with_normals, texture=tex, smooth_shading=True)
    p.show()


pp2()   
#dist = np.linspace(0, 10, 6)
#print(dist)

