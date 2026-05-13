import bpy, math, sys, json, pathlib
from mathutils import Vector
argv=sys.argv
idx=argv.index("--") if "--" in argv else len(argv)
mesh_path=pathlib.Path(argv[idx+1])
tex_dir=pathlib.Path(argv[idx+2])
out_glb=pathlib.Path(argv[idx+3])
out_png=pathlib.Path(argv[idx+4])
out_report=pathlib.Path(argv[idx+5])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(mesh_path))
objs=[o for o in bpy.context.scene.objects if o.type=="MESH"]
# Smart UV unwrap for probe; production assets need manual UV review.
for obj in objs:
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.03)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
# Material setup
mat=bpy.data.materials.new("TA_probe_crate_pbr")
mat.use_nodes=True
nodes=mat.node_tree.nodes
bsdf=nodes.get("Principled BSDF")
created=[]
def add_tex(name, path, colorspace):
    node=nodes.new("ShaderNodeTexImage")
    node.name=name
    node.label=name
    node.image=bpy.data.images.load(str(path))
    
    available = [item.identifier for item in node.image.colorspace_settings.bl_rna.properties["name"].enum_items]
    node.image.colorspace_settings.name = colorspace if colorspace in available else ("Linear" if "Linear" in available else available[0])
    created.append(name)
    return node
base=add_tex("basecolor", tex_dir/"tactical_crate_basecolor.png", "sRGB")
rough=add_tex("roughness", tex_dir/"tactical_crate_roughness.png", "Non-Color")
metal=add_tex("metallic", tex_dir/"tactical_crate_metallic.png", "Non-Color")
normal_img=add_tex("normal", tex_dir/"tactical_crate_normal.png", "Non-Color")
normal=nodes.new("ShaderNodeNormalMap")
normal.inputs["Strength"].default_value=0.8
links=mat.node_tree.links
links.new(base.outputs["Color"], bsdf.inputs["Base Color"])
links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
links.new(metal.outputs["Color"], bsdf.inputs["Metallic"])
links.new(normal_img.outputs["Color"], normal.inputs["Color"])
links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
for obj in objs:
    obj.data.materials.clear()
    obj.data.materials.append(mat)
# Bounds and camera
coords=[]
for obj in objs:
    for c in obj.bound_box:
        coords.append(obj.matrix_world @ Vector(c))
if coords:
    xs=[c.x for c in coords]; ys=[c.y for c in coords]; zs=[c.z for c in coords]
    center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2))
    size=max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs), 0.001)
else:
    center=Vector((0,0,0)); size=1
empty=bpy.data.objects.new("PreviewTarget", None)
bpy.context.collection.objects.link(empty)
empty.location=center
bpy.ops.object.light_add(type="AREA", location=(3,-4,5))
key=bpy.context.object
key.data.energy=550
key.data.size=4
bpy.ops.object.camera_add(location=(size*1.8, -size*2.2, size*1.2), rotation=(math.radians(62),0,math.radians(40)))
camera=bpy.context.object
bpy.context.scene.camera=camera
con=camera.constraints.new(type="TRACK_TO")
con.track_axis="TRACK_NEGATIVE_Z"
con.up_axis="UP_Y"
con.target=empty
# Export and render
bpy.ops.export_scene.gltf(filepath=str(out_glb), export_format="GLB")
bpy.context.scene.render.engine="BLENDER_EEVEE"
bpy.context.scene.render.resolution_x=1280
bpy.context.scene.render.resolution_y=720
bpy.context.scene.view_settings.view_transform="Standard"
bpy.context.scene.render.filepath=str(out_png)
bpy.ops.render.render(write_still=True)
report={
 "input_mesh": str(mesh_path),
 "output_glb": str(out_glb),
 "output_png": str(out_png),
 "mesh_objects": len(objs),
 "vertices": sum(len(o.data.vertices) for o in objs),
 "polygons": sum(len(o.data.polygons) for o in objs),
 "material": mat.name,
 "texture_nodes": created,
 "uv_layers": {o.name: [uv.name for uv in o.data.uv_layers] for o in objs},
 "status": "textured_preview_probe_only"
}
out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
