import bpy, math, sys, json, pathlib
argv = sys.argv
idx = argv.index("--") if "--" in argv else len(argv)
args = argv[idx+1:]
in_path = pathlib.Path(args[0])
out_png = pathlib.Path(args[1])
out_report = pathlib.Path(args[2])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(in_path))
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for obj in objs:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
# center and scale
if objs:
    minx=min((obj.bound_box[i][0] for obj in objs for i in range(8)), default=0)
# compute world bounds
coords=[]
for obj in objs:
    for corner in obj.bound_box:
        coords.append(obj.matrix_world @ __import__("mathutils").Vector(corner))
if coords:
    xs=[c.x for c in coords]; ys=[c.y for c in coords]; zs=[c.z for c in coords]
    center=((min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2)
    size=max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs), 0.001)
else:
    center=(0,0,0); size=1
empty = bpy.data.objects.new("PreviewTarget", None)
bpy.context.collection.objects.link(empty)
empty.location=center
# lighting
bpy.ops.object.light_add(type="AREA", location=(3,-4,5))
light=bpy.context.object
light.name="Preview_Key_Area"
light.data.energy=450
light.data.size=4
bpy.ops.object.camera_add(location=(size*1.8, -size*2.2, size*1.2), rotation=(math.radians(62), 0, math.radians(40)))
camera=bpy.context.object
bpy.context.scene.camera=camera
# track camera to target
constraint=camera.constraints.new(type="TRACK_TO")
constraint.track_axis="TRACK_NEGATIVE_Z"
constraint.up_axis="UP_Y"
constraint.target=empty
# set material if none
for obj in objs:
    if not obj.data.materials:
        mat=bpy.data.materials.new(obj.name+"_preview_mat")
        mat.diffuse_color=(0.55,0.48,0.34,1)
        obj.data.materials.append(mat)
bpy.context.scene.render.engine="BLENDER_EEVEE"
bpy.context.scene.render.resolution_x=1280
bpy.context.scene.render.resolution_y=720
bpy.context.scene.view_settings.view_transform="Standard"
bpy.context.scene.render.filepath=str(out_png)
bpy.ops.render.render(write_still=True)
report={
  "input": str(in_path),
  "output_png": str(out_png),
  "mesh_objects": len(objs),
  "materials": sum(len(o.data.materials) for o in objs),
  "polygons": sum(len(o.data.polygons) for o in objs),
  "vertices": sum(len(o.data.vertices) for o in objs),
  "bounds_size": size,
}
out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
