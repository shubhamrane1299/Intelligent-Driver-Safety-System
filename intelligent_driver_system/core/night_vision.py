import cv2

def apply_night_vision(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    enhanced = cv2.equalizeHist(gray)

    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)