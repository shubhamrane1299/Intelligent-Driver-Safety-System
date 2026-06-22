import pywhatkit as kit
import threading

PHONE_NUMBER = "+919529600747"

def send_sos():

    try:

        message = '''

🚨 DRIVER EMERGENCY 🚨

Possible:
- Drowsiness
- Unsafe condition
- Driver asked for help

Please contact immediately.
'''

        print("SENDING SOS...")

        kit.sendwhatmsg_instantly(

            PHONE_NUMBER,

            message,

            wait_time=20,

            tab_close=True,

            close_time=15

        )

        print("SOS SENT")

    except Exception as e:

        print("SOS ERROR:",e)

def send_sos_thread():

    threading.Thread(

        target=send_sos,

        daemon=True

    ).start()