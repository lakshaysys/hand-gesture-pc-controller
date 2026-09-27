# 🌟🖐️ Advanced Hand Gesture PC Controller (V4) 🖐️🌟

<p align="center">
  <em>Transform your workspace with next-generation computer vision, multi-hand tracking, and touchless desktop interaction.</em>
</p>

---

## 🚀 Overview

Welcome to the ultimate evolution of the **Hand Gesture PC Controller (V4)**! Powered by cutting-edge computer vision libraries like **OpenCV** and **MediaPipe**, this application turns any standard webcam into a high-precision, contactless virtual mouse, keyboard, media controller, and gesture-control interface. 

Featuring advanced **multi-hand support**, dynamic boundary tracking, drag-and-drop state machines, and a real-time HUD, you can smoothly navigate screens, execute precise clicks, adjust volume with an air-slider, and zoom in or out using natural hand movements.

---

## ✨ Comprehensive Gesture Control Matrix

| Gesture Command | Primary System Action | Visual Representation | Technical Trigger Logic |
| :--- | :--- | :--- | :--- |
| **Index Finger Only** | **Smooth Mouse Navigation** | ☝️ | Tracks single index landmark inside bounded active zone coordinates. |
| **Thumb + Index Pinch (Tap)** | **Left-Click Execution** | 🤏 | Quick Euclidean distance drop below threshold triggers click. |
| **Thumb + Index Pinch (Hold)**| **Drag-and-Drop Feature** | 🤏⏱️ | Holding pinch past 0.3 seconds engages `mouseDown` for dragging items. |
| **Index + Middle Fingers** | **Right-Click Contextual Menu** | ✌️ | Detects dual upper elevation state for secondary click actions. |
| **Thumb Out + Pinky Up** | **Virtual Air-Slider (Volume)** | 🤙 | Shaka-style pose tracking vertical wrist position to change volume up/down. |
| **Open Palm** | **Pause & Standby Mode** | 🖐️ | Registers all four primary digits raised simultaneously to hold tracking. |
| **Fist Formation** | **Keyboard Spacebar Trigger** | ✊ | Closes all fingers entirely to execute automation commands. |
| **Two Hands Moving Apart** | **Zoom Out (-)** | 👐 | Tracks distance between dual wrists expanding to trigger screen zoom-out. |
| **Two Hands Clapping** | **Zoom In (+)** | 👏 | Brings both wrist landmarks close together to trigger screen zoom-in. |
| **Press 'Q' Key** | **Safe Application Exit** | ⌨️ | Gracefully terminates video capture loops and releases resources. |

---

## 🛠️ System Prerequisites

* **Python Environment:** Version `3.10` or newer installed on your machine.
* **Hardware:** A standard built-in or external USB webcam with clear optical capture capability.
* **OS-Specific Permissions:**
  * **macOS:** Ensure your IDE or Terminal is granted explicit **Accessibility** and **Camera** rights under System Preferences.
  * **Windows / Linux:** Verify that runtime script executions are permitted to control peripheral mouse/keyboard inputs via `PyAutoGUI`.

---

## 📦 Installation & Setup Instructions

To get up and running locally, execute the following commands in your terminal:

```bash
# 1. Clone the official repository
git clone https://github.com/lakshaysys/hand-gesture-pc-controller.git
cd hand-gesture-pc-controller

# 2. Initialize a dedicated virtual environment (Recommended)
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate

# 3. Install required dependencies
pip install opencv-python mediapipe pyautogui
```

---

## 🎮 Running the Controller

Once dependencies are installed and your webcam is plugged in, launch the script:

```bash
python main.py
```

*Look for the live camera HUD window, position your hand inside the yellow bounding box, and start controlling your desktop seamlessly! Press `q` anytime to quit.*
