import cv2
from ultralytics import YOLO
import mediapipe as mp

model = YOLO("yolov8s.pt")   # upgrade from yolov8n.pt

mobile_counter = 0

mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

def detect_mobile(frame):

    global mobile_counter

    detected = False

    h, w, _ = frame.shape

    # =========================
    # FACE DETECTION
    # =========================

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_results = face_detector.process(rgb)

    face_box = None

    if face_results.detections:

        det = face_results.detections[0]

        bbox = det.location_data.relative_bounding_box

        fx = int(bbox.xmin * w)
        fy = int(bbox.ymin * h)
        fw = int(bbox.width * w)
        fh = int(bbox.height * h)

        face_box = (fx, fy, fw, fh)

    # =========================
    # YOLO PHONE DETECTION
    # =========================

    results = model(frame, verbose=False)

    for r in results:

        for box in r.boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            # cell phone class
            if cls == 67 and conf > 0.35:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                phone_cx = (x1 + x2) // 2
                phone_cy = (y1 + y2) // 2

                # Draw box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"PHONE {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

                # =========================
                # PHONE NEAR FACE
                # =========================

            if cls == 67 and conf > 0.25:
    
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                phone_cx = (x1 + x2) // 2
                phone_cy = (y1 + y2) // 2

                cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                2
               )

                cv2.putText(
                frame,
                f"PHONE {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
                )
                
                detected = True
                

    # =========================
    # STABLE DETECTION
    # =========================

    if detected:
        mobile_counter += 1
    else:
        mobile_counter = max(0, mobile_counter - 1)

    if mobile_counter >= 3:
        return True

    return False

