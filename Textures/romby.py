import numpy as np
import math
from PIL import Image

def generate_seamless_map(res=1024, tiles=6):
    """
    Генерирует идеально бесшовную ромбовидную карту высот.
    tiles - количество повторений узора по каждой оси.
    """
    y, x = np.mgrid[0:1:complex(res), 0:1:complex(res)]
    
    # Переводим в радианы для периодичности (0..1 -> 0..2*pi)
    # Умножаем на tiles, чтобы узор повторился n раз
    u = x * 2 * np.pi * tiles
    v = y * 2 * np.pi * tiles
    
    # Математика ромбовидного узора (чешуи):
    # Смещаем синусы относительно друг друга
    pattern = np.cos(u) + np.cos(v)
    
    # Нормализуем в диапазон 0..1
    pattern = (pattern - pattern.min()) / (pattern.max() - pattern.min())
    
    # Чтобы сделать "чешую" более острой (как на фото), добавим степень
    pattern = np.power(pattern, 1.5) 
    
    return pattern

res = 1024
tiles = 8 # Обязательно целое число для бесшовности

print(f"Генерация бесшовного узора ({tiles}x{tiles})...")
data = generate_seamless_map(res, tiles)
arr_uint8 = (data * 255.0).astype(np.uint8)

img = Image.fromarray(arr_uint8, mode='L')
img.save("./stl/rot_seamless.png")
print("Готово! Файл rot_seamless.png создан.")