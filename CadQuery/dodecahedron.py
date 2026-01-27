import cadquery as cq
from ocp_vscode import show
import math




def dode():
    #dodecahedron    
    r = 1
    di  = 116.57 #dihedral angle in a dodecahedron
    al = (180 - 116.57) / 180 * math.pi  #the angle between two radii of an inscribed sphere
    z = r * math.cos(al)
    r0 = r * math.sin(al)
    points = [(0, 0, r), (0, 0, -r)]
    for i in range(5):
        aa = i*math.tau/5
        points.append((r0*math.cos(aa), r0*math.sin(aa), z))
    
    for i in range(5):
        aa = i*math.tau/5 + math.tau/10
        points.append((r0*math.cos(aa), r0*math.sin(aa), -z))    

    res = cq.Workplane("XY").sphere(2*r)
    
    for ori in points: 
        pl = cq.Plane(origin=ori, normal= ori)
        res2 = cq.Workplane(pl).box(1000, 1000, 1000, centered=(True, True, False)).val()
        res = res.cut(res2)
        
    
    return res.val()

#Small stellated dodecahedron.
def small_dode():
    #dodecahedron    
    r = 1
    di  = 116.57 #dihedral angle in a dodecahedron
    adeg = (180 - 116.57)
    al = (180 - 116.57) / 180 * math.pi  #the angle between two radii of an inscribed sphere
    z = r * math.cos(al)
    r0 = r * math.sin(al)
    points = [(0, 0, r), (0, 0, -r)]
    for i in range(5):
        aa = i*math.tau/5
        points.append((r0*math.cos(aa), r0*math.sin(aa), z))
    
    for i in range(5):
        aa = i*math.tau/5 + math.tau/10
        points.append((r0*math.cos(aa), r0*math.sin(aa), -z))    

    res = cq.Workplane("XY").sphere(2*r)
    
    # a - len = 2, r - radius inscribed sphere, r = fi^2 / eps,   a =  R * 2 * eps/fi^2 
    fi = (1 + math.sqrt(5))/2
    eps = math.sqrt(3 - fi)
    a = r * 2 * eps/fi/fi
    r2 = a/2/math.sin(math.pi/5)
    h2 = a/2*math.tan(math.pi * 2 / 5)
    h3 = r2*math.cos(math.pi/5)
    h = math.sqrt(h2*h2 - h3*h3)

    n = 5
    a0 = math.tau/n
    r3 = r2*0.01
    pyramid_points = [(r2*math.cos(-a0/2 + t*a0), r2*math.sin(-a0/2 + t*a0), 0) for t in range(n+1)]
    pyramid_points2 = [(r3*math.cos(-a0/2 + t*a0), r3*math.sin(-a0/2 + t*a0), 0) for t in range(n+1)]
    pir_top = cq.Workplane("XY", origin=(0, 0, r)).polyline(pyramid_points).close().workplane(offset=h).polyline(pyramid_points2).close().loft(combine=True)
    pir_bot = pir_top.rotate((0, 0, 0), (0, 1, 0), 180)
    
    for ori in points: 
        pl = cq.Plane(origin=ori, normal= ori)
        res2 = cq.Workplane(pl).box(1000, 1000, 1000, centered=(True, True, False))
        res = res.cut(res2)

    pirs = [res.val(), pir_top.val(), pir_bot.val()]    
    for i in range(5):
        res4 = pir_top.rotate((0, 0, 0), (0, 0, 1), 36).rotate((0, 0, 0), (0, 1, 0), adeg).rotate((0, 0, 0), (0, 0, 1), 360/5*i)
        pirs.append(res4.val())
        res5 = pir_bot.rotate((0, 0, 0), (0, 0, 1), 36).rotate((0, 0, 0), (0, 1, 0), adeg).rotate((0, 0, 0), (0, 0, 1), 360/5*i)
        pirs.append(res5.val())
    
    cm = cq.Compound.makeCompound(pirs)
    return cm


#Icosahedron
def icos():
    #vertex of icosahedron is a centre of dodecahedron face 
    r = 1
    di  = 116.57 #dihedral angle in a dodecahedron
    al = (180 - 116.57) / 180 * math.pi  #the angle between two radii of an inscribed sphere
    z = r * math.cos(al)
    r0 = r * math.sin(al)
    tp = (0, 0, r)
    bp = (0, 0, -r)
    topp = []
    
    for i in range(5):
        aa = i*math.tau/5
        topp.append((r0*math.cos(aa), r0*math.sin(aa), z))
    
    botp = []
    for i in range(5):
        aa = i*math.tau/5 + math.tau/10
        botp.append((r0*math.cos(aa), r0*math.sin(aa), -z))  

    triangles_data = []
    for i in range(5):      
        tri = (tp, topp[i], topp[(i+1)%5])
        triangles_data.append(tri)
        tri = (bp, botp[(i+1)%5], botp[i])
        triangles_data.append(tri)
        tri = (topp[(i+1)%5], botp[i], topp[i])
        triangles_data.append(tri)
        tri = (botp[i], topp[(i+1)%5], botp[(i+1)%5])
        triangles_data.append(tri)
        

    faces = []
    for tri in triangles_data:
        # 1. Vec
        pts = [cq.Vector(v) for v in tri]
        
        # 2. Edges
        edges = [
            cq.Edge.makeLine(pts[0], pts[1]),
            cq.Edge.makeLine(pts[1], pts[2]),
            cq.Edge.makeLine(pts[2], pts[0])
        ]
        
        # 3.  Wire & Face
        wire = cq.Wire.combine(edges)[0]
        face = cq.Face.makeFromWires(wire)
        faces.append(face)

    # 4. Shell
    shell = cq.Shell.makeShell(faces)

    # 5. Solid
    solid = cq.Solid.makeSolid(shell)
    return solid
        


res = small_dode()#icos()#dode()#small_dode()    
ass = cq.Assembly()
ass.add(res)
ass.save('./stl/small_dode.glb')


res = icos()
ass = cq.Assembly()
ass.add(res)
ass.save('./stl/icos.glb')

res = dode()
ass = cq.Assembly()
ass.add(res)
ass.save('./stl/dode.glb')

print("ok")