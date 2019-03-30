"""
@author Dominick Taylor

File for screen capture.
"""

import cv2
import numpy as np
from PIL import Image
from mss import mss


def run(driver):
    screen_cap = mss()

    emu_region = {'top': driver.window_top, 'left': driver.window_left,
                  'width': driver.window_width+150, 'height': driver.window_height+100}

    cv2.namedWindow('Agent Capture', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('Agent Capture', driver.window_width, driver.window_height)

    while 1:
        img = np.array(screen_cap.grab(emu_region))
        # img = Image.frombytes('RGB', (screen_cap.width, screen_cap.height), screen_cap.img)
        cv2.resize(img, (800, 800))
        cv2.imshow('Agent Capture', img)
        if cv2.waitKey(10) == ord('q'):
            break

    cv2.destroyAllWindows()
