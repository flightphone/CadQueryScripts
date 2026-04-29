import numpy as np
from PIL import Image

def hash_np(p):
    x = np.sin(p.real * 12.9898 + p.imag * 78.233) * 43758.5453
    return x - np.floor(x)

def noise(x):
    i = np.floor(x.real) + 1j*np.floor(x.imag)
    f = (x.real - np.floor(x.real)) + 1j*(x.imag - np.floor(x.imag))
    u = (f.real**2 * (3.0 - 2.0 * f.real)) + 1j*(f.imag**2 * (3.0 - 2.0 * f.imag))
    a, b, c, d = hash_np(i), hash_np(i + 1), hash_np(i + 1j), hash_np(i + 1 + 1j)
    return a*(1-u.real)*(1-u.imag) + b*u.real*(1-u.imag) + c*(1-u.real)*u.imag + d*u.real*u.imag

def get_palette(t):
    t = t[..., None]
    # Настройки для "жемчужного" спектра
    a = np.array([0.95, 0.85, 0.9])   # Базовый цвет (почти белый)
    b = np.array([0.15, 0.15, 0.15])  # Интенсивность радуги
    c = np.array([1.0, 1.0, 1.0])     # Частота
    d = np.array([0.0, 0.33, 0.67])   # Сдвиг фаз
    return a + b * np.cos(2 * np.pi * (c * t + d))

def create_shell_nacre():
    res = 2048 # Увеличим разрешение для деталей
    scale = 6.0
    u, v = np.meshgrid(np.linspace(0, scale, res), np.linspace(0, scale, res))
    U = u + 1j*v

    # 1. Основная форма (плавные искажения)
    f1 = noise(U * 0.5)
    f2 = noise(U + f1 * 2.0)
    
    # 2. Эффект "наслоения" (террасирование шума)
    # Вместо плавного шума делаем его ступенчатым
    layer_noise = noise(U * 1.5 + f2)
    steps = np.floor(layer_noise * 12.0) / 12.0 # Создаем 12 четких слоев
    
    # Смешиваем плавность и ступеньки для реализма
    final_val = mix(layer_noise, steps, 0.7) 

    # 3. Цвет
    color = get_palette(final_val * 2.0)
    
    # 4. Тонкие "царапины" и чешуйки (микро-детали)
    detail_noise = hash_np(U * 50.0 + final_val * 10.0)
    color -= detail_noise[..., None] * 0.03 # Едва заметная зернистость
    
    img = Image.fromarray((np.clip(color, 0, 1) * 255).astype(np.uint8))
    img.save("./stl/shell_nacre.png")
    print("Текстура для ракушки готова!")

def mix(a, b, t): return a*(1-t) + b*t

create_shell_nacre()
