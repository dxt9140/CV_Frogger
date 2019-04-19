"""
@author Dominick Taylor

File for screen capture.
"""

import cv2
import numpy as np
import os
from mss import mss
from definitions import OS
from definitions import TEMPLATE_DIR
import PIL
from pynput.keyboard import Controller, Key


def run(driver, Emulator):
    screen_cap = mss()
    emu_region = {'top': driver.window_top, 'left': driver.window_left,
                  'width': driver.window_width, 'height': driver.window_height}
    #
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
    # Emulator.take_screenshot()

    # grab the screen shot and delete when it is done
    # img = '../Screenshots/Frogger_1983_Konami_J_0000.png'

    # if OS in ['Linux', 'Darwin', 'Windows']:
    frogs = ['Frog.png', 'Frog_Left.png', 'Frog_Right.png', 'Frog_Down.png']
    # elif OS in ['Windows']:
    #    templates = [TEMPLATE_DIR + 'Frog.png', TEMPLATE_DIR + 'Frog_Left.png', TEMPLATE_DIR + 'Frog_Right.png',
    # TEMPLATE_DIR + 'Frog_Down.png']

    enemies = ['Car1.png', 'Car2.png', 'Car3.png', 'Car4.png', 'Danger.png']
    surfaces = ['Wall.png', 'Start.png', 'Road.png', 'Gray_Toad.png']
    goal = ['Goal.png']

    found_frog = False

    while 1:
        img = cv2.cvtColor(np.array(screen_cap.grab(emu_region)), cv2.COLOR_BGRA2BGR)
        display = img.copy()

        # pause
        Emulator.pause()

        up = ''
        down = ''
        left = ''
        right = ''

        # find the frog (it can be facing up, left, right and down)
        for template in frogs:
            pts, img_rbg, t = template_match_minimal(img, TEMPLATE_DIR + template, threshold=0.6)
            pts = list(pts)
            if len(pts) != 0:
                pt = pts[0]
                cv2.rectangle(display, pt, (pt[0]+t.shape[1], pt[1]+t.shape[0]), (0, 255, 0), -1)
                # up, down, left, right = match_neighbors(pt, img_rbg, t)
                found_frog = True
                break

        # found the frog, find what it on its up, down, right and left (return in this sequence)
        # if there aren't any object or it cannot be matched, it will return _
        if found_frog:
            print("Found frog!")
            # print("Up\t" + up)
            # print("Down\t" + down)
            # print("Right\t" + right)
            # print("Left\t" + left)
            # remove_screenshot()
            # return up, down, right, left
        else:
            # no frog found, there might be a dead frog
            # if it is a dead frog, it will return Dead Frog and _ for others
            pts, img_rbg, t = template_match_minimal(img, TEMPLATE_DIR + 'Dead_Frog.png')
            if pts:
                pt = pts[0]
                print("Dead Frog Found at " + str(pt))
                cv2.rectangle(display, pt, (pt[0]+t.shape[1], pt[1]+t.shape[0]), (0, 0, 0), 1)
                # remove_screenshot()
                # return 'Dead Frog', '_', '_', '_'
            else:
                # no frog detected, return all _
                print("No Frog Found")
                # remove_screenshot()
                # return '_', '_', '_', '_'

        for template in surfaces:
            pts, img, t = template_match_minimal_color(img, TEMPLATE_DIR + template)
            if pts:
                uniques = get_all_upper_lefts(pts, t.shape)
                for pt in uniques:
                    cv2.rectangle(display, pt, (pt[0]+t.shape[1], pt[1]+t.shape[0]), (255, 0, 0), 1)

        for template in enemies:
            pts, img, t = template_match_minimal(img, TEMPLATE_DIR + template)
            if pts:
                # TODO Template match returns multiple points for same instance of enemy. Can we trim
                # the templates? Also, consider using the alpha channel

                # TODO Update: Alpha channel doesnt play with with opencv. Maybe we can figure out if a returned
                # point has already been outlined if it is within the bounds of the template +/- 5px or so

                uniques = get_all_upper_lefts(pts, t.shape)
                for pt in uniques:
                    cv2.rectangle(display, pt, (pt[0]+t.shape[1], pt[1]+t.shape[0]), (0, 0, 255), 1)

        for template in goal:
            pts, img, t = template_match_minimal_color(img, TEMPLATE_DIR + template)

            if pts:
                uniques = get_all_upper_lefts(pts, t.shape)
                for pt in uniques:
                    cv2.rectangle(display, pt, (pt[0]+t.shape[1], pt[1]+t.shape[0]), (0, 255, 255), 1)

        cv2.imshow(driver.win_name, display)
        cv2.waitKey(1)

        # play
        Emulator.pause()
        print()


def get_all_upper_lefts(pts, shape):
    # For all points in a set, find the upper left of each instance with $shape

    # Handles case where input pts is only 1 tuple
    if type(pts) is tuple:
        l = list()
        l.append(pts)
        processing = l
    else:
        processing = pts

    matches = list()

    while processing:
        keep = list()
        max = top_left(processing)
        matches.append(max)
        for p in processing:
            # If x is inside the x boundary
            if p[0] > max[0] and p[0] < max[0] + shape[0]:
                continue

            # If y is inside the y boundary
            if p[1] < max[1] and p[1] > max[1] + shape[1]:
                continue

            # If p equals max, it either IS max or a duplicate. Ignore it
            if p[0] == max[0] and p[1] == max[1]:
                continue

            # Otherwise, hold onto it for a while
            keep.append(p)

        processing = keep

    return matches


def top_left(pts):
    # Given a set of points, choose the one with the greatest y and least x
    chosen = None
    for p in pts:
        if chosen is None or p[1] > chosen[1]:
            chosen = p
        elif p[1] == chosen[1] and p[0] < chosen[0]:
            chosen = p
    return chosen


def remove_screenshot():
    # remove the screen shot
    os.remove("../Screenshots/Frogger_1983_Konami_J_0000.png")


def template_match(img, template):
    """
    :param img: input screen
    :param template: template to match
    :return: points which have greater than 0.8 threshold, input screen, template
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
    threshold = 0.6
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        return pt, img_rbg, t

    return 0, 0, 0


# find what is on the up, down, left and right
# if nothing is found it will return _
def match_neighbors(pt, img_rbg, t):
    print(t.shape)
    w, h, b = t.shape

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
        threshold = 0.6
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


def template_match_minimal(img, template, threshold=0.6):
    if type(img) is str:
        img = cv2.imread(img)

    if type(template) is str:
        template = cv2.imread(template)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    t_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img_gray, t_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    pt = zip(*loc[::-1])
    return list(pt), img, template
    # for pt in zip(*loc[::-1]):
    #   return pt, img, template


def template_match_minimal_color(img, template, threshold=0.8):
    if type(img) is str:
        img = cv2.imread(img)

    if type(template) is str:
        template = cv2.imread(template)

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        return pt, img, template

    return 0, img, template


def find_emulator_screen(driver):
    templates = ["digiblue_icon.png"]
    return find_object_with_templates(driver, templates, threshold=0.1)


def find_frogger_main_menu(driver):
    templates = ["main_menu.png"]
    return find_object_with_templates(driver, templates, threshold=0.9)


def find_frogger_game_screen(driver):
    # Actually, let's just find the frog
    templates = ['Time_Box.png', 'Frog_transparent.png', 'Wall.png']
    find_object_with_templates(driver, templates, threshold=0.5)


def find_object_with_templates(driver, templates, color=False, threshold=0.8):
    for t in range(len(templates)):
        if type(templates[t]) is str:
            templates[t] = cv2.imread(TEMPLATE_DIR + templates[t])

    screen_cap = mss()
    emu_region = {'top': driver.window_top, 'left': driver.window_left,
                  'width': driver.window_width, 'height': driver.window_height}

    # Reversed the logic. Assume we will exit right away. If any of the above templates are not matched,
    # make stop False. Thus, the loop will continue until no templates are not matched
    # (Read: All templates are matched).
    stop = True
    while 1:
        img = np.array(screen_cap.grab(emu_region))

        for t in templates:
            if color:
                pt, img_rgb, t = template_match_minimal_color(img, t, threshold=threshold)
            else:
                pt, img_rgb, t = template_match_minimal(img, t, threshold=threshold)

            if not pt:
                stop = False

        if stop:
            break
        else:
            stop = True

        cv2.imshow(driver.win_name, img)
        cv2.waitKey(1)

    return True

