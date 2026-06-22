from collections import deque
import time

# store last 100 states
history = deque(maxlen=100)

# weight system
weights = {
    "Normal": 0,
    "Yawning": 2,
    "Drowsy": 4,
    "Very Drowsy": 6,
    "Critical": 10,
    "Looking Left": 2,
    "Looking Right": 2,
    "Looking Down": 3
}

def update_score(state):
    history.append((state, time.time()))

def get_score():
    if not history:
        return 0

    total = 0
    for s, _ in history:
        total += weights.get(s, 0)

    return round(total / len(history), 2)