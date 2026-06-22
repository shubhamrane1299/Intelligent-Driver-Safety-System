from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_accessories(frame):

    results = model(frame)

    labels = []

    for r in results:

        for box in r.boxes:

            cls = int(box.cls[0])

            name = model.names[cls]

            labels.append(name)

    if "cell phone" in labels:
        return "Mobile Usage"

    return None