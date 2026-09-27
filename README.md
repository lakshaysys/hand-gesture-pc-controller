# 🌟🖐️ Advanced Hand Gesture PC Controller (V5)  🖐️🌟

<p align="center">
  <em>Transform your workspace with next-generation computer vision, biometric security lock, media control, and touchless desktop interaction.</em>
</p>

---

## 🚀 Overview

Welcome to **Version 5** of the **Hand Gesture PC Controller**! Featuring a military-grade **Biometric Palm Scan Security Lock**, **Media Playback Control**, **Virtual Air-Slider Volume Control**, and multi-hand zoom capabilities, this update turns your webcam into a fully secured, contactless virtual command center.

---

## ✨ Comprehensive Gesture Control Matrix

| Gesture Command | Primary System Action | Visual Representation | Technical Trigger Logic |
| :--- | :--- | :--- | :--- |
| **Open Palm (Hold 2s)** | **Biometric Unlock** | 🖐️⏳ | Holds steady open palm for 2 seconds to pass security authentication. |
| **Index Finger Only** | **Smooth Mouse Navigation** | ☝️ | Tracks single index landmark inside bounded active zone coordinates. |
| **Thumb + Index Pinch (Tap)** | **Left-Click Execution** | 🤏 | Quick Euclidean distance drop below threshold triggers click. |
| **Thumb + Index Pinch (Hold)**| **Drag-and-Drop Feature** | 🤏⏱️ | Holding pinch past 0.3 seconds engages `mouseDown` for dragging items. |
| **Index + Middle Fingers** | **Right-Click Contextual Menu** | ✌️ | Detects dual upper elevation state for secondary click actions. |
| **Index + Middle + Ring** | **Media Play / Pause** | 🖖 | Triggers system media playback toggle (Spotify, YouTube, VLC). |
| **Thumb Out + Pinky Up** | **Virtual Air-Slider (Volume)** | 🤙 | Shaka-style pose tracking vertical wrist position to change volume up/down. |
| **Fist Formation** | **Keyboard Spacebar Trigger** | ✊ | Closes all fingers entirely to execute automation commands. |
| **Two Hands Moving Apart** | **Zoom Out (-)** | 👐 | Tracks distance between dual wrists expanding to trigger screen zoom-out. |
| **Two Hands Clapping** | **Zoom In (+)** | 👏 | Brings both wrist landmarks close together to trigger screen zoom-in. |
| **Press 'Q' Key** | **Safe Application Exit** | ⌨️ | Gracefully terminates video capture loops and releases resources. |

---

## 📦 Installation & Setup

```bash
pip install opencv-python mediapipe pyautogui
python main.py
