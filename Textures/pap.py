import numpy as np
from PIL import Image
import os

def generate_barnsley_fern(width, height, iterations=500000):
    # Коэффициенты аффинных преобразований [a, b, c, d, e, f, probability]
    coeffs = [
        [0.00,  0.00,  0.00,  0.16,  0.00, 0.00, 0.01],
        [0.85,  0.04, -0.04,  0.85,  0.00, 1.60, 0.85],
        [0.20, -0.26,  0.23,  0.22,  0.00, 1.60, 0.07],
        [-0.15, 0.28,  0.26,  0.24,  0.00, 0.44, 0.07]
    ]

    # Подготовка матриц (A) и векторов сдвига (B)
    matrices = [np.array([[c[0], c[1]], [c[2], c[3]]]) for c in coeffs]
    offsets = [np.array([c[4], c[5]]) for c in coeffs]
    probs = [c[6] for c in coeffs]

    # Генерация последовательности шагов заранее (NumPy оптимизация)
    indices = np.random.choice(len(coeffs), size=iterations, p=probs)
    
    # Массив для хранения координат
    points = np.zeros((iterations, 2))
    current_point = np.array([0.0, 0.0])

    for i in range(iterations):
        idx = indices[i]
        current_point = matrices[idx] @ current_point + offsets[idx]
        points[i] = current_point

    # Проекция координат на сетку пикселей
    # Границы папоротника: x ~ (-2.18, 2.65), y ~ (0, 9.99)
    x, y = points[:, 0], points[:, 1]
    
    x_img = ((x + 2.182) / (2.656 + 2.182) * (width - 1)).astype(int)
    y_img = ((10.0 - y) / 10.0 * (height - 1)).astype(int)

    # Создание маски (img_data)
    img_data = np.zeros((height, width), dtype=float)
    
    # Оставляем только точки внутри холста
    valid = (x_img >= 0) & (x_img < width) & (y_img >= 0) & (y_img < height)
    img_data[y_img[valid], x_img[valid]] = 1.0

    return img_data

# Настройки
width, height = 1024, 1024
fname = "barnsley_fern.png"

# Генерация данных
img_data = generate_barnsley_fern(width, height)

# Ваш блок сохранения
arr_uint8 = (img_data * 255.0).astype(np.uint8)
if not os.path.exists("./stl"): os.makedirs("./stl")
Image.fromarray(arr_uint8).save(f"./stl/{fname}")

print(f"Готово! Файл сохранен в ./stl/{fname}")
