#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
GLB = ROOT / "assets" / "models" / "groza_procedural_candidate.glb"
SOURCE = pathlib.Path("/Users/yuanshaochen/Documents/14.html")

EXPECTED_SOURCE_SHA256 = "ad82e7d5da575f8e2f783b39e1bfed4736dc032faa6be7ed8be6a66dacbad8b3"
EXPECTED_GLB_SHA256 = "484a001db8aecd926a0069ae1dbca923d9572dc48dc1919fde7cede4b04179ea"
EXPECTED_M5_WEAPON_SHA256 = {
    "pistol": "aa1fd450ed947ecff9dc9c9ff07a5f4f329d6359d3a462064483bac72cd60255",
    "shotgun": "9a4c3cd89716952c365853ad58de15d4223db95bc3a5f412ad39b5ac7a63bad2",
    "dmr": "52f1acdfef814aed6ca4e5ee8351bc47f5f38db5720ed50e090e4abc293f20c8",
}


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    require(INDEX.exists(), "derived index.html exists", failures)
    require(GLB.exists(), "copied groza_procedural_candidate.glb exists", failures)
    require(SOURCE.exists(), "source 14.html exists for non-mutation check", failures)

    if SOURCE.exists():
        require(sha256(SOURCE) == EXPECTED_SOURCE_SHA256, "source 14.html sha256 unchanged from pre-copy baseline", failures)
    if GLB.exists():
        require(sha256(GLB) == EXPECTED_GLB_SHA256, "copied GLB sha256 matches selected hero candidate", failures)
        header = GLB.read_bytes()[:12]
        require(header[:4] == b"glTF" and header[4:8] == (2).to_bytes(4, "little"), "GLB header is glTF 2.0", failures)
    for kind, expected in EXPECTED_M5_WEAPON_SHA256.items():
        path = ROOT / "assets" / "models" / f"{kind}_m5_candidate.glb"
        require(path.exists(), f"M5 {kind} GLB exists", failures)
        if path.exists():
            require(sha256(path) == expected, f"M5 {kind} GLB sha256 matches generated report", failures)
            header = path.read_bytes()[:12]
            require(
                header[:4] == b"glTF" and header[4:8] == (2).to_bytes(4, "little"),
                f"M5 {kind} GLB header is glTF 2.0",
                failures,
            )

    if INDEX.exists():
        text = INDEX.read_text(encoding="utf-8")
        checks = {
            "built-in GLB loader is included": "async function loadEmbeddedGlb" in text,
            "rifle asset path points inside experiment": 'url:"assets/models/groza_procedural_candidate.glb"' in text,
            "M5 multi-weapon asset registry is included": "const weaponAssets" in text and "pistol_m5_candidate.glb" in text and "dmr_m5_candidate.glb" in text,
            "rifle proxy/collider nodes are hidden": '.includes("proxy")' in text and '.includes("collider")' in text,
            "rifle model is rotated from Blender +X to game +Z": "model.rotation.y=-PI/2" in text,
            "rifle model has game-view placement adjustments": "rifle:{modelScale:.34,modelPos:[0,-.06,.72]" in text,
            "all weapon types attempt GLB replacement before procedural fallback": "const weaponAssetModel=createWeaponAssetModel(type,skinful)" in text,
            "fallback warning is explicit": "procedural fallback remains active" in text,
            "GLB wrapper assigns userData.muzzle": "g.userData.muzzle=muzzle" in text,
            "evidence rifle mode is available": 'evidenceMode==="rifle"' in text and "activateEvidenceRifleMode" in text,
            "M5 evidence showcase is available": 'get("evidence")!=="m5"' in text and "m5_weapon_asset_showcase" in text,
            "runtime probe exposes rifle asset state": "window.__realismProbe" in text,
            "runtime probe exposes all M5 weapon asset states": "weaponAssets:Object.fromEntries" in text,
            "GLB weapon view/third-person scales are specialized": "viewGun.userData.isGlbWeapon" in text and "thirdGun.userData.isGlbWeapon" in text,
            "GLB weapon first-person camera target is specialized": "if(viewGun?.userData?.isGlbWeapon)" in text,
            "evidence mode shows camera-attached rifle showcase": "evidence_camera_groza_rifle" in text,
            "flash updater is defined for gameplay loop": "function updateFlashes" in text and "updateFlashes(dt)" in text,
            "evidence mode avoids pointer-lock rejection": 'get("evidence")==null' in text and "lock?.catch" in text,
            "player rebuild path still calls createGunModel": "viewGun=createGunModel(player.weapon,true)" in text,
            "third-person path still calls createGunModel": "thirdGun=createGunModel(player.weapon,true)" in text,
            "loot weapon path still calls createGunModel": "const gun=createGunModel(item.weapon,false)" in text,
            "NPC weapon path still calls createGunModel": "const gun=createGunModel(enemy.weapon,false)" in text,
            "M5 character tactical gear helper is present": "function addM5TacticalGear" in text,
            "M5 character gear covers helmet comms and backpack": "parts.headParts.push(earL,earR,boom)" in text and "plate carrier, pouches, comms, backpack and pads" in text,
            "M5 loot prop helper is present": "function createM5LootProp" in text,
            "M5 loot prop covers ammo, medical, armor, helmet, revive": 'item.kind==="ammo"' in text and 'item.kind==="revive"' in text and 'item.kind==="helmet"' in text and 'item.kind==="vest"' in text and 'item.kind==="medkit"' in text,
            "M5 non-weapon loot path uses detailed prop helper": "else createM5LootProp(g,item,material);" in text,
            "M5 container detail helper is present": "function addM5ContainerDetails" in text,
            "M5 containers include ribs, hinges, and warning strips": "ribMat" in text and "hingeMat" in text and "warnMat" in text,
        }
        for message, ok in checks.items():
            require(ok, message, failures)

    if failures:
        print(f"\n{len(failures)} check(s) failed.")
        return 1
    print("\nAll integration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
