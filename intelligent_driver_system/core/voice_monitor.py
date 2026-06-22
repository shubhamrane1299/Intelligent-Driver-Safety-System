
import speech_recognition as sr
import threading
import time

running = False

def listen_loop():

    global running

    recognizer = sr.Recognizer()

    mic = sr.Microphone()

    with mic as source:

        recognizer.adjust_for_ambient_noise(

            source,

            duration=1
        )

    while running:

        try:

            with mic as source:

                print("Listening...")

                audio = recognizer.listen(

                    source,

                    timeout=3,

                    phrase_time_limit=4
                )

            text = recognizer.recognize_google(

                audio
            )

            print("VOICE :", text)

        except sr.WaitTimeoutError:

            pass

        except sr.UnknownValueError:

            pass

        except Exception as e:

            print("Voice Error :", e)

        time.sleep(1)

def start_voice_monitor():

    global running

    if running:

        return

    running = True

    threading.Thread(

        target=listen_loop,

        daemon=True

    ).start()

def stop_voice_monitor():

    global running

    running = False

