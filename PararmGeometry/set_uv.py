import pyvista as pv

# 1. Создаем объект-ридер для файла
reader = pv.GLTFReader("./stl/flowerpot2.glb")

multiblock = reader.read()
# Берем первый блок (индекс 0) и приводим к типу PolyData
mesh = multiblock[0].extract_geometry()

# 2. Удаляем швы (склеиваем дублирующиеся точки)
# merge_points объединяет точки, находящиеся в одной координате
clean_mesh = mesh#.clean(tolerance=0.00000001)

# 3. Считаем нормали
# generate_normals создаст плавные (smooth) нормали для вершин и граней

final_mesh = clean_mesh.compute_normals(
    cell_normals=True, 
    point_normals=True, 
    split_vertices=False # False помогает скрыть визуальные швы
)

# 3. Визуализируем

p = pv.Plotter()
p.add_mesh(final_mesh,  smooth_shading=True)
p.show()