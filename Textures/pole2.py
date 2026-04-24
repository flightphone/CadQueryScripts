import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

# --- Настройки ---
RES = 1024
POINTS = np.array([[0.0, 0.5], [0.0, -0.5], [-0.3, 0], [0.3, 0]]) 
SIGNS = np.array([1, -1, 1, -1])

def FF(p):
    """ Потенциал для физики (без логов) """
    res = np.zeros(p.shape[:-1])
    for a, s in zip(POINTS, SIGNS):
        dist = np.linalg.norm(p - a, axis=-1)
        res += s / (dist + 1e-9)
    return res

def get_gradient(p):
    """ Аналитический градиент для точности RK4 """
    grad = np.zeros_like(p)
    for a, s in zip(POINTS, SIGNS):
        diff = p - a
        d2 = np.sum(diff**2) + 1e-9
        grad -= s * diff / (d2**1.5)
    return grad

def trace_field_line(start_p, dt=0.01, steps=2000):
    """ Трассировка одной линии методом RK4 """
    path = [start_p]
    curr = np.array(start_p)
    for _ in range(steps):
        # RK4 шаг
        k1 = get_gradient(curr)
        k1 /= (np.linalg.norm(k1) + 1e-10)
        
        k2 = get_gradient(curr + k1 * dt / 2)
        k2 /= (np.linalg.norm(k2) + 1e-10)
        
        k3 = get_gradient(curr + k2 * dt / 2)
        k3 /= (np.linalg.norm(k3) + 1e-10)
        
        k4 = get_gradient(curr + k3 * dt)
        k4 /= (np.linalg.norm(k4) + 1e-10)
        
        curr = curr + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        path.append(curr.copy())
        if np.linalg.norm(curr) > 2.5: break # Выход за границы
    return np.array(path)

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def generate_scene():
    # 1. Сетка координат
    y, x = np.mgrid[1:-1:complex(RES), -1:1:complex(RES)]
    coords = np.stack([x, y], axis=-1)
    
    # 2. Генерируем пучок линий
    all_path_points = []
    num_lines = 2
    radius = 0.05
    
    print("Трассировка линий...")
    for i, s in enumerate(SIGNS):
        if s > 0: # Выпускаем линии из положительных зарядов
            for angle in np.linspace(0, 2*np.pi, num_lines, endpoint=False):
                start = POINTS[i] + np.array([np.cos(angle), np.sin(angle)]) * radius
                line = trace_field_line(start)
                all_path_points.extend(line)
    
    # 3. Считаем расстояния через KD-Tree
    print("Построение дерева расстояний...")
    tree = cKDTree(all_path_points)
    flat_coords = coords.reshape(-1, 2)
    dists, _ = tree.query(flat_coords)
    dists = dists.reshape(RES, RES)
    
    # 4. Отрисовка потенциала (красный)
    field = FF(coords)
    field_viz = np.sign(field) * np.log(1 + np.abs(field)) * 6
    # Модуль градиента для толщины линий потенциала
    gy, gx = np.gradient(field_viz, 2.0/RES)
    grd = np.sqrt(gx**2 + gy**2)
    
    mask_poten = smoothstep(0.005 * grd, 0, np.abs(field_viz - np.floor(field_viz) - 0.5))
    
    # 5. Отрисовка силовых линий (синий)
    mask_lines = smoothstep(0.01, 0, dists)
    
    # 6. Композиция
    img = np.ones((RES, RES, 3))
    # Красные линии потенциала
    img = img * (1 - mask_poten[..., None]) + mask_poten[..., None] * np.array([1, 0.4, 0.4])
    # Синие силовые линии поверх
    img = img * (1 - mask_lines[..., None]) + mask_lines[..., None] * np.array([0.2, 0.2, 1.0])
    
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)

# Запуск
print("Начало генерации...")
final_image = generate_scene()
Image.fromarray(final_image).save("./stl/perfect_field.png")
print("Готово! Файл perfect_field.png сохранен.")
