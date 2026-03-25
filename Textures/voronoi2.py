import numpy as np
from PIL import Image

def generate_voronoi_border(res=1024, nn=7.0):
    # Те же координаты, что и в твоем коде
    y_grid, x_grid = np.mgrid[1:0:complex(res), 0:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1) * nn
    grid_coords = np.floor(coords)
    
    # Теперь нам нужно ДВА массива: для ближайшего (d1) и второго (d2) расстояний
    d1 = np.full((res, res), 100.0)
    d2 = np.full((res, res), 100.0)

    for i in range(-1, 2):
        for j in range(-1, 2):
            g = np.array([float(i), float(j)])
            p_grid_cell = grid_coords + g
            
            # Твоя функция хэша из voronoi.glsl
            hash_offset = hash_vec2(p_grid_cell) 
            r_vector = (p_grid_cell + hash_offset) - coords
            d_current = np.sqrt(np.sum(r_vector**2, axis=-1)) # Берем корень для линейности

            # Обновляем d1 и d2 через маски NumPy
            # Если новое расстояние меньше самого маленького (d1)
            mask1 = d_current < d1
            # d2 становится старым d1, а d1 — новым расстоянием
            d2 = np.where(mask1, d1, np.minimum(d2, d_current))
            d1 = np.minimum(d1, d_current)
            
            # Если d_current не меньше d1, но меньше d2
            mask2 = (~mask1) & (d_current < d2)
            d2 = np.where(mask2, d_current, d2)

    # Вычисляем границу: расстояние от d2 до d1
    # Именно это создаст эффект «стенок», как на той вазе
    border = d2 - d1
    
    # Можно инвертировать, чтобы стенки были белыми (высокими)
    # return 1.0 - np.clip(border, 0, 1)
    return border

# Хэш-функция из твоего шейдера
def hash_vec2(p):
    p_dot = np.stack([np.dot(p, [127.1, 311.7]), np.dot(p, [269.5, 183.3])], axis=-1)
    sin_p = np.sin(p_dot) * 18.5453
    return sin_p - np.floor(sin_p)

# Генерируем и сохраняем
border_map = generate_voronoi_border()
arr_uint8 = (np.clip(border_map * 255, 0, 255)).astype(np.uint8)
Image.fromarray(arr_uint8, mode='L').save("./stl/voronoi_border.png")