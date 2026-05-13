"""Tests for verify_artifact_hashes.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent / "tools"
VERIFY_SCRIPT = TOOLS_DIR / "verify_artifact_hashes.py"


def run_verify(*manifests: Path, cwd: Path | None = None) -> tuple[int, str, str]:
    """Run verify_artifact_hashes.py on given manifests. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT)] + [str(m) for m in manifests],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


class TestEvidenceShape:
    def test_valid_manifest(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence"
        manifest_dir.mkdir()
        file_a = manifest_dir / "file_a.txt"
        file_a.write_text("hello")

        import hashlib
        sha_a = hashlib.sha256(b"hello").hexdigest()

        manifest = {"file_a.txt": {"sha256": sha_a, "size_bytes": 5}}
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_dir / "artifact_hashes.json")
        assert rc == 0
        assert "verified 1 hashes" in out
        assert err == ""

    def test_missing_file(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence"
        manifest_dir.mkdir()
        manifest = {"nonexistent.txt": {"sha256": "a" * 64}}
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_dir / "artifact_hashes.json")
        assert rc == 1
        assert "missing file" in err

    def test_hash_mismatch(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence"
        manifest_dir.mkdir()
        file_a = manifest_dir / "file_a.txt"
        file_a.write_text("hello")

        manifest = {"file_a.txt": {"sha256": "b" * 64}}
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_dir / "artifact_hashes.json")
        assert rc == 1
        assert "hash mismatch" in err

    def test_size_mismatch(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence"
        manifest_dir.mkdir()
        file_a = manifest_dir / "file_a.txt"
        file_a.write_text("hello")

        import hashlib
        sha_a = hashlib.sha256(b"hello").hexdigest()

        manifest = {"file_a.txt": {"sha256": sha_a, "size_bytes": 99}}
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_dir / "artifact_hashes.json")
        assert rc == 1
        assert "size mismatch" in err

    def test_nested_relative_paths(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence"
        sub_dir = manifest_dir / "sub"
        sub_dir.mkdir(parents=True)
        file_a = sub_dir / "file_a.txt"
        file_a.write_text("nested")

        import hashlib
        sha_a = hashlib.sha256(b"nested").hexdigest()

        manifest = {"sub/file_a.txt": {"sha256": sha_a}}
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_dir / "artifact_hashes.json")
        assert rc == 0
        assert "verified 1 hashes" in out

    def test_multiple_files(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence"
        manifest_dir.mkdir()
        file_a = manifest_dir / "a.txt"
        file_b = manifest_dir / "b.txt"
        file_a.write_text("content_a")
        file_b.write_text("content_b")

        import hashlib
        sha_a = hashlib.sha256(b"content_a").hexdigest()
        sha_b = hashlib.sha256(b"content_b").hexdigest()

        manifest = {
            "a.txt": {"sha256": sha_a},
            "b.txt": {"sha256": sha_b},
        }
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_dir / "artifact_hashes.json")
        assert rc == 0
        assert "verified 2 hashes" in out


class TestAssetChainShape:
    def test_valid_manifest(self, tmp_path: Path) -> None:
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()
        file_a = artifact_dir / "file_a.txt"
        file_a.write_text("hello")

        import hashlib
        sha_a = hashlib.sha256(b"hello").hexdigest()

        manifest = {
            "generated_at": "2026-05-13T00:00:00+00:00",
            "artifacts": [
                {"path": str(artifact_dir / "file_a.txt"), "sha256": sha_a, "role": "test"}
            ],
        }
        manifest_path = tmp_path / "asset_chain.json"
        manifest_path.write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_path, cwd=tmp_path)
        assert rc == 0
        assert "verified 1 hashes" in out
        assert err == ""

    def test_repo_relative_path_fallback(self, tmp_path: Path) -> None:
        artifact_dir = tmp_path / "repo" / "artifacts"
        artifact_dir.mkdir(parents=True)
        file_a = artifact_dir / "file_a.txt"
        file_a.write_text("hello")

        import hashlib
        sha_a = hashlib.sha256(b"hello").hexdigest()

        manifest = {
            "artifacts": [
                {"path": "artifacts/file_a.txt", "sha256": sha_a}
            ],
        }
        manifest_path = tmp_path / "repo" / "asset_chain.json"
        manifest_path.write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_path, cwd=tmp_path / "repo")
        assert rc == 0
        assert "verified 1 hashes" in out

    def test_missing_file(self, tmp_path: Path) -> None:
        manifest = {
            "artifacts": [
                {"path": "nonexistent.txt", "sha256": "a" * 64}
            ],
        }
        manifest_path = tmp_path / "asset_chain.json"
        manifest_path.write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_path, cwd=tmp_path)
        assert rc == 1
        assert "missing file" in err

    def test_hash_mismatch(self, tmp_path: Path) -> None:
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()
        file_a = artifact_dir / "file_a.txt"
        file_a.write_text("hello")

        manifest = {
            "artifacts": [
                {"path": str(artifact_dir / "file_a.txt"), "sha256": "b" * 64}
            ],
        }
        manifest_path = tmp_path / "asset_chain.json"
        manifest_path.write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_path, cwd=tmp_path)
        assert rc == 1
        assert "hash mismatch" in err


class TestErrorHandling:
    def test_invalid_json(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "bad.json"
        manifest_path.write_text("{not valid json")

        rc, out, err = run_verify(manifest_path)
        assert rc == 1
        assert "invalid JSON" in err

    def test_unsupported_shape(self, tmp_path: Path) -> None:
        manifest = {"some": "random", "shape": "here"}
        manifest_path = tmp_path / "unknown.json"
        manifest_path.write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_path)
        assert rc == 1
        assert "unsupported manifest shape" in err

    def test_evidence_shape_missing_sha256(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence"
        manifest_dir.mkdir()
        manifest = {"file_a.txt": {"size_bytes": 5}}
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_dir / "artifact_hashes.json")
        assert rc == 1
        assert "missing sha256" in err

    def test_asset_chain_missing_artifacts_key(self, tmp_path: Path) -> None:
        # manifest with only generated_at has no artifacts key and doesn't match evidence shape
        manifest = {"generated_at": "2026-05-13T00:00:00+00:00"}
        manifest_path = tmp_path / "no_artifacts.json"
        manifest_path.write_text(json.dumps(manifest))

        rc, out, err = run_verify(manifest_path)
        assert rc == 1
        assert "unsupported manifest shape" in err


class TestCliInterface:
    def test_no_arguments(self) -> None:
        rc, out, err = run_verify()
        assert rc == 1
        assert "Usage:" in err

    def test_multiple_manifests_all_pass(self, tmp_path: Path) -> None:
        for i in range(2):
            manifest_dir = tmp_path / f"evidence_{i}"
            manifest_dir.mkdir()
            file_a = manifest_dir / "file_a.txt"
            file_a.write_text(f"content_{i}")

            import hashlib
            sha_a = hashlib.sha256(f"content_{i}".encode()).hexdigest()

            manifest = {"file_a.txt": {"sha256": sha_a}}
            (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        rc, out, err = run_verify(
            tmp_path / "evidence_0" / "artifact_hashes.json",
            tmp_path / "evidence_1" / "artifact_hashes.json",
        )
        assert rc == 0
        assert "verified 1 hashes" in out
        assert out.count("verified 1 hashes") == 2

    def test_multiple_manifests_one_fails(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / "evidence_0"
        manifest_dir.mkdir()
        file_a = manifest_dir / "file_a.txt"
        file_a.write_text("content_0")

        import hashlib
        sha_a = hashlib.sha256(b"content_0").hexdigest()
        manifest = {"file_a.txt": {"sha256": sha_a}}
        (manifest_dir / "artifact_hashes.json").write_text(json.dumps(manifest))

        bad_manifest = tmp_path / "evidence_1" / "artifact_hashes.json"
        bad_manifest.parent.mkdir()
        bad_manifest.write_text(json.dumps({"nonexistent.txt": {"sha256": "a" * 64}}))

        rc, out, err = run_verify(
            tmp_path / "evidence_0" / "artifact_hashes.json",
            bad_manifest,
        )
        assert rc == 1
        assert "verified 1 hashes" in out
        assert "missing file" in err
