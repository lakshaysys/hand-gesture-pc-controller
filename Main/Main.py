import cv2
import mediapipe as mp
import pyautogui
import time
import math

"""
======================================
J.A.R.V.I.S. HAND GESTURE CONTROLLER V4
======================================
Gestures:
- Index finger up          -> Move mouse
- Pinch (thumb+index)      -> Left click (hold for drag-and-drop)
- Index + Middle up        -> Right click
- Thumb out + Pinky up     -> Virtual Air-Slider (Volume Control up/down)
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
last_vol_change = 0

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

print("J.A.R.V.I.S. Neural Interface active. Press 'q' on the video window to quit.")

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
        active_volume_level = None  # For visual HUD bar
        
        # TWO-HAND GESTURES (Zoom In / Zoom Out)
        if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
            hand1 = result.multi_hand_landmarks[0]
            hand2 = result.multi_hand_landmarks[1]
            
            hands_dist = dist(hand1.landmark[0], hand2.landmark[0])
            
            now = time.time()
            if now - last_zoom > 0.4:
                if hands_dist < 0.2:
                    gesture = "ZOOM IN"
                    pyautogui.hotkey('ctrl', '+')
                    last_zoom = now
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
            
            # Check for Shaka / Air-Slider Gesture (Thumb extended + Pinky up, Index/Middle/Ring down)
            thumb_extended = dist(lm[4], lm[17]) > 0.15
            is_volume_gesture = thumb_extended and pinky_up and not index_up and not middle_up and not ring_up
            
            if is_volume_gesture:
                gesture = "VOLUME SLIDER"
                now = time.time()
                # Map vertical position of wrist (landmark 0) to volume steps
                hand_y = lm[0].y  # 0.0 is top, 1.0 is bottom
                active_volume_level = int((1.0 - hand_y) * 100) # Invert so up is higher volume
                active_volume_level = max(0, min(100, active_volume_level))
                
                if now - last_vol_change > 0.15:
                    if hand_y < 0.4:  # Hand is high up -> Volume Up
                        pyautogui.press('volumeup')
                        last_vol_change = now
                    elif hand_y > 0.6:  # Hand is low down -> Volume Down
                        pyautogui.press('volumedown')
                        last_vol_change = now
                        
            # 1) PINCH LOGIC (CLICK vs DRAG AND DROP)
            elif pinch < 0.05:
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
        cv2.rectangle(frame, (15, 15), (460, 120), (20, 20, 20), -1)
        cv2.putText(frame, "J.A.R.V.I.S. INTERFACE V4", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        gesture_color = (0, 0, 255) if is_dragging else (255, 255, 255)
        cv2.putText(frame, f"Gesture: {gesture}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.65, gesture_color, 2)
        
        # Draw Virtual Volume Bar HUD if Air-Slider is active
        if active_volume_level is not None:
            bar_x, bar_y, bar_w, bar_h = 500, 30, 30, 200
            fill_h = int((active_volume_level / 100) * bar_h)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), 2)
            cv2.rectangle(frame, (bar_x, bar_y + bar_h - fill_h), (bar_x + bar_w, bar_y + bar_h), (0, 255, 0), -1)
            cv2.putText(frame, f"VOL: {active_volume_level}%", (bar_x - 10, bar_y + bar_h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow("Hand Gesture PC Controller", frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
                
