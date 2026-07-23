# config.py

BACKEND = "ydotool"

# ---- Camera ----
CAM_INDEX = 0
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
CAM_FPS = 60

# ---- MediaPipe ----
MAX_NUM_HANDS = 1
MODEL_COMPLEXITY = 0
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# ---- Gesture thresholds ----
PINCH_ENGAGE = 0.20
PINCH_RELEASE = 0.35

# ---- Movement (relative + clutch) ----
# Higher = cursor moves faster per unit of pinky movement.
SENS_X = 2600
SENS_Y = 2600
SMOOTHING_ALPHA = 0.6

# ---- Pinky extend/curl (this IS the clutch: curled = frozen, extended = active) ----
PINKY_EXTEND_ENGAGE = 1.65
PINKY_EXTEND_RELEASE = 1.45

# ---- Pinch click debounce ----
PINCH_CONFIRM_FRAMES = 4

# ---- Debug / performance ----
SHOW_DEBUG_WINDOW = True     # set False entirely for max CPU savings in 24/7 use
DRAW_LANDMARKS = False       # skeleton overlay costs CPU per frame; off by default
DEBUG_WINDOW_WIDTH = 240
DEBUG_WINDOW_HEIGHT = 180