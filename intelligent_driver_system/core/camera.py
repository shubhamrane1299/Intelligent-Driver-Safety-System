import cv2

def open_camera():
    return cv2.VideoCapture(0)

def get_frame(cap):
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

def close_camera(cap):
    cap.release()
    cv2.destroyAllWindows()