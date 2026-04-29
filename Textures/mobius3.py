import numpy as np
import math
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter, zoom

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def qu(U):
    dx = 2/(U.shape[0]-1)
    #dy = 2/(U.shape[1]-1)
    gx, gy = np.gradient(np.abs(U), dx)
    grd = np.sqrt(gx**2 + gy**2)
    lines = U.real * 2
    lines2 = U.imag * 2
    
    cells = np.floor(lines) 
    cells2 = np.floor(lines2)
    lines = lines - cells
    lines2 = lines2 - cells2
    
    #sign = np.mod(cells + cells2, 2) * 2 - 1
    sign = np.mod(cells2, 2) * 2 - 1
    hh = 0.003*grd
    vsm = smoothstep(0., hh, lines) * (1 - smoothstep(1.-hh, 1., lines))
    hsm = smoothstep(0., hh, lines2) * (1 - smoothstep(1.-hh, 1., lines2))
    r = 1
    #r *= vsm
    r *= hsm
    r = r * sign*0.5 + 0.5
    
    
    #r = np.where(U.real < 0, 1.0 - r, r) 
    #r = np.where(np.mod(np.floor(U.real * 0.5), 2) == 0, 1.0 - r, r)
    #r = np.where(np.angle(U) > 0, 1.0 - r, r)
    res = np.stack([r, r, r], axis=-1)
    return res

def readimage():
    #filepath = './stl/grid2.png'
    #so = Image.open(filepath).convert("RGB")
    #soa = np.array(so)
    #res_v, res_u, _  = soa.shape


    res = 1024
    u = np.linspace(-1, 1, res)
    v = np.linspace(-1, 1, res)
    u, v = np.meshgrid(u, v)
    U = np.stack([u, v], axis=-1)
    U = u + 1j*v

    #U = 1 / (U + 1e-9)
    U = np.log((U - 0.5) / (U + 0.5))
    #U = U * (1.511 + 3j/math.pi)  #+
    U = U * (1.114 + 4j/math.pi)
    
    result = qu(U)


    # 1. Слегка размываем (sigma зависит от того, во сколько раз уменьшаем)
    # Для уменьшения в 2 раза sigma=0.5 — 1.0 будет достаточно
    #blurred = gaussian_filter(result, sigma=(1, 1, 0)) 
    # 2. Уменьшаем
    #final_image = zoom(blurred, (0.5, 0.5, 1), order=3)
    
    
    final_image = result
    arr_uint8 = (final_image * 255).astype(np.uint8)
    img = Image.fromarray(arr_uint8)
    img.save("./stl/tex23_lm.png")
    
    
    print("ok")


readimage()    