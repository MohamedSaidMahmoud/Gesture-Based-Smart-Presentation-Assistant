import cv2
import os
import mediapipe as mp
import numpy as np

# Configuration
AUTH_DB = "user_db"
FACE_MATCH_THRESHOLD = 0.85
MIN_FACE_SIZE = 15000
DISPLAY_TIME = 30  # Frames to show access message (~1 second)

def initialize_database():
    if not os.path.exists(AUTH_DB):
        os.makedirs(AUTH_DB)
        print(f"Created auth database at: {AUTH_DB}")
        print(f"Add approved user images as '{AUTH_DB}/username.jpg'")

def initialize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap

def compare_faces(live_frame, stored_img, face_mesh):
    live_rgb = cv2.cvtColor(live_frame, cv2.COLOR_BGR2RGB)
    stored_rgb = cv2.cvtColor(stored_img, cv2.COLOR_BGR2RGB)
    
    live_results = face_mesh.process(live_rgb)
    stored_results = face_mesh.process(stored_rgb)
    
    if not (live_results.multi_face_landmarks and stored_results.multi_face_landmarks):
        return 0.0
    
    live_landmarks = np.array([(lm.x, lm.y) for lm in live_results.multi_face_landmarks[0].landmark])
    stored_landmarks = np.array([(lm.x, lm.y) for lm in stored_results.multi_face_landmarks[0].landmark])
    
    dot_product = np.dot(live_landmarks.flatten(), stored_landmarks.flatten())
    norm_product = np.linalg.norm(live_landmarks) * np.linalg.norm(stored_landmarks)
    return (dot_product / norm_product + 1) / 2

def authenticate_presenter():
    initialize_database()
    approved_users = [f.split(".")[0] for f in os.listdir(AUTH_DB) 
                     if f.lower().endswith(('.jpg', '.png'))]
    
    if not approved_users:
        print(f"No approved users in {AUTH_DB}")
        return None, False  # Return tuple (user, success)

    cap = initialize_camera()
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    authenticated = False
    auth_user = None
    auth_frame_count = 0
    last_face_id = None  # To track face consistency

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            display_frame = frame.copy()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            current_face_id = None
            face_changed = False

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                current_face_id = hash(tuple((lm.x, lm.y) for lm in landmarks[:5]))  # Use first 5 landmarks as ID

                if last_face_id and current_face_id != last_face_id:
                    face_changed = True
                    authenticated = False
                    auth_user = None

                last_face_id = current_face_id

                h, w = frame.shape[:2]
                x_coords = [lm.x * w for lm in landmarks]
                y_coords = [lm.y * h for lm in landmarks]
                face_area = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))

                if face_area > MIN_FACE_SIZE and not authenticated:
                    best_match = ("Unknown", 0)
                    for user in approved_users:
                        user_img = cv2.imread(f"{AUTH_DB}/{user}.jpg")
                        if user_img is not None:
                            similarity = compare_faces(frame, user_img, face_mesh)
                            if similarity > best_match[1]:
                                best_match = (user, similarity)

                    if best_match[1] > FACE_MATCH_THRESHOLD:
                        authenticated = True
                        auth_user = best_match[0]
                        auth_frame_count = DISPLAY_TIME

            else:
                if last_face_id:
                    face_changed = True
                last_face_id = None
                authenticated = False
                auth_user = None

            if authenticated and auth_frame_count > 0:
                cv2.putText(display_frame, f"ACCESS GRANTED: {auth_user}", 
                           (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                           (0, 255, 0), 3)
                auth_frame_count -= 1
            else:
                cv2.putText(display_frame, "ACCESS DENIED", (50, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            cv2.imshow("Presenter Authentication", display_frame)

            # Exit if user presses 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Exit loop immediately when authentication successful and display time elapsed
            if authenticated and auth_frame_count == 0:
                break

    finally:
        cap.release()
        face_mesh.close()
        cv2.destroyAllWindows()

    return auth_user, authenticated