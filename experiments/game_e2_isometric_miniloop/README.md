# GAME-E2 Isometric Mini Loop

This is a no-download browser prototype baseline. It tests the controller's ability to produce a runnable concept-to-playable artifact without a game engine install or model download.

Run:

```bash
python3 -m http.server 8124 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8124/index.html`.

Interpretation:

- This is a procedural baseline, not a claim about frontier AI game-generation tools.
- It covers a small child-friendly loop: move a rover, collect batteries, avoid a moving hazard, reach the finish pad.
- Later experiments should replace procedural blocks with generated/imported GLB assets and a real engine or Three.js/Godot path.
