import numpy as np
import math
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter, zoom




def readimage():
    filepath = './stl/tex1.jpg'
    so = Image.open(filepath).convert("RGB")
    texture = np.array(so)
    h, w, _  = texture.shape


    res = 1024
    u = np.linspace(-1, 1, res)
    v = np.linspace(-1, 1, res)
    u, v = np.meshgrid(u, v)
    U = np.stack([u, v], axis=-1)
    U = u + 1j*v

    #U = 1 / (U + 1e-9)
    #U = np.log(U)
    U = np.log((U - 0.5) / (U + 0.5))
    U = 2 * U * (1 + 6j/math.tau)
    
    U.real -= np.floor(U.real)
    U.imag -= np.floor(U.imag)


    coords_y = U.imag * (h - 1)
    coords_x = U.real * (w - 1)

    # 3. Сборка в стек для scipy
    coords = np.array([coords_y.ravel(), coords_x.ravel()])

    # 4. Интерполяция
    if texture.ndim == 3:
        channels = []
        for i in range(texture.shape[2]):
            ch = map_coordinates(texture[..., i], coords, order=3, mode='wrap')
            channels.append(ch.reshape(U.shape))
        result = np.stack(channels, axis=-1)
    else:
        result = map_coordinates(texture, coords, order=3, mode='wrap').reshape(U.shape)



    # 1. Слегка размываем (sigma зависит от того, во сколько раз уменьшаем)
    # Для уменьшения в 2 раза sigma=0.5 — 1.0 будет достаточно
    blurred = gaussian_filter(result, sigma=(1, 1, 0)) 

    # 2. Уменьшаем
    final_image = zoom(blurred, (0.5, 0.5, 1), order=3)




    img = Image.fromarray(final_image)
    img.save("./stl/tex5_lm.png")

    
    
    
    print("ok")


readimage()    