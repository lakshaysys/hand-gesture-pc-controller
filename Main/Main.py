import cv2
import mediapipe as mp
import pyautogui
import time
import math

"""
==============================
HAND GESTURE PC CONTROLLER (V2)
==============================
Gestures:
Index finger up       -> move mouse
Pinch (thumb+index)   -> left click (or hold for drag-and-drop)
Two fingers up        -> right click
Open palm             -> pause/stop mouse control
Fist                  -> press Space
Press Q to quit.
"""

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

# Set standard responsive capture dimensions
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_x, prev_y = screen_w // 2, screen_h // 2
smooth = 0.3  # Adjusted responsiveness factor
last_click = 0
last_space = 0

# Drag and drop state variables
is_dragging = False
pinch_start_time = 0
DRAG_HOLD_DELAY = 0.3  # Time in seconds before a pinch becomes a drag

# Active frame boundaries to avoid edge-stretching
frame_margin = 150

def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def fingers_up(hand):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    states = []
    for tip, pip in zip(tips, pips):
        states.append(hand.landmark[tip].y < hand.landmark[pip].y)
    return states

print("Hand Gesture Controller active. Press 'q' on the video window to quit.")

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Error: Empty frame read from camera.")
            break
        
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        
        gesture = "NO HAND"
        
        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            lm = hand.landmark
            up = fingers_up(hand)
            index_up, middle_up, ring_up, pinky_up = up
            
            pinch = dist(lm[4], lm[8])
