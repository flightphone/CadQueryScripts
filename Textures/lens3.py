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

def diamond_line_AI(p, a, b, d = 0.02, r = 0.05): # r теперь по умолчанию маленький
    #google AI
    ab = b - a
    l = np.linalg.norm(ab)
    if l < 0.0001: return np.zeros(p.shape[:-1]) # защита от нулевых линий
    
    v = p - a
    h = d * l
    
    # Расстояние до прямой (поперек)
    dist = np.abs((v[..., 0] * ab[1] - v[..., 1] * ab[0]) / l)
    
    # Проекция на линию (вдоль, от 0 до 1)
    t = np.clip((v[..., 0] * ab[0] + v[..., 1] * ab[1]) / (l * l), 0, 1)
    
    # Резкое затухание на концах (маска длины)
    # Используем очень узкий smoothstep для имитации удара резца
    edge_softness = r 
    sh = smoothstep(0, edge_softness, t) * (1 - smoothstep(1 - edge_softness, 1, t))
    
    # ФОРМУЛА ГРАНИ:
    # Вместо плавного (h-dist)/h используем линейный спад к краям
    # Это создает визуальное "ребро"
    res = np.clip(1.0 - (dist / (h * sh + 1e-6)), 0, 1)
    
    # Добавляем небольшую кривизну, чтобы свет "играл" на грани (опционально)
    # res = np.power(res, 1.5) 
    
    return res

def diamond_line(p, a, b, d = 0.02, r = 0.05):
    ab = b - a
    l = np.linalg.norm(ab)
    v = p - a
    h = d*l
    dist = np.abs((v[..., 0] * ab[1] - v[...,1] * ab[0])/l)  #псевдоскалярное произведение
    t = np.clip((v[..., 0] * ab[0] + v[...,1] * ab[1])/l/l, 0, 1)
    sh = smoothstep(0, r, t)*(1 - smoothstep(1-r, 1, t))
    res = np.clip((h*sh - dist)/h, 0, 1)
    #res = np.power(res, 1.5) 
    return res

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

def npcross(r, s):
    return r[0]*s[1] - r[1]*s[0]


def intersect(a, b, c, d):
    #google AI
    # Направляющие векторы
    r = b - a
    s = d - c
    
    # Знаменатель для поиска точки (векторное произведение направляющих векторов)
    denom =  npcross(r, s)
    
    # Если denom == 0, отрезки параллельны
    if denom == 0:
        return None

    # Параметры t и u для уравнений прямых: 
    # P(t) = a + t*r
    # Q(u) = c + u*s
    t = npcross(c - a, s) / denom
    u = npcross(c - a, r) / denom

    # Отрезки пересекаются, если 0 <= t <= 1 и 0 <= u <= 1
    if 0 <= t <= 1 and 0 <= u <= 1:
        return a + t * r
    
    return None # Пересечения в пределах отрезков нет    

def render():
    res = 2048

    # 1. Создаем сетку координат p (аналог fragCoord)
    # Диапазон от -1 до 1 по обеим осям
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    p = np.stack([x_grid, y_grid], axis=-1)
    x, y = p[..., 0], p[..., 1]
    alf = (np.arctan2(y, x) + math.tau) % math.tau

    # 2. Основной цикл (аналог mainImage)
    res_mask = np.zeros((res, res))

    
    #==============center star=====================

    r0 = 0.35
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


    angle3 = -np.floor(alf/loop2)*loop2 - loop2/2
    X3 = x * np.cos(angle3) - y * np.sin(angle3)
    Y3 = x * np.sin(angle3) + y * np.cos(angle3)
    p3 = np.stack([X3, Y3], axis=-1)

    # Создаем матрицу поворота
    R = np.array([
    [np.cos(loop2/2), -np.sin(loop2/2)],
    [np.sin(loop2/2),  np.cos(loop2/2)]
    ])


    r1 = 0.55
    r2 = 0.92
    a_points2 = [r1*np.array([math.cos(loop2/2), math.sin(loop2/2)]), r1*np.array([math.cos(-loop2/2), math.sin(-loop2/2)])]
    b_points2 = [r2*np.array([math.cos(-loop2/2), math.sin(-loop2/2)]), r2*np.array([math.cos(loop2/2), math.sin(loop2/2)])]
    ins1 = intersect(a_points2[0], b_points2[0], a_points2[1], b_points2[1])
    
    
    
    for a, b in zip(a_points2, b_points2):
        current_lens = diamond_line(p2, a, b, 0.02)
        mask = current_lens > res_mask    # shape: (res, res)
        res_mask[mask] = current_lens[mask]

    
    #косая 1
    a_points3 = [a_points2[0] for _ in range(2)]
    b_points3 = [a_points2[1] + (ins1 - a_points2[1])*(0.5 + i/4) for i in range(2)]
    for a, b in zip(a_points3, b_points3):
        current_lens = diamond_line(p2, a, b, 0.01)*0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]

    #косая 2
    a_points3 = [a_points2[1] for _ in range(2)]
    b_points3 = [a_points2[0] + (ins1 - a_points2[0])*(0.5 + i/4) for i in range(2)]
    for a, b in zip(a_points3, b_points3):
        current_lens = diamond_line(p2, a, b, 0.01)*0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]    
    

    r3 = (r1 + r2)/2
    points3 = [r1*np.array([math.cos(loop2/2), math.sin(loop2/2)]), r1*np.array([math.cos(-loop2/2), math.sin(-loop2/2)])]
    aa = np.array([r3, 0])
    for b in points3:
        current_lens = diamond_line(p2, aa, b, 0.04)
        mask = current_lens > res_mask    # shape: (res, res)
        res_mask[mask] = current_lens[mask]

    
    ins2 = intersect(a_points2[0], b_points2[0], a_points2[1], aa)
    ins3 = np.array([ins2[0], -ins2[1]])
    n4 = 15
    a_points4 = [a_points2[1] + (ins2 - a_points2[1])*i/n4 for i in range(1, n4)]
    b_points4 = [a_points2[1] + (ins1 - a_points2[1])*i/n4 for i in range(1, n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p2, a, b, 0.07)*0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]    

    a_points4 = [a_points2[0] + (ins3 - a_points2[0])*i/n4 for i in range(1, n4)]
    b_points4 = [a_points2[0] + (ins1 - a_points2[0])*i/n4 for i in range(1, n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p2, a, b, 0.07)*0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]        
    
    points = [ins1, (ins2 + ins1)/2, ins2, (ins2 + aa)/2, aa, (aa + ins3)/2, ins3, (ins1 + ins3)/2]    
    for i in range(8):
        j = (i + 3) % 8
        current_lens = diamond_line(p2, points[i], points[j], 0.03)*0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]        

    ins23 = ins2 @ R.T
    ins33 = np.array([ins23[0], -ins23[1]])
    v1 = np.array([r1, 0])
    v2 = np.array([r2, 0])

    n4 = 4
    a_points4 = [v1 + (ins23 - v1)*i/n4 for i in range(1, n4)]
    b_points4 = [ins33 + (v2 - ins33)*i/n4 for i in range(1, n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.02)
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]   

    
    a_points4 = [v1 + (ins23 - v1)*(i/n4 + 1/2/n4) for i in range(n4)]
    b_points4 = [ins33 + (v2 - ins33)*(i/n4 + 1/2/n4) for i in range(n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.01) * 0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]         

    a_points4 = [v1 + (ins33 - v1)*i/n4 for i in range(1, n4)]
    b_points4 = [ins23 + (v2 - ins23)*i/n4 for i in range(1, n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.02)
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]     

    a_points4 = [v1 + (ins33 - v1)*(i/n4 + 1/2/n4) for i in range(n4)]
    b_points4 = [ins23 + (v2 - ins23)*(i/n4 + 1/2/n4) for i in range(n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.01) * 0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]     

    a_points4 = [v1 + (ins33 - v1)*i/2/n4 for i in range(1, 2*n4)]
    b_points4 = [v1 + (ins23 - v1)*i/2/n4 for i in range(1, 2*n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.02) * 0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]                 

    a_points4 = [v2 + (ins33 - v2)*i/2/n4 for i in range(1, 2*n4)]
    b_points4 = [v2 + (ins23 - v2)*i/2/n4 for i in range(1, 2*n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.02) * 0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]                     

    a_points4 = [v2 + (ins33 - v2)*i/2/n4 for i in range(1, 2*n4)]
    b_points4 = [v1 + (ins33 - v1)*i/2/n4 for i in range(1, 2*n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.02) * 0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]    

    a_points4 = [v2 + (ins23 - v2)*i/2/n4 for i in range(1, 2*n4)]
    b_points4 = [v1 + (ins23 - v1)*i/2/n4 for i in range(1, 2*n4)]
    for a, b in zip(a_points4, b_points4):
        current_lens = diamond_line(p3, a, b, 0.02) * 0.5
        mask = current_lens > res_mask    
        res_mask[mask] = current_lens[mask]        
    
    #куст
    rr = 0.1
    num = 11
    angle_a = math.tau/num
    points = [rr * np.array([np.cos(angle_a*i), np.sin(angle_a*i)]) for i in range(num)]
    points = points + aa + np.array([rr, 0])
    for b in points:
        current_lens = lens(p2, aa, b, 0.2)
        mask = current_lens > res_mask    # shape: (res, res)
        res_mask[mask] = current_lens[mask]


    arr_uint8 = (res_mask * 255).astype(np.uint8)
    img = Image.fromarray(arr_uint8, mode='L')
    img.save("./stl/lens3.png")
    print("texture generate")

render()
