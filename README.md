# 🖐️ Hand Gesture PC Controller

A simple, webcam-based virtual mouse and keyboard controller for Windows, macOS, and Linux. Control your computer hands-free using computer vision and MediaPipe!

![Demo](docs/demo.gif) <!-- Replace with an actual GIF or screenshot of your project -->

## ✨ Gestures

| Gesture | Action | Visual |
| :--- | :--- | :---: |
| **Index finger only** | Move Mouse | ☝️ |
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
   git clone https://github.com/your-username/hand-gesture-pc-controller.git
   cd hand-gesture-pc-controller
```

2. (Optional but recommended) Create a virtual environment:
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
   pip install -r requirements.txt
```

## ▶️ Usage

Run the main script:
```bash
python main.py
```
A window will pop up showing your webcam feed with hand tracking overlays. Perform the gestures listed above to control your PC. Press **`Q`** in the webcam window to exit.

## 📝 Notes

- **Lighting:** Ensure your hand is clearly visible and well-lit for the best tracking accuracy.
- **Smoothing:** Cursor control is deliberately smoothed via an exponential moving average to reduce cursor shaking.
- **Camera Permissions:** If the webcam doesn't open, ensure your OS has granted camera permissions to your terminal or IDE.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
