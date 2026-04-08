import numpy as np
import math
from PIL import Image


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def generate_map(res=1024, nn=7.0):
    """
    Генерирует  карту высот, аналогичную GLSL-шейдеру.
    """
    # 1. Настройка координат, аналогичная mainImage
    # Координаты p = (fragCoord) / iResolution.y.
    # В GLSL x идет от 0 до iResolution.x/iResolution.y, y идет от 0 до 1.
    # Мы генерируем квадратную текстуру, iResolution.x == iResolution.y,
    # координаты идут от 0 до 1 по обеим осям.
    # Но в Python y-инверсия. Чтобы изображение было идентичным final.png,
    # нужно задать сетку от 1 до 0 сверху вниз.
    
    y_grid, x_grid = np.mgrid[0:1:complex(res), 0:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1) # shape (res, res, 2)
    

    a = np.radians(45)  # угол в радианах
    # Создаем матрицу поворота
    R = np.array([
    [np.cos(a), -np.sin(a)],
    [np.sin(a),  np.cos(a)]
    ])
    
    coords = coords @ R.T


    # 2. Масштабирование 
    dd = 1./math.cos(a)/nn
    scaled_coords = coords / dd
    

    # 3. Voronoi расчет n = floor(scaled_coords);
    grid_coords = np.floor(scaled_coords) # shape (res, res, 2)

    grid_center = grid_coords*dd + 0.5*dd

    # Предварительно задаем массив минимальных расстояний
    dl = coords - grid_center 
    mm = np.sum(dl**2, axis=-1)
    final_col_np = 1 - mm/dd/dd * 2

    pp = 0.5
    dp = 0.05
    final_col_np = smoothstep(pp, pp+dp, final_col_np) 
    
    return final_col_np

# --- Параметры рендера ---
# Разрешение для текстуры
res = 1024
# Масштаб 
nn = 4.0

# Генерируем массив данных
print("Генерация текстуры...")
img_data =  generate_map(res=res, nn=nn)


print("Сохранение в grid3.png...")
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8, mode='L').save("./stl/grid3.png")
print("Текстура сгенерирована успешно.")