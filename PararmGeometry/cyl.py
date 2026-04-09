import numpy as np
import pyvista as pv
from svgpathtools import Path, Line, CubicBezier, parse_path
import math


def cyl():
    res_v = 50
    res_u = 50
    
    
    u = np.linspace(0, math.tau, res_u)
    
    # Общая длина всего пути
    height = 3
    v = np.linspace(0, height, res_v)
    v2 = np.linspace(0.2, height, res_v)
    R = 1
    r = 0.8
    
    U, V = np.meshgrid(u, v)
    _, V2 = np.meshgrid(u, v2)
    
    x = R * np.cos(U)
    y = R * np.sin(U)
    z = V

    x2 = r * np.cos(U)
    y2 = r * np.sin(U)
    z2 = V2
    
    
    
    
    
    # 1. Получаем индексы точек верхнего и нижнего краев
    # Для res_u точек в ряду:
    top_points = np.column_stack((x[0, :], y[0, :], z[0, :]))
    bottom_points = np.column_stack((x2[0, :], y2[0, :], z2[0, :]))

    # 2. Создаем полигоны (грани)
    # Формат PyVista для одной грани: [количество_точек, id1, id2, ..., idN]
    top_face = np.hstack([[res_u], np.arange(res_u)])
    bottom_face = np.hstack([[res_u], np.arange(res_u)])

    # 3. Создаем PolyData для крышечек
    grid0 = pv.PolyData(top_points, faces=top_face)
    grid1 = pv.PolyData(bottom_points, faces=bottom_face)
    #grid0 = pv.PolyData(top_points).delaunay_2d()


    
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    points2 = np.column_stack((x2.ravel(), y2.ravel(), z2.ravel()))
    grid = pv.StructuredGrid()
    grid.points =  np.vstack((points, points2))
    grid.dimensions = [res_u, res_v, 2]



    merged_grid = grid.extract_geometry()
    merged_grid = merged_grid.merge(grid0).merge(grid1)
    
    

    tex_u = np.linspace(0, 1, res_u)*3
    tex_v = np.linspace(1, 0, res_v)
    
    

    tex_u, tex_v = np.meshgrid(tex_u, tex_v)
    uvcoord = np.column_stack((tex_u.ravel(), tex_v.ravel()))
    uvcoord2 = np.vstack((uvcoord, uvcoord))
    merged_grid.active_texture_coordinates = uvcoord2
    
    
    
    surface_with_normals = merged_grid.compute_normals(
        cell_normals=False,
        point_normals=True,
    )
    
    #sp = pv.Sphere(1.5)
    #surface_with_normals = surface_with_normals.clip_surface(sp, invert=False)

    surface_with_normals.save("./stl/cyl_model.obj")

    tex = pv.read_texture("./stl/lens2.png")
    tex.repeat = True

    # Визуализация
    p = pv.Plotter()
    p.add_mesh(surface_with_normals, texture=tex, smooth_shading=True, show_edges=True)
    #p.add_mesh(grid0)
    #p.add_mesh(grid1)
    p.show()




cyl()   

