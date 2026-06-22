import cv2
import tkinter as tk
from tkinter import ttk
import threading
import sqlite3
import pandas as pd

from sympy import python
from core.analytics import get_driver_stats
from core.gps import get_location
from PIL import Image, ImageTk
from datetime import datetime
from core.database import start_trip, end_trip

from core.detection import detect
from core.mobile_detection import detect_mobile
from core.alerts import (send_sos,
                         trigger_alert)
from core.auth import register_window, face_login
from core.voice_monitor import start_voice_monitor
from core.database import init_db, log_event
from core.score import update_score
from core.night_vision import apply_night_vision
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==========================================
# FUTURISTIC COLORS
# ==========================================

BG = "#050505"

PANEL = "#111111"

CYAN = "#00ffff"

RED = "#ff0033"

GREEN = "#00ff99"

YELLOW = "#ffaa00"

TEXT = "#ffffff"



# =========================================================
# INIT DB
# =========================================================

init_db()

# =========================================================
# GLOBALS
# =========================================================

running = False
cap = None
current_user = None
authorized_status = "NOT LOGGED IN"
latest_frame = None
gps_data = {}

sos_sent = False

eyes_closed_start = None
 


sound_enabled = True
mobile_detection_enabled = True
trip_start_time = None

# =========================================================
# START SYSTEM
# =========================================================

def start_system():

    global running
    global cap

    if running:
        return

    running = True
    global gps_data

    gps_data = get_location()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)



    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():

        print("Camera Not Opening")

        running = False

        return

    threading.Thread(
        target=camera_loop,
        daemon=True
    ).start()

def stop_system():
    
    global running
    global cap

    running = False

    if cap is not None:

        cap.release()

    cv2.destroyAllWindows()
    
    if current_user and trip_start_time:
    
       trip_end = datetime.now()

       duration = trip_end - trip_start_time

       end_trip(

        current_user,

        str(trip_end),

        str(duration)
    )

    print("System Stopped")    

# ================================
# CAMERA LOOP FIX
# app_gui.py
# Replace OLD camera_loop()
# ================================



def export_logs():

    try:

        conn = sqlite3.connect("data/users.db")

        query = "SELECT * FROM logs"

        df = pd.read_sql_query(

            query,

            conn
        )

        df.to_excel(

            "driver_logs.xlsx",

            index=False
        )

        conn.close()

        print("REPORT EXPORTED")

    except Exception as e:

        print("EXPORT ERROR :", e)


def camera_loop():

    global running
    global cap
    global latest_frame
    global current_user
    global sos_sent

    print("Camera Loop Started")

    while running:

        ret, frame = cap.read()

        if not ret:
            continue

       
        frame = cv2.GaussianBlur(frame, (3,3), 0)



        frame = apply_night_vision(frame)

        # =====================================
        # DETECTION FRAME
        # =====================================

        

        state = detect(frame)
       
        if state == "Critical":

         cv2.rectangle(

        frame,

        (0,0),

        (1280,60),

        (0,0,255),

        -1
    )

        cv2.putText(

        frame,

        "CRITICAL DRIVER CONDITION",

        (350,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.2,

        (255,255,255),

        3
        )



        # =====================================
        # MOBILE DETECTION
        # =====================================

        if mobile_detection_enabled:

            if detect_mobile(frame):

                state = "Mobile Usage"

        # =====================================
        # LOG EVENT
        # =====================================

        if current_user:

            log_event(current_user, state)

        # =====================================
        # SCORE
        # =====================================

        score = update_score(state)

        # =====================================
        # ALERTS
        # =====================================

        trigger_alert(state)

        # =====================================
        # SOS
        # =====================================

        if state == "Critical":

            if not sos_sent:

                
                print("SENDING SOS...")

                send_sos(
                current_user,
                state,
                gps_data
            )



                sos_sent = True

        else:

            sos_sent = False

        # =====================================
        # COLORS
        # =====================================

        colors = {

            "Normal": (0,255,0),

            "Drowsy": (0,255,255),

            "Critical": (0,0,255),

            "Yawning": (255,0,255),

            "Looking Left": (255,255,0),

            "Looking Right": (255,255,0),

            "Looking Up": (0,255,255),

            "Looking Down": (255,0,0),

            "Mobile Usage": (0,0,255),

            "No Face": (120,120,120)
        }

        color = colors.get(
            state,
            (255,255,255)
        )

        # =====================================
        # HUD
        # ==========
# ==========================================
# FUTURISTIC HUD PANEL
# ==========================================

        cv2.rectangle(

           frame,

           (20,20),

           (420,260),

           (15,15,15),

          -1
)

        cv2.rectangle(

         frame,

        (20,20),

        (420,260),

        (0,255,255),

        2
)

# TITLE

        cv2.putText(

         frame,

         "AI DRIVER SYSTEM",

         (40,55),

         cv2.FONT_HERSHEY_SIMPLEX,

         1,

         (0,255,255),

         2
)

# STATE

        cv2.putText(

         frame,

         f"STATE : {state}",

         (40,100),

         cv2.FONT_HERSHEY_SIMPLEX,

         0.8,

         color,

         2
)

# SCORE

        cv2.putText(

         frame,

         f"SCORE : {score}",

         (40,140),

         cv2.FONT_HERSHEY_SIMPLEX,

         0.8,

         (0,255,255),

         2
)

# USER

        cv2.putText(

         frame,

         f"USER : {current_user}",

         (40,180),

         cv2.FONT_HERSHEY_SIMPLEX,

         0.7,

         (255,255,255),

         2
)

# GPS

        cv2.putText(

         frame,

         f"GPS : {gps_data['city']}",

         (40,220),

         cv2.FONT_HERSHEY_SIMPLEX,

         0.7,

         (0,255,255),

         2
)


        
        # =====================================
        # TARGET UI
        # =====================================

        h, w, _ = frame.shape

        cx = w // 2
        cy = h // 2

        cv2.circle(
            frame,
            (cx,cy),
            5,
            color,
            -1
        )

        cv2.circle(
            frame,
            (cx,cy),
            40,
            color,
            2
        )

        cv2.line(
            frame,
            (cx-60,cy),
            (cx+60,cy),
            color,
            1
        )

        cv2.line(
            frame,
            (cx,cy-60),
            (cx,cy+60),
            color,
            1
        )

        # =====================================
        # SAVE FRAME
        # =====================================

        latest_frame = frame.copy()

        # =====================================
        # WINDOW
        # =====================================

        cv2.namedWindow(
            "AI DRIVER CAMERA",
            cv2.WINDOW_NORMAL
        )

        cv2.resizeWindow(
            "AI DRIVER CAMERA",
            1400,
            900
        )
       
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        cv2.putText(

        frame,

        f"FPS : {fps}",

        (1100,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0,255,255),

        2
)
       
# ==================================
# FUTURISTIC BORDER
# ==================================

        cv2.rectangle(

        frame,

        (10,10),

        (1270,710),

        (0,255,255),

        2
)

# ==================================
# AI SCAN TEXT
# ==================================

        cv2.putText(

        frame,

        "AI DRIVER MONITOR ACTIVE",

        (30,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0,255,255),

        2
)

# ==================================
# RADAR CIRCLE
# ==================================

        cv2.circle(
 
        frame,

        (1150,600),

        50,

        (0,255,255),

        2
)

        cv2.circle(

        frame,

        (1150,600),

        10,

        (0,255,255),

        -1
)

 

   
        cv2.imshow(
            "AI DRIVER CAMERA",
            frame
        )

        key = cv2.waitKey(1)

        if key == 27:

            stop_system()

            break

    if cap is not None:

        cap.release()



# =========================================================
# UPDATE CAMERA UI
# =========================================================


# =========================================================
# LOGIN
# =========================================================

def login_user():
    
    global current_user
    global authorized_status

    user = face_login()

    if user:

        current_user = user

        authorized_status = "AUTHORIZED"

        print("Authorized Driver")
        global trip_start_time

        trip_start_time = datetime.now()

        start_trip(

        current_user,

        str(trip_start_time)
)
        
        start_system()

    else:
        current_user = None
        authorized_status = "UNAUTHORIZED"

        print("Unauthorized Driver")
# ==========================================
# UPDATE CAMERA
# ==========================================

def update_camera():

    global latest_frame

    if latest_frame is not None:

        rgb = cv2.cvtColor(
            latest_frame,
            cv2.COLOR_BGR2RGB
        )

        img = Image.fromarray(rgb)

        img = img.resize((900,500))

        imgtk = ImageTk.PhotoImage(image=img)

        camera_label.imgtk = imgtk

        camera_label.configure(image=imgtk)

    root.after(10, update_camera)    
 
# ==========================================
# UPDATE ANALYTICS
# ==========================================

# ==========================================
# UPDATE ANALYTICS
# ==========================================

def update_analytics():

    global current_user

    ax.clear()

    if current_user:

        stats = get_driver_stats(current_user)

        text = f"""

Driver : {current_user}

Total Logs : {stats['total_logs']}

Normal : {stats['normal']}

Drowsy : {stats['drowsy']}

Critical : {stats['critical']}

Yawning : {stats['yawning']}

Mobile Usage : {stats['mobile']}

No Face : {stats['no_face']}
"""

        analytics_label.config(text=text)

        labels = [
            "Normal",
            "Drowsy",
            "Critical",
            "Mobile",
            "Yawning"
        ]

        values = [

            stats['normal'],

            stats['drowsy'],

            stats['critical'],

            stats['mobile'],

            stats['yawning']
        ]

        ax.bar(labels, values)

        ax.set_title("Driver State Analytics")
        ax.bar(labels, values)

        ax.set_title("Driver State Analytics")

        import os
        os.makedirs("reports", exist_ok=True)

        fig.savefig(
        f"reports/{current_user}_graph.png"
)

    else:

        analytics_label.config(
            text="No Driver Logged In"
        )

    canvas.draw()

    root.after(2000, update_analytics)   

# =========================================================
# SETTINGS
# =========================================================

def update_settings():

    global sound_enabled
    global mobile_detection_enabled

    sound_enabled = sound_var.get()

    mobile_detection_enabled = mobile_var.get()

# =========================================================
# UI
# =========================================================

root = tk.Tk()

root.title("AI DRIVER SAFETY SYSTEM")

root.geometry("1100x700")

root.configure(bg=BG)

root.state("zoomed")

# =========================================================
# STYLE
# =========================================================

style = ttk.Style()

style.theme_use("clam")

style.configure(
    "TNotebook",
    background="#0d0d0d"
)

style.configure(
    "TNotebook.Tab",
    background="#1a1a1a",
    foreground="white",
    padding=[20,10],
    font=("Arial",11,"bold")
)

# =========================================================
# TITLE
# =========================================================

title = tk.Label(

    root,

    text="INTELLIGENT DRIVER MONITORING SYSTEM",

    font=("Orbitron",36,"bold"),

    fg=CYAN,

    bg=BG
)

title.pack(pady=15)








# =========================================================
# NOTEBOOK
# =========================================================

notebook = ttk.Notebook(root)

notebook.pack(

    fill="both",

    expand=True,

    padx=20,

    pady=10
)

# =========================================================
# TABS
# =========================================================

dashboard_tab = tk.Frame(notebook,bg="#0d0d0d")
auth_tab = tk.Frame(notebook,bg="#0d0d0d")
settings_tab = tk.Frame(notebook,bg="#0d0d0d")
about_tab = tk.Frame(notebook,bg="#0d0d0d")
drivers_tab = tk.Frame(notebook,bg="#0d0d0d")
logs_tab = tk.Frame(notebook,bg="#0d0d0d")
 
reports_tab = tk.Frame(notebook,bg="#0d0d0d")
analytics_tab = tk.Frame(notebook,bg="#0d0d0d")



notebook.add(dashboard_tab,text="Dashboard")
notebook.add(auth_tab,text="Authentication")
notebook.add(settings_tab,text="Settings")
notebook.add(about_tab,text="About AI")
notebook.add(drivers_tab,text="Drivers")
notebook.add(logs_tab,text="Logs")
notebook.add(analytics_tab,text="Analytics")
notebook.add(reports_tab,text="Reports")



# =========================================================
# DASHBOARD
# =========================================================

dash_title = tk.Label(

    dashboard_tab,

    text="AI MONITORING DASHBOARD",

    font=("Arial",24,"bold"),

    fg="white",

    bg="#0d0d0d"
)

dash_title.pack(pady=30)


status_frame = tk.Frame(

    dashboard_tab,

    bg=PANEL,

    highlightbackground=CYAN,

    highlightthickness=2
)

status_frame.pack(

    pady=15,

    padx=20,

    fill="x"
)

live_status = tk.Label(

    status_frame,

    text="AI SYSTEM ACTIVE",

    font=("Arial",18,"bold"),

    fg=GREEN,

    bg=PANEL
)

live_status.pack(

    pady=15
)


start_btn = tk.Button(

    dashboard_tab,

    text="START AI SYSTEM",

    font=("Arial",16,"bold"),

    bg=CYAN,

    fg="black",

    activebackground=GREEN,

    relief="flat",

    padx=20,

    pady=12,

    command=start_system
)

start_btn.pack(pady=15)









stop_btn = tk.Button(

    dashboard_tab,

    text="STOP SYSTEM",

    font=("Arial",16,"bold"),

    bg="red",

    fg="white",

    width=20,

    height=2,

    relief="flat",

    command=stop_system
)

stop_btn.pack(pady=10)

# ==========================================
# ANALYTICS PANEL
# ==========================================

analytics_frame = tk.Frame(
    dashboard_tab,
    bg="#111111",
    bd=2,
    relief="solid"
)

analytics_frame.pack(pady=20)

analytics_title = tk.Label(
    analytics_frame,
    text="LIVE DRIVER ANALYTICS",
    font=("Arial",18,"bold"),
    fg="cyan",
    bg="#111111"
)

analytics_title.pack(pady=10)

analytics_label = tk.Label(
    analytics_frame,
    text="No Driver Logged In",
    justify="left",
    font=("Consolas",13),
    fg="lime",
    bg="#111111"
)

analytics_label.pack(padx=20,pady=20)

camera_label = tk.Label(

    dashboard_tab,

    bg="black"
)

camera_label.pack(pady=20)

# ==========================================
# GRAPH PANEL
# ==========================================

graph_frame = tk.Frame(
    dashboard_tab,
    bg="#0d0d0d"
)

graph_frame.pack(pady=20)

fig = Figure(
    figsize=(6,4),
    dpi=100
)

ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(
    fig,
    master=graph_frame
)

canvas.get_tk_widget().pack()
# =========================================================
# AUTH TAB
# =========================================================

auth_title = tk.Label(

    auth_tab,

    text="FACE AUTHENTICATION",

    font=("Arial",24,"bold"),

    fg="white",

    bg="#0d0d0d"
)

auth_title.pack(pady=30)

register_btn = tk.Button(

    auth_tab,

    text="REGISTER DRIVER",

    font=("Arial",15,"bold"),

    bg="lime",

    fg="black",

    width=22,

    height=2,

    relief="flat",

    command=lambda: register_window(root)
)

register_btn.pack(pady=20)

login_btn = tk.Button(

    auth_tab,

    text="FACE LOGIN",

    font=("Arial",15,"bold"),

    bg="cyan",

    fg="black",

    width=22,

    height=2,

    relief="flat",

    command=login_user
)

login_btn.pack(pady=20)

# =========================================================
# SETTINGS TAB
# =========================================================

settings_title = tk.Label(

    settings_tab,

    text="SYSTEM SETTINGS",

    font=("Arial",24,"bold"),

    fg="white",

    bg="#0d0d0d"
)

settings_title.pack(pady=30)

sound_var = tk.BooleanVar(value=True)

mobile_var = tk.BooleanVar(value=True)

tk.Checkbutton(

    settings_tab,

    text="Enable Voice Alerts",

    variable=sound_var,

    command=update_settings,

    font=("Arial",14),

    fg="cyan",

    bg="#0d0d0d",

    selectcolor="#1a1a1a"

).pack(pady=15)

tk.Checkbutton(

    settings_tab,

    text="Enable Mobile Detection",

    variable=mobile_var,

    command=update_settings,

    font=("Arial",14),

    fg="cyan",

    bg="#0d0d0d",

    selectcolor="#1a1a1a"

).pack(pady=15)

# =========================================================
# ABOUT TAB
# =========================================================

about_title = tk.Label(

    about_tab,

    text="AI FEATURES",

    font=("Arial",24,"bold"),

    fg="white",

    bg="#0d0d0d"
)

about_title.pack(pady=30)

features = """

🔥 Drowsiness Detection

🔥 Yawning Detection

🔥 Looking Left / Right

🔥 Looking Up / Down

🔥 YOLO Mobile Detection

🔥 Face Authentication

🔥 Real-time Voice Alerts

🔥 WhatsApp SOS

🔥 Dark Futuristic UI

🔥 AI Driver Monitoring

🔥 Production Level Dashboard

"""

feature_label = tk.Label(

    about_tab,

    text=features,

    justify="left",

    font=("Arial",16),

    fg="cyan",

    bg="#0d0d0d"
)

feature_label.pack(pady=20)

# =========================================================
# DRIVERS TAB
# =========================================================

drivers_title = tk.Label(

    drivers_tab,

    text="REGISTERED DRIVERS",

    font=("Arial",24,"bold"),

    fg="white",

    bg="#0d0d0d"
)

drivers_title.pack(pady=20)

drivers_frame = tk.Frame(drivers_tab,bg="#0d0d0d")

drivers_frame.pack()

# =========================================================
# LOAD REGISTERED DRIVERS
# =========================================================

def load_drivers():

    for widget in drivers_frame.winfo_children():

        widget.destroy()

    try:

        conn = sqlite3.connect("data/users.db")

        cur = conn.cursor()

        cur.execute(
            "SELECT username, face_path FROM users"
        )

        users = cur.fetchall()

        conn.close()

        col = 0

        for username, face_path in users:

            try:

                img = Image.open(face_path)

                img = img.resize((120,120))

                photo = ImageTk.PhotoImage(img)

                card = tk.Frame(
                    drivers_frame,
                    bg="#1a1a1a",
                    padx=10,
                    pady=10
                )

                card.grid(
                    row=0,
                    column=col,
                    padx=20,
                    pady=20
                )

                label_img = tk.Label(
                    card,
                    image=photo,
                    bg="#1a1a1a"
                )

                label_img.image = photo

                label_img.pack()

                tk.Label(
                    card,
                    text=username,
                    font=("Arial",14,"bold"),
                    fg="cyan",
                    bg="#1a1a1a"
                ).pack(pady=10)

                col += 1

            except Exception as e:

                print("Driver Image Error :", e)

    except Exception as e:

        print("Driver Load Error :", e)


# =========================================================
# LOGS TAB
# =========================================================

logs_title = tk.Label(

    logs_tab,

    text="DRIVER STATE LOGS",

    font=("Arial",24,"bold"),

    fg="white",

    bg="#0d0d0d"
)

logs_canvas = tk.Canvas(

    logs_tab,

    bg="#0d0d0d",

    highlightthickness=0
)

logs_canvas.pack(

    fill="both",

    expand=True
)




# =========================================================
# LOAD LOGS
# =========================================================

def load_logs():

    global logs_canvas

    logs_canvas.delete("all")

    try:

        conn = sqlite3.connect("data/users.db")

        cur = conn.cursor()

        cur.execute(

            "SELECT username, state, time FROM logs ORDER BY id DESC LIMIT 30"

        )

        rows = cur.fetchall()

        conn.close()

        y = 20

        for row in rows:

            username = row[0]

            state = row[1]

            timestamp = row[2]

            # ==================================
            # COLORS
            # ==================================

            color = "#00ff99"

            if state == "Critical":

                color = "#ff0033"

            elif state == "Drowsy":

                color = "#ffaa00"

            elif state == "Mobile Usage":

                color = "#00ccff"

            # ==================================
            # LOG CARD
            # ==================================

            logs_canvas.create_rectangle(

                20,

                y,

                900,

                y + 70,

                fill="#111111",

                outline=color,

                width=2

            )

            logs_canvas.create_text(

                40,

                y + 20,

                anchor="w",

                text=f"USER : {username}",

                fill="white",

                font=("Arial",12,"bold")

            )

            logs_canvas.create_text(

                40,

                y + 45,

                anchor="w",

                text=f"STATE : {state}",

                fill=color,

                font=("Arial",12)

            )

            logs_canvas.create_text(

                600,

                y + 45,

                anchor="w",

                text=f"TIME : {timestamp}",

                fill="cyan",

                font=("Arial",10)

            )

            y += 90

    except Exception as e:

        print("LOG ERROR :", e)

    root.after(2000, load_logs)




reports_title = tk.Label(

    reports_tab,

    text="AI REPORTS & EXPORTS",

    font=("Arial",24,"bold"),

    fg="cyan",

    bg="#0d0d0d"
)



reports_title.pack(pady=20)
def save_graph():

    fig.savefig("analytics_graph.png")

    print("GRAPH SAVED")


save_graph_btn = tk.Button(

    analytics_tab,

    text="SAVE GRAPH",

    font=("Arial",14,"bold"),

    bg=CYAN,

    fg="black",

    command=save_graph
)

save_graph_btn.pack(pady=20)


export_btn = tk.Button(

    reports_tab,

    text="EXPORT DRIVER REPORTS",

    font=("Arial",16,"bold"),

    bg=CYAN,

    fg="black",

    width=25,

    height=2,

    command=export_logs
)

export_btn.pack(pady=30)

# pdf_btn = Button(
#     root,
#     text="Export PDF",
#     command=export_pdf
# )

# pdf_btn.pack()



analytics_title = tk.Label(

    analytics_tab,

    text="ADVANCED AI ANALYTICS",

    font=("Arial",24,"bold"),

    fg="cyan",

    bg="#0d0d0d"
)

analytics_title.pack(pady=20)


    


# =========================================================
# START SERVICES
# =========================================================

start_voice_monitor()

load_drivers()





load_logs()

# =========================================================
# MAIN
# =========================================================
update_camera()

update_analytics()


root.mainloop()