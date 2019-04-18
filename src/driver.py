"""
Hopefully this becomes the main file for Frogger.
"""

import configparser
import os, shutil
import sys
import threading
import time
import subprocess
import cv2
from src.definitions import *
from src.screen_cap import run
from src.screen_cap import find_frogger_main_menu
from src.screen_cap import find_frogger_game_screen
from pynput.keyboard import Controller, Key
import pyautogui as pg
import pynput.mouse as ms


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
            # self.kb.press(Key(Key.shift))
            # self.kb.press(Key(Key.esc))
            # self.kb.release(Key(Key.esc))
            # self.kb.release(Key(Key.shift))
            pg.press(['shift', 'esc'])
        self._stop_event.set()

        self.running = False

    def stop(self):
        self.should_stop = True

    def is_stopped(self):
        return self._stop_event.is_set()

    def take_screenshot(self):
        # self.kb.press(Key.print_screen.value)
        # self.kb.release(Key.print_screen.value)
        pg.press(['printscrn'])

    def send_keys(self, keys):
        print(keys)
        for key in keys:
            self.kb.press(key)
            self.kb.release(key)


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

    def send_keys(self, keys):
        for key in keys:
            self.kb.press(key)
            self.kb.release(key)


class WindowsDriver:

    def __init__(self):
        cf_parser = configparser.ConfigParser()
        path = PROJECT_DIR + '\\bluemsx.ini'
        cf_parser.read(path, encoding='utf-8')

        self.window_left = int(cf_parser['config']['video.windowX']) + 75
        self.window_top = int(cf_parser['config']['video.windowY']) + 125
        self.window_width = int(cf_parser['config']['video.fullscreen.width'])
        self.window_height = int(cf_parser['config']['video.fullscreen.height'])

        cv2.namedWindow('Agent Capture', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Agent Capture', self.window_width, self.window_height)

        self.win_name = 'Agent Capture'


class LinuxDriver:

    def __init__(self):
        self.window_width = 640
        self.window_height = 480

        cv2.namedWindow('Agent Capture', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Agent Capture', self.window_width, self.window_height)

        self.win_name = 'Agent Capture'

    def find_screen(self):
        _ = None


def main():
    """
    @TODO Determine OS and begin Frogger automatically depending on the OS
    """
    kb = Controller()

    if OS in ['Windows']:
        driver = WindowsDriver()
    elif OS in ['Linux', 'Darwin']:
        driver = LinuxDriver()
    else:
        sys.exit(-1)

    # Execute MSX emulator
    if OS in ['Windows']:
        # Emulator = BlueMSX(kb)
        Emulator = BlueMSX(kb)
    elif OS in ['Linux']:
        # Emulator = OpenMSX(kb)
        Emulator = OpenMSX(kb)
    else:
        sys.exit(-1)
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
    # keyboard.press_and_release('F9')

    print("Waiting for main menu")
    find_frogger_main_menu(driver)

    time.sleep(1)
    # Option 3 in the main menu is Single Player with KB
    # Emulator.send_keys(['3'])
    kb.press('3')
    kb.release('3')

    print("Waiting for game screen")
    find_frogger_game_screen(driver)
    time.sleep(1)

    print("Found game screen")
    # for i in range(5):
    #    Emulator.send_keys(['a'])
    #    Emulator.send_keys(['a'])
    #    Emulator.send_keys(['d'])
    #    Emulator.send_keys(['d'])

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
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
