import numpy as np
import math
from PIL import Image
from scipy.ndimage import gaussian_filter, shift

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a*(1-t) + b*t

def length(p):
     return np.sqrt(np.sum(p**2, axis=-1))


def FF(p):
    a = np.array([0.0, 0.5]) 
    l1 = length(p-a)
    l2 = length(p+a)
    res = np.abs(np.pow(l1, -1) - np.pow(l2, -1))
    res = np.log((1. +  res))
    return res * 8   
    
def EE(p):
    a = np.array([0.0, 0.5]) 
    l1 = length(p-a)
    l2 = length(p+a)

    n1 = (p-a)[:,:,1]/l1
    n2 = (p+a)[:,:,1]/l2
    return (n1 - n2)*10


def grd_fun(p, fn):
    eps = 0.00001
    x = (fn(p + np.array([eps, 0])) - fn(p - np.array([eps, 0])))/2/eps
    y = (fn(p + np.array([0, eps])) - fn(p - np.array([0, eps])))/2/eps
    grd = np.stack([x, y], axis=-1)  
    return np.sqrt(np.sum(grd**2, axis=-1))



def generate_map(res=1024):
    
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1) # shape (res, res, 2)
    
    final_col_np = np.full((res, res, 3), fill_value = [1, 1, 1], dtype=np.uint8)
    d = 0.004
    
    grd1 = grd_fun(coords, FF)
    field = FF(coords)
    mask1 = smoothstep(d*grd1, 0, np.abs(field - np.floor(field) - 0.5))
    col1 = mix(final_col_np, np.array([1, 0, 0]), mask1[..., None])
    
    
    grd2 = grd_fun(coords, EE)
    line = EE(coords)
    mask2 = smoothstep(d*grd2, 0, np.abs(line - np.floor(line) - 0.5))
    col2 = mix(final_col_np, np.array([0, 0, 1]), mask2[..., None])

    final_col_np = mix(col1, col2, 0.5)
    return final_col_np



def generate_map2(res=1024, t=0.0):
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1)
    
    # Фон теперь черный
    img = np.zeros((res, res, 3))
    d = 0.005 # Базовая толщина

    # Считаем поля
    field_f = FF(coords)
    field_e = EE(coords)
    
    # Считаем градиенты для одинаковой толщины линий (как в твоем коде)
    grd_f = grd_fun(coords, FF)
    grd_e = grd_fun(coords, EE)

    # 1. Линии поля F (Красные) + анимация движения
    # Добавляем t к полю, чтобы линии "плыли"
    mask_f = smoothstep(d * grd_f, 0, np.abs((field_f + t) % 1.0 - 0.5))
    img = mix(img, np.array([1.0, 0.2, 0.2]), mask_f[..., None])

    # 2. Линии поля E (Синие)
    mask_e = smoothstep(d * grd_e, 0, np.abs((field_e + t*0.5) % 1.0 - 0.5))
    img = mix(img, np.array([0.2, 0.5, 1.0]), mask_e[..., None])

    # --- ПОСТ-ЭФФЕКТЫ ---
    # Добавляем Bloom, чтобы линии "горели"
    bloom = gaussian_filter(img, sigma=8)
    img += bloom * 1.2
    
    # Хроматическая аберрация (сделаем её сильнее к краям)
    img[:, :, 0] = shift(img[:, :, 0], [2, 2])
    img[:, :, 2] = shift(img[:, :, 2], [-2, -2])

    return np.clip(img, 0, 1)

# render

res = 1024



print("generation texture...")
img_data =  generate_map2(res=res)

fname = "dipole2.png"
print(f"save {fname}...")
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8).save(f"./stl/{fname}")
print("successfuly")