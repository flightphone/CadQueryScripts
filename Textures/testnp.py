import numpy as np

res_v = 3
res_u = 5
y_grid, x_grid = np.mgrid[0:4:complex(res_v), 0:1:complex(res_u)]
coords = np.stack([x_grid, y_grid], axis=-1)
print(coords)
print (x_grid)
print(y_grid)


u = np.linspace(0, 1, res_u)
v = np.linspace(0, 4, res_v)
U, V = np.meshgrid(u, v)

#print(V)
#print(U)