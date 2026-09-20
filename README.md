# 🖐️ Hand Gesture PC Controller
A modern, high-performance webcam-based virtual mouse and keyboard controller for Windows, macOS, and Linux. Control your computer completely hands-free using computer vision, MediaPipe, and PyAutoGUI!
![Demo](docs/demo.gif) <!-- Replace with an actual GIF or screenshot of your project -->
## ✨ Gestures & Controls

| Gesture | Action | Visual |
| :--- | :--- | :--- |
| **Index finger only** | Move Mouse (Mapped with active frame boundaries) | ☝️ |
| **Thumb + Index pinch** | Left Click | 🤏 |
| **Index + Middle fingers** | Right Click | ✌️ |
| **Open palm** | Pause / Stop Control | 🖐️ |
| **Fist** | Press Spacebar | ✊ |
| **Press 'Q'** | Quit Application | ⌨️ |

## 🛠️ Prerequisites
- Python 3.10 or newer
- A working Webcam
- *(macOS users)* Terminal/IDE granted **Accessibility** permissions in System Settings to allow `pyautogui` to control the mouse/keyboard.
## 🚀 Installation
1. Clone this repository:
```bash
   git clone [https://github.com/lakshaysys/hand-gesture-pc-controller.git](https://github.com/lakshaysys/hand-gesture-pc-controller.git)
   cd hand-gesture-pc-controller

## 📝 Notes

- **Lighting:** Ensure your hand is clearly visible and well-lit for the best tracking accuracy.
- **Smoothing:** Cursor control is deliberately smoothed via an exponential moving average to reduce cursor shaking.
- **Camera Permissions:** If the webcam doesn't open, ensure your OS has granted camera permissions to your terminal or IDE.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
