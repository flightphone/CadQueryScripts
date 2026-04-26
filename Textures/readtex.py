import numpy as np
import math
from PIL import Image



def readimage():
    filepath = './stl/tex1.jpg'
    so = Image.open(filepath).convert("RGB")
    soa = np.array(so)
    res_v, res_u, _  = soa.shape


    res = 1014
    u = np.linspace(-1, 1, res_u)
    v = np.linspace(-1, 1, res_v)
    u, v = np.meshgrid(u, v)
    U = np.stack([u, v], axis=-1)
    


    # 1. Moebius transform (аналог U = (U+U - z) / z.y уже сделан в linspace -1..1)
    # Смещение и инверсия
    z = U - np.array([-1.0, 0.0])
    U_shifted = U - np.array([0.5, 0.0])

    # Реализация матричного умножения mat2(z,-z.y,z.x) через комплексные числа или вручную:
    denom = np.sum(U_shifted**2, axis=-1, keepdims=True)
    # Чтобы избежать деления на ноль:
    denom[denom == 0] = 1e-6

    # Применяем матрицу [ [z.x, -z.y], [z.y, z.x] ]
    new_ux = (U_shifted[..., 0] * z[..., 0] - U_shifted[..., 1] * z[..., 1]) / denom[..., 0]
    new_uy = (U_shifted[..., 0] * z[..., 1] + U_shifted[..., 1] * z[..., 0]) / denom[..., 0]
    U = np.stack([new_ux, new_uy], axis=-1)
    #R = np.array([ [z[..., 0], -z[..., 1]], [z[..., 1], z[..., 0]] ])
    #U = (U_shifted @ R) / denom[..., 0]

    # 2. Spiraling (Log-polar mapping)
    U += 0.5
    r = np.sqrt(np.sum(U**2, axis=-1))
    theta = np.arctan2(U[..., 1], U[..., 0])

    # iTime можно заменить на константу или переменную цикла
    iTime = 5

    # Собираем финальные координаты
    U_final = np.zeros_like(U)
    # Log-spiral часть
    U_final[..., 0] = np.log(r + 1e-6) * 0.5 + iTime/8.0 + (theta / 6.3) * 5.0
    U_final[..., 1] = np.log(r + 1e-6) * -0.5 + iTime/8.0 + (theta / 6.3) * 1.0

    # 3. Тайлинг (fract)
    U = U_final * 3.0
    U = U - np.floor(U)

    
    ures = (U[..., 0] *(res_u - 1)).astype(int)
    vres = (U[..., 1]* (res_v - 1)).astype(int)

    res_image = soa[vres, ures]
    res_image[..., 2] = 0
    res_image[..., 0] = 0
    img = Image.fromarray(res_image)
    img.save("./stl/tex1_lm.png")
    
    #p = np.stack([u, v], axis=-1)
    print("ok")


readimage()    