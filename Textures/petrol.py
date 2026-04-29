import numpy as np
import math
import random
from PIL import Image

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a*(1-t) + b*t

def hash(p):
    res = 10000 * np.sin(117*p.real + 0.1*p.imag) * (0.1 + np.abs(np.sin(p.imag*133 + p.real)))
    res = res - np.floor(res)
    return res


def noise(x):
    i = np.floor(x.real) + 1j*np.floor(x.imag)
    fr = x - i
    f = np.stack([fr.real, fr.imag], axis = -1)
    a = hash(i)
    b = hash(i + 1)
    c = hash(i + 1j)
    d = hash(i + 1 + 1j)
    u = f*f *(3.0 - 2.0*f)
    ux = u[..., 0]
    uy = u[..., 1]
    res = mix(a, b, ux) + (c - a) * uy * (1.0 - ux) + (d - b) * ux * uy
    return res

def readimage():
    
    res = 1024
    scale = 1
    u = np.linspace(-scale, scale, res)
    v = np.linspace(-scale, scale, res)
    dx = 2*scale/(res-1)
    u, v = np.meshgrid(u, v)
    U = np.stack([u, v], axis=-1)
    U = u + 1j*v

    colors = (np.array([
        [1., 0.5, 0.5], [0.5, 1., 0.5], [0.5, 0.5, 1.], [1., 1., 0.5], [1., 0.5, 1.], [0.5, 1., 1.],
    ]))
    ncolors = colors.shape[0]

    n = 4
    n3 = 2
    n2 = 5
    x = U + random.random()*100
    shift = 0.1 + 0.2j
    rot = np.exp(0.5j)
    x = x*rot + shift
    t = 1.8*noise(x*n3)
    x = x*rot + shift
    t += 0.5*noise(x*n2)

    y = U.imag
    y += t
    y *= n
    fy = np.floor(y)
    yy = y - fy
    i = np.mod(fy, ncolors).astype(int)
    col = colors[i]
    colline = np.full_like(col, [0, 0, 0])


    gx, gy = np.gradient(y, dx) 
    grad = np.sqrt(gx**2 + gy**2)
    h = 0.002 * grad * scale
    eps = h
    s1 = smoothstep(1. - h-eps, 1-h, yy)  	
    s2 = (1 - smoothstep(h, h+eps, yy))
    col = mix(col, colline, s1[..., None])
    col = mix(col, colline, s2[..., None])
    
    final_image = col
    
    arr_uint8 = (final_image * 255).astype(np.uint8)
    img = Image.fromarray(arr_uint8)
    img.save("./stl/petrol.png")
    
    print("ok")


readimage()    