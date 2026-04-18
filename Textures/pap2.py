import numpy as np
from PIL import Image
import os

def generate_barnsley_fern_gradient(width, height, iterations=2000000):
    # Коэффициенты [a, b, c, d, e, f, prob]
    coeffs = [
        [0.00,  0.00,  0.00,  0.16,  0.00, 0.00, 0.01],
        [0.85,  0.04, -0.04,  0.85,  0.00, 1.60, 0.85],
        [0.20, -0.26,  0.23,  0.22,  0.00, 1.60, 0.07],
        [-0.15, 0.28,  0.26,  0.24,  0.00, 0.44, 0.07]
    ]

    matrices = [np.array([[c[0], c[1]], [c[2], c[3]]]) for c in coeffs]
    offsets = [np.array([c[4], c[5]]) for c in coeffs]
    probs = [c[6] for c in coeffs]

    indices = np.random.choice(len(coeffs), size=iterations, p=probs)
    points = np.zeros((iterations, 2))
    current_point = np.array([0.0, 0.0])

    # Основной цикл генерации
    for i in range(iterations):
        idx = indices[i]
        current_point = matrices[idx] @ current_point + offsets[idx]
        points[i] = current_point

    # Проекция на пиксели
    x, y = points[:, 0], points[:, 1]
    x_img = ((x + 2.182) / (2.656 + 2.182) * (width - 1)).astype(int)
    y_img = ((10.0 - y) / 10.0 * (height - 1)).astype(int)

    # Создаем RGB холст (H, W, 3)
    img_data = np.zeros((height, width, 3), dtype=float)
    
    # Фильтруем точки внутри холста
    valid = (x_img >= 0) & (x_img < width) & (y_img >= 0) & (y_img < height)
    x_v, y_v = x_img[valid], y_img[valid]
    
    # Создаем градиент: нормализуем индекс итерации от 0 до 1
    # Это даст плавный переход цвета от основания к кончикам
    t = np.linspace(0, 1, iterations)[valid]

    # Задаем цвета (например, от темно-зеленого к ярко-салатовому)
    # Цвет = (1-t)*Color1 + t*Color2
    img_data[y_v, x_v, 0] = t * 0.2    # R
    img_data[y_v, x_v, 1] = 0.5 + t * 0.5  # G
    img_data[y_v, x_v, 2] = t * 0.3    # B

    return img_data

# Параметры
width, height = 1024, 1024
fname = "gradient_fern.png"
img_data = generate_barnsley_fern_gradient(width, height)

# Сохранение по вашему шаблону (теперь для RGB)
arr_uint8 = (img_data * 255.0).astype(np.uint8)
if not os.path.exists("./stl"): os.makedirs("./stl")
Image.fromarray(arr_uint8).save(f"./stl/{fname}")

print(f"Красивый фрактал сохранен в ./stl/{fname}")
