import threading
import subprocess
import os
import shutil
from pynput.keyboard import Controller, Key

class OpenMSX(threading.Thread):

    def __init__(self, kb):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.running = False
        self.kb = kb
        self.should_stop = False

    def run(self):
        pipe = subprocess.Popen("openmsx -cart Frogger*")

        # clear the screenshots
        if os.path.isdir("../Screenshots"):
            shutil.rmtree("../Screenshots")

        self.running = True

        while not self.should_stop:
            continue

        if self.should_stop and not self.is_stopped():
            self.kb.press(Key(Key.shift))
            self.kb.press(Key(Key.esc))
            self.kb.release(Key(Key.esc))
            self.kb.release(Key(Key.shift))
        self._stop_event.set()

        self.running = False

    def stop(self):
        self.should_stop = True

    def is_stopped(self):
        return self._stop_event.is_set()

    def take_screenshot(self):
        self.kb.press(Key.print_screen.value)
        self.kb.release(Key.print_screen.value)

    def pause(self):
        # TODO Hardcoded f9. Is there a way to find this programmatically?
        self.send_keys(Key.f9)

    def send_keys(self, keys):
        for key in keys:
            self.kb.press(key)
            self.kb.release(key)


