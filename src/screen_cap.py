"""
@author Dominick Taylor

File for screen capture.
"""

import cv2
import numpy as np
import math
import os
from mss import mss
from definitions import OS
from definitions import TEMPLATE_DIR
import PIL
from pynput.keyboard import Controller, Key
import time


def dist(p1, p2):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
def overlap(r1p1, r1p2, r2p1, r2p2):
    return (r1p1[1] < r2p2[1]) and (r1p2[1] > r2p1[1]) and (r1p1[0] < r2p2[0]) and (r1p2[0] > r2p1[0])


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
    frogs = ['Frog.png', 'Frog_Left.png', 'Frog_Right.png', 'Frog_Down.png', 'Frog_transparent.png']
    # elif OS in ['Windows']:
    #    templates = [TEMPLATE_DIR + 'Frog.png', TEMPLATE_DIR + 'Frog_Left.png', TEMPLATE_DIR + 'Frog_Right.png',
    # TEMPLATE_DIR + 'Frog_Down.png']

    enemies = ['Car1.png', 'Car2.png', 'Car3.png', 'Car4.png', 'Danger_small.png', 'Frog_win.png']
    surfaces = ['Wall_small.png', 'Start_small.png', 'Road.png']
    floaters = ['Gray_Toad_one.png', "Log_small.png", "Toad_one.png"]
    good_floaters_and_goal = ['Toad_one.png', 'Gray_Toad_one.png' , 'log_small.png', 'Goal.png']
    goal = ['Goal.png']

    while 1:

        # pause
        print("\nTick started...")
        Emulator.pause()
        
        found_frog = False
        
        img = cv2.cvtColor(np.array(screen_cap.grab(emu_region)), cv2.COLOR_BGRA2BGR)
        display = img.copy()

        up = ''
        down = ''
        left = ''
        right = ''
        
        lfrog = None
        rfrog = None
        lfrog_up = None
        rfrog_up = None
        
        up_okay = True
        up_is_water = False
        up_is_toad = False

        # find the frog (it can be facing up, left, right and down)
        for template in frogs:
            pts, img_rbg, t = template_match_minimal(img, TEMPLATE_DIR + template, threshold=0.6)
            pts = list(pts)
            # if len(pts) == 0:
                # pts, img_rbg, t = template_match_minimal_color(img, TEMPLATE_DIR + template, threshold=0.6)
                # pts = list(pts)
            if len(pts) != 0:
                pt = pts[0]
                lfrog = pt
                rfrog = (pt[0]+t.shape[1], pt[1]+t.shape[0])
                lfrog_up = (pt[0], pt[1]-t.shape[0]-2)
                rfrog_up = (pt[0]+t.shape[1], pt[1]-7)
                cv2.rectangle(display, lfrog, rfrog, (0, 255, 0), -1)
                cv2.rectangle(display, lfrog_up, rfrog_up, (0, 255, 0), 1)
                #print("Max: " + str(np.max(display[lfrog_up[0]:rfrog_up[0],lfrog_up[1]:rfrog_up[1],0])))
                print("Blue Max: " + str(np.max(display[lfrog_up[1]:rfrog_up[1],lfrog_up[0]:rfrog_up[0],0])))
                if np.max(display[lfrog_up[1]:rfrog_up[1],lfrog_up[0]:rfrog_up[0],0]) > 240:
                            print("Water collision detected!")
                            up_is_water = True
                            up_okay = False
                            y = rfrog_up[0]+1
                            x = rfrog_up[1]+1
                # for x in range(lfrog_up[1], rfrog_up[1]):
                    # for y in range(lfrog_up[0], rfrog_up[0]):
                        # pixel = display[y,x]
                        # if int(pixel[0]) > 200 and pixel[1] < 30 and pixel[2] < 30:
                            # #print(pixel, x, y)
                            # print("Water collision detected!")
                            # up_is_water = True
                            # up_okay = False
                            # y = rfrog_up[0]+1
                            # x = rfrog_up[1]+1
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
            pts, img_rbg, t = template_match_minimal(img, TEMPLATE_DIR + 'Dead_Frog.png', threshold=0.7)
            if pts:
                pt = pts[0]
                print("Dead Frog Found at " + str(pt))
                up_okay = False
                cv2.rectangle(display, pt, (pt[0]+t.shape[1], pt[1]+t.shape[0]), (0, 0, 0), 1)
                # remove_screenshot()
                # return 'Dead Frog', '_', '_', '_'
            else:
                # no frog detected, return all _
                print("No Frog Found")
                # remove_screenshot()
                # return '_', '_', '_', '_'

        # for template in surfaces:
            # pts, img, t = template_match_minimal_color(img, TEMPLATE_DIR + template, threshold=0.95)  # Don't change pls
            # if pts:
                # ul = top_left(pts)
                # ur = get_upper_left_of_rightmost(pts)
                # cv2.rectangle(display, ul, (ur[0]+t.shape[1], ur[1]+t.shape[0]), (255, 255, 0), 1)

        #if up_is_water:
        for template in good_floaters_and_goal:
            wadj = 5 if template[0] == 'G' else 5
            pts, img, t = template_match_minimal_color(img, TEMPLATE_DIR + template, threshold=0.7)
            if pts:
                uniques = get_all_upper_lefts(pts, t.shape)
                for pt in uniques:
                    right_ul = get_sequential_rightmost(pts, pt, t.shape)
                    cv2.rectangle(display, (pt[0]+wadj,pt[1]), (right_ul[0]+t.shape[1]-wadj, right_ul[1]+t.shape[0]), (255, 255, 0), 1)
                    if found_frog and up_is_water and not up_okay:
                        if overlap(lfrog_up, rfrog_up, (pt[0]+wadj,pt[1]), (right_ul[0]+t.shape[1]-wadj, right_ul[1]+t.shape[0])):
                            print("Predicted safe footing!")
                            up_okay = True
                            if template[0] == 'T':
                                up_is_toad = True

        for template in enemies:
            wadj = 5 if template[0] == 'C' else 0
            pts, img, t = template_match_minimal(img, TEMPLATE_DIR + template, threshold=0.7)
            if pts:
                uniques = get_all_upper_lefts(pts, t.shape)
                for pt in uniques:
                    cv2.rectangle(display, pt, (pt[0]+t.shape[1]+wadj, pt[1]+t.shape[0]), (0, 0, 255), 1)
                    if found_frog and up_okay:
                        if overlap(lfrog_up, rfrog_up, pt, (pt[0]+t.shape[1]+wadj, pt[1]+t.shape[0])):
                            print("Predicted enemy collision!")
                            up_okay = False
                            
                    

        # for template in goal:
            # pts, img, t = template_match_minimal_color(img, TEMPLATE_DIR + template, threshold=0.7)
            # if pts:
                # uniques = get_all_upper_lefts(pts, t.shape)
                # for pt in uniques:
                    # cv2.rectangle(display, pt, (pt[0]+t.shape[1], pt[1]+t.shape[0]), (0, 255, 255), 1)

        cv2.imshow(driver.win_name, display)
        cv2.waitKey(1)

        # play
        Emulator.pause()
        if found_frog and up_okay:
            print("Proceeding.")
            Emulator.up()
            if up_is_toad:
                time.sleep(1)
                Emulator.up()
                up_is_toad = False
        time.sleep(0.050)
        


def get_upper_left_of_rightmost(pts):
    if type(pts) is tuple:
        l = list()
        l.append(pts)
        processing = l
    else:
        processing = pts

    pt = None
    for p in processing:
        if pt is None or p[1] < pt[1]:
            pt = p
        elif p[0] > pt[0]:
            pt = p

    return pt


def get_sequential_rightmost(pts, ul, shape, bias=5):
    left = ul
    right = ul
    for pt in pts:
        if (pt[1] <= left[1] + bias and pt[1] >= left[1] - bias) \
                and pt[0] >= left[0] and pt[0] <= left[0] + shape[0] + bias:
            left = right
            right = pt

    return right


def remove_sequential_matches(pts, ul, shape, bias=5):
    keep = list()
    left = ul
    for pt in pts:
        # If point is not a sequential match of the ul, keep it
        # if pt[1] in range(left[1] - bias, left[1] + bias) \
        #        and pt[0] >= left[0] and pt[0] <= left[0] + shape[0] + bias:
        #    left = pt
        #    continue

        # If the distance between the point is a multiple of the shape, it is probably sequential
        if pt[1] in range(left[1] - bias, left[1] + bias) and abs(pt[0]-ul[0]) % shape[0]+bias > bias:
            continue

        if pt[0] == ul[0] and pt[1] == ul[1]:
            continue

        keep.append(pt)

    return keep


def find_sequential_texture_upper_left(pts, shape):
    if type(pts) is tuple:
        l = list()
        l.append(pts)
        processing = l
    else:
        processing = pts

    matches = list()
    while processing:
        left = top_left(pts)
        matches.append(left)
        processing = remove_sequential_matches(processing, left, shape)

    return matches


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
            # if dist(max, p) < dist(max, (max[0]+shape[1], max[1]+shape[0])):
            #    continue
            if p[0] > max[0] and p[0] < max[0] + shape[0]:
                continue

            if p[1] < max[1] and p[1] > max[1] - shape[1]:
                continue

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
    threshold = 0.9
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
        threshold = 0.9
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


def template_match_minimal(img, template, threshold=0.9):
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


def template_match_minimal_color(img, template, threshold=0.9):
    if type(img) is str:
        img = cv2.imread(img)

    if type(template) is str:
        template = cv2.imread(template)

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    pt = zip(*loc[::-1])

    return list(pt), img, template


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

        if pt:
            break

    return True

