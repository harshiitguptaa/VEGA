# controller.py
import subprocess
import config

class MouseController:
    def __init__(self):
        self.backend = config.BACKEND
        if self.backend == "pynput":
            from pynput.mouse import Controller, Button
            self._mouse = Controller()
            self._Button = Button
        elif self.backend == "ydotool":
            pass
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def move_relative(self, dx, dy):
        dx, dy = int(dx), int(dy)
        if dx == 0 and dy == 0:
            return
        if self.backend == "pynput":
            self._mouse.move(dx, dy)
        else:
            subprocess.run(
                ["ydotool", "mousemove", "-x", str(dx), "-y", str(dy)],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def mouse_down(self):
        if self.backend == "pynput":
            self._mouse.press(self._Button.left)
        else:
            subprocess.run(
                ["ydotool", "click", "0x40"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def mouse_up(self):
        if self.backend == "pynput":
            self._mouse.release(self._Button.left)
        else:
            subprocess.run(
                ["ydotool", "click", "0x80"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )