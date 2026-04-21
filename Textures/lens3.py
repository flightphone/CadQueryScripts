import numpy as np
import math
from PIL import Image
from scipy.ndimage import maximum_filter

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
    
    return flens(p)


def render1():
    # --- Настройки рендера ---
    res = 1024
    block_size = 16
    

    # 1. Создаем сетку координат p (аналог fragCoord)
    # Диапазон от -1 до 1 по обеим осям
    y_grid, x_grid = np.mgrid[-1:1:complex(res), -1:1:complex(res)]
    p = np.stack([x_grid, y_grid], axis=-1)
    x, y = p[..., 0], p[..., 1]
    alf = (np.arctan2(y, x) + math.tau) % math.tau

    # 2. Основной цикл (аналог mainImage)
    res_mask = np.zeros((res, res))

    
    #==============center star=====================
    r0 = 0.4
    num = 26
    loop = math.tau/num
    angle = -np.floor((alf+loop/2)/loop)*loop
    X = x * np.cos(angle) - y * np.sin(angle)
    Y = x * np.sin(angle) + y * np.cos(angle)
    p1 = np.stack([X, Y], axis=-1)
    
    
    points = [np.array([r0, 0])]
    a = np.array([0, 0])
    for b in points:
        current_lens = lens(p1, a, b, 0.2)
        mask = current_lens > res_mask    # shape: (res, res)
        res_mask[mask] = current_lens[mask]
    #==============center star=====================

    #==========radial==============================
    num2 = 7
    loop2 = math.tau/num2
    angle2 = -np.floor((alf+loop2/2)/loop2)*loop2
    X2 = x * np.cos(angle2) - y * np.sin(angle2)
    Y2 = x * np.sin(angle2) + y * np.cos(angle2)
    p2 = np.stack([X2, Y2], axis=-1)
    r1 = 0.5
    r2 = 0.98
    a_points2 = [r1*np.array([math.cos(loop2/2), math.sin(loop2/2)]), r1*np.array([math.cos(-loop2/2), math.sin(-loop2/2)])]
    b_points2 = [r2*np.array([math.cos(-loop2/2), math.sin(-loop2/2)]), r2*np.array([math.cos(loop2/2), math.sin(loop2/2)])]
    for a, b in zip(a_points2, b_points2):
        current_lens = lens(p2, a, b, 0.07)
        mask = current_lens > res_mask    # shape: (res, res)
        res_mask[mask] = current_lens[mask]

    r3 = (r1 + r2)/2
    points3 = [r1*np.array([math.cos(loop2/2), math.sin(loop2/2)]), r1*np.array([math.cos(-loop2/2), math.sin(-loop2/2)])]
    a = np.array([r3, 0])
    for b in points3:
        current_lens = lens(p2, a, b, 0.1)
        mask = current_lens > res_mask    # shape: (res, res)
        res_mask[mask] = current_lens[mask]

    rr = 0.1
    num = 11
    angle_a = math.tau/num
    points = [rr * np.array([np.cos(angle_a*i), np.sin(angle_a*i)]) for i in range(num)]
    points = points + a + np.array([rr, 0])
    for b in points:
        current_lens = lens(p2, a, b, 0.2)
        mask = current_lens > res_mask    # shape: (res, res)
        res_mask[mask] = current_lens[mask]


    arr_uint8 = (res_mask * 255).astype(np.uint8)
    img = Image.fromarray(arr_uint8, mode='L')
    img.save("./stl/lens3.png")

    

    
    
    print("texture generate")

render1()
