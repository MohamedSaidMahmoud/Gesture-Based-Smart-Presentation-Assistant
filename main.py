import cv2
import os
from authentication import authenticate_presenter
from HandTracker import HandDetector
from dottedline import drawrect, drawline
import numpy as np
import comtypes.client
import pyttsx3
import threading

# ========== SETTINGS ==========
pptx_path = r"C:\Users\alima\Downloads\Gesture-Based Smart Presentation Assistant FINAL\Dataanalysesproject.pptx"
output_folder = "ConvertedSlides"
width, height = 1280, 720
hs, ws = int(120 * 1.2), int(213 * 1.2)
ge_thresh_y = 400
ge_thresh_x = 750
delay = 15

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume (0 to 1)

def speak_feedback(text):
    def speak():
        engine.say(text)
        engine.runAndWait()
    # Run speech in a separate thread to avoid blocking the main program
    threading.Thread(target=speak, daemon=True).start()

# ========== USER AUTHENTICATION SYSTEM ==========
auth_user, authenticated = authenticate_presenter()
if not authenticated:
    exit(0)
print(f"Authenticated user: {auth_user}")

# ========== CONVERT PPTX TO IMAGES ==========
def convert_pptx_to_images(pptx_path, output_folder):
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"PowerPoint file not found at: {pptx_path}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    try:
        powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
        powerpoint.Visible = 1
        presentation = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
        presentation.SaveAs(os.path.abspath(output_folder), 17)
        presentation.Close()
        powerpoint.Quit()
        print(f"Successfully converted PowerPoint to images in {output_folder}")
    except Exception as e:
        print(f"PowerPoint conversion failed: {str(e)}")
        raise

try:
    convert_pptx_to_images(pptx_path, output_folder)
except Exception as e:
    print(f"\nError: {str(e)}\nPlease fix the above issue and run the program again.")
    exit(1)

# ========== INIT ==========
slide_num = 0
gest_done = False
gest_counter = 0
annotations = [[]]
annot_num = 0
annot_start = False
presentation_started = False
feedback = ""

# Load converted images
frames_folder = output_folder
path_imgs = sorted([img for img in os.listdir(frames_folder) if img.lower().endswith(('.jpg', '.png', '.jpeg'))], key=len)

if not path_imgs:
    raise FileNotFoundError(f"No slides were found in: {frames_folder}")

cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Load camera calibration data if available
calib_file = 'calib_data.npz'
if os.path.exists(calib_file):
    with np.load(calib_file) as X:
        mtx, dist = [X[i] for i in ('mtx', 'dist')]
    print('Camera calibration data loaded.')
else:
    mtx, dist = None, None
    print('Camera calibration data not found. Running without undistortion.')

detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # Undistort the frame if calibration data is available
    if mtx is not None and dist is not None:
        frame = cv2.undistort(frame, mtx, dist, None, mtx)

    # Draw a grid overlay for calibration check
    grid_color = (0, 255, 255)
    grid_thickness = 1
    grid_spacing = 80  # pixels
    h_grid, w_grid = frame.shape[:2]
    for x in range(0, w_grid, grid_spacing):
        cv2.line(frame, (x, 0), (x, h_grid), grid_color, grid_thickness)
    for y in range(0, h_grid, grid_spacing):
        cv2.line(frame, (0, y), (w_grid, y), grid_color, grid_thickness)

    if presentation_started:
        slide_path = os.path.join(frames_folder, path_imgs[slide_num])
        slide_current = cv2.imread(slide_path)
        slide_current = cv2.resize(slide_current, (width, height))
    else:
        slide_current = np.zeros((height, width, 3), np.uint8)
        cv2.putText(slide_current, "Show all fingers to START presentation", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(slide_current, f"Presenter: {auth_user}", (200, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    hands, frame = detector.findHands(frame)
    drawrect(frame, (width, 0), (ge_thresh_x, ge_thresh_y), (0, 255, 0), 5, 'dotted')

    if hands and not gest_done:
        hand = hands[0]
        cx, cy = hand["center"]
        lm_list = hand["lmList"]
        fingers = detector.fingersUp(hand)
        x_val = int(np.interp(lm_list[8][0], [width // 2, width], [0, width]))
        y_val = int(np.interp(lm_list[8][1], [150, height - 150], [0, height]))
        index_fing = x_val, y_val

        # Start Presentation
        if not presentation_started and fingers == [1, 1, 1, 1, 1]:
            presentation_started = True
            gest_done = True
            feedback = "Presentation Started"
            speak_feedback(f"Welcome {auth_user}. Presentation Started")

        # End Presentation
        elif presentation_started and fingers == [0, 0, 1, 1, 1]:
            presentation_started = False
            slide_num = 0
            annotations = [[]]
            annot_num = 0
            gest_done = True
            feedback = "Presentation Ended"
            speak_feedback("Presentation Ended. Thank you.")

        elif presentation_started:
            if cy < ge_thresh_y and cx > ge_thresh_x:
                annot_start = False
                if fingers == [1, 0, 0, 0, 0]:  # Previous Slide
                    if slide_num > 0:
                        slide_num -= 1
                        annotations = [[]]
                        annot_num = 0
                        gest_done = True
                        feedback = "Previous Slide"
                        speak_feedback("Moving to Previous Slide")
                elif fingers == [0, 0, 0, 0, 1]:  # Next Slide
                    if slide_num < len(path_imgs) - 1:
                        slide_num += 1
                        annotations = [[]]
                        annot_num = 0
                        gest_done = True
                        feedback = "Next Slide"
                        speak_feedback("Moving to Next Slide")

            if fingers == [0, 1, 1, 0, 0]:  # Show Pointer
                cv2.circle(slide_current, index_fing, 4, (0, 0, 255), cv2.FILLED)
                annot_start = False
                feedback = "Pointer"

            elif fingers == [0, 1, 0, 0, 0]:  # Draw
                if not annot_start:
                    annot_start = True
                    annot_num += 1
                    annotations.append([])
                    speak_feedback("Drawing mode activated")
                annotations[annot_num].append(index_fing)
                cv2.circle(slide_current, index_fing, 4, (0, 0, 255), cv2.FILLED)
                feedback = "Drawing"

            else:
                annot_start = False

            if fingers == [0, 1, 1, 1, 0]:  # Erase Last
                if annotations and annot_num >= 0:
                    annotations.pop(-1)
                    annot_num -= 1
                    gest_done = True
                    feedback = "Last Annotation Erased"
                    speak_feedback("Erasing last annotation")
    else:
        annot_start = False

    if gest_done:
        gest_counter += 1
        if gest_counter > delay:
            gest_counter = 0
            gest_done = False

    # Draw annotations
    if presentation_started:
        for annotation in annotations:
            for j in range(1, len(annotation)):
                cv2.line(slide_current, annotation[j - 1], annotation[j], (0, 0, 255), 6)

    # Draw webcam in bottom right
    img_small = cv2.resize(frame, (ws, hs))
    h, w, _ = slide_current.shape
    slide_current[h - hs:h, w - ws:w] = img_small

    # Draw feedback text
    if feedback:
        cv2.putText(slide_current, f"Gesture: {feedback}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)
    
    # Draw presenter name
    presenter_text = f"Presenter: {auth_user}"
    # Get text size to position it properly in bottom right
    (text_width, text_height), _ = cv2.getTextSize(presenter_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    text_x = width - text_width - 20  # 20 pixels padding from right
    cv2.putText(slide_current, presenter_text, (text_x, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    cv2.imshow("Slides", slide_current)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()