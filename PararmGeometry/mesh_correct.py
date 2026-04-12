import pyvista as pv
import pyacvd
import numpy as np

# 1. Загрузка GLB
# PyVista загружает GLB как MultiBlock. Нам нужно извлечь из него геометрию.
mesh = pv.read("./stl/vase_body.obj")


# 2. Очистка и подготовка (Аналог trimesh.process)
# - clean() удаляет дубликаты точек и вырожденные грани
# - fill_holes() заделывает дыры (аргумент — макс. размер дыры)
cleaned = mesh.clean(tolerance=0.001).fill_holes(hole_size=0.001) 

# 2. Глубокая очистка (Ключевой момент)
# extract_surface(pass_point_ids=False) превращает любой меш в чистую оболочку
cleaned = mesh.extract_surface().triangulate()

# Удаляем мелкие дефекты, которые могут сбивать алгоритм
cleaned = cleaned.clean(tolerance=1e-5)

# 3. Фикс для pyacvd: 
# Алгоритму нужно, чтобы массив граней (faces) состоял строго из троек.
# Иногда после triangulate() проскакивают пустые ячейки.
if not cleaned.is_all_triangles:
    # Принудительная триангуляция через внешнюю логику, если встроенная подвела
    cleaned = cleaned.cast_to_unstructured_grid().extract_surface().triangulate()

# 4. Ремешинг
clus = pyacvd.Clustering(cleaned)
clus.subdivide(3)
clus.cluster(50000)
remeshed = clus.create_mesh()
remeshed.save("./stl/vase_body6.obj")
# Визуализация
remeshed.plot(show_edges=True)

