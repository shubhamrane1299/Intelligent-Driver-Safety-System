
import pygame
import pyttsx3
import time

# ==========================================
# INIT
# ==========================================

pygame.init()

pygame.mixer.init()

# ==========================================
# CHANNELS
# ==========================================

voice_channel = pygame.mixer.Channel(0)

alert_channel = pygame.mixer.Channel(1)

# ==========================================
# VOICE ENGINE
# ==========================================

engine = pyttsx3.init()

engine.setProperty('rate', 165)

voices = engine.getProperty('voices')

if len(voices) > 1:

    engine.setProperty(

        'voice',

        voices[1].id

    )


# ==========================================
# COOLDOWN
# ==========================================

last_alert_time = 0

ALERT_COOLDOWN = 2

# ==========================================
# SOUND FILES
# ==========================================

sound_files = {

    "Drowsy": "sounds/drowsy.mp3",

    "Critical": "sounds/critical.mp3",

    "Yawning": "sounds/yawn.mp3",

    "Looking Left": "sounds/left.mp3",

    "Looking Right": "sounds/right.mp3",

    "Looking Down": "sounds/down.mp3",

    "Looking Up": "sounds/up.mp3",

    "Mobile Usage": "sounds/mobile.mp3",

    "No Face": "sounds/no_face.mp3"
}


# ==========================================
# BEEP / SIREN SOUNDS
# ==========================================


# ==========================================
# ALERT SOUNDS
# ==========================================

beep_sounds = {

    "Drowsy": "sounds/beep.mp3",

    "Critical": "sounds/siren.mp3",

    "Yawning": "sounds/yawn_alert.mp3",

    "Looking Left": "sounds/left_alert.mp3",

    "Looking Right": "sounds/right_alert.mp3",

    "Looking Down": "sounds/down_alert.mp3",

    "Looking Up": "sounds/up_alert.mp3",

    "Mobile Usage": "sounds/mobile_alert.mp3",

    "No Face": "sounds/warning.mp3"
}



# ==========================================
# MAIN ALERT
# ==========================================

# ==========================================
# MAIN ALERT
# ==========================================

def trigger_alert(state):

    global last_alert_time

    current_time = time.time()

    # ======================================
    # NORMAL
    # ======================================

    if state == "Normal":

        pygame.mixer.stop()

        engine.stop()

        return

    # ======================================
    # COOLDOWN
    # ======================================

    if current_time - last_alert_time < ALERT_COOLDOWN:

        return

    last_alert_time = current_time

    try:

        # ==================================
        # STOP PREVIOUS ALERT
        # ==================================

        pygame.mixer.stop()

        engine.stop()

        # ==================================
        # MAIN VOICE SOUND
        # ==================================

        if state in sound_files:

            pygame.mixer.music.load(

                sound_files[state]

            )

            pygame.mixer.music.set_volume(1.0)

            pygame.mixer.music.play()

        # ==================================
        # EXTRA ALERT SOUND
        # ==================================

        if state in beep_sounds:

            extra_sound = pygame.mixer.Sound(

                beep_sounds[state]

            )

            alert_channel.play(extra_sound)

        # ==================================
        # SPEECH
        # ==================================

        engine.say(state)

        engine.runAndWait()

    except Exception as e:

        print("ALERT ERROR :", e)
        


# ==========================================
# STOP ALERTS
# ==========================================

def stop_alerts():

    try:

        pygame.mixer.music.stop()

        engine.stop()

    except:
        pass

# ==========================================
# SOS
# ==========================================

def send_sos(user, state, gps_data):

    print("SOS SENT")

