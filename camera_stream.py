# camera_stream.py
import cv2
import threading
import config

class ThreadedCamera:
    """Grabs frames in a background thread so processing never waits on I/O.
    This is the single biggest lag-killer for a live webcam pipeline."""

    def __init__(self):
        self.cap = cv2.VideoCapture(config.CAM_INDEX, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAM_FPS)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # drop stale frames, always get newest

        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera. Check CAM_INDEX in config.py")

        self.lock = threading.Lock()
        self.frame = None
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def read(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.running = False
        self.thread.join(timeout=1)
        self.cap.release()