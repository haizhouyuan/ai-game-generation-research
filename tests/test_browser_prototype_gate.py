import hashlib
import json
import struct
import zlib

from tools.run_browser_prototype_gate import (
    build_release_packet,
    is_local_request,
    png_pixel_stats,
    summarize_checks,
    summarize_console_events,
    summarize_network_events,
    write_closeout,
    write_hashes,
)


def make_rgba_png(width, height, rows):
    raw = b"".join(b"\x00" + row for row in rows)
    compressed = zlib.compress(raw)

    def chunk(kind, payload):
        return (
            struct.pack("!I", len(payload))
            + kind
            + payload
            + struct.pack("!I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


def test_png_pixel_stats_detects_nonblank_rgba_image():
    png = make_rgba_png(
        2,
        1,
        [
            bytes(
                [
                    255,
                    0,
                    0,
                    255,
                    0,
                    128,
                    255,
                    255,
                ]
            )
        ],
    )

    stats = png_pixel_stats(png)

    assert stats["width"] == 2
    assert stats["height"] == 1
    assert stats["nontransparent_pixels"] == 2
    assert stats["distinct_sample_colors"] == 2
    assert stats["nonblank"] is True


def test_build_release_packet_marks_only_g4_as_promotable():
    packet = build_release_packet(
        release_id="test_release",
        prototype_id="p1_rover_workshop",
        entrypoint="experiments/game_p1_rover_workshop_demo/index.html",
        gate_level="G4",
        checks={
            "load": "pass",
            "nonblank_canvas": "pass",
            "hud": "pass",
            "input": "pass",
            "pickup": "pass",
            "hazard": "pass",
            "gate_or_puzzle": "pass",
            "finish": "pass",
            "screenshots": "pass",
            "hashes": "pass",
            "console_errors": "pass",
            "network_failures": "pass",
            "external_requests": "pass",
        },
        artifacts=[],
        asset_provenance=[],
        known_limitations=[],
    )

    assert packet["packet_version"] == "prototype_evidence_gate.v1"
    assert packet["promotable"] is True


def test_build_release_packet_requires_fail_close_checks_for_g4_promotable():
    packet = build_release_packet(
        release_id="test_release",
        prototype_id="p1_rover_workshop",
        entrypoint="experiments/game_p1_rover_workshop_demo/index.html",
        gate_level="G4",
        checks={
            "load": "pass",
            "nonblank_canvas": "pass",
            "hud": "pass",
            "input": "pass",
            "pickup": "pass",
            "hazard": "pass",
            "gate_or_puzzle": "pass",
            "finish": "pass",
            "screenshots": "pass",
            "hashes": "pass",
        },
        artifacts=[],
        asset_provenance=[],
        known_limitations=[],
    )

    assert packet["promotable"] is False


def test_build_release_packet_keeps_g2_non_promotable():
    packet = build_release_packet(
        release_id="test_release",
        prototype_id="p0_chatgpt_html_baseline",
        entrypoint="experiments/game_p0_chatgpt_html_baseline_20260509/14.html",
        gate_level="G2",
        checks={
            "load": "pass",
            "nonblank_canvas": "pass",
            "hud": "pass",
            "input": "pass",
            "pickup": "not_applicable",
            "hazard": "not_applicable",
            "gate_or_puzzle": "not_applicable",
            "finish": "not_applicable",
            "screenshots": "pass",
            "hashes": "pass",
        },
        artifacts=[],
        asset_provenance=[],
        known_limitations=["P0 is a smoke baseline, not a release demo."],
    )

    assert packet["promotable"] is False


def test_summarizes_console_and_network_events():
    events = [
        {
            "method": "Runtime.consoleAPICalled",
            "params": {"type": "warning", "args": [{"value": "careful"}]},
        },
        {
            "method": "Log.entryAdded",
            "params": {"entry": {"level": "error", "text": "failed to load"}},
        },
        {
            "method": "Network.requestWillBeSent",
            "params": {
                "requestId": "1",
                "type": "Document",
                "request": {"url": "http://127.0.0.1:8000/index.html", "method": "GET"},
            },
        },
        {
            "method": "Network.responseReceived",
            "params": {
                "requestId": "1",
                "response": {
                    "status": 200,
                    "mimeType": "text/html",
                    "url": "http://127.0.0.1:8000/index.html",
                },
            },
        },
        {
            "method": "Network.requestWillBeSent",
            "params": {
                "requestId": "2",
                "type": "Script",
                "request": {"url": "https://cdn.example.com/app.js", "method": "GET"},
            },
        },
    ]

    console = summarize_console_events(events)
    network = summarize_network_events(events, "http://127.0.0.1:8000/index.html")

    assert console["warnings"] == [{"level": "warning", "message": "careful"}]
    assert console["errors"] == [{"level": "error", "message": "failed to load"}]
    assert network["request_count"] == 2
    assert network["external_requests"] == [
        {"method": "GET", "type": "Script", "url": "https://cdn.example.com/app.js"}
    ]


def test_network_summary_uses_response_url_when_request_event_is_missing():
    events = [
        {
            "method": "Network.responseReceived",
            "params": {
                "requestId": "module-response-only",
                "response": {
                    "status": 200,
                    "mimeType": "text/javascript",
                    "url": "http://127.0.0.1:8000/module.js",
                },
            },
        }
    ]

    network = summarize_network_events(events, "http://127.0.0.1:8000/index.html")

    assert network["requests"] == [
        {"mimeType": "text/javascript", "status": 200, "url": "http://127.0.0.1:8000/module.js"}
    ]
    assert network["external_requests"] == []


def test_summarize_checks_fails_on_console_or_network_problems():
    step_results = [
        {
            "step": {"id": "load"},
            "state": {"checks": {"page_ready": True}, "hudText": "Ready"},
            "pixel_stats": {"nonblank": True, "width": 10},
        },
        {
            "step": {"id": "input"},
            "state": {"checks": {"position_changed": True}},
            "pixel_stats": {"nonblank": True, "width": 10},
        },
    ]
    console_summary = {"errors": [{"level": "error", "message": "boom"}], "warnings": []}
    network_summary = {
        "external_requests": [{"url": "https://cdn.example.com/app.js"}],
        "failures": [{"url": "https://cdn.example.com/app.js", "errorText": "net::ERR_FAILED"}],
    }

    checks = summarize_checks("G2", step_results, console_summary, network_summary)

    assert checks["console_errors"] == "fail"
    assert checks["network_failures"] == "fail"
    assert checks["external_requests"] == "fail"


def test_local_request_classification_accepts_loopback_forms():
    assert is_local_request("http://127.0.0.1/index.html")
    assert is_local_request("http://127.0.0.1:8000/index.html")
    assert is_local_request("https://localhost/app.js")
    assert is_local_request("http://[::1]:8000/index.html")
    assert is_local_request("data:,")
    assert is_local_request("blob:http://127.0.0.1/id")
    assert is_local_request("about:blank")
    assert not is_local_request("https://cdn.example.com/app.js")


def test_closeout_hash_manifest_recomputes(tmp_path):
    packet = build_release_packet(
        release_id="test_release",
        prototype_id="p1_rover_workshop",
        entrypoint="experiments/game_p1_rover_workshop_demo/index.html",
        gate_level="G4",
        checks={"load": "pass", "hashes": "pass"},
        artifacts=[],
        asset_provenance=[],
        known_limitations=[],
    )

    write_closeout(tmp_path, packet, packet["checks"])
    write_hashes(tmp_path)

    manifest = json.loads((tmp_path / "artifact_hashes.json").read_text())
    actual = hashlib.sha256((tmp_path / "closeout.md").read_bytes()).hexdigest()
    assert manifest["closeout.md"]["sha256"] == actual
