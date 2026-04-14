import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter, shift
from PIL import Image

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a * (1 - t) + b * t

def epicycloid(num_points = 10000):
    #https://www.mathcurve.com/courbes2d.gb/epicycloid/epicycloid.shtml
    a = 0.5
    q = 4.5
    t = np.linspace(0, 4*np.pi, num_points)
    x = a * ((q+1)*np.cos(t) - np.cos((q+1)*t)) / q
    y = a * ((q+1)*np.sin(t) - np.sin((q+1)*t)) / q
    
    return np.stack([x, y], axis=-1)




def generate_map(res=1024):
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1)
    
    curve_points = epicycloid(num_points=8000)
    tree = cKDTree(curve_points)
    dists, _ = tree.query(coords.reshape(-1, 2), k=1)
    dists = dists.reshape(res, res)
    
    # Базовый цвет (нежно-голубой/фиолетовый)
    base_color = np.array([0.6, 0.6, 1.0])
    
    # 1. Формируем "стержень" и базовое свечение
    core = smoothstep(0.005, 0, dists)
    glow_mask = np.exp(-dists / 0.08) * 0.5
    img = base_color * (core + glow_mask)[..., None]

    # --- ПОСТПРОЦЕССИНГ ---

    # 2. BLOOM (Мягкое сияние)
    # Делаем копию и сильно размываем её
    bloom = gaussian_filter(img, sigma=15)
    img = img + bloom * 0.8 # Смешиваем оригинал с размытием

    # 3. ХРОМАТИЧЕСКАЯ АБЕРРАЦИЯ
    # Сдвигаем красный и синий каналы в разные стороны на пару пикселей
    img[:, :, 0] = shift(img[:, :, 0], [2, 2])  # Красный вправо-вниз
    img[:, :, 2] = shift(img[:, :, 2], [-2, -2]) # Синий влево-вверх

    # 4. ЗЕРНИСТОСТЬ (Film Grain)
    # Генерируем шум и накладываем его поверх
    noise = np.random.normal(0, 0.03, img.shape)
    img = np.clip(img + noise, 0, 1)

    # 5. ВИНЬЕТКА (бонус: акцент на центр)
    rad = np.sqrt(x_grid**2 + y_grid**2)
    vignette = smoothstep(1.2, 0.5, rad)
    img *= vignette[..., None]

    return img

# Запуск и сохранение прежние
img_data = generate_map(res=1024)
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8).save("./stl/epicycloid_fancy.png")
print("Эффекты применены!")
