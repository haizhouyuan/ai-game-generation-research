import argparse
from pathlib import Path

import pytest

from experiments.blender_host_probe_20260513.blender_glb_cleanup_probe import (
    MATERIAL_STRATEGIES,
    TEXTURE_STRATEGIES,
    default_output_name,
    parse_args,
    validate_output_name,
)


def test_default_output_name_uses_input_stem() -> None:
    assert default_output_name(Path("rw_rover_001.glb")) == "rw_rover_001_blender_cleaned_with_proxy.glb"


def test_parse_args_accepts_explicit_output_name(tmp_path: Path) -> None:
    input_glb = tmp_path / "source.glb"
    out_dir = tmp_path / "out"

    parsed_input, parsed_out, output_name, material_strategy, texture_strategy, texture_size = parse_args(
        [str(input_glb), str(out_dir), "--output-name", "custom_cleaned.glb"]
    )

    assert parsed_input == input_glb.resolve()
    assert parsed_out == out_dir.resolve()
    assert output_name == "custom_cleaned.glb"
    assert material_strategy == "preserve"
    assert texture_strategy == "none"
    assert texture_size == 512


def test_parse_args_accepts_material_strategy(tmp_path: Path) -> None:
    input_glb = tmp_path / "source.glb"
    out_dir = tmp_path / "out"

    _, _, _, material_strategy, _, _ = parse_args(
        [str(input_glb), str(out_dir), "--material-strategy", "rover-v1"]
    )

    assert "rover-v1" in MATERIAL_STRATEGIES
    assert material_strategy == "rover-v1"


def test_parse_args_accepts_texture_strategy(tmp_path: Path) -> None:
    input_glb = tmp_path / "source.glb"
    out_dir = tmp_path / "out"

    _, _, _, _, texture_strategy, texture_size = parse_args(
        [
            str(input_glb),
            str(out_dir),
            "--material-strategy",
            "rover-v1",
            "--texture-strategy",
            "rover-v1-procedural",
            "--texture-size",
            "256",
        ]
    )

    assert "rover-v1-procedural" in TEXTURE_STRATEGIES
    assert texture_strategy == "rover-v1-procedural"
    assert texture_size == 256


@pytest.mark.parametrize("name", ["../bad.glb", "bad.gltf", "", ".", "nested/bad.glb"])
def test_output_name_must_be_bare_glb_filename(name: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        validate_output_name(name)
