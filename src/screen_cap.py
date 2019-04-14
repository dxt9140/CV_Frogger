"""
@author Dominick Taylor

File for screen capture.
"""

import cv2
import numpy as np
import os
from mss import mss
from src.definitions import OS
from src.definitions import TEMPLATE_DIR


def run(driver, Emulator):
    # screen_cap = mss()
    # emu_region = {'top': driver.window_top, 'left': driver.window_left,
    #               'width': driver.window_width, 'height': driver.window_height}
    #
    # cv2.namedWindow('Agent Capture', cv2.WINDOW_NORMAL)
    # # cv2.resizeWindow('Agent Capture', driver.window_width, driver.window_height)
    #
    # while 1:
    #     img = np.array(screen_cap.grab(emu_region))
    #     # img = Image.frombytes('RGB', (driver.window_width, driver.window_height), screen_cap.img)
    #     cv2.resize(img, (800, 800))
    #     cv2.imshow('Agent Capture', img)
    #     if cv2.waitKey(10) == ord('q'):
    #         break
    #
    # cv2.destroyAllWindows()

    # get the game screen
    # this will create a Screenshots folder and save the game screen as a .png file
    Emulator.take_screenshot()

    # grab the screen shot and delete when it is done
    img = '../Screenshots/Frogger_1983_Konami_J_0000.png'

    templates = None
    if OS in ['Linux', 'Darwin']:
        templates = ['../Templates/Frog.png', '../Templates/Frog_Left.png', '../Templates/Frog_Right.png',
                     '../Templates/Frog_Down.png']
    elif OS in ['Windows']:
        templates = [TEMPLATE_DIR + 'Frog.png', TEMPLATE_DIR + 'Frog_Left.png', TEMPLATE_DIR + 'Frog_Right.png',
                     TEMPLATE_DIR + 'Frog_Down.png']

    if templates is None:
        return
    else:
        print(templates)

    found_frog = False

    up = ''
    down = ''
    left = ''
    right = ''

    # find the frog (it can be facing up, left, right and down)
    for template in templates:
        pt, img_rbg, t = template_match(img, template)
        if pt != 0:
            up, down, left, right = match_neighbors(pt, img_rbg, t)
            found_frog = True
            break

    # found the frog, find what it on its up, down, right and left (return in this sequence)
    # if there aren't any object or it cannot be matched, it will return _
    if found_frog:
        print("Up\t" + up)
        print("Down\t" + down)
        print("Right\t" + right)
        print("Left\t" + left)
        remove_screenshot()
        return up, down, right, left
    else:
        # no frog found, there might be a dead frog
        # if it is a dead frog, it will return Dead Frog and _ for others
        pt, img_rbg, t = template_match(img, '../Templates/Dead_Frog.png')
        if pt != 0:
            print("Dead Frog Found")
            remove_screenshot()
            return 'Dead Frog', '_', '_', '_'
        else:
            # no frog detected, return all _
            print("No Frog Found")
            remove_screenshot()
            return '_', '_', '_', '_'

    # cv2.imshow('Template Matching', img_rbg)
    # cv2.waitKey(0)


def remove_screenshot():
    # remove the screen shot
    os.remove("../Screenshots/Frogger_1983_Konami_J_0000.png")


def template_match(img, template):
    """
    @TODO Can you briefly describe what the return values are?
    :param img:
    :param template:
    :return:
    """

    if type(img) is str:
        img_rbg_org = cv2.imread(img)
    else:
        img_rbg_org = img

    # crop the score section
    img_rbg = img_rbg_org[48:432, 48:400]
    img_gray = cv2.cvtColor(img_rbg, cv2.COLOR_BGR2GRAY)

    t = cv2.imread(template, 0)
    res = cv2.matchTemplate(img_gray, t, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        return pt, img_rbg, t

    return 0, 0, 0


# find what is on the up, down, left and right
# if nothing is found it will return _
def match_neighbors(pt, img_rbg, t):
    w, h = t.shape[::-1]

    # cv2.rectangle(img_rbg, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    up = '_'
    down = '_'
    left = '_'
    right = '_'

    # up
    if pt[1]-h > 0:
        # cv2.rectangle(img_rbg, (pt[0], pt[1] - h), (pt[0] + w, pt[1]-3), (0, 255, 0), 2)
        up = img_rbg[pt[1]-h:pt[1]-3, pt[0]:pt[0]+w]
        # print("UP")
        # cv2.imwrite("up.png", up)
        up = find_object(up)

    # down
    if pt[1]+h+h < 384:
        # cv2.rectangle(img_rbg, (pt[0], pt[1] + h), (pt[0] + w, pt[1] + h + h - 3), (0, 255, 0), 2)
        down = img_rbg[pt[1]+h: pt[1]+h+h-3, pt[0]:pt[0]+w]
        # print("Down")
        # cv2.imwrite("down.png", down)
        down = find_object(down)

    # right
    if pt[0]+w+w < 352:
        # cv2.rectangle(img_rbg, (pt[0] + w, pt[1]), (pt[0] + w + w, pt[1] + h-3), (0, 255, 0), 2)
        right = img_rbg[pt[1]:pt[1]+h-3, pt[0]+w:pt[0]+w+w]
        # print("Right")
        # cv2.imwrite("right.png", right)
        right = find_object(right)

    # left
    if pt[0] - w > 0:
        # cv2.rectangle(img_rbg, (pt[0] - w, pt[1]), (pt[0], pt[1] + h - 3), (0, 255, 0), 2)
        left = img_rbg[pt[1]:pt[1]+h-3, pt[0]-w:pt[0]]
        # print("Left")
        # cv2.imwrite("left.png", left)
        left = find_object(left)

    # cv2.imshow('Template Matching', img_rbg)
    # cv2.waitKey(0)

    return up, down, right, left


# helper function to find the object
def find_object(object):
    images_to_read = {"../Templates/Water.png", "../Templates/Water1.png", "../Templates/Water2.png",
                      "../Templates/Start.png", "../Templates/Log.png", "../Templates/Toad.png",
                      "../Templates/Gray_Toad.png", "../Templates/Wall.png", "../Templates/Car1.png",
                      "../Templates/Car2.png", "../Templates/Car3.png", "../Templates/Car4.png",
                      "../Templates/Danger.png", "../Templates/Goal.png"}
    images = []

    found_object = False

    for img in images_to_read:
        i = cv2.imread(img)
        images.append(i)

        img_gray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)

        t = cv2.cvtColor(object, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(img_gray, t, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            found_object = True
            break

        if found_object:
            # is it really water?
            if img == "../Templates/Water.png":
                red, blue, green = cv2.split(object)
                intensity = np.sum(object.sum())
                # the object is black -> ROAD
                if np.sum(red)/intensity == np.sum(blue)/intensity and np.sum(red)/intensity == np.sum(green)/intensity:
                    img = "../Templates/Road.png"
            obj = img.split('/')[2].split('.')[0]
            return obj

    return '_'


def template_match_minimal(img, template):
    if type(img) is str:
        img = cv2.imread(img)

    if type(template) is str:
        template = cv2.imread(template)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    t_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img_gray, t_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        return pt, img, template

    return 0, 0, 0


def find_frogger_main_menu(driver):
    template = TEMPLATE_DIR + "main_menu.png"
    template = cv2.imread(template)

    screen_cap = mss()
    emu_region = {'top': driver.window_top+150, 'left': driver.window_left+75,
                  'width': driver.window_width, 'height': driver.window_height}

    cv2.namedWindow('Agent Capture', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Agent Capture', driver.window_width, driver.window_height)

    while 1:
        img = np.array(screen_cap.grab(emu_region))
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cv2.resize(img, (800, 800))
        # cv2.imshow('Agent Capture', img)
        # if cv2.waitKey(10) == ord('q'):
        #    break

        pt, img_rgb, t = template_match_minimal(img, template)

        if img_rgb is 0:
            img_rgb = np.ones_like(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        cv2.imshow('Agent Capture', img_rgb)
        cv2.waitKey(1)

        if pt:
            break

    cv2.destroyAllWindows()
    return True
