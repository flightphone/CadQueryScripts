import numpy as np
import math
from PIL import Image


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def mix(a, b, t):
    return a*(1-t) + b*t

def length(p):
     return np.sqrt(np.sum(p**2, axis=-1))


def FF(p):
    a = np.array([0.0, 0.5]) 
    l1 = length(p-a)
    l2 = length(p+a)
    res = np.abs(np.pow(l1, -1) - np.pow(l2, -1))
    res = np.log((1. +  res))
    return res * 8   
    
def EE(p):
    a = np.array([0.0, 0.5]) 
    l1 = length(p-a)
    l2 = length(p+a)

    n1 = (p-a)[:,:,1]/l1
    n2 = (p+a)[:,:,1]/l2
    return (n1 - n2)*10


def grd_fun(p, fn):
    eps = 0.00001
    x = (fn(p + np.array([eps, 0])) - fn(p - np.array([eps, 0])))/2/eps
    y = (fn(p + np.array([0, eps])) - fn(p - np.array([0, eps])))/2/eps
    grd = np.stack([x, y], axis=-1)  
    return np.sqrt(np.sum(grd**2, axis=-1))



def generate_map(res=1024):
    
    y_grid, x_grid = np.mgrid[1:-1:complex(res), -1:1:complex(res)]
    coords = np.stack([x_grid, y_grid], axis=-1) # shape (res, res, 2)
    
    final_col_np = np.full((res, res, 3), fill_value = [1, 1, 1], dtype=np.uint8)
    d = 0.004
    grd1 = grd_fun(coords, FF)
    field = FF(coords)
    mask1 = smoothstep(d*grd1, 0, np.abs(field - np.floor(field) - 0.5))
    col1 = mix(final_col_np, np.array([1, 0, 0]), mask1[..., None])
    
    
    grd2 = grd_fun(coords, EE)
    line = EE(coords)
    mask2 = smoothstep(d*grd2, 0, np.abs(line - np.floor(line) - 0.5))
    col2 = mix(final_col_np, np.array([0, 0, 1]), mask2[..., None])

    final_col_np = mix(col1, col2, 0.5)
    return final_col_np

# render

res = 1024



print("generation texture...")
img_data =  generate_map(res=res)

fname = "dipole.png"
print(f"save {fname}...")
arr_uint8 = (img_data * 255.0).astype(np.uint8)
Image.fromarray(arr_uint8).save(f"./stl/{fname}")
print("successfuly")