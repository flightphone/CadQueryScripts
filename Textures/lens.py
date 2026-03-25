import numpy as np
import math
from PIL import Image

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def length(vec_array):
    # Вычисляет длину векторов для каждого пикселя
    return np.sqrt(np.sum(vec_array**2, axis=-1))

def lens(p, a, b, d):
    c = (a + b) / 2.0
    norm_vec = b - a
    l = np.linalg.norm(norm_vec) / 2.0
    
    # Нормаль к отрезку
    norm_dir = np.array([-norm_vec[1], norm_vec[0]])
    norm_dir /= np.linalg.norm(norm_dir)
    
    x_val = d * l
    y_val = l / d
    r = (x_val + y_val) / 2.0
    h = r - x_val
    
    c1 = c + norm_dir * h
    c2 = c - norm_dir * h
    
    # Расстояния от каждой точки p до центров окружностей c1 и c2
    # p имеет форму (res, res, 2), c1 имеет форму (2,)
    
    def flens(pp):
        dist1 = r - length(pp - c1)
        dist2 = r - length(pp - c2)
        di = np.minimum(dist1, dist2)
        hh = 0.01
        di = smoothstep(0.0, hh, di) * di
        di = np.power(np.maximum(di, 0.0), 0.5)
        x_pow = np.power(x_val, 0.5)
        return di / x_pow
    
    hh = 0.001
    dx = np.array([hh, 0])
    dy = np.array([0, hh])

    ddx = (flens(p + dx) - flens(p - dx)) / (2 * hh)
    ddy = (flens(p + dy) - flens(p - dy)) / (2 * hh)

    # собираем вектор нормали: shape (res, res, 3)
    ones = np.ones(p.shape[:2])
    norm = np.stack([-ddx, -ddy, ones], axis=-1)
    
    # нормализуем
    length1 = np.sqrt((norm ** 2).sum(axis=-1, keepdims=True))
    norm = norm / length1
    
    return flens(p),  norm


def render1():
    # --- Настройки рендера ---
    res = 2048
    TAU = math.tau

    # 1. Создаем сетку координат p (аналог fragCoord)
    # Диапазон от -1 до 1 по обеим осям
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]


    p = np.stack([x_grid, y_grid], axis=-1)

    # 2. Основной цикл (аналог mainImage)
    res_mask = np.zeros((res, res))
    res_norm = np.zeros((res, res, 3))
    res_norm[:,:, 2] = 1.
    
    
    
    r0 = 0.95
    num_steps = 13

    for i in range(num_steps):
        angle_a = (TAU / num_steps) * i
        angle_b = (TAU / num_steps) * (i + 5.0)
        
        a = r0 * np.array([np.cos(angle_a), np.sin(angle_a)])
        b = r0 * np.array([np.cos(angle_b), np.sin(angle_b)])
        
        # Сравниваем текущий результат с предыдущим (аналог max(res, ...))
        current_lens, current_norm = lens(p, a, b, 0.05)
        #res_mask = np.maximum(res_mask, current_lens)
        
        # булева маска: True там, где новая фигура выше
        mask = current_lens > res_mask    # shape: (res, res)

        # обновляем высоту
        res_mask[mask] = current_lens[mask]

        # для нормалей нужно расширить маску до (res, res, 3)
        mask3 = mask[:, :, np.newaxis]  # shape: (res, res, 1) — broadcasting сам растянет до (res, res, 3)
        res_norm = np.where(mask3, current_norm, res_norm)  # аналог тернарного оператора: где True берёт из cur_norm, где False — оставляет normals


    arr_uint8 = (res_mask * 255).astype(np.uint8)
    normals_map = ((res_norm * 0.5 + 0.5) * 255).astype(np.uint8)
    
    '''
    # 3. Подготовка данных для PIL
    rgba = np.zeros((res, res, 3), dtype=np.uint8)
    rgba[:, :, 0] = arr_uint8  # Red
    rgba[:, :, 1] = arr_uint8  # Green
    rgba[:, :, 2] = arr_uint8  # Blue
    img = Image.fromarray(rgba)
    '''
    # Grayscale напрямую — PIL сам разберётся
    img = Image.fromarray(arr_uint8, mode='L')
    img.save("./stl/lens.png")
    
    img_norm = Image.fromarray(normals_map)
    img_norm.save("./stl/lens_norm.png")
    
    print("ok")

render1()
