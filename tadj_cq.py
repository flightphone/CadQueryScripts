import cadquery as cq
import math

#https://cadquery.readthedocs.io/en/latest/_static/cadquery_cheatsheet.html

baseh = 0.532
basew0 = 0.98
basew1 = 0.234
nboth = 1.3

def pyramid(n, r, h):
    a = math.pi*2/n
    r2 = r*0.01
    points = [(r*math.cos(-a/2 + t*a), r*math.sin(-a/2 + t*a), 0) for t in range(n+1)]
    points2 = [(r2*math.cos(-a/2 + t*a), r2*math.sin(-a/2 + t*a), 0) for t in range(n+1)]
    return cq.Workplane("XY").polyline(points).close().workplane(offset=h).polyline(points2).close().loft(combine=True)
    
def prism (n, r, h):
    a = math.pi*2/n
    r2 = r*0.01
    points = [(r*math.cos(-a/2 + t*a), r*math.sin(-a/2 + t*a), 0) for t in range(n+1)]
    return cq.Workplane("XY").polyline(points).close().extrude(h)


def arc(w, h, l):
    cy = cq.Workplane("YZ").cylinder(l, w).translate((l/2, 0, h))
    box = cq.Workplane("XY").box(l, w*2, h).translate((l/2, 0, h/2))
    res = cy.union(box)
    return res



def tadj_onion(r1, al):
    cone_solid = cq.Solid.makeCone(r1*math.cos(al), 0, r1/math.cos(math.pi/2 - al) - r1*math.sin(al))
    cone_solid = cone_solid.translate((0, 0, r1*math.sin(al)))
    res = cq.Workplane("XY").sphere(r1).add(cone_solid)
    return res

def tadj_cyl(w1, h1):
    r1 = w1/2
    al = 67/180*math.pi
    #res = Part.makeCylinder(r1, h1)
    res = cq.Workplane("XY").cylinder(h1, r1).translate((0, 0, h1 /2.))
    sp = tadj_onion(r1, al)
    sp = sp.translate((0, 0, h1))
    res = res.union(sp)
    return res

def tadj_face(boxw, fw0, fw1, r2):
    w1 = 0.315
    h1 = 0.306
    dx = fw0/2 -fw1/2

    w2 = 0.132
    h2 = 0.125
    pz = 0.248
    
    w22 = 0.045
    arc0 = tadj_cyl(w1, h1)
    arc0 = arc0.translate((0, boxw/2 + w22/2, 0)) 
    
    arc1 = tadj_cyl(w2, h2)
    arc1 = arc1.translate((dx, boxw/2, pz))
    arc2 = tadj_cyl(w2, h2)
    arc2 = arc2.translate((dx, boxw/2, 0))

    arc3 = tadj_cyl(w2, h2)
    arc3 = arc3.translate((-dx, boxw/2, pz))
    arc4 = tadj_cyl(w2, h2)
    arc4 = arc4.translate((-dx, boxw/2, 0))


    arc5 = tadj_cyl(w2, h2)
    arc5 = arc5.translate((0, r2, pz))
    arc5 = arc5.rotate((0, 0, 0), (0, 0, 1), 45)


    arc6 = tadj_cyl(w2, h2)
    arc6 = arc6.translate((0, r2, 0))
    arc6 = arc6.rotate((0, 0, 0), (0, 0, 1), 45)
    
    arcs = [arc1, arc2, arc3, arc4, arc5, arc6]
    res = arc0
    for shape in arcs:
        res = res.union(shape)
    return res

def tadj_minaret1(r, h, k=1):
    n = 8
    a = math.pi*2/n
    l = r*math.sin(a/2)*2 *0.6
    
    pri0 = prism(n, r, h)
    rs = r*math.cos(a/2)*0.98
    al = 53/180*math.pi
    sp = tadj_onion(rs, al)
    sp = sp.translate((0, 0, h))
    pri0 = pri0.union(sp)
    
    '''
    sph = 0.1
    sh = shpil(sph)
    sh.translate(App.Vector(0, 0, h + rs/math.cos(math.pi/2 - al)))
    pri0 = pri0.fuse(sh)
    '''

    r1 = 0.85*r
    h1 = 0.75*h

    r2 = 0.97*r
    h2 = 0.25*h

    pri1 = prism(n, r1, h1)
    res = pri0.cut(pri1)

    r5 = r + (h - h1)/2*k
    h5 = (h - h1)/2/(r5-r) * r5 
    pri5 = pyramid(n, r5, h5)
    pri5 = pri5.translate((0, 0, h1))
    res = res.union(pri5)


    
    boxm = cq.Workplane("XY").box(10, l, h1, False).translate((0, -l/2, 0))
    for i in range(n):
        boxm = boxm.rotate((0, 0, 0), (0, 0, 1), a*180/math.pi)
        res = res.cut(boxm)

    pri2 = prism(n, r2, h2)
    pri2 = pri2.cut(pri1)
    
    cy = cq.Workplane("YZ").cylinder(10, l/2)
    for _ in range(n):
        cy = cy.rotate((0, 0, 0), (0, 0, 1), 360/n)
        pri2 = pri2.cut(cy)
    
    pri2 = pri2.translate((0, 0, h*0.5))
    res = res.union(pri2)
    return res

def tadj_minaret5(r, h):
    res = tadj_minaret1(r, h, 2)
    box = cq.Workplane("XY").box(10, 10, h/2, False).translate((-5, -5, 0))
    res = res.cut(box)
    r0 = r/10
    clm = cq.Workplane("XY").cylinder(h/2, r0).translate((r-r0, 0, h/4))
    clm = clm.rotate((0, 0, 0), (0, 0, 1), 22.5)
    n = 8
    for _ in range(8):
        clm = clm.rotate((0, 0, 0), (0, 0, 1), 45)
        res = res.union(clm)
    return res

def tadj_minaret2():
    rp = 0.11
    r = 0.085
    r2 = r/1.5
    h = baseh + 0.25

    con_solid = cq.Solid.makeCone(r, r2, h)
    con = cq.Workplane("XY").add(con_solid)
    #con = Part.makeCone(r, r2, h)
    kh = 9/7
    dd = 0.03
    hh1 = 0.282
    rr1 = ((h-hh1)/h * (r - r2) + r2) * kh
    
    hh2 = 0.552
    rr2 = ((h-hh2)/h * (r - r2) + r2) * kh
    


    #c1 = Part.makeCylinder(rr1, dd, App.Vector(0, 0, hh1-dd))
    c1 = cq.Workplane("XY").cylinder(dd,rr1).translate((0, 0, hh1-dd + dd /2))
    con = con.union(c1)

    #c2 = Part.makeCylinder(rr2, dd, App.Vector(0, 0, hh2-dd))
    c2 = cq.Workplane("XY").cylinder(dd,rr2).translate((0, 0, hh2-dd + dd /2))
    con = con.union(c2)

    #c3 = Part.makeCylinder(r2*kh, dd, App.Vector(0, 0, h-dd))
    c3 = cq.Workplane("XY").cylinder(dd, r2*kh).translate((0, 0, h-dd + dd /2))
    con = con.union(c3)
    
    pri = prism(8, rp, baseh/nboth)
    pri = pri.translate((0, 0, -baseh/nboth))
    con = con.union(pri)
    
    mi = tadj_minaret5(r2, 0.095)
    mi = mi.translate((0, 0, h))
    con = con.union(mi)
    return con            


def tadj_box():
    w0 = basew0
    w1 = basew1
    w2 = 0.045
    h0 = baseh
    h1 = 0.029
    h2 = 0.647
    boxw = w0 + w1*math.sqrt(2)
    #box = Part.makeBox(boxw, boxw, h0, App.Vector(-boxw/2, -boxw/2, 0))
    box = cq.Workplane("XY").box(boxw, boxw, h0, False).translate((-boxw/2, -boxw/2, 0))
    
    r1_2 = w0*w0/4 + boxw*boxw/4
    r2 = math.sqrt(r1_2 - w1*w1/4)
    boxm = cq.Workplane("XY").box(w1, w1, h0, False).translate((-w1/2, r2, 0))
    boxm = boxm.rotate((0, 0, 0), (0, 0, 1), 45)

    
    wp = w0 - 2*w1
    #boxp = Part.makeBox(wp, w2, h2, App.Vector(-wp/2, boxw/2 -  w2/2, 0))        
    boxp = cq.Workplane("XY").box(wp, w2, h2, False).translate((-wp/2, boxw/2 -  w2/2, 0))        
    tfase = tadj_face(boxw, w0, w1, r2)

    for i in range(4):
        box_cut = boxm.rotate((0, 0, 0), (0, 0, 1), i*90)
        box = box.cut(box_cut)
    
    '''
    box2 = make_offset(doc, box, -w2/2, "box")
    box2 = Part.makeCompound([box2])
    box2.translate(App.Vector(0, 0, h0 - w2/2 - h1))    
    box = box.cut(box2)
    '''

    for i in range(4):    
        boxa = boxp.rotate((0, 0, 0), (0, 0, 1), i*90)
        box = box.union(boxa)
    
    
    for i in range(4):        
        tfase_cut = tfase.rotate((0, 0, 0), (0, 0, 1), i*90)
        box = box.cut(tfase_cut)
    

    #boxbot = Part.makeBox(boxw*2, boxw*2, h0/nboth, App.Vector(-boxw, -boxw, -h0/nboth))
    boxbot = cq.Workplane("XY").box(boxw*2, boxw*2, h0/nboth, False).translate((-boxw, -boxw, -h0/nboth))
    box = box.union(boxbot)
    
    
    mi2 = tadj_minaret2()
    mi2 = mi2.translate((boxw, boxw, 0))
    for _ in range(4):    
        mi2 = mi2.rotate((0, 0, 0), (0, 0, 1), 90)
        box = box.union(mi2)

    
    return box    

def tadj_cupol():
    
    h0 = 0.25
    w0 = 0.98
    w1 = 0.234
    rc = (w0 - 2*w1)/2*1.2
    r1 = rc*1.1
    dz = math.sqrt(r1*r1 - rc*rc)
    h1 = baseh + h0 + dz
    al = 53/180*math.pi
    sp = tadj_onion(r1, al)
    sp = sp.translate((0, 0, h1))
    res = cq.Workplane("XY").cylinder(h0, rc).translate((0, 0, baseh + h0/2)) 
    res = res.union(sp)

    #sph = 0.173
    #sh = shpil(sph)
    #sh.translate(App.Vector(0, 0, h1 + r1/math.cos(math.pi/2 - al)))
    #res = res.fuse(sh)
    return res

def tadj():
    h1 = 0.029
    box = tadj_box()

    cupol = tadj_cupol()
    cupol = cupol.translate((0, 0, -h1))
    res = box.union(cupol)
    
    boxw = (basew0 + basew1*math.sqrt(2))*1.2
    rm = 0.14
    hm = 0.2
    m1 = tadj_minaret1(rm, hm)
    m1 = m1.translate((boxw/4, boxw/4, baseh))

    m1 = m1.translate((0, 0, -h1))
    res = res.union(m1)

    
    m1 = m1.translate((0, -boxw/2, 0))
    res = res.union(m1)

    
    m1 = m1.translate((-boxw/2, 0, 0))
    res = res.union(m1)

    
    m1 = m1.translate((0, boxw/2, 0))
    res = res.union(m1)

    return res
    



def tower():
    h1 = 3
    h2 = 2
    n = 9
    res = prism(n, 2, h1)
    res2 = pyramid(n, 2, h2).translate((0, 0, h1))
    main_body = res.union(res2)
    cutter = arc(0.4, 2, 10)
    for i in range(n):
        angle = i /n * 360
        rotated_cutter = cutter.rotate((0,0,0), (0,0,1), angle)
        main_body = main_body.cut(rotated_cutter)

    return main_body


def create_tadj():
    res = tadj()
    cq.exporters.export(res, './stl/tadj.stl')   
    print("ok")

def create_tower():
    res = tower()
    cq.exporters.export(res, './stl/tower.stl')   
    print("ok")    

create_tadj()
#create_tower()
