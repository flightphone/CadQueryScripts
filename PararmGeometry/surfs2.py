import numpy as np
import pyvista as pv
from surfgeometry import surf_geom, surf_points
from cyl import cyl
import math
import trimesh
from vase1 import vase

def pv_boolean_difference(target_pv, cutter_pv, transform_matrix=None):
    """
    Выполняет вычитание (Difference) через Trimesh/Manifold.
    
    :param target_pv: Основной меш (из которого вычитаем)
    :param cutter_pv: Объект-резак
    :param transform_matrix: Матрица 4x4 для перемещения/поворота резака (опционально)
    :return: Результат в формате pyvista.PolyData
    """
    
    def to_trimesh(pv_mesh):
        # Обязательно триангулируем и чистим перед конвертацией
        tri_mesh = pv_mesh.triangulate().clean()
        v = tri_mesh.points
        # Форматируем грани из [3, v1, v2, v3...] в [[v1, v2, v3]...]
        f = tri_mesh.faces.reshape(-1, 4)[:, 1:]
        return trimesh.Trimesh(vertices=v, faces=f)

    def tryclear(target):    
       # Заполняет плоские дыры
        target.fill_holes()
        # Исправляет ориентацию граней (лицо/изнанка)
        target.fix_normals()
        # Пытается сделать меш герметичным
        target.process(validate=True)
    
    # 1. Конвертируем в Trimesh
    target_tri = to_trimesh(target_pv)
    cutter_tri = to_trimesh(cutter_pv)



    
    
    # 2. Применяем трансформацию к резаку, если она передана
    if transform_matrix is not None:
        cutter_tri.apply_transform(transform_matrix)

    # 3. Лечим меши (важно для грязной геометрии)
    tryclear(target_tri)
    tryclear(cutter_tri)
    #target_tri.process(validate=True)
    #cutter_tri.process(validate=True)

    print(f"Target is volume: {target_tri.is_volume}")
    print(f"Cutter is volume: {cutter_tri.is_volume}")

    if not target_tri.is_volume or not cutter_tri.is_volume:
        return None



    # 4. Булева операция через Manifold
    # engine='manifold' — самый стабильный вариант для "плохих" мешей
    result_tri = target_tri.difference(cutter_tri, engine='manifold')

    # 5. Конвертируем обратно в PyVista
    v_out = result_tri.vertices
    f_out = result_tri.faces
    # Собираем массив граней в формате PyVista [3, v1, v2, v3, ...]
    faces_pv = np.column_stack((np.full(len(f_out), 3), f_out)).ravel()
    
    return pv.PolyData(v_out, faces_pv)


def wave_cone(u, v):
    u = u*math.tau
    h = 2
    r = 2.3
    n = 10
    hh = h*0.1
    dd = hh * np.sin(u*n)
    rt = v * r
    x = rt * np.cos(u)  
    y = rt * np.sin(u)
    z = h - v*(h + dd)
    return x, y, z

def wave_cone_think():
    geom = surf_geom(wave_cone, vmin=0.2, vmax=1, res_u=200, res_v=50)
    geom = geom.clean(tolerance=0.001)
    geom = geom.fill_holes(hole_size=0.001)
    geom = geom.extrude((0, 0, -1.5), capping=True)
    #geom = geom.clean(tolerance=0.001)
    #geom = geom.fill_holes(hole_size=0.001)
    geom = geom.compute_normals(
            cell_normals=False,
            point_normals=True,
        )
    
    geom = geom.rotate_x(180)
    geom = geom.translate((0, 0, 8.6))
    return geom


def cylclear():
    
    geom2 = cyl()
    geom2 = geom2.clean(tolerance=0.001)
    geom2 = geom2.fill_holes(hole_size=0.001)
    geom2 = geom2.extract_surface()
    geom2 = geom2.clean(tolerance=0.001)
    geom2 = geom2.fill_holes(hole_size=0.001)
    
    
    return geom2


tex = pv.read_texture("./stl/grid5.png")
tex.repeat = True
p = pv.Plotter()


geom1 = vase()
#geom2 = pv.Sphere(3)
geom2 = wave_cone_think()

#geom1.save("./stl/vase4.obj")
#geom2.save("./stl/wave_cone4.obj")



#geom1 = pv.Cube()
#geom2 = pv.Sphere(radius=0.7, center=(0.5, 0.5, 0.5))

geo = pv_boolean_difference(geom1, geom2)
geo.save("./stl/vase_wave.obj")
#geo = True
if geo != None:
    p.add_mesh(geo, show_edges=True)
    #p.add_mesh(geom1, texture = tex)
    #p.add_mesh(geom2)
    p.show()
