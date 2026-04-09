import numpy as np
import math
from PIL import Image


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def generate_map(res=1024, nn=7.0):
    """
    аналог GLSL-шейдера.
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
    
    # 2. Масштабирование по х
    lines = coords[:, :, 0]*nn
    cells = np.floor(lines) 
    lines = lines - cells
    sign = np.mod(cells, 2) * 2 - 1
    hh = 0.2
    final_col_np = smoothstep(0., hh, lines) * (1 - smoothstep(1.-hh, 1., lines))*sign*0.5 + 0.5 

    return final_col_np

# --- Параметры рендера ---
# Разрешение для текстуры
res = 1024
# Масштаб 
nn = 10.0

# Генерируем массив данных
print("Генерация текстуры...")
img_data =  generate_map(res=res, nn=nn)

fname = "lines.png"
print(f"Сохранение в {fname}...")
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8, mode='L').save(f"./stl/{fname}")
print("Текстура сгенерирована успешно.")