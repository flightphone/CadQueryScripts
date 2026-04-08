import pyvista as pv

#еще хуже
# 1. Создаем объект-ридер для файла
reader = pv.GLTFReader("./stl/vase_body.glb")
multiblock = reader.read()
# Берем первый блок (индекс 0) и приводим к типу PolyData
mesh = multiblock[0].extract_geometry()

# 1. Делаем сетку очень плотной (разбиваем вытянутые CAD-треугольники)
temp = mesh.subdivide(3)

# 2. Сглаживаем, чтобы выровнять вершины (Taubin не съедает объем)
#temp = temp.smooth_taubin(n_iter=50)

# 3. Укрупняем сетку до нужного состояния (оставляем, например, 10% ячеек)
# Это сделает сетку крупной, но из-за шага 1 и 2 она будет равномерной
final_mesh = temp.decimate(0.95)




'''
# очень долго
# Создание равномерной сетки вокруг объекта с нужным шагом (spacing)
grid = pv.create_grid(mesh, dimensions=(60, 60, 100)) 
# 2. Переносим данные с вазы на эту сетку
# (вычисляем расстояние от узлов сетки до поверхности вазы)
sampled = grid.compute_implicit_distance(mesh)

# 3. Генерируем поверхность там, где расстояние равно 0
# Именно это превратит "куб" в "равномерную вазу"
uniform_mesh = sampled.contour([0.0])
uniform_mesh = uniform_mesh.smooth(n_iter=100)
'''
# 3. Считаем нормали
# generate_normals создаст плавные (smooth) нормали для вершин и граней
'''
final_mesh = clean_mesh.compute_normals(
    cell_normals=True, 
    point_normals=True, 
    split_vertices=False # False помогает скрыть визуальные швы
)
'''
# 3. Визуализируем

p = pv.Plotter()
p.add_mesh(final_mesh,  smooth_shading=True, show_edges=True)
p.show()