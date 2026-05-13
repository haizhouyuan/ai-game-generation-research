#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw


PROXY_KEYS = [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_synthetic_images(image_dir: Path) -> list[Path]:
    image_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("synthetic_block.png", "block"),
        ("synthetic_tower.png", "tower"),
    ]
    out = []
    for filename, kind in specs:
        image = Image.new("RGB", (512, 512), (128, 128, 128))
        draw = ImageDraw.Draw(image)
        if kind == "block":
            draw.rounded_rectangle((150, 190, 360, 335), radius=22, fill=(215, 226, 233), outline=(62, 72, 80), width=4)
            draw.rectangle((180, 335, 220, 382), fill=(75, 88, 99))
            draw.rectangle((290, 335, 330, 382), fill=(75, 88, 99))
            draw.ellipse((205, 218, 242, 255), fill=(88, 151, 230))
            draw.ellipse((270, 218, 307, 255), fill=(88, 151, 230))
        else:
            draw.rectangle((222, 112, 290, 372), fill=(210, 218, 224), outline=(54, 64, 73), width=4)
            draw.polygon([(170, 372), (342, 372), (316, 420), (196, 420)], fill=(96, 113, 126), outline=(45, 54, 62))
            draw.ellipse((205, 72, 307, 174), fill=(232, 198, 95), outline=(73, 69, 47), width=4)
            draw.line((256, 174, 256, 372), fill=(74, 86, 96), width=5)
        path = image_dir / filename
        image.save(path)
        out.append(path)
    return out


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: run_triposr_synthetic_homepc.py <source_root> <model_root> <experiment_root>", file=sys.stderr)
        return 2

    source_root = Path(sys.argv[1]).resolve()
    model_root = Path(sys.argv[2]).resolve()
    experiment_root = Path(sys.argv[3]).resolve()
    image_dir = experiment_root / "images"
    output_dir = experiment_root / "output"
    evidence_dir = experiment_root / "evidence"
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for idx in range(2):
      (output_dir / str(idx)).mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    for key in PROXY_KEYS:
        env.pop(key, None)
    env.update({
        "NO_PROXY": "*",
        "no_proxy": "*",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "TRIPOSR_DINO_CONFIG": str(source_root / "local_dino_vitb16_config.json"),
        "CUDA_VISIBLE_DEVICES": env.get("CUDA_VISIBLE_DEVICES", "1"),
    })

    images = make_synthetic_images(image_dir)
    env_proof = {
        "network_mode": "offline/no-proxy",
        "proxy_keys_present_after_unset": {key: env.get(key) for key in PROXY_KEYS if env.get(key)},
        "NO_PROXY": env.get("NO_PROXY"),
        "no_proxy": env.get("no_proxy"),
        "HF_HUB_OFFLINE": env.get("HF_HUB_OFFLINE"),
        "TRANSFORMERS_OFFLINE": env.get("TRANSFORMERS_OFFLINE"),
        "source_root": str(source_root),
        "model_root": str(model_root),
        "experiment_root": str(experiment_root),
        "input_images": [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in images],
    }
    (evidence_dir / "environment_no_proxy.json").write_text(json.dumps(env_proof, indent=2))

    command = [
        sys.executable,
        str(source_root / "run.py"),
        str(images[0]),
        str(images[1]),
        "--pretrained-model-name-or-path",
        str(model_root),
        "--output-dir",
        str(output_dir),
        "--model-save-format",
        "glb",
        "--no-remove-bg",
        "--mc-resolution",
        "64",
        "--chunk-size",
        "4096",
    ]
    start = time.time()
    result = subprocess.run(command, cwd=source_root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
    elapsed = time.time() - start
    (evidence_dir / "triposr_synthetic_run.log").write_text(result.stdout)

    outputs = []
    for idx, name in enumerate(["triposr_p5_synthetic_block.glb", "triposr_p5_synthetic_tower.glb"]):
        mesh_path = output_dir / str(idx) / "mesh.glb"
        outputs.append({
            "label": name,
            "path": str(mesh_path),
            "exists": mesh_path.exists(),
            "bytes": mesh_path.stat().st_size if mesh_path.exists() else None,
            "sha256": sha256(mesh_path) if mesh_path.exists() else None,
        })
    summary = {
        "command": command,
        "returncode": result.returncode,
        "elapsed_seconds": elapsed,
        "outputs": outputs,
    }
    (evidence_dir / "triposr_synthetic_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
