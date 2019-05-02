import threading
import os
from pynput.keyboard import Controller, Key
import shutil
import subprocess
from definitions import PROJECT_DIR
import time


class BlueMSX(threading.Thread):

    def __init__(self, kb):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.should_stop = False
        self.running = False
        self.kb = kb

    def run(self):
        try:
            pipe = subprocess.Popen(PROJECT_DIR + "\\blueMSX.exe")
        except WindowsError:
            print("Exception thrown when opening pipe. Exiting.")
            return

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
        self.send_keys([Key.f9])

    def send_keys(self, keys):
        for key in keys:
            self.kb.press(key)
            self.kb.release(key)
    
    def up(self):
        time.sleep(0.010)
        self.kb.press('w')
        time.sleep(0.020)
        self.kb.release('w')
        time.sleep(0.010)

    def down(self):
        time.sleep(0.010)
        self.kb.press('s')
        time.sleep(0.020)
        self.kb.release('s')
        time.sleep(0.010)

    def left(self):
        time.sleep(0.010)
        self.kb.press('a')
        time.sleep(0.020)
        self.kb.release('a')
        time.sleep(0.010)

    def right(self):
        time.sleep(0.010)
        self.kb.press('d')
        time.sleep(0.020)
        self.kb.release('d')
        time.sleep(0.010)









