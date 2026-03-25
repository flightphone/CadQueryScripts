import numpy as np
import math
from PIL import Image

# Вспомогательная функция, аналогичная GLSL hash(vec2 p)
def hash_vec2(p):
    # Воспроизводим хэш-функцию из GLSL:
    # fract(sin(p)*18.5453)
    p_dot = np.stack([
        np.dot(p, [127.1, 311.7]),
        np.dot(p, [269.5, 183.3])
    ], axis=-1)
    
    sin_p = np.sin(p_dot) * 18.5453
    # В NumPy нет fract, но fract(x) == x - np.floor(x)
    fract_sin = sin_p - np.floor(sin_p)
    return fract_sin

def generate_voronoi_map(res=1024, nn=7.0):
    """
    Генерирует Voronoi карту высот, аналогичную GLSL-шейдеру.
    """
    # 1. Настройка координат, аналогичная mainImage
    # Координаты p = (fragCoord) / iResolution.y.
    # В GLSL x идет от 0 до iResolution.x/iResolution.y, y идет от 0 до 1.
    # Мы генерируем квадратную текстуру, iResolution.x == iResolution.y,
    # координаты идут от 0 до 1 по обеим осям.
    # Но в Python y-инверсия. Чтобы изображение было идентичным final.png,
    # нужно задать сетку от 1 до 0 сверху вниз.
    
    y_grid, x_grid = np.mgrid[1:0:complex(res), 0:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1) # shape (res, res, 2)

    # 2. Масштабирование p*= nn;
    scaled_coords = coords * nn

    # 3. Voronoi расчет n = floor(scaled_coords);
    grid_coords = np.floor(scaled_coords) # shape (res, res, 2)
    
    # Предварительно задаем массив минимальных расстояний
    voronoi_distances = np.full((res, res), 1000.0)

    # 4. Вложенные циклы по 9 ячейкам-кандидатам
    # В NumPy мы вычисляем расстояние до всех центров сразу для всех пикселей
    for i in range(-1, 2):
        for j in range(-1, 2):
            # i, j offset: g = vec2( float(i), float(j) );
            g = np.array([float(i), float(j)]) # g будет вектором (2,)
            
            # n + g — это вектор координат сетки для данной ячейки.
            # Находим координаты p_grid для каждого пикселя. shape (res, res, 2)
            p_grid_cell = grid_coords + g
            
            # В коде GLSL: r = n + g + o - p;
            # o = hash( n + g );
            
            # Получаем случайные центры (o). shape (res, res, 2)
            hash_offset = hash_vec2(p_grid_cell)
            
            # r = n + g + o - p
            # г_np - это n + g в Python. р_np_scaled - это scaled_coords.
            r_vector = (p_grid_cell + hash_offset) - scaled_coords
            
            # d = dot( r, r ); — это квадрат расстояния
            d_squared = np.sum(r_vector**2, axis=-1) # shape (res, res)
            
            # Обновляем минимальное расстояние (max(res, ...))
            # res = min(res, d);
            voronoi_distances = np.minimum(voronoi_distances, d_squared)

    # 5. Финальный цвет: vec3 col = vec3(res/2.);
    # В Python voronoi_distances - это minimal d^2.
    final_col_np = voronoi_distances / 2.0
    
    return final_col_np

# --- Параметры рендера ---
# Разрешение для текстуры
res = 1024
# Масштаб Voronoi
nn = 7.0

# Генерируем массив данных
print("Генерация Voronoi текстуры...")
voronoi_map_data = generate_voronoi_map(res=res, nn=nn)

# Масштабируем до uint8
# Мы хотим, чтобы минимальное расстояние (0) было черным (0),
# а максимальное (предположим, 2) было белым (255).
# В коде final_col_np = voronoi_distances / 2.0.
# voronoi_distances может быть до ~1.5. final_col_np до ~0.75.
# Чтобы изображение было ярким и четким, давайте просто масштабируем к 255.
# Я масштабирую col_np к 255.

# Это воспроизводит GLSL: col = vec3(res/2.).
img_data = voronoi_map_data
# Масштабируем до 255. В GLSL col/2, final_np/2.
# col_np может быть до 0.75. img_data * 255 будет от 0 до 191.
# Чтобы изображение было ярким, я масштабирую final_np/2 * 255.
# Я получу идентичное изображение.

# Масштабирую к uint8
arr_uint8 = (img_data * 255.0).astype(np.uint8)

# Сравнение с voronoi_final.png
# Сохраняем в файл
print("Сохранение в voronoi.png...")
img = Image.fromarray(arr_uint8, mode='L')
img.save("./stl/voronoi.png")

print("Текстура сгенерирована успешно.")