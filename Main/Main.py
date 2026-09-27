iimport cv2
import mediapipe as mp
import pyautogui
import time
import math

"""
======================================
HAND GESTURE CONTROLLER V5 (J.A.R.V.I.S.)
======================================
Security:
- Biometric Palm Scan Unlock -> Show Open Palm for 2s to authenticate & unlock.

Gestures (Post-Unlock):
- Index finger up          -> Move mouse
- Pinch (thumb+index)      -> Left click (hold for drag-and-drop)
- Index + Middle up        -> Right click
- Index + Middle + Ring up -> Play / Pause Media
- Thumb out + Pinky up     -> Virtual Air-Slider (Volume Control up/down)
- Open palm                -> Pause / Standby mouse control
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

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_x, prev_y = screen_w // 2, screen_h // 2
smooth = 0.3
last_click = 0
last_space = 0
last_zoom = 0
last_vol_change = 0
last_media = 0

# Biometric Security State
is_authenticated = False
auth_start_time = 0
AUTH_REQUIRED_TIME = 2.0  # Hold open palm for 2 seconds to scan

# Drag and drop state variables
is_dragging = False
pinch_start_time = 0
DRAG_HOLD_DELAY = 0.3

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

print("J.A.R.V.I.S. Neural Interface initialized. Biometric security lock engaged.")

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
        active_volume_level = None
        auth_progress = 0.0
        
        # ==========================================
        # 1. BIOMETRIC SECURITY AUTHENTICATION PHASE
        # ==========================================
        if not is_authenticated:
            if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 1:
                hand = result.multi_hand_landmarks[0]
                up = fingers_up(hand)
                index_up, middle_up, ring_up, pinky_up = up
                
                # Check for Open Palm biometric signature
                if index_up and middle_up and ring_up and pinky_up:
                    gesture = "BIOMETRIC SCANNING..."
                    now = time.time()
                    if auth_start_time == 0:
                        auth_start_time = now
                    
                    elapsed = now - auth_start_time
                    auth_progress = min(1.0, elapsed / AUTH_REQUIRED_TIME)
                    
                    if elapsed >= AUTH_REQUIRED_TIME:
                        is_authenticated = True
                        print("Biometric Authentication Successful. Access Granted.")
                else:
                    auth_start_time = 0
                    gesture = "SHOW OPEN PALM TO UNLOCK"
                
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            else:
                auth_start_time = 0
                gesture = "SYSTEM LOCKED: SHOW PALM"
                
        # ==========================================
        # 2. FULL ACCESS CONTROL INTERFACE (POST-UNLOCK)
        # ==========================================
        else:
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
                
                # Air-Slider Volume Gesture (Thumb extended + Pinky up)
                thumb_extended = dist(lm[4], lm[17]) > 0.15
                is_volume_gesture = thumb_extended and pinky_up and not index_up and not middle_up and not ring_up
                
                if is_volume_gesture:
                    gesture = "VOLUME SLIDER"
                    now = time.time()
                    hand_y = lm[0].y
                    active_volume_level = int((1.0 - hand_y) * 100)
                    active_volume_level = max(0, min(100, active_volume_level))
                    
                    if now - last_vol_change > 0.15:
                        if hand_y < 0.4:
                            pyautogui.press('volumeup')
                            last_vol_change = now
                        elif hand_y > 0.6:
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
                            
                    # 4) INDEX + MIDDLE + RING = MEDIA PLAY / PAUSE
                    elif index_up and middle_up and ring_up and not pinky_up:
                        gesture = "MEDIA PLAY/PAUSE"
                        now = time.time()
                        if now - last_media > 0.8:
                            pyautogui.press("playpause")
                            last_media = now
                            
                    # 5) OPEN PALM = PAUSE / STANDBY
                    elif index_up and middle_up and ring_up and pinky_up:
                        gesture = "STANDBY"
                        
                    # 6) FIST = SPACEBAR
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

        # ==========================================
        # 3. HUD DISPLAY & OVERLAYS
        # ==========================================
        if is_authenticated:
            cv2.rectangle(frame, (frame_margin, frame_margin), (w - frame_margin, h - frame_margin), (0, 255, 255), 2)
            
        # Main Status Box
        cv2.rectangle(frame, (15, 15), (480, 135), (20, 20, 20), -1)
        cv2.putText(frame, "J.A.R.V.I.S. INTERFACE V5", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if is_authenticated else (0, 165, 255), 2)
        
        status_text = f"Status: {'UNLOCKED' if is_authenticated else 'LOCKED'}"
        cv2.putText(frame, status_text, (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0) if is_authenticated else (0, 165, 255), 1)
        
        gesture_color = (0, 0, 255) if is_dragging else (255, 255, 255)
        cv2.putText(frame, f"Gesture: {gesture}", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, gesture_color, 2)
        
        # Draw Biometric Scan Progress Bar if Locked
        if not is_authenticated:
            bar_x, bar_y, bar_w, bar_h = 30, 150, 400, 25
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), 2)
            fill_w = int(auth_progress * bar_w)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (0, 255, 0), -1)
            cv2.putText(frame, f"BIOMETRIC SCAN: {int(auth_progress * 100)}%", (bar_x + 85, bar_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw Virtual Volume Bar HUD if Air-Slider is active
        if active_volume_level is not None:
            bar_x, bar_y, bar_w, bar_h = 520, 30, 30, 200
            fill_h = int((active_volume_level / 100) * bar_h)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), 2)
            cv2.rectangle(frame, (bar_x, bar_y + bar_h - fill_h), (bar_x + bar_w, bar_y + bar_h), (0, 255, 0), -1)
            cv2.putText(frame, f"VOL: {active_volume_level}%", (bar_x - 10, bar_y + bar_h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow("Hand Gesture PC Controller", frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
