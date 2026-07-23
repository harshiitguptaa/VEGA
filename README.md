# VEGA — Virtually Engineered Gesture Automator

VEGA lets you control your mouse cursor using only your webcam and your hand — no mouse, no touchpad. Move your pinky finger to move the cursor, pinch your thumb and index finger together to click and hold. Built for Linux (Wayland/KDE), designed to run quietly in the background 24/7 with minimal CPU overhead.

## What it does

- **Cursor movement** — controlled by your pinky finger position, tracked in real time from your webcam.
- **Left click** — pinch your thumb and index finger together (a quick pinch = click, a held pinch = click-and-drag).
- **Clutch (reposition without moving the cursor)** — curl your pinky finger inward and the cursor freezes in place. Move your hand anywhere, extend your pinky again, and tracking resumes from the new position with zero jump — the same trick you use when you lift a physical mouse off the desk to reposition it.
- **Idle by default** — if your hand isn't pinching and isn't clearly visible, nothing happens. No accidental input.

## How it works

VEGA is a small real-time pipeline made of four stages that run in a loop, dozens of times per second:

1. **Camera capture** (`camera_stream.py`) — grabs frames from your webcam on a background thread, so frame grabbing never blocks or slows down the rest of the pipeline. Runs at a low resolution (320×240) since hand-tracking doesn't need high-res video, and lower resolution means less data to process per frame — this is one of the biggest lag-reduction choices in the whole project.

2. **Hand tracking** (`hand_tracker.py`) — uses **Google's MediaPipe Hands** model to detect a hand in each frame and locate 21 landmark points on it (fingertips, knuckles, wrist, etc). From these landmarks we calculate two things every frame:
   - **Pinch ratio** — the distance between your thumb tip and index fingertip, normalized against your palm size (so it works regardless of how close or far your hand is from the camera).
   - **Pinky extend ratio** — how far your pinky fingertip is from your wrist, compared to your pinky's base knuckle. This tells us whether your pinky is extended (tracking active) or curled in (clutch/frozen).

3. **Gesture logic** (`main.py`) — turns those raw numbers into intentional actions:
   - **Hysteresis thresholds** — separate "engage" and "release" thresholds (rather than one single cutoff) for both pinch and pinky-curl detection. This creates a small dead zone that absorbs natural hand-tracking jitter, so a slightly shaky hand doesn't cause flickering false clicks or a flickering freeze state.
   - **Debounce frame counting** — a gesture only triggers after it's been detected consistently for several frames in a row, not just one. This filters out single-frame tracking noise before it ever reaches your cursor.
   - **Relative movement with a "believed position" baseline** — instead of mapping camera coordinates directly to screen coordinates (which breaks down at the edges of your camera's view), VEGA tracks how much your pinky *moved* since the last active frame and moves the cursor by that same relative amount. This is exactly how a real physical mouse works, and it's what makes the clutch (freeze/resume) possible without any positional jump.

4. **Mouse control** (`controller.py`) — sends the actual click and movement commands to the operating system. On Wayland (which KDE Fedora uses by default), regular input-simulation libraries don't work due to Wayland's security model, so VEGA uses **`ydotool`**, which works by talking to the Linux kernel's `uinput` interface directly — the same layer real input devices use.

## Tech stack

| Component | Purpose |
|---|---|
| [OpenCV](https://opencv.org/) | Camera capture and frame processing |
| [MediaPipe](https://developers.google.com/mediapipe) | Real-time hand landmark detection |
| [ydotool](https://github.com/ReimuNotMoe/ydotool) | Synthetic mouse input on Wayland (via Linux `uinput`) |
| Python 3.11 | Everything is glued together in plain Python |

## Project structure

```
VEGA/
├── requirements.txt     # Python dependencies
├── config.py             # All tunable settings in one place
├── camera_stream.py       # Threaded webcam capture
├── hand_tracker.py        # MediaPipe hand landmark processing + gesture math
├── controller.py          # Sends mouse movement/click commands via ydotool
└── main.py                # Main loop tying everything together
```

## Setup (Fedora / KDE / Wayland)

```bash
# System dependencies
sudo dnf install python3.11 ydotool

# Enable the ydotool background daemon (required for mouse control on Wayland)
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/ydotoold.service << 'EOF'
[Unit]
Description=ydotool daemon

[Service]
ExecStart=/usr/bin/ydotoold
Restart=always

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now ydotoold.service

# Python environment
cd VEGA
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** your user needs to be in the `input` group for `ydotool` to have permission to send input events (`sudo usermod -aG input $USER`, then log out and back in).

## Running it

```bash
source venv/bin/activate
python main.py
```

Press `q` in the debug window to quit (if `SHOW_DEBUG_WINDOW` is enabled in `config.py`).

## Configuration

All behavior is tunable from `config.py` without touching the core logic — sensitivity, click thresholds, clutch thresholds, debounce delay, and debug/performance options are all in one place with comments explaining what each does.

## Is this actually useful day-to-day?

Right now, honestly: **it's a solid working prototype and a great hands-on systems project** (camera pipelines, ML inference, Wayland's input model, threading, debouncing/hysteresis design) — but it's not yet a practical daily mouse replacement. A few honest caveats:

- It's slower and less precise than a physical mouse or trackpad for fine work (e.g. small UI targets, precise dragging).
- It depends on stable lighting and a clear camera view of your hand at all times.
- Extended use in front of a camera holding a gesture is more physically tiring than resting a hand on a desk.

Where it genuinely shines: **accessibility use cases** (for people who have difficulty using a physical mouse), **hands-free control** in specific situations (presenting, cooking, workshop/dirty-hands scenarios), and as a **foundation to build on** — the same pipeline architecture here can be extended to gesture-based media controls, presentation remotes, accessibility tooling, or combined with other input methods (e.g. a physical clicker for reliable clicks, gesture only for movement).

## Roadmap / ideas not yet built

- Object-tracking (e.g. a colored pen tip) as an alternative to hand tracking, for more precision
- Right-click and scroll gestures
- Autostart as a background service for true 24/7 operation
- On-screen status indicator instead of full camera debug window

## License

MIT