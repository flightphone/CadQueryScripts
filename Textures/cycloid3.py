import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter, shift
from PIL import Image
import imageio # Библиотека для GIF

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a * (1 - t) + b * t

def epicycloid(q, num_points=5000):
    a = 0.5
    t = np.linspace(0, 2 * np.pi * (1 if q % 1 == 0 else 10), num_points)
    x = a * ((q+1)*np.cos(t) - np.cos((q+1)*t)) / q
    y = a * ((q+1)*np.sin(t) - np.sin((q+1)*t)) / q
    return np.stack([x, y], axis=-1)

def render_frame(q_val, glow_intensity, res=512): # Уменьшил res для скорости сборки GIF
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1)
    
    curve_points = epicycloid(q_val)
    tree = cKDTree(curve_points)
    dists, _ = tree.query(coords.reshape(-1, 2), k=1)
    dists = dists.reshape(res, res)
    
    base_color = np.array([0.6, 0.7, 1.0])
    core = smoothstep(0.006, 0, dists)
    glow_mask = np.exp(-dists / 0.06) * 0.4
    
    img = base_color * (core + glow_mask)[..., None]
    
    # Эффект пульсирующего Bloom
    bloom = gaussian_filter(img, sigma=10)
    img = img + bloom * glow_intensity # glow_intensity меняется от кадра к кадру
    
    # Хроматическая аберрация
    img[:, :, 0] = shift(img[:, :, 0], [1, 1])
    img[:, :, 2] = shift(img[:, :, 2], [-1, -1])
    
    # Зернистость
    img = np.clip(img + np.random.normal(0, 0.02, img.shape), 0, 1)
    
    return (img * 255).astype(np.uint8)

# --- Настройки для плавной анимации ---
num_frames = 90 # Больше кадров = медленнее и плавнее переход
frames = []

print("Рендерим плавную анимацию (90 кадров)...")

for i in range(num_frames):
    # Нормализуем шаг от 0 до 1, затем в радианы для синуса
    t = 2 * np.pi * i / num_frames
    
    # Слегка меняем форму (q), чтобы лепестки "шевелились"
    current_q = 4.5 + np.sin(t) * 0.15 
    
    # Свечение: плавная пульсация от 0.5 до 1.8
    # sin(t) дает значения от -1 до 1, поэтому смещаем его
    current_glow = 1.1 + np.sin(t) * 0.7 
    
    frame = render_frame(current_q, current_glow, res=512)
    frames.append(frame)
    
    if i % 10 == 0:
        print(f"Прогресс: {i}/{num_frames}")

# Сохраняем с замедленным темпом
# 24 кадра в секунду при 90 кадрах дадут ~3.7 секунды чистого цикла
imageio.mimsave('./stl/epicycloid_slow_breath.gif', frames, fps=24, loop=0)
print("Готово! Теперь она должна 'дышать' гораздо спокойнее.")