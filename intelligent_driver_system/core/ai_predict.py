import cv2
import numpy as np

from tensorflow.keras.models import load_model

# ==========================================
# LOAD MODEL
# ==========================================

model = load_model("models/driver_model.h5")

classes = [

    "closed",
    "open"
    
]

# ==========================================
# FACE CASCADE
# ==========================================

face_cascade = cv2.CascadeClassifier(

    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# ==========================================
# PREDICT
# ==========================================

def predict_state(frame):

    gray = cv2.cvtColor(

        frame,

        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(

        gray,

        1.3,

        5
    )

    if len(faces) == 0:

        return "No Face",0,None

    for (x,y,w,h) in faces:

        face = frame[y:y+h,x:x+w]

        face = cv2.resize(face,(64,64))

        face = face / 255.0

        face = np.expand_dims(face,axis=0)

        prediction = model.predict(face,verbose=0)

        class_index = np.argmax(prediction)

        confidence = np.max(prediction)

        label = classes[class_index]

        # ==================================
        # STATES
        # ==================================

        if label == "closed":
    
            state = "Drowsy"
        else:

            state = "Normal"

        return state,confidence,(x,y,w,h)

    return "Normal",0,None