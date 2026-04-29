import numpy as np
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
    # Коэффициенты для нежных перламутровых переливов
    # t - это значение шума от 0 до 1
    t = t[..., None]
    #a = np.array([0.9, 0.8, 0.85])  # Смещение (яркость)
    #b = np.array([0.2, 0.2, 0.15])  # Амплитуда (насыщенность)
    a = np.array([0.8, 0.2, 0.2])  # Смещение (яркость)
    b = np.array([0.2, 0.2, 0.8])  # Амплитуда (насыщенность)
    c = np.array([1.0, 1.0, 1.0])   # Частота
    d = np.array([0.0, 0.33, 0.67]) # Фаза (сдвиг цветов радуги)
    
    return (a + b * np.cos(2 * np.pi * (c * t + d)))
    


def create_nacre():
    res = 1024
    scale = 1.5
    dx = scale / (res-1)
    u = np.linspace(0, scale, res)
    v = np.linspace(0, scale, res)
    uu, vv = np.meshgrid(u, v)
    U = uu + 1j*vv
    
    
    
    
    shift = 3 + 2.5j
    rot = np.exp(np.pi * 1j / 7)
    
    
    U = U*rot + shift
    final_val = 1.8*noise(2*U)  
    U = U*rot + shift
    final_val = final_val + 0.5*noise(5*U) 
    U = U*rot + shift
    final_val = final_val + 0.05*noise(30*U) 

    #final_val = 4*final_val**3
    final_val = 4*final_val

    nn1 = np.floor(final_val)
    layers = final_val - nn1
    
    
    
    col = get_palette(layers)
    colline = np.full_like(col, [1, 1, 1])

    gx, gy = np.gradient(final_val, dx)
    grad = np.sqrt(gx**2 + gy**2)

    k = 4
    eps = 0.001 * grad * scale * k
    h = eps/2
    
    layers = layers*k
    nn2 = np.floor(layers)
    layers = layers - nn2

    #толстые белые линии
    h = np.where(np.mod((nn1 * nn2), 16) == 12, h*50, h)
    h = np.where(np.mod((nn1 * nn2), 16) == 8, h*50, h)
    
    

    s1 = smoothstep(1. - h-eps, 1-h, layers)  	
    s2 = (1 - smoothstep(h, h+eps, layers))
    col = mix(col, colline, s1[..., None])
    col = mix(col, colline, s2[..., None])

    
    
    
    
    # Добавляем микро-блеск (высокочастотный шум)
    grain = hash_np(U * 10.0) 
    col += (grain[..., None] - 0.5) * 0.05
    
    color = np.clip(col, 0, 1)
    img = Image.fromarray((color * 255).astype(np.uint8))
    img.save("./stl/agat_texture.png")
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

'''