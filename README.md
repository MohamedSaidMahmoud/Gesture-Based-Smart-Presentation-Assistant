# Gesture-Based Smart Presentation Assistant

## Overview
The Gesture-Based Smart Presentation Assistant is an intelligent system that allows presenters to control and annotate PowerPoint slides using only hand gestures, eliminating the need for remotes or keyboards. It leverages computer vision and hand tracking to recognize gestures for slide navigation, annotation, and pointer control. The system also features secure presenter authentication using facial recognition and provides real-time audio feedback.

---

## Features
- **Gesture Recognition:** Navigate slides, draw annotations, and use a virtual pointer with intuitive hand gestures.
- **Presenter Authentication:** Uses face recognition to ensure only authorized users can control the presentation.
- **Real-Time Audio Feedback:** Text-to-speech feedback guides the presenter through actions.
- **No-Touch Interaction:** Ideal for hygienic, hands-free environments.
- **Automatic Slide Conversion:** Converts PowerPoint slides to images for seamless display and interaction.

---

## Technologies Used
- Python 3.x
- OpenCV
- MediaPipe
- pyttsx3 (Text-to-Speech)
- comtypes (PowerPoint automation)
- NumPy

---

## Project Structure
```
Gesture-Based Smart Presentation Assistant FINALLLLLLLLLLLLL/
│
├── main.py                  # Main application script
├── HandTracker.py           # Hand detection and gesture recognition
├── authentication.py        # Face recognition-based authentication
├── camera_calibration.py    # Camera calibration utility
├── dottedline.py            # Drawing utilities for annotations
├── Dataanalysesproject.pptx # Example PowerPoint file
├── calib_data.npz           # Camera calibration data
├── user_db/                 # Directory for storing authorized user images
├── ConvertedSlides/         # Auto-generated slide images from PowerPoint
└── ...
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Gesture-Based Smart Presentation Assistant FINALLLLLLLLLLLLL"
```

### 2. Install Dependencies
Create a virtual environment (optional but recommended) and install required packages:
```bash
pip install opencv-python mediapipe numpy pyttsx3 comtypes
```

### 3. Prepare PowerPoint Slides
- Place your `.pptx` file in the project directory (or update the path in `main.py`).
- The system will automatically convert slides to images on first run.

### 4. Camera Calibration (Recommended)
For best hand tracking accuracy, calibrate your camera:
```bash
python camera_calibration.py
```
- Follow on-screen instructions using a chessboard pattern (9x6 inner corners).
- At least 10 images are recommended for reliable calibration.
- Calibration data will be saved as `calib_data.npz`.

### 5. Add Authorized Users
- Place a clear, front-facing photo of each authorized presenter in the `user_db/` directory, named as `username.jpg` (e.g., `alice.jpg`).

---

## Usage
Run the main application:
```bash
python main.py
```

### Authentication
- The system will prompt for face authentication using your webcam.
- Only authorized users (with images in `user_db/`) can start the presentation.

### Gesture Controls
- **Show all fingers:** Start presentation
- **Thumb up:** Previous slide
- **Pinky up:** Next slide
- **Index and middle up:** Show pointer
- **Index up:** Draw annotation
- **Index, middle, and ring up:** Erase last annotation
- **Middle, ring, and pinky up:** End presentation

Audio feedback will confirm each action.

---

## Customization
- **PowerPoint Path:** Edit `pptx_path` in `main.py` to use your own presentation.
- **Gesture Thresholds:** Adjust gesture detection thresholds in `main.py` as needed.

---

## Troubleshooting
- **No slides detected:** Ensure your `.pptx` file is present and the path is correct.
- **Authentication fails:** Add a clear image to `user_db/` and ensure good lighting.
- **Hand tracking issues:** Calibrate your camera and ensure your hand is visible to the webcam.

---

## License
This project is for educational and research purposes.

---

## Acknowledgments
- Built using [MediaPipe](https://mediapipe.dev/) and [OpenCV](https://opencv.org/).
- Inspired by the need for touchless, smart presentation tools.
