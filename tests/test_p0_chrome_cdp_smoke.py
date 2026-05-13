from pathlib import Path

from tools.p0_chrome_cdp_smoke import build_chrome_command


def test_chrome_launch_preserves_webgl_for_threejs_smoke():
    command = build_chrome_command(
        chrome_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        port=9237,
        user_data_dir=Path("/tmp/p0-profile"),
        url="http://127.0.0.1:8766/14.html",
    )

    assert "--disable-gpu" not in command
    assert "--ignore-gpu-blocklist" in command
    assert "--use-gl=angle" in command
    assert "--use-angle=metal" in command
