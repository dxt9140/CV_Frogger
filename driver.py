"""
Hopefully this becomes the main file for Frogger.
"""

import os
import threading
import time
import subprocess
from pynput.keyboard import Controller, Key
import pynput.mouse as ms

F9 = 0x78


class EmulatorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        subprocess.run("blueMSX.exe")


def main():
    """
    @TODO Determine OS and begin Frogger automatically depending on the OS
    """
    # Execute MSX emulator
    Emulator = EmulatorThread()
    Emulator.start()

    kb = Controller()

    # Sleep for a sec to let the emulator boot
    print("Waiting for window...")
    time.sleep(5)

    # Start the emulator.
    print("Press F9")
    kb.press(Key.f9.value)
    kb.release(Key.f9.value)

    # Sleep for a bit then exit the emulator
    print("Exiting the Emulator")
    time.sleep(10)
    kb.press(Key(Key.shift))
    kb.press(Key(Key.esc))
    kb.release(Key(Key.esc))
    kb.release(Key(Key.shift))


if __name__ == '__main__':
    main()
