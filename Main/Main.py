import cv2
import mediapipe as mp
import pyautogui
import time
import math

"""
==============================
HAND GESTURE PC CONTROLLER
==============================
Gestures:
Index finger up       -> move mouse
Pinch (thumb+index)   -> left click
Two fingers up        -> right click
Open palm             -> pause/stop mouse control
Fist                  -> press Space
Press Q to quit.
"""

pyautogui.PAUSE = 0.02
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()
    
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_x, prev_y = screen_w // 2, screen_h // 2
smooth = 0.25
last_click = 0
last_space = 0

def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def fingers_up(hand):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    states = []
    for tip, pip in zip(tips, pips):
        states.append(hand.landmark[tip].y < hand.landmark[pip].y)
    return states

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.65,
    min_tracking_confidence=0.65
) as hands:
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        
        gesture = "NO HAND"
        
        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            lm = hand.landmark
            up = fingers_up(hand)
            index_up, middle_up, ring_up, pinky_up = up
            
            pinch = dist(lm[4], lm[8])
            
            # 1) INDEX ONLY = MOUSE MOVE
            if index_up and not middle_up and not ring_up and not pinky_up:
                gesture = "MOVE"
                x = int(lm[8].x * screen_w)
                y = int(lm[8].y * screen_h)
                prev_x = int(prev_x + (x - prev_x) * smooth)
                prev_y = int(prev_y + (y - prev_y) * smooth)
                pyautogui.moveTo(prev_x, prev_y)
            
            # 2) PINCH = LEFT CLICK
            if pinch < 0.055:
                gesture = "LEFT CLICK"
                now = time.time()
                if now - last_click > 0.65:
                    pyautogui.click()
                    last_click = now
                    
            # 3) INDEX + MIDDLE = RIGHT CLICK
            elif index_up and middle_up and not ring_up and not pinky_up:
                gesture = "RIGHT CLICK"
                now = time.time()
                if now - last_click > 0.65:
                    pyautogui.rightClick()
                    last_click = now
                    
            # 4) OPEN PALM = STOP
            elif index_up and middle_up and ring_up and pinky_up:
                gesture = "PAUSE"
                
            # 5) FIST = SPACE
            elif not index_up and not middle_up and not ring_up and not pinky_up:
                gesture = "SPACE"
                now = time.time()
                if now - last_space > 0.8:
                    pyautogui.press("space")
                    last_space = now
                    
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            
        # HUD
        cv2.rectangle(frame, (15, 15), (430, 100), (15, 15, 15), -1)
        cv2.putText(frame, "HAND PC CONTROLLER", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Gesture: {gesture}", (30, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        
        cv2.imshow("Hand Gesture PC Controller", frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
