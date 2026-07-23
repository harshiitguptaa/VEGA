# main.py
import cv2
import config
from camera_stream import ThreadedCamera
from hand_tracker import HandTracker
from controller import MouseController


def main():
    cam = ThreadedCamera()
    tracker = HandTracker()
    mouse = MouseController()

    pinching = False
    pinch_frame_count = 0
    release_frame_count = 0

    smooth_pinky = None
    prev_active_pinky = None   # baseline for relative delta; None = "just resumed, don't move yet"
    pinky_extended = True

    if config.SHOW_DEBUG_WINDOW:
        cv2.namedWindow("VEGA Debug", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("VEGA Debug", config.DEBUG_WINDOW_WIDTH, config.DEBUG_WINDOW_HEIGHT)

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = tracker.process(frame_rgb)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                pinch_ratio, pinky_tip, pinky_extend_ratio = tracker.get_gesture_data(hand_landmarks)

                # --- Smooth raw pinky position ---
                if smooth_pinky is None:
                    smooth_pinky = pinky_tip
                else:
                    a = config.SMOOTHING_ALPHA
                    smooth_pinky = (
                        a * pinky_tip[0] + (1 - a) * smooth_pinky[0],
                        a * pinky_tip[1] + (1 - a) * smooth_pinky[1],
                    )

                # --- Extend/curl state (clutch) with hysteresis ---
                if pinky_extend_ratio > config.PINKY_EXTEND_ENGAGE:
                    pinky_extended = True
                elif pinky_extend_ratio < config.PINKY_EXTEND_RELEASE:
                    pinky_extended = False

                if pinky_extended:
                    if prev_active_pinky is not None:
                        # Normal case: move by how much pinky moved since last active frame
                        dx = (smooth_pinky[0] - prev_active_pinky[0]) * config.SENS_X
                        dy = (smooth_pinky[1] - prev_active_pinky[1]) * config.SENS_Y
                        mouse.move_relative(dx, dy)
                    # else: this is the FIRST frame after resuming -> set baseline only, move nothing
                    prev_active_pinky = smooth_pinky
                else:
                    # Curled -> frozen. Drop baseline so resume doesn't jump.
                    prev_active_pinky = None

                # --- Pinch debounce state machine (click only) ---
                if pinch_ratio < config.PINCH_ENGAGE:
                    pinch_frame_count += 1
                    release_frame_count = 0
                elif pinch_ratio > config.PINCH_RELEASE:
                    release_frame_count += 1
                    pinch_frame_count = 0
                else:
                    pinch_frame_count = 0
                    release_frame_count = 0

                if not pinching and pinch_frame_count >= config.PINCH_CONFIRM_FRAMES:
                    pinching = True
                    mouse.mouse_down()
                    pinch_frame_count = 0
                elif pinching and release_frame_count >= config.PINCH_CONFIRM_FRAMES:
                    pinching = False
                    mouse.mouse_up()
                    release_frame_count = 0

                if config.SHOW_DEBUG_WINDOW and config.DRAW_LANDMARKS:
                    tracker.mp_draw.draw_landmarks(
                        frame, hand_landmarks, tracker.mp_hands.HAND_CONNECTIONS
                    )
            else:
                if pinching:
                    pinching = False
                    mouse.mouse_up()
                pinch_frame_count = 0
                release_frame_count = 0
                smooth_pinky = None
                prev_active_pinky = None

            if config.SHOW_DEBUG_WINDOW:
                cv2.imshow("VEGA Debug", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        if pinching:
            mouse.mouse_up()
        cam.stop()
        tracker.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()