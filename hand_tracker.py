# hand_tracker.py
import mediapipe as mp
import math
import config

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            model_complexity=config.MODEL_COMPLEXITY,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process(self, frame_rgb):
        """Returns mediapipe results (or None-ish empty result if no hand found)."""
        return self.hands.process(frame_rgb)

    @staticmethod
    def get_landmark_dict(hand_landmarks):
        return {i: (lm.x, lm.y) for i, lm in enumerate(hand_landmarks.landmark)}

    @staticmethod
    def dist(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def get_gesture_data(self, hand_landmarks):
        """Returns (pinch_ratio, pinky_pos, pinky_extend_ratio)."""
        lm = self.get_landmark_dict(hand_landmarks)

        thumb_tip = lm[4]
        index_tip = lm[8]
        wrist = lm[0]
        middle_mcp = lm[9]
        pinky_mcp = lm[17]
        pinky_tip = lm[20]

        palm_size = self.dist(wrist, middle_mcp)
        if palm_size < 1e-6:
            palm_size = 1e-6

        pinch_ratio = self.dist(thumb_tip, index_tip) / palm_size

        # How extended the pinky is: tip-to-wrist vs base-to-wrist.
        # Extended pinky -> ratio well above 1.0. Curled pinky -> ratio drops toward/below 1.0.
        base_dist = self.dist(wrist, pinky_mcp)
        if base_dist < 1e-6:
            base_dist = 1e-6
        tip_dist = self.dist(wrist, pinky_tip)
        pinky_extend_ratio = tip_dist / base_dist

        return pinch_ratio, pinky_tip, pinky_extend_ratio

    def close(self):
        self.hands.close()