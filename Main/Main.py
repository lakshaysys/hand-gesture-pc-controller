import cv2
import mediapipe as mp
import pyautogui
import time
import math

"""
==============================
HAND GESTURE PC CONTROLLER (V3)
==============================
Gestures:
- Index finger up          -> Move mouse
- Pinch (thumb+index)      -> Left click (hold for drag-and-drop)
- Index + Middle up        -> Right click
- Open palm                -> Pause / Stop mouse control
- Fist                     -> Press Space
- Two hands moving apart   -> Zoom Out (-)
- Two hands clapping       -> Zoom In (+)
- Press Q to quit.
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
smooth = 0.3
last_click = 0
last_space = 0
last_zoom = 0

# Drag and drop state variables
is_dragging = False
pinch_start_time = 0
DRAG_HOLD_DELAY = 0.3

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

# Updated to detect up to 2 hands for zoom features
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
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
        
        # TWO-HAND GESTURES (Zoom In / Zoom Out)
        if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
            hand1 = result.multi_hand_landmarks[0]
            hand2 = result.multi_hand_landmarks[1]
            
            # Measure distance between wrists or center palms (using landmark 0 - wrist)
            hands_dist = dist(hand1.landmark[0], hand2.landmark[0])
            
            now = time.time()
            if now - last_zoom > 0.4:  # Cooldown to prevent spamming
                # Clap / Hands close together = Zoom In
                if hands_dist < 0.2:
                    gesture = "ZOOM IN"
                    pyautogui.hotkey('ctrl', '+')
                    last_zoom = now
                # Hands far apart = Zoom Out
                elif hands_dist > 0.6:
                    gesture = "ZOOM OUT"
                    pyautogui.hotkey('ctrl', '-')
                    last_zoom = now
            else:
                gesture = "TWO HANDS DETECTED"
                
            for hand in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                
        # SINGLE-HAND GESTURES
        elif result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 1:
            hand = result.multi_hand_landmarks[0]
            lm = hand.landmark
            up = fingers_up(hand)
            index_up, middle_up, ring_up, pinky_up = up
            
            pinch = dist(lm[4], lm[8])
            
            # 1) PINCH LOGIC (CLICK vs DRAG AND DROP)
            if pinch < 0.05:
                now = time.time()
                if pinch_start_time == 0:
                    pinch_start_time = now
                
                if not is_dragging and (now - pinch_start_time > DRAG_HOLD_DELAY):
                    pyautogui.mouseDown()
                    is_dragging = True
                
                if is_dragging:
                    gesture = "DRAGGING"
                    raw_x = lm[8].x * w
                    raw_y = lm[8].y * h
                    x = max(0, min(1, (raw_x - frame_margin) / (w - 2 * frame_margin))) * screen_w
                    y = max(0, min(1, (raw_y - frame_margin) / (h - 2 * frame_margin))) * screen_h
                    prev_x = int(prev_x + (x - prev_x) * smooth)
                    prev_y = int(prev_y + (y - prev_y) * smooth)
                    try:
                        pyautogui.moveTo(prev_x, prev_y)
                    except Exception:
                        pass
                else:
                    gesture = "PINCHING..."
            else:
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False
                
                if pinch_start_time > 0 and (time.time() - pinch_start_time <= DRAG_HOLD_DELAY):
                    now = time.time()
                    if now - last_click > 0.5:
                        pyautogui.click()
                        last_click = now
                
                pinch_start_time = 0
                
                # 2) INDEX ONLY = MOUSE MOVE
                if not is_dragging and index_up and not middle_up and not ring_up and not pinky_up:
                    gesture = "MOVE"
                    raw_x = lm[8].x * w
                    raw_y = lm[8].y * h
                    x = max(0, min(1, (raw_x - frame_margin) / (w - 2 * frame_margin))) * screen_w
                    y = max(0, min(1, (raw_y - frame_margin) / (h - 2 * frame_margin))) * screen_h
                    prev_x = int(prev_x + (x - prev_x) * smooth)
                    prev_y = int(prev_y + (y - prev_y) * smooth)
                    try:
                        pyautogui.moveTo(prev_x, prev_y)
                    except Exception:
                        pass
                
                # 3) INDEX + MIDDLE = RIGHT CLICK
                elif index_up and middle_up and not ring_up and not pinky_up:
                    gesture = "RIGHT CLICK"
                    now = time.time()
                    if now - last_click > 0.6:
                        pyautogui.rightClick()
                        last_click = now
                        
                # 4) OPEN PALM = STOP / PAUSE
                elif index_up and middle_up and ring_up and pinky_up:
                    gesture = "PAUSE"
                    
                # 5) FIST = SPACE
                elif not index_up and not middle_up and not ring_up and not pinky_up:
                    gesture = "SPACE"
                    now = time.time()
                    if now - last_space > 0.7:
                        pyautogui.press("space")
                        last_space = now
                    
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        else:
            if is_dragging:
                pyautogui.mouseUp()
                is_dragging = False
            pinch_start_time = 0
            
        # Draw motion boundary rectangle on HUD
        cv2.rectangle(frame, (frame_margin, frame_margin), (w - frame_margin, h - frame_margin), (0, 255, 255), 2)
        
        # HUD Display Overlay
        cv2.rectangle(frame, (15, 15), (450, 110), (20, 20, 20), -1)
        cv2.putText(frame, "HAND PC CONTROLLER V3", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        
        gesture_color = (0, 0, 255) if is_dragging else (255, 255, 255)
        cv2.putText(frame, f"Gesture: {gesture}", (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, gesture_color, 2)
        
        cv2.imshow("Hand Gesture PC Controller", frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
            
