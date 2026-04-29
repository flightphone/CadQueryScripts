import numpy as np
from PIL import Image

def hash_np(p):
    x = np.sin(p.real * 12.9898 + p.imag * 78.233) * 43758.5453
    return x - np.floor(x)

def noise(x):
    i = np.floor(x.real) + 1j*np.floor(x.imag)
    f = (x.real - np.floor(x.real)) + 1j*(x.imag - np.floor(x.imag))
    u = f.real**2 * (3.0 - 2.0 * f.real) + 1j*(f.imag**2 * (3.0 - 2.0 * f.imag))
    
    a, b = hash_np(i), hash_np(i + 1)
    c, d = hash_np(i + 1j), hash_np(i + 1 + 1j)
    
    return a*(1-u.real)*(1-u.imag) + b*u.real*(1-u.imag) + \
           c*(1-u.real)*u.imag + d*u.real*u.imag

def get_malachite_palette(t):
    # Глубокие зеленые и почти черные тона
    t = t[..., None]
    a = np.array([0.02, 0.15, 0.05]) # Базовый тон
    b = np.array([0.1, 0.35, 0.15]) # Амплитуда
    c = np.array([1.0, 1.2, 1.1])   # Частота каналов
    d = np.array([0.5, 0.3, 0.4])   # Сдвиг фазы
    return a + b * np.cos(2 * np.pi * (c * t + d))

def create_malachite():
    res = 1024
    scale = 4.0
    u = np.linspace(0, scale, res)
    v = np.linspace(0, scale, res)
    uu, vv = np.meshgrid(u, v)
    
    # 1. СТРАТЕГИЯ БЕСШОВНОСТИ (TILING)
    # Вместо abs используем синусоидальное искажение координат
    U = np.sin(2 * np.pi * uu / scale) + 1j * np.sin(2 * np.pi * vv / scale)

    # 2. DOMAIN WARPING (Искривление пространства)
    # Это создает "текучесть" малахита
    offset = noise(U * 0.8) + 1j * noise(U * 0.8 + 5.6)
    U_warped = U + offset * 0.5

    # 3. ГЕНЕРАЦИЯ БАЗОВОГО ШУМА (Фрактальный шум)
    f_val = 1.0 * noise(U_warped * 1.5)
    f_val += 0.5 * noise(U_warped * 4.0)
    f_val += 0.1 * noise(U_warped * 12.0)

    # 4. ПРЕОБРАЗОВАНИЕ В ПЛАТО (Тот самый tanh)
    H = 12.0          # Высота/количество слоев
    threshold = 0.8   # Уровень среза
    steepness = 15.0  # Резкость краев плато
    
    # Создаем резкие переходы
    plato = (H / 2) * (np.tanh(steepness * (f_val - threshold)) + 1)
    
    # Добавляем микро-рельеф на плато (чтобы оно не было идеально плоским)
    final_texture = plato + 0.3 * f_val * (plato > 0.1)

    # 5. РИТМ СЛОЕВ (Нелинейный синус)
    # Возведение в степень 0.8 делает слои разной толщины
    layers = (np.sin(final_texture**0.8 * 2.5) + 1) / 2
    
    # 6. ЦВЕТ И ЛИНИИ
    col = get_malachite_palette(layers)
    
    # Добавляем светлые прожилки по градиенту
    dx = scale / res
    gx, gy = np.gradient(plato, dx)
    grad = np.sqrt(gx**2 + gy**2)
    
    # Белые линии там, где самый резкий подъем плато
    line_mask = np.clip(grad * 0.05, 0, 1)
    line_mask = np.power(line_mask, 3) # Делаем линии тоньше
    
    light_green = np.array([0.4, 0.8, 0.5]) # Цвет светлой прожилки
    col = col * (1 - line_mask[..., None]) + light_green * line_mask[..., None]

    # Финализация
    color = np.clip(col, 0, 1)
    img = Image.fromarray((color * 255).astype(np.uint8))
    img.save("./stl/malachite_pro.png")
    print("Шедевр готов!")

#create_malachite()
def create_malachite_no_mirror():
    res = 1024
    scale = 4.0
    u = np.linspace(0, scale, res)
    v = np.linspace(0, scale, res)
    uu, vv = np.meshgrid(u, v)
    
    # 1. ЧЕСТНАЯ БЕСШОВНОСТЬ БЕЗ СИММЕТРИИ
    # Мы переносим 2D координаты на поверхность тора в 4D пространстве
    angle_u = 2 * np.pi * uu / scale
    angle_v = 2 * np.pi * vv / scale
    
    # Вместо U = sin + 1j*sin используем две разные "фазы" для шума
    # Это уберет эффект калейдоскопа
    X1, Y1 = np.cos(angle_u), np.sin(angle_u)
    X2, Y2 = np.cos(angle_v), np.sin(angle_v)
    
    # Генерируем два независимых шума для искажения координат (Domain Warping)
    # Используем комбинации X1, Y1, X2, Y2, чтобы края сошлись
    warp_x = noise(X1 + 1j*X2) + noise(Y1 + 1j*Y2)
    warp_y = noise(X1 + 5.2 + 1j*Y2) + noise(Y1 + 1j*(X2 + 3.1))
    
    # Смешиваем координаты для получения итогового значения
    # Теперь здесь нет функции abs() или простых синусов, дающих зеркало
    f_val = 1.0 * noise((X1 + warp_x*0.5) + 1j*(X2 + warp_y*0.5))
    f_val += 0.5 * noise((Y1*2 + warp_x) + 1j*(Y2*2 + warp_y))
    f_val += 0.1 * noise((X1*10) + 1j*(Y2*10))

    # 2. ПРЕОБРАЗОВАНИЕ (Ваш любимый tanh и слои)
    H = 10.0
    threshold = 0.5
    steepness = 12.0
    
    plato = (H / 2) * (np.tanh(steepness * (f_val - threshold)) + 1)
    
    # Ритм слоев (убираем симметрию и здесь, чуть смещая фазу)
    final_texture = plato + 0.2 * f_val
    layers = (np.sin(final_texture**0.8 * 3.0 + f_val) + 1) / 2
    
    # Дальше отрисовка (get_malachite_palette и градиенты) как в прошлом коде...
    col = get_malachite_palette(layers)
    
    # Добавляем прожилки (через градиент plato)
    dx = scale / res
    gx, gy = np.gradient(plato, dx)
    grad = np.sqrt(gx**2 + gy**2)
    line_mask = np.power(np.clip(grad * 0.04, 0, 1), 3)
    
    light_green = np.array([0.3, 0.7, 0.4])
    col = col * (1 - line_mask[..., None]) + light_green * line_mask[..., None]
    
    # Сохранение
    color = np.clip(col, 0, 1)
    img = Image.fromarray((color * 255).astype(np.uint8))
    img.save("./stl/malachite_random.png")
    print("Текстура без симметрии готова!")

create_malachite_no_mirror()

