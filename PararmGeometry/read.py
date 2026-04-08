from __future__ import annotations

import pyvista as pv
from pyvista import examples

pl = pv.Plotter()
pl.import_gltf("./stl/candy_bowl.glb")
#cubemap = pv.read_texture("./stl/env1.hdr")
#pl.set_environment_texture(cubemap)
pl.camera.zoom(1.8)
pl.show()