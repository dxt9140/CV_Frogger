"""
Hopefully this becomes the main file for Frogger.
"""

import configparser
import os, shutil
import sys
import threading
import time
import subprocess
from src.definitions import *
from src.screen_cap import run
from src.screen_cap import find_frogger_main_menu
from pynput.keyboard import Controller, Key
import pynput.mouse as ms


class EmulatorThread(threading.Thread):

    def __init__(self, kb):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.kb = kb
        self.should_stop = False
        self.running = False

    def run(self):
        try:
            pipe = subprocess.Popen(PROJECT_DIR + "\\blueMSX.exe")
        except WindowsError:
            print("Exception thrown when opening pipe. Exiting.")
            return

        # clear the screenshots
        if os.path.isdir("../Screenshots"):
            shutil.rmtree("../Screenshots")

        print("Got here")
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

    def send_keys(self, keys):
        for key in keys:
            self.kb.press(key)
        for key in range(len(keys)-1, 0, -1):
            self.kb.release(key)


class WindowsDriver:

    def __init__(self):
        cf_parser = configparser.ConfigParser()
        path = PROJECT_DIR + '\\bluemsx.ini'
        cf_parser.read(path, encoding='utf-8')

        self.window_left = int(cf_parser['config']['video.windowX'])
        self.window_top = int(cf_parser['config']['video.windowY'])
        self.window_width = int(cf_parser['config']['video.fullscreen.width'])
        self.window_height = int(cf_parser['config']['video.fullscreen.height'])


def main():
    """
    @TODO Determine OS and begin Frogger automatically depending on the OS
    """
    kb = Controller()

    driver = None
    if OS in ['Windows']:
        driver = WindowsDriver()
    elif OS in ['Linux', 'Darwin']:
        _=_
        # driver = LinuxDriver()
    else:
        sys.exit(-1)

    # Execute MSX emulator
    Emulator = EmulatorThread(kb)
    Emulator.start()

    # Sleep for a sec to let the emulator boot
    print("Waiting for window...")
    time.sleep(1)

    timer = 0
    while Emulator.running is False:
        if timer == 10:
            print("Emulator failed to boot. Timing out.")
            sys.exit()
        time.sleep(1)
        timer += 1

    # Start the emulator.
    print("Press F9")
    kb.press(Key.f9.value)
    kb.release(Key.f9.value)

    """
    @TODO Might need to pause the game since screen shot might take a few seconds.
    """
    find_frogger_main_menu(driver)

    for i in range(20):
        Emulator.send_keys([Key.down.value])
        time.sleep(0.5)
        Emulator.send_keys([Key.down.value])
        time.sleep(0.5)
        Emulator.send_keys([Key.up.value])
        time.sleep(0.5)
        Emulator.send_keys([Key.up.value])
        time.sleep(0.5)

    """
    @TODO getting this screenshot should be in screen_cap.py at the top of the run method.
    Before run is called, make sure we get into the Frogger game
    """
    # might need to pause here
    run(driver, Emulator)

    # Sleep for a bit then exit the emulator
    time.sleep(1)
    print("Exiting the Emulator")
    Emulator.stop()

    Emulator.join()


if __name__ == '__main__':
    main()
