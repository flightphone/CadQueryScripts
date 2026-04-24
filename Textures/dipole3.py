import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct

def reconstruct_potential_dct(df_dx, df_dy, size, dx):
    """Восстановление поля через DCT (решение уравнения Пуассона)"""
    # 1. Вычисляем дивергенцию градиента
    d2f_dx2 = np.gradient(df_dx, dx, axis=1)
    d2f_dy2 = np.gradient(df_dy, dx, axis=0)
    laplacian = d2f_dx2 + d2f_dy2
    
    # 2. Дискретное косинусное преобразование
    f_dct = dct(dct(laplacian, axis=0, type=2), axis=1, type=2)
    
    # 3. Знаменатель (собственные числа дискретного оператора Лапласа)
    nx = np.arange(size).reshape(1, -1)
    ny = np.arange(size).reshape(-1, 1)
    
    # Формула собственных чисел для DCT-II
    denom = (2 * np.cos(np.pi * nx / size) - 2) / dx**2 + \
            (2 * np.cos(np.pi * ny / size) - 2) / dx**2
    
    denom[0, 0] = 1.0  # избегаем деления на 0
    f_dct_solved = f_dct / denom
    f_dct_solved[0, 0] = 0 # зануляем среднее значение (константу)
    
    # 4. Обратное DCT
    res = idct(idct(f_dct_solved, axis=1, type=3), axis=0, type=3)
    
    # Масштабирование idct (в scipy idct(type 3) требует деления на 2N)
    return res / (4 * size**2)

# --- Настройка примера ---
size = 512 # уменьшим для скорости отрисовки
coords = np.linspace(-1, 1, size)
dx = coords[1] - coords[0]
X, Y = np.meshgrid(coords, coords)

# Аналитические производные для двух зарядов (+1 в (0.3, 0.3) и -1 в (-0.3, -0.3))
def get_grad(x, y):
    def charge_grad(qx, qy, sign):
        r_sq = (x - qx)**2 + (y - qy)**2 + 1e-6
        return sign * (x - qx) / r_sq**1.5, sign * (y - qy) / r_sq**1.5
    
    gx1, gy1 = charge_grad(0.3, 0.3, 1)
    gx2, gy2 = charge_grad(-0.3, -0.3, -1)
    return gx1 + gx2, gy1 + gy2

df_dx, df_dy = get_grad(X, Y)

# Восстановление
F_rec = reconstruct_potential_dct(df_dx, df_dy, size, dx)

# --- Визуализация ---
plt.figure(figsize=(14, 6))

# Поле градиентов (силовые линии)
plt.subplot(1, 2, 1)
skip = 32 # пропуск для читаемости стрелок
plt.quiver(X[::skip, ::skip], Y[::skip, ::skip], df_dx[::skip, ::skip], df_dy[::skip, ::skip], 
           color='blue', alpha=0.6)
plt.title("Входные данные: Векторное поле grad(F)")
plt.xlabel("x")
plt.ylabel("y")

# Восстановленный потенциал
plt.subplot(1, 2, 2)
cp = plt.contourf(X, Y, F_rec, levels=50, cmap='RdBu_r')
plt.colorbar(cp, label='Потенциал F')
plt.contour(X, Y, F_rec, levels=20, colors='black', alpha=0.3) # изолинии
plt.title("Результат: Восстановленное поле F")
plt.xlabel("x")

plt.tight_layout()
plt.show()
