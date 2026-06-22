import sqlite3
from collections import Counter

# ==========================================
# GET DRIVER STATS
# ==========================================

def get_driver_stats(username):

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute(
        "SELECT state FROM logs WHERE username=?",
        (username,)
    )

    rows = cur.fetchall()

    conn.close()

    states = [r[0] for r in rows]

    total = len(states)

    counter = Counter(states)

    return {

        "total_logs": total,

        "normal": counter.get("Normal", 0),

        "drowsy": counter.get("Drowsy", 0),

        "critical": counter.get("Critical", 0),

        "mobile": counter.get("Mobile Usage", 0),

        "yawning": counter.get("Yawning", 0),

        "no_face": counter.get("No Face", 0)
    }

# ==========================================
# GET ALL DRIVERS
# ==========================================

def get_all_drivers():

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute(
        "SELECT username FROM users"
    )

    rows = cur.fetchall()

    conn.close()

    return [r[0] for r in rows]