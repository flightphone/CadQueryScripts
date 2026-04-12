import numpy as np
import pyvista as pv
from surfgeometry import surf_geom, surf_points, check_volume
import math

def fix_seam_after_clean(mesh):
    """
    Разрезает сетку по шву UV, если clean() уже объединил точки.
    """
    # 1. Получаем текущие UV координаты
    uv = mesh.active_texture_coordinates.copy()
    u = uv[:, 0]
    
    # 2. Инструменты для пересборки
    new_points = list(mesh.points)
    new_uv = list(uv)
    
    # Разбираем массив faces (формат [n, i1, i2, ..., n, j1, j2, ...])
    faces = mesh.faces.reshape(-1, 4) # Работает для треугольников (3 + 1)
    
    modified = False
    point_map = {} # (original_idx, target_u) -> new_idx

    for i in range(len(faces)):
        f_indices = faces[i, 1:]
        u_face = u[f_indices]
        
        # Если разброс U велик, значит это шов (например, 0.99 и 0.01)
        if np.max(u_face) - np.min(u_face) > 0.5:
            modified = True
            for j in range(3):
                idx = f_indices[j]
                # Если у вершины маленькое U, её нужно "перенести" в U+1
                if u[idx] < 0.5:
                    key = (idx, u[idx] + 1.0)
                    if key not in point_map:
                        # Создаем дубликат вершины в пространстве
                        new_idx = len(new_points)
                        new_points.append(mesh.points[idx])
                        # Но с новым U
                        new_uv.append([u[idx] + 1.0, uv[idx, 1]])
                        point_map[key] = new_idx
                    
                    # Обновляем индекс в полигоне
                    faces[i, j+1] = point_map[key]

    if not modified:
        return mesh

    # 3. Собираем новую сетку (уже PolyData, так как StructuredGrid не позволит дубликатов)
    new_mesh = pv.PolyData(np.array(new_points), faces.ravel())
    new_mesh.active_texture_coordinates = np.array(new_uv)
    
    return new_mesh

def cycl(U, V):
    R = 1.
    x = R * np.cos(U)
    y = R * np.sin(U)
    z = V
    return x, y, z



def shell(u, v, b): 
    a = 3 
    m = -0.1 
    k = 2.5
    
    x = np.exp(m * u) * np.cos(u) * (a + b * np.cos(v))
    y = np.exp(m * u) * np.sin(u) * (a + b * np.cos(v))
    z = np.exp(m * u) * (k * a + b * np.sin(v))
    h = k * a + b
    z -= h / 2.
    return x, y, z

def think_shell(umin = 0, umax = 1, vmin = 0, vmax = 1,  res_u = 50, res_v = 10, repeat_u=10, repeat_v=2):
    points1, _, _ = surf_points(lambda u, v: shell(u, v, 2.5), umin, umax, vmin, vmax,  res_u, res_v)
    points2, _, _ = surf_points(lambda u, v: shell(u, v, 2.3), umin, umax, vmin, vmax,  res_u, res_v)
    grid = pv.StructuredGrid()
    grid.points =  np.vstack((points1, points2))
    grid.dimensions = [res_u, res_v, 2]
    geom = grid.extract_geometry()
    

    tex_u = np.linspace(0, 1, res_u)*repeat_u
    tex_v = np.linspace(0, 1, res_v)*repeat_v
    tex_u, tex_v = np.meshgrid(tex_u, tex_v)
    uvcoord = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    uvcoord2 = np.vstack((uvcoord, uvcoord))
    geom.active_texture_coordinates = uvcoord2

    #geom = geom.clean()

    geom = geom.compute_normals(
        cell_normals=False,
        point_normals=True,
       
    )
    return geom


def onion(u, v, n_lobes=10):
    uu = u*n_lobes
    I = np.floor(uu)
    U = (uu-I)*math.pi - math.pi/2
    V = v*math.pi
     # 1. Профиль и РАЗДУТИЕ
    p = np.pi/2 + 35/180 * np.pi
    R_base = 1.0
    
    # Добавляем "пузатость": увеличиваем радиус в середине дуги v
    R = np.where(V > p, R_base / np.cos(V - p), R_base) 
    
    z = - R * np.cos(V)
    r_big = np.abs(R * np.sin(V))

    # 2. Геометрия дольки и Twist
    twist = (np.cos(V) + 1) / 4 * np.pi
    al = 2 * np.pi / n_lobes
    r_small = r_big * np.sin(al / 2)
    
    _x = r_small * np.cos(U) + r_big * np.cos(al / 2)
    _y = r_small * np.sin(U)
    

    # 3. Поворот вокруг оси Z
    angle = al * I + twist
    x = _x * np.cos(angle) - _y * np.sin(angle)
    y = _x * np.sin(angle) + _y * np.cos(angle)
    return x, y, z


def umbrella(v, u, n=6):
    r = 1
    v = v*n
    u = u * math.pi/2
    x0 = np.floor(v)
    x = v - x0
    x1 = np.mod(x0 + 1, n)
    def vv(xx):
        return np.array([r*np.cos(xx*math.tau/n)*np.cos(u), r*np.sin(xx*math.tau/n)*np.cos(u), r*np.sin(u)])
    
    
    v0 = vv(x0)
    v1 = vv(x1)
    res = (v1 - v0)*x + v0
    return res

def think_umbrella():
    nn = 8
    umin = 0
    umax = 1
    vmin = 0
    vmax = 1
    res_u = 50*nn
    res_v = 50
    repeat_u=nn
    repeat_v = 1
    
    
    points1, _, _ = surf_points(lambda u, v: umbrella(u, v, nn), umin, umax, vmin, vmax,  res_u, res_v)
    points2 = points1.copy()*0.95
    grid = pv.StructuredGrid()
    grid.points =  np.vstack((points1, points2))
    grid.dimensions = [res_u, res_v, 2]
    geom = grid.extract_geometry()
    

    tex_u = np.linspace(0, 1, res_u)*repeat_u
    tex_v = np.linspace(0, 1, res_v)*repeat_v
    tex_u, tex_v = np.meshgrid(tex_u, tex_v)
    uvcoord = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    uvcoord2 = np.vstack((uvcoord, uvcoord))
    geom.active_texture_coordinates = uvcoord2

    #geom = geom.clean()

    geom = geom.compute_normals(
        cell_normals=False,
        point_normals=True,
       
    )
    return geom



tex = pv.read_texture("./stl/lines.png")
tex.repeat = True
#geom = surf_geom(cycl, 0, math.tau, 0, 3, repeat_u=1, top = 3)
#geom = think_shell(0, 14 * math.pi, 0, 2 * math.pi, 300, 100, repeat_u=10, repeat_v=2)
#geom = surf_geom(lambda u, v: shell(u, v, 2.5), 0, 14 * math.pi, 0, 2 * math.pi, 300, 100, repeat_u=10, repeat_v=2)
#geom.save("./stl/shell_model.obj")
#geom = surf_geom(onion, res_u=500, res_v=50, vmin=0.05, vmax=1, top = 1)
#geom = geom.clean(tolerance=0.0001)
#geom = geom.fill_holes(hole_size=1)

#geom = fix_seam_after_clean(geom)
#print(f"is volume: {check_volume(geom)}")
#geom.save("./stl/onion_model2.obj")
nn = 10
geom = surf_geom(lambda u, v: umbrella(u, v, nn), res_v=50, res_u=nn*50)

#geom = think_umbrella()
'''
geom = geom.extract_surface()
geom = geom.clean()
geom = geom.fill_holes(0.0001)
geom = geom.compute_normals(
        cell_normals=False,
        point_normals=True,
    )
'''
#geom = geom.extrude((0, 0, -0.3), capping=True)

geom.save("./stl/umbrella_model2.obj")

p = pv.Plotter()
p.add_mesh(geom, texture = tex, smooth_shading=True)
#p.export_gltf("./stl/umbrella_model1.glb")
#p.show_bounds(grid='front', location='outer', all_edges=True)
p.show()
