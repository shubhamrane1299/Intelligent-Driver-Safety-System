
# ================================
# core/detection.py
# ================================

import cv2
import mediapipe as mp
import math
import time

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

UPPER_LIP = 13
LOWER_LIP = 14

NOSE = 1

eyes_closed_start = None

def euclidean(p1, p2):

    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )

def eye_ratio(eye, landmarks):

    vertical = euclidean(
        landmarks[eye[1]],
        landmarks[eye[5]]
    )

    horizontal = euclidean(
        landmarks[eye[0]],
        landmarks[eye[3]]
    )

    return vertical / horizontal

def detect(frame):

    global eyes_closed_start

    h, w, _ = frame.shape

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:

        return "No Face"

    face_landmarks = results.multi_face_landmarks[0]

    landmarks = face_landmarks.landmark

    # =====================================
    # FACE DOTS
    # =====================================

    for lm in landmarks:

        x = int(lm.x * w)
        y = int(lm.y * h)

        cv2.circle(
            frame,
            (x, y),
            1,
            (0,255,255),
            -1
        )

    # =====================================
    # EYE DETECTION
    # =====================================

    left = eye_ratio(LEFT_EYE, landmarks)
    right = eye_ratio(RIGHT_EYE, landmarks)

    ear = (left + right) / 2

    

# =====================================
# DROWSINESS DETECTION
# =====================================

    if ear < 0.23:

        if eyes_closed_start is None:

          eyes_closed_start = time.time()

        closed_time = time.time() - eyes_closed_start

        print("EYES CLOSED :", round(closed_time,2))

    # =================================
    # DROWSY
    # =================================

        if closed_time >= 2 and closed_time < 5:

          return "Drowsy"

    # =================================
    # CRITICAL
    # =================================

        elif closed_time >= 5:

          return "Critical"

    else:

     eyes_closed_start = None


    

  


    
     



    # =====================================
    # YAWNING
    # =====================================

    upper = landmarks[UPPER_LIP]
    lower = landmarks[LOWER_LIP]

    mouth_distance = abs(upper.y - lower.y)

    if mouth_distance > 0.07:

        return "Yawning"

    # =====================================
    # HEAD POSITION
    # =====================================

    nose = landmarks[NOSE]

    if nose.x < 0.40:

        return "Looking Left"

    if nose.x > 0.60:

        return "Looking Right"

    if nose.y < 0.35:

        return "Looking Up"

    if nose.y > 0.65:

        return "Looking Down"

    return "Normal"
