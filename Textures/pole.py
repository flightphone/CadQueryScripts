import numpy as np
import math
from PIL import Image
from scipy.integrate import cumulative_trapezoid

points = np.array([[0.0, 0.5], [0.0, -0.5]])#, [-0.3, 0], [0.3, 0], [0.4, 0.4], [-0.4, -0.4]*/]) 
signs = np.array([1, -1])#, 1, -1, 1, -1])

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a*(1-t) + b*t

def length(p):
     return np.sqrt(np.sum(p**2, axis=-1))


def FF(p):
    
    res = np.zeros((p.shape[0], p.shape[1]))
    for a, s in zip(points, signs):
        l = length(p - a)
        res = res + s*np.pow(l, -1)
    return res

def grd_fun(p, fn):
    eps = 0.00001
    x = (fn(p + np.array([eps, 0])) - fn(p - np.array([eps, 0])))/2/eps
    y = (fn(p + np.array([0, eps])) - fn(p - np.array([0, eps])))/2/eps
    grd = np.stack([x, y], axis=-1)  
    return np.sqrt(np.sum(grd**2, axis=-1))    

def grd(p, fn):
    eps = 0.00001
    x = (fn(p + np.array([eps, 0])) - fn(p - np.array([eps, 0])))/2/eps
    y = (fn(p + np.array([0, eps])) - fn(p - np.array([0, eps])))/2/eps
    grd = np.stack([x, y], axis=-1)
    return grd




def generate_map(res=1024):
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1)
    dx = 2.0 / (res - 1)
    d = 0.004
    
    

    #psi_raw = get_universal_stream_function(field_raw)
    
    # 2. Применяем логарифмическое сжатие для визуализации
    # Используем sign * log(1 + abs), чтобы сохранить полярность
    def transform(x, intensity=8):
        return np.sign(x) * np.log(1.0 + np.abs(x)) * intensity

    def FFt(p):
        return transform(FF(p))

    field_viz = FFt(coords)
    # 3. Считаем градиенты уже ОТ ТРАНСФОРМИРОВАННЫХ полей
    # Это гарантирует, что толщина линии d будет соответствовать визуальному шагу
    #gy1, gx1 = np.gradient(field_viz, dx)
    #grd1 = np.sqrt(gx1**2 + gy1**2)
    grd1 = grd_fun(coords, FFt)

    # 1. Считаем "чистую" физику
    #field_raw = FF(coords) 
    #g = grd(coords, FF)
    xg, yg = np.gradient(field_viz, dx)
    psi_x = cumulative_trapezoid(x = coords, y = -yg, axis=-1, initial=0) 
    psi_y = cumulative_trapezoid(x = coords, y = xg, axis=-1, initial=0) 
    psi = psi_x + psi_y
    


    psi_viz = psi
    gy2, gx2 = np.gradient(psi_viz, dx)
    grd2 = np.sqrt(gx2**2 + gy2**2)
    
    # 4. Рисуем маски
    # Вычитаем 0.5, чтобы линии шли посередине между "целыми" уровнями логарифма
    mask1 = smoothstep(d * grd1, 0, np.abs(field_viz - np.floor(field_viz) - 0.5))
    mask2 = smoothstep(d * grd2, 0, np.abs(psi_viz - np.floor(psi_viz) - 0.5))
    
    # Смешиваем цвета
    final_col_np = np.full((res, res, 3), 1.0)
    col1 = mix(final_col_np, np.array([1, 0, 0]), mask1[..., None]) # Красный
    col2 = mix(final_col_np, np.array([0, 0, 1]), mask2[..., None]) # Синий
    
    # Чтобы в местах пересечения был фиолетовый, используем умножение или среднее
    return (col1 + col2) / 2.0 




# render

res = 1024



print("generation texture...")
img_data =  generate_map(res=res)

fname = "pole.png"
print(f"save {fname}...")
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8).save(f"./stl/{fname}")
print("successfuly")