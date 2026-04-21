import numpy as np
from scipy.spatial import cKDTree
from PIL import Image

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a * (1 - t) + b * t

def epicycloid(num_points = 10000):
    #https://www.mathcurve.com/courbes2d.gb/epicycloid/epicycloid.shtml
    a = 0.55
    q = 3.5
    t = np.linspace(0, 4*np.pi, num_points)
    x = a * ((q+1)*np.cos(t) - np.cos((q+1)*t)) / q
    y = a * ((q+1)*np.sin(t) - np.sin((q+1)*t)) / q
    
    return np.stack([x, y], axis=-1)



def generate_map(res=1024):
    # Сетка координат от -1 до 1
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1)
    
    # 1. Генерируем точки (увеличили плотность для плавности)
    #curve_points = get_cycloid_points(num_points=15000)
    curve_points = epicycloid(num_points=5000)
    
    # 2. Строим дерево и считаем расстояния
    tree = cKDTree(curve_points)
    flat_coords = coords.reshape(-1, 2)
    dists, _ = tree.query(flat_coords, k=1)
    dists = dists.reshape(res, res)
    
    # 3. Отрисовка (черный фон, синяя линия)
    final_col_np = np.zeros((res, res, 3))
    red_color = np.array([1, 1, 1])
    
    h = 0.03
    dd = np.clip(dists, 0, h)
    #mask = 1 - np.sqrt(dd/h)
    mask = 1 - dd/h
    
    
    # Смешиваем с белым фоном (или черным для максимального эффекта!)
    final_col_np = mix(final_col_np, red_color, mask[..., None])
    
    return final_col_np

# Запуск
res = 1024
img_data = generate_map(res=res)

# Сохранение
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8).save("./stl/epicycloid4.png")
print("Готово! Файл сохранен.")
