import cadquery as cq
from ocp_vscode import show
import math
import numpy as np

def fnsteam(x):
    return 0.8*x*x

def inverse_fnsteam(y):
    return math.sqrt(y/0.8)



def fn_r8(r):
    a = math.tan(math.pi/8)
    x = a*r/(1 + a)
    r8 = math.sqrt(x*x + (r-x)*(r-x))
    return r8
    

def wine2():
    r0 = 0.9  #diameter at the thinnest part of the leg
    h0 = 3.5    #height of the thinnest part of the leg  
    r1 = r0 + fnsteam(h0) - 1.5  #We calculate the diameter of the base of the leg
    r2 = 0.45*r1 #diameter of the ball at the middle of the leg
    h2 = 1.6*r2     #height of the prism for the ball in the middle

    r8 = fn_r8(r2/2)  #We calculate the smaller radius in an eight-pointed star
    r8a = r8/math.cos(math.pi/8) 

    h8 = h0 - inverse_fnsteam(2*r8a - r0)
    r2a = r2/2 * math.cos(math.pi/8)
    h28 = h2 - h2*r8/r2a  #We calculate the sharpening cross-section for the eight-pointed star in the middle  = h28 - h8


    h3 = h0 - (h8 - h28)  

    rbox = 2*fnsteam(h0) + 2

    h9 = 1.0 * (h0 - h8) #height of the upper section of the leg
    r9 = fnsteam(h9) + r0 #
    w9 = 0.3

    bowl_h = 1.2*h0
    bowl_r1 = 1.7*r1/2
    bowl_r2 = bowl_r1 * 0.3
    
    bowl_w = 0.2

    
    # ellipsoid
    bowl = cq.Workplane("XZ").ellipseArc(bowl_r1, bowl_r2, 90, 270).close().revolve()
    bowl = (cq.Workplane("XY").cylinder(bowl_h, bowl_r1, centered=(True, True, False))
            .add(bowl.translate((0, 0, bowl_r2)).val())
    )
    bowl_cut = (cq.Workplane("XY").cylinder(bowl_h, bowl_r1-bowl_w, centered=(True, True, False))
    )
    bowl = bowl.cut(bowl_cut)
    bowl = bowl.edges(">Z").fillet(bowl_w/3)
    bowl = bowl.translate((0, 0, h0 + 2*h3 + h9 + bowl_r2 + w9))

    

    n = 20  



    sp = cq.Workplane("XY").polygon(4, r2).extrude(h2)
    sp = sp.union(sp.rotate((0, 0, 0), (0, 0, 1), 45))

    sharpener0 = cq.Workplane("XY").polygon(8, r2).workplane(offset=h2).polygon(8, 0.01).loft()
    sharpener0 = cq.Workplane("XY").box(r2 + 0.5, r2 + 0.5, h2, centered=(True, True, False)).cut(sharpener0)
    sp = sp.cut(sharpener0)
    
    #show(sp)
    
    stem = cq.Workplane("XY")
    for i in range (n+1):
        x = i/n * h0
        r = r0 + fnsteam(x)
        z = h0 - x
        stem.workplane(offset=z).polygon(8, r)

    stem = stem.loft()   
    sharpener1 = cq.Workplane("XY").box(rbox, rbox, 3*h0, centered=(True, True, True)).faces(">Z").workplane().hole(r1)
    stem_bot = stem.cut(sharpener1)

    sharpener1 = cq.Workplane("XY").box(rbox, rbox, 3*h0, centered=(True, True, True)).faces(">Z").workplane().hole(r9)
    stem_top = stem.cut(sharpener1)
    sharpener1 = cq.Workplane("XY").box(rbox, rbox, h0, centered=(True, True, False)).translate((0, 0, -h3-w9))
    stem_top = stem_top.cut(sharpener1)
    stem_top = stem_top.translate((0, 0, -h0)).rotate((0, 0, 0), (0, 1, 0), 180).translate((0, 0, h0 + 2*h3))

    
    sharpener2 = cq.Workplane("XY").box(rbox/2, rbox/2, 3*h0, centered=(True, True, False)).cut(stem)
    sharpener2 = sharpener2.translate((0, 0, h28 - h8))
    sp = sp.cut(sharpener2)
    
    #calculate bevel
    a = np.array([r2/2, 0, 0])
    b = np.array([r8 * math.cos(math.pi/8), r8 * math.sin(math.pi/8), h28])
    c = np.array([r8 * math.cos(math.pi/8), -r8 * math.sin(math.pi/8), h28])
    v1 = b - a
    v2 = c - a
    norm = np.cross(v1, v2)
    norm = norm/np.linalg.norm(norm)
    m = (a + b + c)/3
    d = np.linalg.norm(v1+v2)
    pl = cq.Plane(origin=(m[0], m[1], m[2]), normal = (norm[0], norm[1], norm[2]))
    sharpener40 = cq.Workplane(pl).box(d, d, d, centered=(True, True, False))
    for i in range(8):
        ct = sharpener40.rotate((0, 0, 0), (0, 0, 1), i*45)
        sp = sp.cut(ct)

    sp = sp.union(sp.rotate((0, 0, 0), (0, 1, 0), 180))#.edges("|Z").fillet(0.01*r2)



    sp = sp.translate((0, 0, h0 + h3))
    comp = cq.Compound.makeCompound([sp.val(), stem_bot.val(), stem_top.val(), bowl.val()])
    #comp = cq.Compound.makeCompound([sp.val()])
    ass = cq.Assembly()
    ass.add(comp)
    return ass
    



    


ass = wine2()
ass.save("./stl/wine2.glb")
show(ass)