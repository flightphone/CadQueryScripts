import numpy as np
import math
from PIL import Image

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a*(1-t) + b*t

def hash_np(p):
    # Быстрый векторный хэш для numpy
    x = np.sin(p.real * 12.9898 + p.imag * 78.233) * 43758.5453
    return x - np.floor(x)

def noise(x):
    i = np.floor(x.real) + 1j*np.floor(x.imag)
    f = (x.real - np.floor(x.real)) + 1j*(x.imag - np.floor(x.imag))
    
    # Сглаживание по эрмиту
    u = (f.real**2 * (3.0 - 2.0 * f.real)) + 1j*(f.imag**2 * (3.0 - 2.0 * f.imag))
    
    a = hash_np(i)
    b = hash_np(i + 1)
    c = hash_np(i + 1j)
    d = hash_np(i + 1 + 1j)
    
    res = a * (1 - u.real) * (1 - u.imag) + \
          b * u.real * (1 - u.imag) + \
          c * (1 - u.real) * u.imag + \
          d * u.real * u.imag
    return res

def get_palette(t):
    t = t[..., None]
    # Темно-зеленые, изумрудные и черные тона
    a = np.array([0.0, 0.2, 0.05])  # Базовый темно-зеленый
    b = np.array([0.1, 0.3, 0.1])   # Вариация яркости
    c = np.array([1.0, 1.0, 1.0])   # Частота
    d = np.array([0.5, 0.2, 0.25])  # Сдвиг в сторону зелени
    return a + b * np.cos(2 * np.pi * (c * t + d))
    


def create_nacre():
    res = 1024
    scale = 3
    dx = scale / (res-1)
    u = np.linspace(0, scale, res)
    v = np.linspace(0, scale, res)
    uu, vv = np.meshgrid(u, v)
    U = uu + 1j*vv 
    
    
    
    
    shift = 3 + 2.5j
    rot = np.exp(np.pi * 1j / 7)
    
    #offset = noise(U * 1.2) + 1j * noise(U * 1.2 + 5.0)
    #U = U + offset * 0.4  # Координаты "поплыли"
    
    U = U*rot + shift
    final_val = 1.8*noise(2*U)  
    U = U*rot + shift
    final_val = final_val + 0.5*noise(5*U) 
    U = U*rot + shift
    final_val = final_val + 0.05*noise(20*U) 

    
    #google AI plato
    # Настройки
    H = 3*math.tau - 0.1          # Желаемая высота плато
    threshold = 1.   # Уровень "среза" (на какой высоте исходного холма делать плато)
    delta_u = 0.4     # Ширина перехода (чем меньше, тем резче ступенька)
    k = 3 / delta_u   # Та самая крутизна

    # Преобразование
    final_plateau = (H / 2) * (np.tanh(k * (final_val - threshold)) + 1)
    final_texture = final_plateau# + 0.5 * final_val * (final_plateau > (H/2))

    layers = (np.sin(final_texture) + 1)/2
    col = get_palette(layers)
    
    
    colline = np.full_like(col, [0.4, 0.9, 0.4])
    layers2 = (np.sin(np.log(final_texture + 1)) + 1)/2

  
    h = 0.001
    eps = 3*h
    
      	
    s1 = 1 - smoothstep(h, h+eps, np.abs(layers2 - 1.))  	
    s2 = 1 - smoothstep(4*h, 4*h+4*eps, np.abs(layers2 - 0.98))
    s3 = 1 - smoothstep(4*h, 4*h+4*eps, np.abs(layers2 - 0.55))
    col = mix(col, colline, s1[..., None])
    col = mix(col, colline, s2[..., None])
    col = mix(col, colline, s3[..., None])

    
    
    
    
    # Добавляем микро-блеск (высокочастотный шум)
    grain = hash_np(U * 10.0) 
    col += (grain[..., None] - 0.5) * 0.05
    
    color = np.clip(col, 0, 1)
    img = Image.fromarray((color * 255).astype(np.uint8))
    img.save("./stl/sin_line_texture2.png")
    print("Текстура готова!")

create_nacre()


'''
# Вместо простого сложения:
# final_val = noise(U) + noise(U*2)

# Попробуй так:
p_offset = noise(U * 1.5) + 1j * noise(U * 1.5 + 10.0)
final_val = noise(U + p_offset * 0.5) # Шум искривляет сам себя

Попробуй заменить константу 50 на плавную функцию от координат или другого шума, чтобы толщина линии «гуляла». В камнях жилы редко имеют идеально постоянную толщину.

Цветовая палитра: Сейчас цвета очень яркие и «кислотные» (RGB-цикл). В природе агаты чаще имеют землистые, охристые, серо-голубые или глубокие древесные тона. Попробуй ограничить палитру в get_palette более узким диапазоном.
Толщина слоев: В коде слои имеют почти одинаковую ширину. В настоящем камне есть ритм: серия очень тонких линий, затем одна широкая полупрозрачная полоса. Это можно реализовать, пропустив final_val через нелинейную функцию (например, сложную комбинацию pow или sin).
Domain Warping: Самый «магический» прием для камней. Вместо того чтобы просто складывать слои шума, используй результат одного шума как смещение координат для другого. Это создаст те самые характерные «наплывы» и «складки», как в малахите.


# Добавьте это перед расчетом final_val
offset = noise(U * 1.2) + 1j * noise(U * 1.2 + 5.0)
U_warped = U + offset * 0.4  # Координаты "поплыли"
final_val = 1.8 * noise(2 * U_warped) 

Маленький совет по коду:
Если H у вас по-прежнему около 25, попробуйте поиграть с функцией power:
layers = (np.sin(final_texture ** 0.9) + 1) / 2.
Это создаст ритм, где полосы к центру «почек» становятся чуть гуще или реже, что очень характерно для среза минерала.


1. Переменная толщина линий (Живость)
В природе полосы никогда не бывают одинаковой ширины. Вместо простого sin(final_texture) используйте небольшое искажение фазы:
python
# Слои будут то сжиматься, то расширяться
warped_texture = final_texture + 0.5 * noise(U * 1.5)
layers = (np.sin(warped_texture) + 1) / 2


1. «Танцующая» толщина линий
Сейчас eps (ширина линии) — это константа. Сделай её зависимой от шума, чтобы линия в одном месте была тонкой, а в другом чуть расплывалась:
python
# Вместо eps = 3*h
dynamic_eps = h * (2 + 2 * noise(U * 5).real) 
s1 = 1 - smoothstep(h, h + dynamic_eps, np.abs(layers2 - 1))

2. Эффект «вложенности» через нелинейность
Вместо просто log(final_texture + 1), попробуй «модуляцию частоты». Это создаст те самые пачки тонких линий, чередующиеся с широкими полосами:
python
# Магия в степени: меняя 1.2, ты меняешь ритм слоев
layers2 = (np.sin(np.power(final_texture, 1.2)) + 1) / 2

3. Проблема «кислотности»
На картинке сейчас очень яркий салатовый. В реальном малахите линии часто не чисто белые или зеленые, а имеют легкий подтон. Попробуй подмешивать colline не на 100%, а через умножение:
python
# Вместо чистого mix, попробуй осветление (screen) или наложение
col = mix(col, colline * 1.2, s1[..., None] * 0.7) 

Для стоков «бесконечное» видео — это огромный плюс. Чтобы узор плавно вернулся в начало (через 10–20 секунд), используйте трюк с 4D-шумом или интерполяцией.
Если ваш шум Перлина 3D (где третья координата — это время 
), то для цикла нужно двигаться не по прямой, а по кругу в 4D пространстве. Но есть способ проще — линейное смешивание:
Генерируете последовательность кадров для времени от 
 до 
.
Последние пару секунд видео плавно «растворяете» (через прозрачность) в начальные кадры.
Математическая формула для зацикливания параметра time:
Если noise(p) — ваша функция шума, то цикл можно сделать так:

где 
 меняется от 0 до 1 в конце ролика.


'''

#https://www.dreamstime.com/