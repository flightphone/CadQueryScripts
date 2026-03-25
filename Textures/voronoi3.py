import numpy as np
from PIL import Image

def generate_vase_texture(res=1024, nn=8.0):
    # 1. Создаем сетку координат
    # y идет от 0 (низ) до 1 (верх), x от 0 до 1 (вокруг цилиндра)
    y_grid, x_grid = np.mgrid[0:1:complex(res), 0:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1) * nn
    grid_coords = np.floor(coords)
    
    res_map = np.full((res, res), 100.0)

    # 2. Генерация бесшовного Вороного по оси X
    for i in range(-1, 2):
        for j in range(-1, 2):
            g = np.array([float(i), float(j)])
            
            # Зацикливаем индекс только по X (координата 0)
            # Если хочешь зациклить и по Y, добавь % nn и для g[1]
            neighbor_cell_index = grid_coords + g
            neighbor_cell_index[..., 0] %= nn 
            neighbor_cell_index[..., 1] %= nn 
            
            # Получаем точку в ячейке через хэш
            o = hash_vec2(neighbor_cell_index)
            
            # Считаем расстояние (линейно!)
            r = (grid_coords + g + o) - coords
            d = np.sum(r**2, axis=-1)
            res_map = np.minimum(res_map, d)

    # 3. Создаем маску для донышка
    # y_grid у нас идет от 0 до 1. 
    # Сделаем так: первые 10% высоты — ноль, потом плавный переход
    #mask = np.clip((y_grid - 0.1) / 0.15, 0.0, 1.0)
    
    # Можно сделать маску более "хитрой" (smoothstep)
    #mask = mask * mask * (3 - 2 * mask)

    # 4. Финальный результат: Вороной * Маска
    # Делим на 2, как в твоем шейдере
    #final_map = (res_map / 2.0) * mask
    final_map = (res_map / 2.0)
    
    return final_map

def hash_vec2(p):
    # Твоя проверенная функция хэша
    p_dot = np.stack([np.dot(p, [127.1, 311.7]), np.dot(p, [269.5, 183.3])], axis=-1)
    sin_p = np.sin(p_dot) * 18.5453
    return sin_p - np.floor(sin_p)

# Генерируем
vase_tex = generate_vase_texture()
arr_uint8 = (np.clip(vase_tex * 255, 0, 255)).astype(np.uint8)
Image.fromarray(arr_uint8, mode='L').save("./stl/vase_side_texture.png")