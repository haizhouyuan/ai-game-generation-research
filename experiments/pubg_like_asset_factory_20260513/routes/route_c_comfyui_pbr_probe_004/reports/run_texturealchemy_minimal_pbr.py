import json, pathlib, sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import torch
ROOT = pathlib.Path("/home/yuanhaizhou/ComfyUI/custom_nodes/ComfyUI-TextureAlchemy").resolve()
sys.path.insert(0, str(ROOT))
from normal_utils import HeightToNormal
from map_utils import AOApproximator
inp = pathlib.Path("/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_c_comfyui_pbr_probe_004/inputs/tactical_crate_reference.png")
out = pathlib.Path("/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_c_comfyui_pbr_probe_004/textures")
out.mkdir(parents=True, exist_ok=True)
img = Image.open(inp).convert("RGB").resize((1024,1024), Image.Resampling.LANCZOS)
# Albedo: lightly equalized/desaturated to reduce baked lighting while preserving color.
albedo = ImageEnhance.Color(ImageOps.autocontrast(img, cutoff=1)).enhance(0.85)
height_gray = ImageOps.grayscale(img).filter(ImageFilter.GaussianBlur(radius=0.8))
height_eq = ImageOps.autocontrast(height_gray, cutoff=1)
# Roughness heuristic: tactical crate is worn matte plastic/painted metal; use high roughness with local variation.
gray = np.asarray(height_eq).astype(np.float32) / 255.0
rough = np.clip(0.62 + (1.0 - gray) * 0.24, 0, 1)
metal = np.zeros_like(rough) + 0.08
# Convert height to normal and AO using TextureAlchemy node classes.
height_rgb = np.stack([gray, gray, gray], axis=-1)
height_t = torch.from_numpy(height_rgb).float().unsqueeze(0)
normal_t, normal_info = HeightToNormal().convert(height_t, strength=3.0, method="scharr", output_format="OpenGL", blur_radius=0.2)
ao_t, = AOApproximator().generate_ao(radius=10, strength=1.0, samples=16, contrast=1.2, use_normal=True, height=height_t, normal=normal_t)
def save_rgb(path, arr):
    arr = np.clip(arr,0,1)
    Image.fromarray((arr*255).astype(np.uint8), mode="RGB").save(path)
def save_gray(path, arr):
    arr = np.clip(arr,0,1)
    Image.fromarray((arr*255).astype(np.uint8), mode="L").save(path)
albedo.save(out/"tactical_crate_basecolor.png")
save_gray(out/"tactical_crate_height.png", gray)
save_rgb(out/"tactical_crate_normal.png", normal_t[0].detach().cpu().numpy())
save_gray(out/"tactical_crate_roughness.png", rough)
save_gray(out/"tactical_crate_metallic.png", metal)
save_rgb(out/"tactical_crate_ao.png", ao_t[0].detach().cpu().numpy())
# ORM preview/channel pack: R=AO, G=roughness, B=metallic.
orm = np.stack([ao_t[0,:,:,0].detach().cpu().numpy(), rough, metal], axis=-1)
save_rgb(out/"tactical_crate_orm.png", orm)
report = {
  "input": str(inp),
  "method": "TextureAlchemy node import plus HeightToNormal and AOApproximator; heuristic roughness/metallic",
  "normal_info": normal_info,
  "maps": {p.name: p.stat().st_size for p in sorted(out.glob("tactical_crate_*.png"))},
  "map_count_core": 5,
  "quality_note": "Minimal proof of PBR map production, not final artist-approved texture projection.",
}
pathlib.Path("/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_c_comfyui_pbr_probe_004/reports/material_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
