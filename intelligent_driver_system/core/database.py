import sqlite3
import os

def init_db():
    init_trip_table()

    os.makedirs("data/faces", exist_ok=True)

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        face_path TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        state TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    
    

# ==========================================
# CREATE TRIPS TABLE
# ==========================================

def init_trip_table():

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute("""

    CREATE TABLE IF NOT EXISTS trips(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        start_time TEXT,

        end_time TEXT,

        duration TEXT
    )

    """)

    conn.commit()

    conn.close()    
# ==========================================
# START TRIP
# ==========================================

def start_trip(username, start_time):

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute("""

    INSERT INTO trips(username,start_time,end_time,duration)

    VALUES(?,?,?,?)

    """,

    (username, start_time, "", "")
    )

    conn.commit()

    conn.close()    

# ==========================================
# END TRIP
# ==========================================

def end_trip(username, end_time, duration):

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute("""

    UPDATE trips

    SET end_time=?, duration=?

    WHERE id=(

        SELECT id FROM trips

        WHERE username=?

        ORDER BY id DESC LIMIT 1
    )

    """,

    (end_time, duration, username)
    )

    conn.commit()

    conn.close()
    
def log_event(username, state):

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO logs(username,state) VALUES(?,?)",
        (username, state)
    )

    conn.commit()
    conn.close()
    
def init_reports_table():
    
    conn = sqlite3.connect("data/users.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        trip_date TEXT,
        duration TEXT,
        drowsy_count INTEGER,
        yawn_count INTEGER,
        mobile_count INTEGER,
        distraction_count INTEGER,
        pdf_path TEXT,
        graph_path TEXT
    )
    """)

    conn.commit()
    conn.close()
    
def init_db():
    
    init_trip_table()
    init_reports_table()
    
def save_report(
        username,
        trip_date,
        duration,
        drowsy,
        yawn,
        mobile,
        distraction,
        pdf_path,
        graph_path):

    conn = sqlite3.connect("data/users.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO reports(
        username,
        trip_date,
        duration,
        drowsy_count,
        yawn_count,
        mobile_count,
        distraction_count,
        pdf_path,
        graph_path
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,
    (
        username,
        trip_date,
        duration,
        drowsy,
        yawn,
        mobile,
        distraction,
        pdf_path,
        graph_path
    ))

    conn.commit()
    conn.close()        
        