import cadquery as cq
import math
from ocp_vscode import show

#https://cadquery.readthedocs.io/en/latest/_static/cadquery_cheatsheet.html

def marc(w, h, l = 10):
    cy = cq.Workplane("YZ").cylinder(l, w).translate((l/2, 0, h))
    box = cq.Workplane("XY").box(l, w*2, h).translate((l/2, 0, h/2))
    res = cy.union(box)
    return res


def basi():
    h = 13.6
    w = 22.2
    h2 = 7.8
    h22 = h+h2 + 2
    d = 1.5
    w2 = 12.4
    d2 = 0.7
    h3 = 31
    l = w + 2*w2
    r0 = 0.9*w/2
    r = 1.3*r0

    
    aPnt1=(- w / 2 - d, h)
    aPnt2=(- w / 2,  h)
    aPnt3=(0,  h+h2)
    aPnt4=(w/2,  h)
    aPnt5=(w/2 + d, h)

    '''
    aSegment1=cq.Workplane("XZ").moveTo(aPnt1[0], aPnt1[1]).lineTo(aPnt2[0], aPnt2[1])
    aSegment2=cq.Workplane("XZ").moveTo(aPnt4[0], aPnt4[1]).lineTo(aPnt5[0], aPnt5[1])
    aArcOfCircle = cq.Workplane("XZ").moveTo(aPnt2[0], aPnt2[1]).threePointArc(aPnt3, aPnt4)
    '''
    aWire = (cq.Workplane("XZ").moveTo(aPnt1[0], aPnt1[1]).lineTo(aPnt2[0], aPnt2[1])
             .threePointArc(aPnt3, aPnt4)
             .lineTo(aPnt5[0], aPnt5[1])
             .wire())
    ruf = aWire.offset2D(0.1)
    ruf = ruf.extrude(-w2)
    ruf = ruf.shell(0.4)

    aWire2 = (cq.Workplane("XZ").moveTo(aPnt2[0], aPnt2[1])
             .threePointArc(aPnt3, aPnt4)
             .close()).translate((0, d2, 0))
    ruf2 =aWire2.extrude(-w2 + d2)
    box = cq.Workplane("XY").box(w + 2*d2, w2 - d2, h, False).translate((-w/2-d2, 0, 0))
    boxI = cq.Workplane("XY").box(w + 2*d2-d*2, w2, h-d, False).translate((-w/2-d2+d, d, 0))
    box = box.cut(boxI)
    ruf = ruf.union(ruf2).union(box)
    ruf2 = ruf2.translate((0, d, -d2-d))
    ruf = ruf.cut(ruf2)
    
    #Arc
    ar1 = 3.9/2
    hr1 = 7.4
    arc1 = marc(ar1, hr1).rotate((0, 0, 0),(0, 0, 1), -90).translate((0, d2+d, 0))
    ruf = ruf.cut(arc1)

    ar2 = 1.9/2
    hr2 = 3.9
    xr = 7
    arc2 = marc(ar2, hr2).rotate((0, 0, 0),(0, 0, 1), -90).translate((0, d2+d, hr1+ar1 - hr2 - ar2))
    #ruf = ruf.cut(arc2)

    arc2 = arc2.translate((-xr, 0, 0))
    ruf = ruf.cut(arc2)
    arc2 = arc2.translate((xr*2, 0, 0))
    ruf = ruf.cut(arc2)
    
   
    ar3 = 1.7/2
    hr3 = 4
    arc3 = marc(ar3, hr3).rotate((0, 0, 0),(0, 0, 1), -90).translate((0, d2+d, h))
    ruf = ruf.cut(arc3)

    ar4 = 1.4/2
    hr4 = 5.
    arc4 = marc(ar4, hr4, 40).translate((r0-d, 0, h22))
    
    ruf = ruf.translate((0, -w2-w/2 + d, 0))


    res = cq.Workplane("XY").box(w, w, h22-h, False).translate((-w/2, -w/2, h))
    cy = cq.Workplane("XY").cylinder(h3-h, r0).translate((0, 0, h + (h3-h)/2))
    cyI = cq.Workplane("XY").cylinder(h3+1, r0-d+0.1).translate((0, 0, (h3+1)/2))
    

    dl = math.sqrt(r*r - r0*r0)
    sp = cq.Workplane("XY").sphere(r)
    sp1 = cq.Workplane("XY").sphere(r-d)
    sp = sp.cut(sp1)
    mbox = cq.Workplane("XY").box(100, 100, dl, False).translate((-50, -50, 0))
    mbox2 = cq.Workplane("XY").box(100, 100, 100, False).translate((-50, -50, -100))
    sp = sp.cut(mbox).cut(mbox2).translate((0, 0, h3-dl))
    cy = cy.union(sp)
    
    for i in range(4):
        ruf = ruf.rotate((0, 0, 0), (0, 0, 1), 90)
        res = res.union(ruf)
        arc4 = arc4.rotate((0, 0, 0),(0, 0, 1), 90)
        cy = cy.cut(arc4)    
    
    res = res.union(cy)
    cy2 = cq.Workplane("XY").cylinder(0.1, r0+d2).translate((0, 0, h3 + 0.5))
    cy2 = cy2.shell(0.3)
    

    res = res.union(cy2)
    res = res.cut(cyI)

    #show(res)
    return res
    

res = basi()
ass = cq.Assembly()
ass.add(res.val())
ass.export('./stl/basilica.glb')   
show(ass)
print("ok")

