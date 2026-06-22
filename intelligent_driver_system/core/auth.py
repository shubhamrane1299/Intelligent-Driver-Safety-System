
import cv2
import os
import sqlite3
import face_recognition
from tkinter import simpledialog, messagebox

# =====================================================
# REGISTER
# =====================================================

def register_window(root):

    os.makedirs("data/faces", exist_ok=True)

    username = simpledialog.askstring(
        "Register",
        "Enter Username"
    )

    password = simpledialog.askstring(
        "Register",
        "Enter Password"
    )

    if not username or not password:
        return

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():

        messagebox.showerror(
            "ERROR",
            "Camera Not Opening"
        )

        return

    messagebox.showinfo(
        "FACE REGISTER",
        "Press S to capture face"
    )

    count = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            continue

        cv2.imshow(
            "REGISTER FACE",
            frame
        )

        key = cv2.waitKey(1)

        # SAVE FACE
        if key == ord('s'):

            path = f"data/faces/{username}_{count}.jpg"

            cv2.imwrite(path, frame)

            conn = sqlite3.connect(
                "data/users.db"
            )

            cur = conn.cursor()

            cur.execute(

                "INSERT INTO users(username,password,face_path) VALUES(?,?,?)",

                (username, password, path)
            )

            conn.commit()

            conn.close()

            messagebox.showinfo(
                "SUCCESS",
                "User Registered Successfully"
            )

            count += 1

            break

        # EXIT
        if key == 27:
            break

    cap.release()

    cv2.destroyAllWindows()

# =====================================================
# LOGIN
# =====================================================

def face_login():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():

        messagebox.showerror(
            "ERROR",
            "Camera Not Opening"
        )

        return None

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute(
        "SELECT username, face_path FROM users"
    )

    users = cur.fetchall()

    known_encodings = []

    known_names = []

    # ==========================================
    # LOAD FACES
    # ==========================================

    for username, face_path in users:

        try:

            image = face_recognition.load_image_file(face_path)

            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:

                known_encodings.append(encodings[0])

                known_names.append(username)

        except:
            pass

    if len(known_encodings) == 0:

        messagebox.showerror(
            "ERROR",
            "No registered users found"
        )

        cap.release()

        conn.close()

        return None

    # ==========================================
    # CAMERA LOOP
    # ==========================================

    while True:

        ret, frame = cap.read()

        if not ret:
            continue

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        locations = face_recognition.face_locations(rgb)

        encodings = face_recognition.face_encodings(
            rgb,
            locations
        )

        for (top, right, bottom, left), face_encoding in zip(locations, encodings):

            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=0.5
            )

            name = "Unauthorized"

            color = (0,0,255)

            if True in matches:

                index = matches.index(True)

                name = known_names[index]

                color = (0,255,0)

            # FACE BOX

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                color,
                3
            )

            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

            # LOGIN SUCCESS

            if name != "Unauthorized":

                cv2.putText(
                    frame,
                    "LOGIN SUCCESS",
                    (20,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0),
                    3
                )

                cv2.imshow("FACE LOGIN", frame)

                cv2.waitKey(1500)

                cap.release()

                cv2.destroyAllWindows()

                conn.close()

                return name

        cv2.imshow(
            "FACE LOGIN",
            frame
        )

        key = cv2.waitKey(1)

        if key == 27:
            break

    cap.release()

    cv2.destroyAllWindows()

    conn.close()

    return None
