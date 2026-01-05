import cadquery as cq
import math
from ocp_vscode import show
#https://cadquery.readthedocs.io/en/latest/workplane.html

def tile(l):
    w = 2*l
    h1 = 0.2*l
    h2 = 0.2 *h1
    pa = 0.1*l
    br = 0.4*pa
    br1 = 0.45*pa 
    dd = 2*br

    w1 = w/4
    w2 = w - w1
    tl1 = (cq.Workplane("XY").rect(l, w1).rect(l - 2*pa, w1 - 2*pa).extrude(h1).faces(">Z")
           .workplane().rect(l - 2*pa, w1 - 2*pa).rect(l - 2*pa + 2*br, w1 - 2*pa + 2*br).extrude(h2))
    tl2 = (cq.Workplane("XY").rect(l, w2).rect(l - 2*pa, w2 - 2*pa).extrude(h1)
           .faces(">Z")
           .workplane().rect(l - 2*pa, w2 - 2*pa).rect(l - 2*pa + 2*br, w2 - 2*pa + 2*br).extrude(h2)
    )
    arc = (
            cq.Workplane("XY").moveTo(-l/2+pa + dd, -w2/2 + pa + dd)
            .lineTo(-l/2 + pa + dd, 0.*w2)
            .threePointArc((0, 0.3*w2),(l/2 - pa - dd, 0. *w2))
            .lineTo(l/2-pa - dd, -w2/2 + pa + dd)
            .close()
          ).val()
    
           
    arc2 = cq.Workplane("XY").circle(l*0.3 + br).val()
    
    tl3 = (cq.Workplane("XY")
           .rect(l - 2*pa, w2 - 2*pa)
           .toPending()
           .add(arc)
           .toPending()
           .extrude(0.7*h1)
           
           .faces(">Z")
           .workplane()

            
        

           #.circle(l*0.3)
           #.circle(l*0.3 + br)
            
           
           

           .pushPoints([(2.3*pa-l/2, w2/2 - 2.3*pa), (-2.3*pa + l/2, w2/2 - 2.3*pa)])
           .circle(0.08*l).extrude(0.3*h1)
    )

    '''
    .moveTo(-l/2+pa + dd/2, -w2/2 + pa + dd/2)
            .lineTo(-l/2 + pa + dd/2, 0.*w2)
            .threePointArc((0, 0.3*w2),(l/2 - pa - dd/2, 0. *w2))
            .lineTo(l/2-pa - dd/2, -w2/2 + pa + dd/2)
            .close()
            .toPending()

            .moveTo(-l/2+pa + dd, -w2/2 + pa + dd)
            .lineTo(-l/2 + pa + dd, 0.*w2)
            .threePointArc((0, 0.3*w2),(l/2 - pa - dd, 0. *w2))
            .lineTo(l/2-pa - dd, -w2/2 + pa + dd)
            .close()
            .toPending()
            .extrude(h2)
            '''
    tl2 = tl2.union(tl3)
    
           
           
    
    res = (cq.Workplane("XY").add(tl1.translate((0, ( w - w1/2 - w/2), 0)).val())
           .add(tl2.translate((0, w2/2 - w/2, 0)).val()).combine()
    )
    return res.rotate((0, 0, 0), (1, 0, 0), 90).val()

    #show(res)

def but():
    n = 4
    h = 2
    points = [(0.5 + i - n/2, 0) for i in range(n)]
    steps1 = [tile(1).translate((0.5 + i - n/2, -n/2, 0)) for i in range(n)]
    res1 = cq.Compound.makeCompound(steps1)
    steps2 = [res1.rotate((0, 0, 0), (0, 0, 1), 90*i) for i in range(n)]
    bx = cq.Solid.makeBox(n, n, h).translate((-n/2, -n/2, -h/2))
    steps2.append(bx)
    res2 = cq.Compound.makeCompound(steps2)
    show(res2)

    
    

but()
#res = tile(1)
#show(res)