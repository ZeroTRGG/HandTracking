"""
@author Zero
"""

import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import screen_brightness_control as scb
import os

cap = cv2.VideoCapture(0) 

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volMin, volMax = volume.GetVolumeRange()[:2]

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    lmList = []

    if results.multi_hand_landmarks: 
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy]) 
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)
            
    if lmList != []:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[20][1], lmList[20][2]
        x4, y4 = lmList[16][1], lmList[16][2]

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)  
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED) 
        cv2.circle(img, (x3, y3), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x4, y4), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.line(img, (x3, y3), (x1, y1), (255, 0, 255), 3)
        cv2.line(img, (x4, y4), (x1, y1), (255, 0, 255), 3)

        length = hypot(x2 - x1, y2 - y1)
        light = hypot(x3 - x1, y3 - y1)
        pc =  hypot(x4 - x1, y4 - y1)

        if pc <= 25:
            os.system("shutdown /s /t 1")

        vol = np.interp(length, [15, 220], [volMin, volMax])
        bright = np.interp(light, [25, 145], [0, 100])
        bright = int(bright)

        volume.SetMasterVolumeLevel(vol, None)
        scb.set_brightness(bright)
        cv2.imshow('Image', img) 

    if cv2.waitKey(1) & 0xff == ord('q'): 
        break
