import numpy as np
import math
from PIL import Image


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a*(1-t) + b*t

def el(p):
    a = 0.6
    b = 0.3
    return (p[:, :, 0] * p[:, :, 0] / a / a + p[:, :, 1] * p[:, :, 1]/b/b - 1)

def grd_el(p):
    a = 0.6
    b = 0.3
    grd = np.stack([2*p[:, :, 0]/a/a, 2*p[:, :, 1]/b/b], axis=-1)  
    return np.sqrt(np.sum(grd**2, axis=-1))


def hsin(p):
    scale = 3*math.tau
    return np.sin(p[:, :, 0] * scale)*0.1 - p[:, :, 1]

def grd_hsin(p):
    scale = 3*math.tau
    grd = np.stack([scale * np.cos(p[:, :, 0] * scale)*0.1, np.full((p.shape[0], p.shape[1]), -1)], axis=-1)  
    return np.sqrt(np.sum(grd**2, axis=-1))

def grd_fun(p, fn):
    eps = 0.00001
    x = (fn(p + np.array([eps, 0])) - fn(p - np.array([eps, 0])))/2/eps
    y = (fn(p + np.array([0, eps])) - fn(p - np.array([0, eps])))/2/eps
    grd = np.stack([x, y], axis=-1)  
    return np.sqrt(np.sum(grd**2, axis=-1))

def x2(p):
    x = p[:, :, 0]
    y = p[:, :, 1]
    return np.pow(x, 3) - y

def astroid(p):
    #https://www.mathcurve.com/courbes2d.gb/astroid/astroid.shtml
    a = 0.7
    x = p[:, :, 0]
    y = p[:, :, 1]
    return  np.pow(x*x + y*y - a*a, 3) + 27*a*a*x*x*y*y

def generate_map(res=1024):
    
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1) # shape (res, res, 2)
    
    final_col_np = np.full((res, res, 3), fill_value = [0, 0, 0], dtype=np.uint8)
    color = np.array([0.7, 0.7, 1.0])
    d = 0.005
    #mask = smoothstep(d*grd_el(coords), 0, np.abs(el(coords)))
    #grd = grd_fun(coords, hsin) #grd_hsin(coords) #
    #mask = smoothstep(d*grd, 0, np.abs(hsin(coords)))
    grd = grd_fun(coords, x2)
    mask = smoothstep(d*grd, 0, np.abs(x2(coords)))
    
    final_col_np = mix(final_col_np, color, mask[..., None])
    return final_col_np

# render

res = 1024



print("generation texture...")
img_data =  generate_map(res=res)

fname = "cubic.png"
print(f"save {fname}...")
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8).save(f"./stl/{fname}")
print("successfuly")