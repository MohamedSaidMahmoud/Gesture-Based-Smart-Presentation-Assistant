import cv2
import numpy as np
import os

# Chessboard dimensions (number of inner corners per chessboard row and column)
CHESSBOARD_SIZE = (9, 6)

# Termination criteria for corner sub-pixel accuracy
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points (0,0,0), (1,0,0), ..., (8,5,0)
objp = np.zeros((CHESSBOARD_SIZE[0]*CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)

objpoints = []  # 3d points in real world space
imgpoints = []  # 2d points in image plane.

cap = cv2.VideoCapture(0)
print("Press SPACE to capture a chessboard image. Press ESC when done.")

captured = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)
    disp = frame.copy()
    if found:
        cv2.drawChessboardCorners(disp, CHESSBOARD_SIZE, corners, found)
    cv2.putText(disp, f"Captured: {captured}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow('Calibration', disp)
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
    elif key == 32 and found:  # SPACE
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        captured += 1
        print(f"Captured image {captured}")

cap.release()
cv2.destroyAllWindows()

if captured < 10:
    print("Not enough images captured for reliable calibration. Try again with at least 10 images.")
    exit(1)

# Calibrate camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("Calibration successful.")
print("Camera matrix:\n", mtx)
print("Distortion coefficients:\n", dist)

# Save calibration data
np.savez('calib_data.npz', mtx=mtx, dist=dist)
print("Calibration data saved to calib_data.npz") 