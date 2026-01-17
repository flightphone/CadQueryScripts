import cadquery as cq
import math
from ocp_vscode import show

shift = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

def line_edge(a = (0, 0, 0), b = (1, 1, 1), w = 0.5):
    norm = (b[0]-a[0], b[1]- a[1], b[2]-a[2])
    l = math.sqrt(norm[0]*norm[0] + norm[1]*norm[1] + norm[2]*norm[2])
    pl = cq.Plane(origin=a, normal= norm)
    res = cq.Workplane(pl).box(w, w, l, centered=(True, True, False)).val()
    return res


def make_ver2(a):
    res = []
    for e in shift:
        res.append((a[0]*e[0], a[1]*e[1], a[2]))
    return res

def make_ver(a, b):
    res = []
    fase1 = make_ver2(a)
    for e in fase1:
        res.append(e)
    fase2 = make_ver2(b)    
    for e in fase2:
        res.append(e)    
    return res   

def union_lines(lines):
    wp = cq.Workplane("XY")
    for e in lines:
        wp = wp.union(e)
    return wp.val()        


def rect_edge(a, d):
    fase = make_ver2(a)
    lines = []
    for i in range(4):
        a = fase[i]
        b = fase[(i+1)%4]
        res = line_edge(a, b, d)
        lines.append(res)

    return union_lines(lines)


def vert_edge(a, b, d):
    prism1 = make_ver(a, b)
    lines = []
    for i in range(4):
        a0 = prism1[i]
        b0 = prism1[i+4]    
        res = line_edge(a0, b0, d)
        lines.append(res)

    return union_lines(lines)

def corner_edge(a, b, d):
    prism1 = make_ver(a, b)
    lines = []
    
    for i in range(4, 8):
        a0 = prism1[i]
        b0 = prism1[(i-1) % 4] 
        b1 = prism1[(i+1) % 4]    
        res = line_edge(a0, b0, d)
        lines.append(res)
        res2 = line_edge(a0, b1, d)
        lines.append(res2)

    return union_lines(lines)

def voltage(a, b, w, d):
    a0 = (w, a[1], a[2])
    b0 = (-w, a[1], a[2])
    vers = [a0, b0]
    points = make_ver(a, b)
    links = [0, 3, 4, 7, 1, 2, 5, 6]
    lines = []
    for i in range(2):
        for j in range(4):
            n = i*4 + j
            n = links[n]
            e = line_edge(vers[i], points[n], d)
            lines.append(e)

    return union_lines(lines)        



def hight_vol():
    d = 0.3
    w0 = 6.616   #bottom width
    h2 = 18.5    #height prism
    w2 = 1.5     #top width
    h3 = h2 + 8  #height second section
    
    res = []
    v0 = (w0/2, w0/2, 0)
    v2 = (w2/2, w2/2, h2)
    v3 = (w2/2, w2/2, h3)
    e = vert_edge(v0, v2, d)
    res.append(e)

    e = vert_edge(v2, v3, d)
    res.append(e) 

    
    n = 8
    dh = (h3 - h2)/n
    for i in range(n):
        a0 = (w2/2, w2/2, h2 + i*dh)           
        b0 = (w2/2, w2/2, h2 + (i+1)*dh)
        e = corner_edge(b0, a0, d/2)
        res.append(e)

    r1 = rect_edge(v2, d)
    res.append(r1)

    r2 = rect_edge(v3, d)
    res.append(r2)
    
    ctga = (w0 - w2)/h2/2
    h22 = w0/2/ctga
    L = 4.3  #height first horizontal edge
    #quadratic equation for calculate hx - height first corner intersect
    A = 4 * ctga
    B = - (3 * w0 + 2 * L * ctga)
    C = 2 * L * w0
    D = math.sqrt(B*B - 4*A*C)
    hx = (-B - D)/2/A
    
    #hx = 3
    #L = (w0 - 2*ctga*hx) * hx / (w0 - ctga*hx) / 2  + hx  #for reverse calculate L by hx

    
    el = rect_edge(((w0 - 2*L*ctga)/2, (w0 - 2*L*ctga)/2, L), d)
    res.append(el)

    hsum = 0
    for i in range(5):
        hd = hx* (h22 - hsum)/h22
        a0 = ((w0 - 2*hsum*ctga)/2, (w0 - 2*hsum*ctga)/2, hsum) 
        hsum = hsum + hd
        b0 = ((w0 - 2*hsum*ctga)/2, (w0 - 2*hsum*ctga)/2, hsum) 
        e = corner_edge(a0, b0, d/2)
        res.append(e)
        if i == 2:
            e1 = rect_edge(b0, d)
            res.append(e1)

   
    hshift = hsum 
    hx = 3
    for _ in range(3):
        hd = hx* (h22 - hsum)/(h22 - hshift)
        a0 = ((w0 - 2*hsum*ctga)/2, (w0 - 2*hsum*ctga)/2, hsum) 
        hsum = hsum + hd
        b0 = ((w0 - 2*hsum*ctga)/2, (w0 - 2*hsum*ctga)/2, hsum) 
        e = corner_edge(a0, b0, d/2)
        res.append(e)
   
    #voltage
    a0 = (w2/2, w2/2, h2 + dh)           
    b0 = (w2/2, w2/2, h2 + 2*dh)
    vwidth = 2.1
    v1 = voltage(a0, b0, vwidth, d/2)
    res.append(v1)

    a0 = (w2/2, w2/2, h2 + 4*dh)           
    b0 = (w2/2, w2/2, h2 + 5*dh)
    vwidth = 2.8
    v2 = voltage(a0, b0, vwidth, d/2)
    res.append(v2)

    a0 = (w2/2, w2/2, h2 + 7*dh)           
    b0 = (w2/2, w2/2, h2 + 8*dh)
    vwidth = 2.1
    v3 = voltage(a0, b0, vwidth, d/2)
    res.append(v3)


    return res



res = hight_vol()    
assembly = cq.Assembly()
for i, shard in enumerate(res):
    assembly.add(shard, name=f"shard_{i}")
assembly.export("./stl/voltage_support.glb")
show(assembly)